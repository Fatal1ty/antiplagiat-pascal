"""
Модуль является связующим звеном между модулем веб-интерфейса и базой данных.
Здесь находятся методы, необходимые непосредственно для работы системы
выявления плагиата (сравнение, добавление преподавателей, курсов и пр.).
"""

import tempfile
import os
import random
import string
import threading
import hashlib
import datetime

import pymongo
import ply.lex as lex
import ply.yacc as yacc

import trees
import rules
from bson.objectid import ObjectId


def random_string(length):
    return ''.join([random.choice(string.printable) for i in range(length)])


def check_for_pascal(filename):
    """
    @raise TextError: когда текст в файле filename не соответствует стандарту
                      ISO 10206 или текст в неизвестной кодировке.
    Возвращает текст, содержащийся в файле с именем filename, если он
    соответствует стандарту ISO 10206.
    """
    parser = Parser()
    decoded = False
    parsed = False
    error = None
    try:
        with open(filename, encoding='utf_8_sig') as f:  # UTF-8 с BOM
            text = f.read()
            if not text:
                raise TextError('Ваш файл пуст')
    except UnicodeDecodeError:
        pass
    else:
        decoded = True
        try:
            parser.parse_text(text.lower())
            parsed = True
        except (rules.PascalLexicalError, rules.PascalSyntaxError) as e:
            error = e
    if not parsed:
        try:
            with open(filename, encoding='utf_8') as f:  # UTF-8 без BOM
                text = f.read()
                if not text:
                    raise TextError('Ваш файл пуст')
        except UnicodeDecodeError:
            pass
        else:
            decoded = True
            try:
                parser.parse_text(text.lower())
                parsed = True
            except (rules.PascalLexicalError, rules.PascalSyntaxError) as e:
                if not error or (type(error) is rules.PascalLexicalError and \
                                 type(e) is rules.PascalSyntaxError):
                    error = e
    if not parsed:
        try:
            with open(filename, encoding='cp1251') as f:  # Windows-1251
                text = f.read()
                if not text:
                    raise TextError('Ваш файл пуст')
        except UnicodeDecodeError:
            pass
        else:
            decoded = True
            try:
                parser.parse_text(text.lower())
                parsed = True
            except (rules.PascalLexicalError, rules.PascalSyntaxError) as e:
                if not error or (type(error) is rules.PascalLexicalError and \
                                 type(e) is rules.PascalSyntaxError):
                    error = e
    if parsed:
        return text.lower()
    if not decoded:
        raise TextError('Ваш текст в неизвестной кодировке')
    else:
        raise TextError('Ваш текст не соответствует стандарту ИСО 10206 (%s)' %
                        str(error))


class TextError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return str(self.text)


class Parser:
    def __init__(self):
        lex.lex(module=rules)
        yacc.yacc(module=rules)

    def parse(self, file):
        with open(file) as f:
            text = f.read().lower()
            return yacc.parse(text, debug=0)  # @UndefinedVariable

    def parse_text(self, text):
        self.__init__()  # bug http://code.google.com/p/ply/issues/detail?id=20
        return yacc.parse(text, debug=0)  # @UndefinedVariable


