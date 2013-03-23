"""
Запускайте этот модуль для старта системы выявления плагиата с параметрами
по умолчанию.
Получение списка параметров: python __init__.py -h
                             или
                             python __init__.py --help
Параметры следующие:
    -mongo_port MONGO_PORT (номер порта, по которому доступен сервер MongoDB)
    -mongo_db DATABASE_NAME (название базы данных, используемой системой)
    -port WEB_SERVER_PORT(номер порта, на котором будет запущен веб-сервер)
"""

import random
import string
import time
import threading
import os.path
import urllib.parse
import argparse

import tornado.ioloop
from tornado.web import authenticated
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments import highlight

from core import Antiplagiarism, TextError, random_string


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        current_user = self.get_secure_cookie('username')
        if current_user:
            return current_user
        else:
            self.clear_all_cookies()


class LoginHandler(BaseHandler):
    def get(self):
        error_missing_fields = self.get_argument('error_missing_fields', None)
        error_wrong_user = self.get_argument('error_wrong_user', None)
        if error_missing_fields:
            self.render('login.html', next=self.get_argument('next', '/'),
                        error_missing_fields=True)
        elif error_wrong_user:
            self.render('login.html', next=self.get_argument('next', '/'),
                        error_wrong_user=True)
        else:
            self.render('login.html', next=self.get_argument('next', '/'))

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        next_step = self.get_argument('next', '/')
        if username and password:
            if antiplagiarism.check_user(username, password):
                self.set_secure_cookie('username', username)
                self.redirect(next_step)
            else:
                self.redirect('/login?error_wrong_user=True&%s' %
                              urllib.parse.urlencode({'next': next_step}),
                              True)
        else:
            self.redirect('/login?error_missing_fields=True&%s' %
                          urllib.parse.urlencode({'next': next_step}), True)


class CheckHandler(BaseHandler):
    def get(self):
        if self.get_argument('result_id', None):
            self.render('check.html', result_id=self.get_argument('result_id'))
        else:
            courses = antiplagiarism.get_courses()
            collections = {course_id: antiplagiarism.get_text_groups(course_id)
                           for course_id in courses}
            if self.get_argument('error_large_file', None) == 'True':
                self.render('check.html', courses=courses, upload=True,
                            collections=collections, error_large_file=True)
            elif self.get_argument('error_missed_file', None) == 'True':
                self.render('check.html', courses=courses, upload=True,
                            collections=collections, error_missed_file=True)
            elif self.get_argument('parse_error', None):
                self.render('check.html', courses=courses, upload=True,
                            parse_error=self.get_argument('parse_error'),
                            collections=collections)
            else:
                self.render('check.html', upload=True, courses=courses,
                            collections=collections)

    def post(self):
        if int(self.request.headers.get('Content-Length')) > 1048576:
            self.redirect('/check?error_large_file=True', True)
        else:
            data = self.request.files.get('data')
            collection_id = self.get_argument('collection_id', None)
            if data and collection_id:
                try:
                    raw = data[0]['body']
                    result_id = antiplagiarism.schedule_simple_check(raw,
                                                                 collection_id)
                except TextError as e:
                    self.redirect('/check?%s' % urllib.parse.urlencode(
                                                {'parse_error': str(e)}), True)
                else:
                    self.redirect('/check?result_id=%s' % result_id, True)
            else:
                self.redirect('/check?error_missed_file=True', True)