class Antiplagiarism:
    """
    Связующее звено между модулем веб-сервера и базой данных. Позволяет
    выполнять операции добавления и удаления пользователей, курсов, тестовых
    наборов, текстов, очищать старые загружавшиеся тексты и результаты
    проверок и пр.
    """
    def __init__(self, mongo_port=27017,
                 mongo_db='antiplagiarism', create=False):
        """
        Если create, то база данных mongo_db сначала дропается.
        """
        mongo_host = 'localhost'
        self.connection = pymongo.Connection(mongo_host, mongo_port)
        if create:
            self.connection.drop_database(mongo_db)
        self.db = self.connection[mongo_db]
        self.clear_temp(0)
        print('All temporary texts removed')

    def compare_texts(self, text1, text2):
        """
        Сравнивает два текста text1, text2, возвращает коэффициент их схожести.
        """
        parser = Parser()
        tree1_dict = parser.parse_text(text1)
        tree2_dict = parser.parse_text(text2)
        if tree1_dict == tree2_dict:
            return 1
        tree1 = trees.dict_to_tree(parser.parse_text(text1))
        tree2 = trees.dict_to_tree(parser.parse_text(text2))
        return trees.compare_trees(tree1, tree2)

    def get_courses(self, teacher_username=None):
        """
        Возвращает список курсов
        преподавателя teacher_username в виде {id: name}.
        """
        if teacher_username:
            teacher = self.db.users.find_one({'username': teacher_username})
            if teacher:
                teacher_id = str(teacher['_id'])
                return {str(course['_id']): course['name']
                        for course in self.db.courses.find({'teacher_id':
                                                            teacher_id})}
            else:
                return {}
        else:
            return {str(course['_id']): course['name']
                    for course in self.db.courses.find()}

    def get_text(self, text_id):
        """
        Возвращает текст с ид. text_id.
        """
        document = self.db.texts.find_one({'_id': ObjectId(text_id)})
        return document['text']

    def get_texts(self, group_id):
        """
        Возвращает список названий текстов тестового набора с ид. group_id.
        """
        return [(str(document['_id']), document['name'])
                for document in self.db.texts.find({'group_id': group_id})]

    def get_requested_result(self, result_id):
        """
        Возвращает результат сравнения из БД. Результат может быть:
        1) вещественное число, если проверка окончена, иначе None;
        2) dict {'completed': True | False, result: []}, где result переменной
        длины. Если проверка окончена, то 'completed' == True.
        """
        document = self.db.results.find_one({'_id': ObjectId(result_id)})
        if document is not None:
            result = document.get('result')
            if type(result) is list:
                return {'completed': document['completed'], 'result': result}
            else:
                return result
        else:
            return -1

    def schedule_simple_check(self, raw, text_group_id):
        """
        Запускает в новом потоке упрощенную проверку.
        raw - сырые данные на проверку,
        text_group_id - ид. тестового набора из коллекции text_groups.
        Возвращает ид. результата, который потом
        надо получать с помощью get_requested_result
        """
        text = self.__raw_to_text(raw)
        result_id = self.db.results.insert({'result': None})
        threading.Thread(target=self.__simple_check_with_group,
                         args=(result_id, text, text_group_id)).start()
        return str(result_id)

    def __simple_check_with_group(self, result_id, text, text_group_id):
        ratio = 0
        max_ratio = 0
        for document in self.db.texts.find({'group_id': text_group_id}):
            ratio = self.compare_texts(text, document['text'])
            if ratio > max_ratio:
                if ratio == 1:
                    break
                max_ratio = ratio
        self.db.results.update({'_id': result_id},
                               {'$set': {'result': round(ratio, 2),
                                         'datetime': datetime.datetime.now()}})

    def schedule_advanced_check(self, temporary_text_id, existing_text_id=None,
                                text_group_id=None):
        """
        Запускает в новом потоке расширенную проверку.
        temporary_text_id - ид. временного текста из коллекции temp,
        existing_text_id - ид. текста из коллекции texts,
        text_group_id - ид. тестового набора из коллекции text_groups.
        Указывать надо либо existing_text_id, либо text_group_id.
        Возвращает ид. результата, который потом
        надо получать с помощью get_requested_result
        """
        if text_group_id:
            result_id = self.db.results.insert({'result': [],
                                                'completed': '0'})
            t = threading.Thread(target=self.__advanced_check_with_group,
                                 args=(result_id, temporary_text_id,
                                       text_group_id))
            t.start()
            return str(result_id)
        elif existing_text_id:
            result_id = self.db.results.insert({'result': None})
            t = threading.Thread(target=self.__advanced_check_with_text,
                                 args=(result_id, temporary_text_id,
                                       existing_text_id))
            t.start()
            return str(result_id)

    def __advanced_check_with_text(self, result_id, temporary_text_id,
                            existing_text_id):
        temporary_text = self.db.temp.find_one({'_id':
                                                ObjectId(temporary_text_id)})
        existing_text = self.db.texts.find_one({'_id':
                                                ObjectId(existing_text_id)})
        if temporary_text and existing_text:
            temporary_text = temporary_text['text']
            existing_text = existing_text['text']
            ratio = self.compare_texts(temporary_text, existing_text)
            now = datetime.datetime.now()
            self.db.results.update({'_id': result_id},
                    {'$set': {'result': round(ratio, 2), 'datetime': now}})
        else:
            self.db.results.update({'_id': result_id},
                                   {'$set': {'result': -1, 'datetime':
                                             datetime.datetime.now()}})

    def __advanced_check_with_group(self, result_id, temporary_text_id,
                                  group_id):
        temporary_text = self.db.temp.find_one({'_id':
                                                ObjectId(temporary_text_id)})
        if temporary_text:
            temporary_text = temporary_text['text']
            for text in self.db.texts.find({'group_id': group_id}):
                ratio = self.compare_texts(temporary_text, text['text'])
                text_id = str(text['_id'])
                self.db.results.update({'_id': result_id},
                                       {'$push': {'result': [text_id,
                                                            round(ratio, 2)]}})
            self.db.results.update({'_id': result_id},
                                   {'$set': {'completed': '1', 'datetime':
                                             datetime.datetime.now()}})
        else:
            self.db.results.update({'_id': result_id},
                                   {'$set': {'completed': '1', 'datetime':
                                             datetime.datetime.now()}})

    def __raw_to_text(self, raw):
        """
        Возвращае текст из сырых данных raw.
        """
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(raw)
        f.close()
        try:
            text = check_for_pascal(f.name)
            text = text.lower()
            return text
        except TextError:
            raise
        finally:
            os.remove(f.name)

    def add_temporary_file(self, raw):
        """
        Добавляет временный загружаемый файл с сырыми данными raw.
        Возвращает ид.
        """
        text = self.__raw_to_text(raw)
        document_id = self.db.temp.insert({'text': text,
                                    'datetime': datetime.datetime.now()})
        return str(document_id)

    def get_temporary_text(self, text_id):
        """
        Возвращает текст временного загруженного файла с ид. text_id.
        """
        document = self.db.temp.find_one({'_id': ObjectId(text_id)})
        if document is not None:
            return document['text']

    def get_teachers(self):
        """
        Возвращает список преподавателей в виде {id: name}
        """
        teachers = {str(document['_id']): document['name']
                    for document in self.db.users.find({'username':
                                                        {'$ne': 'admin'}})}
        return teachers

    def add_teacher(self, name, username, password):
        """
        Добавляет преподавателя, пароль хешируется SHA1 с солью. Возвращает ид.
        """
        if self.db.users.find_one({'username': username}):
            return '-1'
        salt = random_string(40).encode()
        h = hashlib.sha1(password.encode() + salt).hexdigest()
        document_id = self.db.users.insert({'name': name, 'username': username,
                                            'password': h, 'salt': salt})
        return str(document_id)

    def remove_teacher(self, teacher_id):
        """
        Удаляет преподавателя с ид. teacher_id.
        Удалил - '1', нечего удалять - '0'.
        """
        if self.db.users.find_one({'_id': ObjectId(teacher_id),
                                   'username': {'$ne': 'admin'}}):
            for course in self.db.courses.find({'teacher_id': teacher_id}):
                self.remove_course(str(course['_id']))
            self.db.users.remove({'_id': ObjectId(teacher_id)})
            return '1'
        else:
            return '0'

    def add_course(self, name, teacher_username):
        """
        Добавляет курс name преподавателю teacher_username.
        Добавил - ид., преподавателя нет: - '-1', курс уже есть - '0'.
        """
        teacher = self.db.users.find_one({'username': teacher_username})
        if teacher:
            teacher_id = str(teacher['_id'])
            if not self.db.courses.find_one({'name': name,
                                         'teacher_id': teacher_id}):
                teacher_id = self.db.courses.insert({'name': name,
                                                     'teacher_id': teacher_id})
                return str(teacher_id)
            else:
                return '0'
        else:
            return '-1'

    def remove_course(self, course_id):
        """
        Удаляет курс с ид. course_id.
        Удалил - '1', нечего удалять - '0'.
        """
        course = self.db.courses.find_one({'_id': ObjectId(course_id)})
        if course:
            for group in self.db.text_groups.find({'course_id': course_id}):
                self.remove_text_group(str(group['_id']))
            self.db.courses.remove(course)
            return '1'
        else:
            return '0'

    def add_text_group(self, name, course_id):
        """
        Добавляет тестовый набор name в курс с ид. course_id.
        Добавил - ид., курса нет: - '-1', набор уже есть - '0'.
        """
        if not self.db.courses.find_one({'_id': ObjectId(course_id)}):
            return '-1'
        if not self.db.text_groups.find_one({'course_id': course_id,
                                             'name': name}):
            group_id = self.db.text_groups.insert({'course_id': course_id,
                                            'name': name})
            return str(group_id)
        else:
            return '0'

    def get_text_groups(self, course_id):
        """
        Возвращает список тестовых наборов
        курса с ид. course_id в виде {id: name}
        """
        return [[str(group['_id']), group['name']] for
                group in self.db.text_groups.find({'course_id': course_id})]

    def remove_text_group(self, group_id):
        """
        Удаляет тестовый набор с ид. group_id.
        Удалил - '1', нечего удалять - '0'.
        """
        group = self.db.text_groups.find_one({'_id': ObjectId(group_id)})
        if group:
            self.db.texts.remove({'group_id': str(group['_id'])})
            self.db.text_groups.remove(group)
            return '1'
        else:
            return '0'

    def add_text(self, raw, name, group_id):
        """
        Добавляет текст с сырыми данными raw, названием name в тестовый
        набор с ид. group_id. Возвращает ид.
        """
        if not self.db.text_groups.find_one({'_id': ObjectId(group_id)}):
            return '-1'
        text = self.__raw_to_text(raw)
        document_id = self.db.texts.insert({'text': text, 'name': name,
                                            'group_id': group_id})
        return str(document_id)

    def remove_text(self, text_id):
        """
        Удаляет текст с ид. text_id.
        Удалил - '1', нечего удалять - '0'.
        """
        text = self.db.texts.find_one({'_id': ObjectId(text_id)})
        if text:
            self.db.texts.remove(text)
            return '1'
        else:
            return '0'

    def check_user(self, username, password):
        """
        Возвращает True, если такой пользователь есть, иначе False.
        """
        user = self.db.users.find_one({'username': username})
        if user and hashlib.sha1(password.encode() +
                                 user['salt']).hexdigest() == user['password']:
            return True
        else:
            return False

    def clear_temp(self, days=1):
        """
        Удаляет старые документы из коллекции temp.
        """
        self.db.temp.remove({'datetime': {'$lt': datetime.datetime.now() -
                                          datetime.timedelta(days)}})

    def clear_results(self, days=1):
        """
        Удаляет старые документы из коллекции results.
        """
        self.db.results.remove({'datetime': {'$lt': datetime.datetime.now() -
                                             datetime.timedelta(days)}})

    def check_rights(self, username=None, user_id=None, course_id=None,
                        text_group_id=None, text_id=None):
        """
        Проверяет владение курсом, тестового набора или текста
        пользователем с username или ид. user_id. Указывать что-то одно.
        Возвращает True или False.
        """
        if username:
            user = self.db.users.find_one({'username': username})
            if not user:
                return False
            user_id = str(user['_id'])
        if not user_id:
            return False
        if course_id:
            if self.db.courses.find_one({'_id': ObjectId(course_id),
                                         'teacher_id': user_id}):
                return True
            else:
                return False
        elif text_group_id:
            text_group = self.db.text_groups.find_one({'_id':
                                                      ObjectId(text_group_id)})
            if not text_group:
                return False
            else:
                return self.check_rights(user_id=user_id,
                                         course_id=text_group['course_id'])
        elif text_id:
            text = self.db.texts.find_one({'_id': ObjectId(text_id)})
            if not text:
                return False
            else:
                return self.check_rights(user_id=user_id,
                                         text_group_id=text['group_id'])


def deploy(mongo_port, mongo_db, admin_password):
    a = Antiplagiarism(mongo_port, mongo_db, create=True)
    salt = random_string(40).encode()
    h = hashlib.sha1(admin_password.encode() + salt).hexdigest()
    a.db.users.insert({'username': 'admin', 'password': h,
                                    'salt': salt})


if __name__ == '__main__':
    ########## config ##########
    mongo_port = 27017
    mongo_db = 'antiplagiarism'
    admin_password = 'admin'
    ########## theend ##########
    deploy(mongo_port, mongo_db, admin_password)