class AdvancedCheckHandler(BaseHandler):
    @authenticated
    def get(self):
        if self.get_argument('step', None) == '1':
            self.render('advanced_check.html', step=1)
        elif self.get_argument('step', None) == '2' and \
                self.get_argument('text_id', None):
            current_user = tornado.escape.xhtml_escape(self.current_user)
            if current_user == 'admin':
                courses = antiplagiarism.get_courses()
            else:
                courses = antiplagiarism.get_courses(
                                tornado.escape.xhtml_escape(self.current_user))
            collections = {course_id: antiplagiarism.get_text_groups(course_id)
                           for course_id in courses}
            self.render('advanced_check.html', step=2, courses=courses,
                        collections=collections)
        elif self.get_argument('error_large_file', None) == 'True':
            self.render('advanced_check.html', error_large_file=True, step=1)
        elif self.get_argument('parse_error', None):
            self.render('advanced_check.html', step=1,
                        parse_error=self.get_argument('parse_error'))
        elif self.get_argument('error_missed_file', None) == 'True':
            self.render('advanced_check.html', error_missed_file=True, step=1)
        else:
            self.render('advanced_check.html', step=1)

    @authenticated
    def post(self):
        if int(self.request.headers.get('Content-Length')) > 1048576:
            self.redirect('/advanced_check?error_large_file=True', True)
        else:
            data = self.request.files.get('data')
            if data:
                try:
                    raw = data[0]['body']
                    text_id = antiplagiarism.add_temporary_file(raw)
                except TextError as e:
                    self.redirect('/advanced_check?%s' %
                         urllib.parse.urlencode({'parse_error': str(e)}), True)
                else:
                    self.redirect('/advanced_check?step=2&text_id=%s' %
                                  text_id, True)
            else:
                self.redirect('/advanced_check?error_missed_file=True', True)


class ResultHandler(BaseHandler):
    def get(self):
        result_id = self.get_argument('result_id', None)
        if result_id:
            result = antiplagiarism.get_requested_result(result_id)
            if result is not None:
                if type(result) is dict:
                    res = '%s;%s' % (result['completed'],
                                     ';'.join(['%s:%s' % (r[0], r[1])
                                               for r in result['result']]))
                    self.finish(res)
                else:
                    self.finish(str(result))
            else:
                self.finish()
        else:
            raise tornado.web.HTTPError(404)


class TextsHandler(BaseHandler):
    @authenticated
    def get(self):
        collection_id = self.get_argument('collection_id', None)
        if collection_id:
            texts = antiplagiarism.get_texts(collection_id)
            self.write(';'.join(['%s,%s' % (text[0], text[1])
                                 for text in texts]))


class TextHandler(BaseHandler):
    @authenticated
    def get(self):
        text_id = self.get_argument('text_id', None)
        if text_id and text_id != '0':
            lexer = get_lexer_by_name('delphi', stripall=True)
            formatter = HtmlFormatter(linenos='inline', cssclass='delphi',
                                      full=True)
            text = antiplagiarism.get_text(text_id)
            self.write(highlight(text, lexer, formatter))


class TemporaryTextHandler(BaseHandler):
    @authenticated
    def get(self):
        text_id = self.get_argument('text_id', None)
        if text_id:
            lexer = get_lexer_by_name('delphi', stripall=True)
            formatter = HtmlFormatter(linenos='inline', cssclass='delphi',
                                      full=True)
            text = antiplagiarism.get_temporary_text(text_id)
            self.write(highlight(text, lexer, formatter))


class CompareHandler(BaseHandler):
    @authenticated
    def get(self):
        collection_id = self.get_argument('collection_id', None)
        temporary_text_id = self.get_argument('temporary_text_id', None)
        existing_text_id = self.get_argument('existing_text_id', None)
        if collection_id and temporary_text_id:
            result_id = antiplagiarism.schedule_advanced_check(
                                temporary_text_id, text_group_id=collection_id)
            self.write(result_id)
        elif temporary_text_id and existing_text_id:
            result_id = antiplagiarism.schedule_advanced_check(
                                           temporary_text_id, existing_text_id)
            self.write(result_id)


class ExitHandler(BaseHandler):
    def post(self):
        self.clear_all_cookies()
        self.redirect('/')


class AdminHandler(BaseHandler):
    @authenticated
    def get(self):
        current_user = tornado.escape.xhtml_escape(self.current_user)
        if current_user == 'admin':
            teachers = antiplagiarism.get_teachers()
            error = self.get_argument('error', None)
            user_added = self.get_argument('user_added', None)
            if error:
                self.render('admin.html', is_admin=True, teachers=teachers,
                            error=error)
            elif user_added:
                self.render('admin.html', is_admin=True, teachers=teachers,
                            user_added=True)
            else:
                self.render('admin.html', is_admin=True, teachers=teachers)
        else:
            parse_error = self.get_argument('parse_error', None)
            error_missing_fields = self.get_argument('error_missing_fields',
                                                     None)
            error_large_file = self.get_argument('error_large_file', None)
            unknown_collection = self.get_argument('unknown_collection', None)
            uploaded = self.get_argument('uploaded', None)
            courses = antiplagiarism.get_courses(current_user)
            #тут надо покрасивее сделать как-то
            if parse_error:
                self.render('admin.html', is_admin=False, courses=courses,
                            parse_error=parse_error)
            elif error_missing_fields:
                self.render('admin.html', is_admin=False, courses=courses,
                            error_missing_fields=error_missing_fields)
            elif error_large_file:
                self.render('admin.html', is_admin=False, courses=courses,
                            error_large_file=error_large_file)
            elif unknown_collection:
                self.render('admin.html', is_admin=False, courses=courses,
                            unknown_collection=unknown_collection)
            elif uploaded:
                self.render('admin.html', is_admin=False, courses=courses,
                            uploaded=uploaded)
            else:
                self.render('admin.html', is_admin=False, courses=courses)


class AddTeacherHandler(BaseHandler):
    @authenticated
    def post(self):
        if tornado.escape.xhtml_escape(self.current_user) == 'admin':
            name = self.get_argument('name', None)
            username = self.get_argument('username', None)
            password = self.get_argument('password', None)
            if name and username and password:
                result = antiplagiarism.add_teacher(name, username, password)
                if result == '-1':
                    self.redirect('/admin?error=duplicate', True)
                    return
                else:
                    self.redirect('/admin?user_added=True', True)
            else:
                self.redirect('/admin?error=missing_fields', True)


class RemoveTeacherHandler(BaseHandler):
    @authenticated
    def get(self):
        if tornado.escape.xhtml_escape(self.current_user) == 'admin':
            teacher_id = self.get_argument('id', None)
            if teacher_id:
                self.write(antiplagiarism.remove_teacher(teacher_id))


class AddCourseHandler(BaseHandler):
    @authenticated
    def post(self):
        current_user = tornado.escape.xhtml_escape(self.current_user)
        if current_user != 'admin':
            name = self.get_argument('name', None)
            if name:
                self.write(antiplagiarism.add_course(name, current_user))
            else:
                self.write('-1')
        else:
            self.write('-1')


class RemoveCourseHandler(BaseHandler):
    @authenticated
    def get(self):
        current_user = tornado.escape.xhtml_escape(self.current_user)
        if current_user != 'admin':
            course_id = self.get_argument('id', None)
            if course_id and \
                    antiplagiarism.check_rights(username=current_user,
                                                   course_id=course_id):
                self.write(antiplagiarism.remove_course(course_id))
            else:
                self.write('-1')


class AddCollectionHandler(BaseHandler):
    @authenticated
    def post(self):
        current_user = tornado.escape.xhtml_escape(self.current_user)
        if current_user != 'admin':
            name = self.get_argument('name', None)
            course_id = self.get_argument('course_id', None)
            if name and course_id and antiplagiarism.check_rights(
                                   username=current_user, course_id=course_id):
                self.write(antiplagiarism.add_text_group(name, course_id))
            else:
                self.write('-1')
        else:
            self.write('-1')


class CollectionsHandler(BaseHandler):
    @authenticated
    def get(self):
        if tornado.escape.xhtml_escape(self.current_user) != 'admin':
            course_id = self.get_argument('course_id', None)
            if course_id:
                collections = antiplagiarism.get_text_groups(course_id)
                self.write(';'.join(['%s,%s' % (collection[0], collection[1])
                                     for collection in collections]))


class RemoveCollectionHandler(BaseHandler):
    @authenticated
    def get(self):
        current_user = tornado.escape.xhtml_escape(self.current_user)
        if current_user != 'admin':
            collection_id = self.get_argument('id', None)
            if collection_id and antiplagiarism.check_rights(
                           username=current_user, text_group_id=collection_id):
                self.write(antiplagiarism.remove_text_group(collection_id))
            else:
                self.write('-1')


class AddTextHandler(BaseHandler):
    @authenticated
    def post(self):
        current_user = tornado.escape.xhtml_escape(self.current_user)
        if current_user != 'admin':
            collection_id = self.get_argument('collection_id', None)
            name = self.get_argument('name', None)
            if not (collection_id and name):
                self.redirect('/admin?error_missing_fields=True', True)
                return
            if not antiplagiarism.check_rights(username=current_user,
                                                  text_group_id=collection_id):
                self.redirect('/admin?unknown_collection=True', True)
                return
            if int(self.request.headers.get('Content-Length')) > 1048576:
                self.redirect('/admin?error_large_file=True', True)
            else:
                data = self.request.files.get('data')
                if data:
                    try:
                        raw = data[0]['body']
                        if antiplagiarism.add_text(raw, name,
                                                   collection_id) == '-1':
                            self.redirect('/admin?unknown_collection=True',
                                          True)
                    except TextError as e:
                        self.redirect('/admin?%s' % urllib.parse.urlencode(
                                                {'parse_error': str(e)}), True)
                    else:
                        self.redirect('/admin?uploaded=True', True)
                else:
                    self.redirect('/admin?error_missing_fields=True', True)


class RemoveTextHandler(BaseHandler):
    @authenticated
    def get(self):
        current_user = tornado.escape.xhtml_escape(self.current_user)
        if current_user != 'admin':
            text_id = self.get_argument('id', None)
            if text_id and antiplagiarism.check_rights(username=current_user,
                                                       text_id=text_id):
                self.write(antiplagiarism.remove_text(text_id))
            else:
                self.write('-1')


class ClearTempHandler(BaseHandler):
    @authenticated
    def get(self):
        if tornado.escape.xhtml_escape(self.current_user) == 'admin':
            antiplagiarism.clear_temp()


class ClearResultsHandler(BaseHandler):
    @authenticated
    def get(self):
        if tornado.escape.xhtml_escape(self.current_user) == 'admin':
            antiplagiarism.clear_results()


if __name__ == "__main__":
    commands_parser = argparse.ArgumentParser()
    commands_parser.add_argument('-mongo_port', default=27017,
                                 help='port of MongoDB instance')
    commands_parser.add_argument('-mongo_db', metavar='DATABASE_NAME',
                                 help='name of database',
                                 default='antiplagiarism')
    commands_parser.add_argument('-port', metavar='WEB_SERVER_PORT',
                                 help='port for web server', default='8888')
    arguments = commands_parser.parse_args()
    antiplagiarism = Antiplagiarism(int(arguments.mongo_port),
                                    arguments.mongo_db)
    settings = {'cookie_secret': random_string(32),
                'login_url': '/login',
                'static_path': os.path.join(os.path.dirname(__file__),
                                            'static'),
                'template_path': os.path.join(os.path.dirname(__file__),
                                            'templates')}
    request_handlers = [('/', CheckHandler),
                        ('/login', LoginHandler),
                        ('/check', CheckHandler),
                        ('/advanced_check', AdvancedCheckHandler),
                        ('/result', ResultHandler),
                        ('/texts', TextsHandler),
                        ('/text', TextHandler),
                        ('/temporary_text', TemporaryTextHandler),
                        ('/compare', CompareHandler),
                        ('/exit', ExitHandler),
                        ('/admin', AdminHandler),
                        ('/add_teacher', AddTeacherHandler),
                        ('/remove_teacher', RemoveTeacherHandler),
                        ('/add_course', AddCourseHandler),
                        ('/remove_course', RemoveCourseHandler),
                        ('/add_collection', AddCollectionHandler),
                        ('/collections', CollectionsHandler),
                        ('/remove_collection', RemoveCollectionHandler),
                        ('/add_text', AddTextHandler),
                        ('/remove_text', RemoveTextHandler),
                        ('/clear_temp', ClearTempHandler),
                        ('/clear_results', ClearResultsHandler)]
    application = tornado.web.Application(request_handlers, **settings)
    application.listen(arguments.port)
    tornado.ioloop.IOLoop.instance().start()
