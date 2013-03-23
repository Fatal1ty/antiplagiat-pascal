"""
Описание грамматики языка Pascal для синтаксического и лексического анализатора
"""


class PascalSyntaxError(Exception):
    def __init__(self, token_type, token_value, lineno):
        self.token_type = token_type
        self.token_value = token_value
        self.lineno = lineno

    def __str__(self):
        return 'Синтаксическая ошибка вблизи токена %s "%s" на строке %d' %\
                (self.token_type, self.token_value, self.lineno)


class PascalLexicalError(Exception):
    def __init__(self, symbol, lineno):
        self.symbol = symbol
        self.lineno = lineno

    def __str__(self):
        return "Недопустимый символ '%s' на строке %d" % (self.symbol,
                                                          self.lineno)

reserved = {'array': 'ARRAY', 'of': 'OF', 'not': 'NOT', 'nil': 'NIL',
            'otherwise': 'OTHERWISE', 'case': 'CASE', 'pow': 'POW',
            'div': 'DIV', 'mod': 'MOD', 'and': 'AND', 'and_then': 'AND_THEN',
            'or': 'OR', 'or_else': 'OR_ELSE', 'in': 'IN', 'type': 'TYPE',
            'bindable': 'BINDABLE', 'value': 'VALUE', 'packed': 'PACKED',
            'record': 'RECORD', 'end': 'END', 'set': 'SET', 'file': 'FILE',
            'restricted': 'RESTRICTED', 'program': 'PROGRAM_WORD',
            'import': 'IMPORT', 'qualified': 'QUALIFIED', 'only': 'ONLY',
            'label': 'LABEL_WORD', 'const': 'CONST', 'var': 'VAR',
            'procedure': 'PROCEDURE', 'protected': 'PROTECTED',
            'function': 'FUNCTION', 'begin': 'BEGIN', 'goto': 'GOTO',
            'if': 'IF', 'then': 'THEN', 'else': 'ELSE', 'repeat': 'REPEAT',
            'until': 'UNTIL', 'while': 'WHILE', 'do': 'DO', 'for': 'FOR',
            'to': 'TO', 'downto': 'DOWNTO', 'with': 'WITH', 'module': 'MODULE',
            'export': 'EXPORT'}

tokens = ('COMMENT', 'DOTDOT', 'STARSTAR', 'LT', 'GT', 'GL', 'LG', 'LE', 'GE',
          'LBRAC', 'RBRAC', 'COMMA', 'DOT', 'LPAREN', 'RPAREN', 'UPARROW',
          'SEMICOLON', 'COLON', 'STAR', 'SLASH', 'PLUS', 'MINUS', 'EQUAL',
          'EG', 'ASSIGNMENT', 'CHARACTER_STRING', 'AND', 'SET', 'POW',
          'AND_THEN', 'FILE', 'IN', 'ARRAY', 'PACKED', 'END', 'RESTRICTED',
          'OR_ELSE', 'BINDABLE', 'TYPE', 'NIL', 'NOT', 'MOD', 'CASE', 'OF',
          'VALUE', 'RECORD', 'DIV', 'OR', 'OTHERWISE', 'PROGRAM_WORD',
          'IMPORT', 'QUALIFIED', 'ONLY', 'LABEL_WORD', 'CONST', 'VAR',
          'PROCEDURE', 'PROTECTED', 'FUNCTION', 'BEGIN', 'GOTO', 'IF', 'THEN',
          'ELSE', 'REPEAT', 'UNTIL', 'WHILE', 'DO', 'FOR', 'TO', 'DOWNTO',
          'WITH', 'MODULE', 'EXPORT', 'ID', 'UNSIGNEDNUMBER', 'EXTENDEDNUMBER')

# Tokens

t_DOTDOT = r'\.\.'
t_STARSTAR = r'\*\*'
t_LT = r'<'
t_GT = r'>'
t_GL = r'><'
t_LG = r'<>'
t_LE = r'<='
t_GE = r'>='
t_LBRAC = r'\['
t_RBRAC = r'\]'
t_COMMA = r'\,'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_UPARROW = r'\^'
t_SEMICOLON = r'\;'
t_COLON = r':'
t_STAR = r'\*'
t_SLASH = r'/'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_EQUAL = r'\='
t_EG = r'\=>'
t_ASSIGNMENT = r':\='

t_AND = r'and'
t_SET = r'set'
t_POW = r'pow'
t_AND_THEN = r'and_then'
t_FILE = r'file'
t_IN = r'in'
t_ARRAY = r'array'
t_PACKED = r'packed'
t_END = r'end'
t_RESTRICTED = r'restricted'
t_OR_ELSE = r'or_else'
t_BINDABLE = r'bindable'
t_TYPE = r'type'
t_NIL = r'nil'
t_NOT = r'not'
t_MOD = r'mod'
t_CASE = r'case'
t_OF = r'of'
t_VALUE = r'value'
t_RECORD = r'record'
t_DIV = r'div'
t_OR = r'or'
t_OTHERWISE = r'otherwise'
t_PROGRAM_WORD = r'program'
t_IMPORT = r'import'
t_QUALIFIED = r'qualified'
t_ONLY = r'only'
t_LABEL_WORD = r'label'
t_CONST = r'const'
t_VAR = r'var'
t_PROCEDURE = r'procedure'
t_PROTECTED = r'protected'
t_FUNCTION = r'function'
t_BEGIN = r'begin'
t_GOTO = r'goto'
t_IF = r'if'
t_THEN = r'then'
t_ELSE = r'else'
t_REPEAT = r'repeat'
t_UNTIL = r'until'
t_WHILE = r'while'
t_DO = r'do'
t_FOR = r'for'
t_TO = r'to'
t_DOWNTO = r'downto'
t_WITH = r'with'
t_MODULE = r'module'
t_EXPORT = r'export'

# Ignored characters
t_ignore = " \t"


def t_CHARACTER_STRING(t):
    r'\'[^\']*\''
    return t


def t_EXTENDEDNUMBER(t):
    r'[0-9]+\#[0-9]+'
    return t


def t_UNSIGNEDNUMBER(t):
    r'[0-9]+(\.[0-9]+)?(e(\+|\-)?[0-9]+)?'
    return t


def t_ID(t):
    r'[a-zA-Z]([a-zA-Z0-9_])*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_COMMENT(t):
    r'(\{ (.|\n)*?\})|(//.*)'
    pass


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    raise PascalLexicalError(t.value[0], t.lineno)

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'SLASH'),
)

# Parsing rules


def p_program(t):
    '''program : program_block'''
    t[0] = {'program': {'program_block': t[1]}}


def p_array_type(t):
    '''array_type : ARRAY LBRAC index_type_list RBRAC OF component_type
                  | ARRAY OF component_type'''
    if len(t) == 7:
        t[0] = {'array_type': [{'index_type_list': t[3]},
                               {'component_type': t[6]}]}
    elif len(t) == 4:
        t[0] = {'array_type': [{'component_type': t[3]}]}


def p_index_type_list(t):
    '''index_type_list : index_type
                       | index_type_list COMMA index_type'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_index_type(t):
    '''index_type : ordinal_type'''
    t[0] = {'index_type': t[1]}


def p_ordinal_type(t):
    '''ordinal_type : new_ordinal_type
                    | ordinal_type_name
                    | type_inquiry
                    | discriminated_schema'''
    t[0] = t[1]


def p_new_ordinal_type(t):
    '''new_ordinal_type : enumerated_type
                        | subrange_type'''
    t[0] = t[1]


def p_enumerated_type(t):
    '''enumerated_type : LPAREN identifier_list RPAREN'''
    t[0] = {'enumerated_type': {'identifier_list': t[1]}}


def p_identifier_list(t):
    '''identifier_list : identifier
                       | identifier_list COMMA identifier'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_identifier(t):
    '''identifier : ID'''
    t[0] = t[1]


def p_subrange_type(t):
    '''subrange_type : subrange_bound DOTDOT subrange_bound'''
    t[0] = {'subrange_type': [{'min': t[1]}, {'max': t[3]}]}


def p_subrange_bound(t):
    '''subrange_bound : expression'''
    t[0] = t[1]


def p_expression(t):
    '''expression : simple_expression
                  | expression relational_operator simple_expression'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 4:
        t[0] = {t[2]: [t[1], t[3]]}


def p_simple_expression(t):
    '''simple_expression : simple_expression_term
                         | sign simple_expression_term'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 3:
        t[0] = {t[1]: t[2]}


def p_simple_expression_term(t):
    '''simple_expression_term : term
                              | simple_expression_term adding_operator '''\
                              '''term'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 4:
        t[0] = {t[2]: [t[1], t[3]]}


def p_term(t):
    '''term : factor
            | term multiplying_operator factor'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 4:
        t[0] = {t[2]: [t[1], t[3]]}


def p_factor(t):
    '''factor : primary
              | primary exponentiating_operator primary'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 4:
        t[0] = {t[2]: [t[1], t[3]]}


def p_primary(t):
    '''primary : variable_access
               | unsigned_constant
               | set_constructor
               | LPAREN expression RPAREN
               | NOT primary'''
    # structured_value_constructor не удается распознать'''
    # identifier будет в variable_access
    # schema_discriminant будет в variable_access
    # constant_access заменяется большим variable_access
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 3:
        t[0] = {t[1]: t[2]}
    elif len(t) == 4:
        t[0] = t[2]


def p_variable_access(t):
    '''variable_access : entire_variable
                       | component_variable
                       | substring_variable
                       | pointer_variable'''
    t[0] = t[1]


def p_entire_variable(t):
    '''entire_variable : name
                       | name actual_parameter_list'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 3:
        #???
        t[0] = {'entire_variable_or_function': [t[1], t[2]]}


def p_component_variable(t):
    '''component_variable : indexed_variable
                          | field_designator'''
    t[0] = t[1]


def p_indexed_variable(t):
    '''indexed_variable : variable_access LBRAC index_expression_list RBRAC'''
    #???
    t[0] = {'indexed_variable': [t[1], {'index_expression_list': t[3]}]}


def p_index_expression_list(t):
    '''index_expression_list : index_expression
                             | index_expression_list COMMA index_expression'''
    #???
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_index_expression(t):
    '''index_expression : expression'''
    t[0] = t[1]


def p_field_designator(t):
    '''field_designator : variable_access DOT identifier'''
    #???
    t[0] = {'field_designator': [{'record_variable': t[1]},
                                 {'field_specifier': {'field_identifier':
                                                      t[3]}}]}


def p_name(t):
    '''name : identifier
            | name DOT identifier'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 4:
        t[0] = '%s.%s' % (t[1], t[3])


def p_pointer_variable(t):
    '''pointer_variable : variable_access UPARROW'''
    t[0] = {'pointer_variable': [t[1], t[2]]}


def p_substring_variable(t):
    '''substring_variable : variable_access LBRAC index_expression DOTDOT '''\
                          '''index_expression RBRAC'''
    t[0] = {'substring_variable': [{'string_variable': t[1]},
                                   {'start': t[3]}, {'end': t[5]}]}


def p_actual_parameter_list(t):
    '''actual_parameter_list : LPAREN actual_parameter_list_list RPAREN'''
    t[0] = {'actual_parameter_list': t[2]}


def p_actual_parameter_list_list(t):
    '''actual_parameter_list_list : actual_parameter
                         | actual_parameter_list_list COMMA actual_parameter'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_actual_parameter(t):
    '''actual_parameter : expression
                        | expression COLON expression
                        | expression COLON expression COLON expression'''
    # name будет в expression, хоть и далеко
    if len(t) == 2:
        t[0] = {'actual_parameter': t[1]}
    elif len(t) == 4:
        t[0] = {'actual_parameter': [t[1], t[3]]}
    elif len(t) == 6:
        t[0] = {'actual_parameter': [t[1], t[3], t[5]]}


def p_unsigned_constant(t):
    '''unsigned_constant : UNSIGNEDNUMBER
                         | CHARACTER_STRING
                         | NIL
                         | EXTENDEDNUMBER'''
    t[0] = t[1]


def p_sign(t):
    '''sign : PLUS
            | MINUS'''
    t[0] = t[1]


def p_set_constructor(t):
    '''set_constructor : LBRAC member_designator_list RBRAC
                       | LBRAC RBRAC'''
    if len(t) == 4:
        t[0] = {'set_constructor': {'member_designator_list': t[2]}}
    elif len(t) == 3:
        t[0] = {'set_constructor': 'empty'}


def p_member_designator_list(t):
    '''member_designator_list : member_designator
                            | member_designator_list COMMA member_designator'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_member_designator(t):
    '''member_designator : expression
                         | expression DOTDOT expression'''
    if len(t) == 2:
        t[0] = {'member_designator': t[1]}
    elif len(t) == 4:
        t[0] = {'member_designator': [{'start': t[1]}, {'end': t[3]}]}

#def p_structured_value_constructor(t):
#    '''structured_value_constructor : name array_value
#                                    | name record_value
#                                    | name set_value'''
#    if list(t[2])[0] == 'array_value':
#        t[0] = {'structured_value_constructor': [{'array_type_name': t[1]},
#                                                 t[2]]}
#    elif list(t[2])[0] == 'record_value':
#        t[0] = {'structured_value_constructor': [{'record_type_name': t[1]},
#                                                 t[2]]}
#    elif list(t[2])[0] == 'set_value':
#        t[0] = {'structured_value_constructor': [{'set_type_name': t[1]},
#                                                 t[2]]}


def p_array_value(t):
    '''array_value : LBRAC array_value_element_list RBRAC
        | LBRAC array_value_element_list SEMICOLON array_value_completer RBRAC
        | LBRAC array_value_element_list SEMICOLON RBRAC
        | LBRAC array_value_element_list SEMICOLON array_value_completer '''\
            '''SEMICOLON RBRAC
        | LBRAC array_value_element_list array_value_completer SEMICOLON RBRAC
        | LBRAC array_value_element_list array_value_completer RBRAC
        | LBRAC array_value_completer SEMICOLON RBRAC
        | LBRAC array_value_completer RBRAC'''
    if len(t) == 4:
        if list(t[2])[0] == 'array_value_completer':
            t[0] = {'array_value': t[2]}
        else:
            t[0] = {'array_value': {'array_value_element_list': t[2]}}
    elif len(t) == 5:
        if list(t[3])[0] == 'array_value_completer':
            t[0] = {'array_value': [{'array_value_element_list': t[2]}, t[3]]}
        else:
            if list(t[2])[0] == 'array_value_completer':
                t[0] = {'array_value': t[2]}
            else:
                t[0] = {'array_value': {'array_value_element_list': t[2]}}
    elif len(t) == 6:
        if list(t[3])[0] == 'array_value_completer':
            t[0] = {'array_value': [{'array_value_element_list': t[2]}, t[3]]}
        else:
            t[0] = {'array_value': [{'array_value_element_list': t[2]}, t[4]]}
    elif len(t) == 7:
        t[0] = {'array_value': [{'array_value_element_list': t[2]}, t[4]]}


def p_array_value_element_list(t):
    '''array_value_element_list : array_value_element
                    | array_value_element_list SEMICOLON array_value_element'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_array_value_completer(t):
    '''array_value_completer : OTHERWISE component_value'''
    t[0] = {'array_value_completer': {t[1]: t[2]}}


def p_component_value(t):
    '''component_value : expression
                       | array_value
                       | record_value'''
    t[0] = {'component_value': t[1]}


def p_record_value(t):
    '''record_value : LBRAC field_list_value RBRAC'''
    t[0] = {'record_value': t[2]}


def p_field_list_value(t):
    '''field_list_value : variant_part_value
                      | variant_part_value SEMICOLON
                      | fixed_part_value
                      | fixed_part_value SEMICOLON
                      | fixed_part_value SEMICOLON variant_part_value
                      | fixed_part_value SEMICOLON variant_part_value SEMICOLON
                      | empty'''
    if len(t) == 2 or len(t) == 3:#возможно тут надо точку с запятой тоже
        if list(t[1])[0] == 'fixed_part_value':
            t[0] = {'field_list_value': {'fixed_part_value': t[1]}}
        else:
            t[0] = {'field_list_value': t[1]}
    elif len(t) == 4 or len(t) == 5:#возможно тут надо точку с запятой тоже
        t[0] = {'field_list_value': [{'fixed_part_value': t[1]}, t[3]]}


def p_variant_part_value(t):
    '''variant_part_value : CASE tag_field_identifier COLON '''\
        '''expression OF LBRAC field_list_value RBRAC
                   | CASE expression OF LBRAC field_list_value RBRAC'''
    if len(t) == 7:
        t[0] = {'variant_part_value': [{t[1]: {'constant_tag_value': t[2]}},
                                       {t[3]: t[5]}]}
    elif len(t) == 9:
        t[0] = {'variant_part_value': [{t[1]: [t[2], {'constant_tag_value':
                                                     t[4]}]}, {t[5]: t[7]}]}


def p_tag_field_identifier(t):
    '''tag_field_identifier : identifier'''
    t[0] = {'tag_field_identifier': {'field_identifier': t[1]}}


def p_constant_expression(t):
    '''constant_expression : expression'''
    t[0] = t[1]


def p_fixed_part_value(t):
    '''fixed_part_value : field_value
                        | fixed_part_value SEMICOLON field_value'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_field_value(t):
    '''field_value : identifier_list COLON component_value'''
    t[0] = {'field_value': [{'identifier_list': t[1]}, t[3]]}


def p_array_value_element(t):
    '''array_value_element : member_designator_list COLON component_value'''
    t[0] = {'array_value_element': [{'member_designator_list': t[1]}, t[3]]}

#def p_set_value(t):
#    '''set_value : set_constructor'''
#    t[0] = {'set_value': t[1]}


def p_exponentiating_operator(t):
    '''exponentiating_operator : STARSTAR
                               | POW'''
    t[0] = t[1]


def p_multiplying_operator(t):
    '''multiplying_operator : STAR
                            | SLASH
                            | DIV
                            | MOD
                            | AND
                            | AND_THEN'''
    t[0] = t[1]


def p_adding_operator(t):
    '''adding_operator : PLUS
                       | MINUS
                       | GL
                       | OR
                       | OR_ELSE'''
    t[0] = t[1]


def p_relational_operator(t):
    '''relational_operator : EQUAL
                           | LG
                           | LT
                           | GT
                           | LE
                           | GE
                           | IN'''
    t[0] = t[1]


def p_discriminated_schema(t):
    '''discriminated_schema : name actual_discriminant_part'''
    t[0] = {'discriminated_schema': [t[1], t[2]]}


def p_actual_discriminant_part(t):
    '''actual_discriminant_part : LPAREN actual_parameter_list RPAREN'''
    #'''actual_discriminant_part : LPAREN discriminant_value_list RPAREN'''
    t[0] = {'actual_discriminant_part': t[2]}


def p_type_inquiry(t):
    '''type_inquiry : TYPE OF name'''
    t[0] = {'type_inquiry': {'type_of': {'type_inquiry_object':
                                              {'parameter_identifier': t[3]}}}}


def p_ordinal_type_name(t):
    '''ordinal_type_name : name'''
    t[0] = {'ordinal_type_name': t[1]}


def p_component_type(t):
    '''component_type : type_denoter'''
    t[0] = t[1]


def p_type_denoter(t):
    '''type_denoter : type_denoter_middle_part
                 | BINDABLE type_denoter_middle_part
                 | type_denoter_middle_part initial_state_specifier
                 | BINDABLE type_denoter_middle_part initial_state_specifier'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 3:
        if list(t[2])[0] == 'type_denoter_middlepart':
            t[0] = {'type_denoter': {t[1]: t[2]}}
        elif list(t[2])[0] == 'initial_state_specifier':
            t[0] = {'type_denoter': [t[1], t[2]]}
    elif len(t) == 4:
        t[0] = {'type_denoter': {t[1]: [t[2], t[3]]}}


def p_type_denoter_middle_part(t):
    '''type_denoter_middle_part : name
                                | new_type
                                | type_inquiry
                                | discriminated_schema'''
    t[0] = t[1]


def p_new_type(t):
    '''new_type : new_ordinal_type
                | new_structured_type
                | new_pointer_type
                | restricted_type'''
    t[0] = t[1]


def p_new_structured_type(t):
    '''new_structured_type : unpacked_structured_type
                           | PACKED unpacked_structured_type'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 3:
        #???
        t[0] = {t[1]: t[2]}


def p_unpacked_structured_type(t):
    '''unpacked_structured_type : array_type
                                | record_type
                                | set_type
                                | file_type'''
    t[0] = t[1]


def p_record_type(t):
    '''record_type : RECORD field_list END'''
    t[0] = {'record_type': t[2]}


def p_field_list(t):
    '''field_list : field_list_left_part
                  | empty'''
    t[0] = {'field_list': t[1]}


def p_field_list_left_part(t):
    '''field_list_left_part : fixed_part SEMICOLON variant_part
                            | fixed_part
                            | fixed_part SEMICOLON
                            | variant_part
                            | variant_part SEMICOLON'''
    if len(t) == 2 or len(t) == 3:
        if list(t[1])[0] == 'fixed_part':
            t[0] = {'fixed_part': t[1]}
        else:
            t[0] = t[1]
    elif len(t) == 4:
        t[0] = [{'fixed_part': t[1]}, t[3]]


def p_fixed_part(t):
    '''fixed_part : record_section
                  | fixed_part SEMICOLON record_section'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_record_section(t):
    '''record_section : identifier_list COLON type_denoter'''
    t[0] = {'record_section': [{'identifier_list': t[1]}, t[3]]}


def p_variant_part(t):
    '''variant_part : CASE variant_selector OF variant_list_element_list
        | CASE variant_selector OF variant_list_element_list SEMICOLON '''\
            '''variant_part_completer
        | CASE variant_selector OF variant_list_element_list '''\
            '''variant_part_completer
        | CASE variant_selector OF variant_part_completer'''
    if len(t) == 5:
        if list(t[4])[0] == 'variant_part_completer':
            t[0] = {'variant_part': [{t[1]: t[2]}, {t[3]: t[4]}]}
        else:
            t[0] = {'variant_part': [{t[1]: t[2]},
                                  {t[3]: {'variant_list_element_list': t[4]}}]}
    elif len(t) == 6 or len(t) == 7:
        t[0] = {'variant_part': [{t[1]: t[2]},
                         {t[3]: [{'variant_list_element_list': t[4]}, t[-1]]}]}


def p_variant_list_element_list(t):
    '''variant_list_element_list : variant_list_element
                  | variant_list_element_list SEMICOLON variant_list_element'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_variant_list_element(t):
    '''variant_list_element : member_designator_list COLON variant_denoter'''
    t[0] = {'variant_list_element': [{'member_designator_list': t[1]}, t[3]]}


def p_variant_denoter(t):
    '''variant_denoter : LPAREN field_list RPAREN'''
    t[0] = {'variant_denoter': t[2]}


def p_variant_selector(t):
    '''variant_selector : tag_field COLON tag_type
                        | tag_type'''
    # identifier будет в tag_type
    if len(t) == 2:
        if list(t[1])[0] == 'identifier':
            t[0] = {'variant_selector': {'discriminant_identifier': t[1]}}
        t[0] = {'variant_selector': t[1]}
    elif len(t) == 4:
        t[0] = {'variant_selector': [t[1], t[3]]}


def p_tag_field(t):
    '''tag_field : identifier'''
    t[0] = {'tag_field': t[1]}


def p_tag_type(t):
    '''tag_type : ordinal_type_name'''
    t[0] = {'tag_type': t[1]}


def p_variant_part_completer(t):
    '''variant_part_completer : OTHERWISE variant_denoter'''
    t[0] = {'variant_part_completer': {t[1]: t[2]}}


def p_set_type(t):
    '''set_type : SET OF base_type'''
    t[0] = {'set_type': {'set_of': t[3]}}


def p_base_type(t):
    '''base_type : ordinal_type'''
    t[0] = {'base_type': t[1]}


def p_file_type(t):
    '''file_type : FILE LBRAC index_type RBRAC OF component_type
                 | FILE OF component_type'''
    if len(t) == 4:
        t[0] = {'file_type': {'file_of': t[3]}}
    elif len(t) == 7:
        t[0] = {'file_type': [{'file_of': t[6]}, {'index_type': t[3]}]}


def p_new_pointer_type(t):
    '''new_pointer_type : UPARROW domain_type'''
    t[0] = {'new_pointer_type': {t[1]: t[2]}}


def p_domain_type(t):
    '''domain_type : name'''
    t[0] = {'domain_type': t[1]}


def p_restricted_type(t):
    '''restricted_type : RESTRICTED name'''
    t[0] = {'restricted_type': {t[1]: t[2]}}


def p_initial_state_specifier(t):
    '''initial_state_specifier : VALUE component_value'''
    t[0] = {'initial_state_specifier': {t[1]: t[2]}}


def p_program_block(t):
    '''program_block : program_component
                     | program_block program_component'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 3:
        t[0] = t[1] + [t[2]]


def p_program_component(t):
    '''program_component : main_program_declaration DOT
                         | module_declaration DOT'''
    t[0] = {'program_component': t[1]}


def p_main_program_declaration(t):
    '''main_program_declaration : program_heading SEMICOLON '''\
        '''main_program_block'''
    t[0] = {'main_program_declaration': [t[1], t[3]]}


def p_program_heading(t):
    '''program_heading : PROGRAM_WORD identifier
                       | PROGRAM_WORD identifier LPAREN '''\
        '''program_parameter_list RPAREN'''
    if len(t) == 3:
        t[0] = {'program_heading': t[2]}
    elif len(t) == 6:
        t[0] = {'program_heading': [t[2], t[4]]}


def p_program_parameter_list(t):
    '''program_parameter_list : identifier_list'''
    t[0] = {'program_parameter_list': {'identifier_list': t[1]}}


def p_main_program_block(t):
    '''main_program_block : block'''
    t[0] = {'main_program_block': t[1]}


def p_block(t):
    '''block : import_part block_middle_part statement_part
             | import_part statement_part'''
    if len(t) == 3:
        t[0] = {'block': [t[1], t[2]]}
    elif len(t) == 4:
        t[0] = {'block': [t[1]] + t[2] + [t[3]]}


def p_block_middle_part(t):
    '''block_middle_part : label_declaration_part
                 | constant_definition_part
                 | type_definition_part
                 | variable_declaration_part
                 | procedure_and_function_declaration_part
                 | block_middle_part label_declaration_part
                 | block_middle_part constant_definition_part
                 | block_middle_part type_definition_part
                 | block_middle_part variable_declaration_part
                 | block_middle_part procedure_and_function_declaration_part'''
    if len(t) == 2:
        if list(t[1])[0] == 'label_declaration_part' or\
            list(t[1])[0] == 'constant_definition_part' or\
            list(t[1])[0] == 'type_definition_part' or\
            list(t[1])[0] == 'variable_declaration_part':
                t[0] = [t[1]]
        else:
            t[0] = [{'procedure_and_function_declaration_part': t[1]}]
    elif len(t) == 3:
        if list(t[2])[0] == 'label_declaration_part' or\
            list(t[2])[0] == 'constant_definition_part' or\
            list(t[2])[0] == 'type_definition_part' or\
            list(t[2])[0] == 'variable_declaration_part':
                t[0] = t[1] + [t[2]]
        else:
            t[0] = t[1] + [{'procedure_and_function_declaration_part': t[2]}]


def p_import_part(t):
    '''import_part : IMPORT import_specification_list
                   | empty'''
    if len(t) == 2:
        t[0] = {'import_part': t[1]}
    elif len(t) == 3:
        t[0] = {'import_part': {t[1]: {'import_specification_list': t[2]}}}


def p_import_specification_list(t):
    '''import_specification_list : import_specification SEMICOLON
                  | import_specification_list import_specification SEMICOLON'''
    if len(t) == 3:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[2]]


def p_import_specification(t):
    '''import_specification : interface_identifier
                    | interface_identifier access_qualifier
                    | interface_identifier import_qualifier
                    | interface_identifier access_qualifier import_qualifier'''
    if len(t) == 2:
        t[0] = {'import_specification': t[1]}
    elif len(t) == 3:
        t[0] = {'import_specification': [t[1], t[2]]}
    elif len(t) == 4:
        t[0] = {'import_specification': [t[1], t[2], t[3]]}


def p_interface_identifier(t):
    '''interface_identifier : identifier'''
    t[0] = {'interface_identifier': t[1]}


def p_access_qualifier(t):
    '''access_qualifier : QUALIFIED'''
    t[0] = {'access_qualifier': t[1]}


def p_import_qualifier(t):
    '''import_qualifier : selective_import_option LPAREN import_list RPAREN
                        | LPAREN import_list RPAREN'''
    if len(t) == 4:
        t[0] = {'import_qualifier': {'import_list': t[2]}}
    elif len(t) == 5:
        t[0] = {'import_qualifier': [t[1], {'import_list': t[3]}]}


def p_selective_import_option(t):
    '''selective_import_option : ONLY'''
    t[0] = {'selective_import_option': t[1]}


def p_import_list(t):
    '''import_list : import_clause
                   | import_list COMMA import_clause'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_import_clause(t):
    '''import_clause : constituent_identifier
                     | import_renaming_clause'''
    t[0] = {'import_clause': t[1]}


def p_constituent_identifier(t):
    '''constituent_identifier : identifier'''
    t[0] = {'constituent_identifier': t[1]}


def p_import_renaming_clause(t):
    '''import_renaming_clause : constituent_identifier EG identifier'''
    t[0] = {'import_renaming_clause': [t[1], t[3]]}


def p_label_declaration_part(t):
    '''label_declaration_part : LABEL_WORD label_list SEMICOLON'''
    t[0] = {'label_declaration_part': {'label_list': t[2]}}


def p_label_list(t):
    '''label_list : label
                  | label_list COMMA label'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_label(t):
    '''label : UNSIGNEDNUMBER'''
    t[0] = {'label': t[1]}


def p_constant_definition_part(t):
    '''constant_definition_part : CONST constant_definition_list'''
    t[0] = {'constant_definition_part': t[2]}


def p_constant_definition_list(t):
    '''constant_definition_list : constant_definition SEMICOLON
                    | constant_definition_list constant_definition SEMICOLON'''
    if len(t) == 3:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[2]]


def p_constant_definition(t):
    '''constant_definition : identifier EQUAL constant_expression'''
    t[0] = {t[1]: t[3]}


def p_type_definition_part(t):
    '''type_definition_part : TYPE type_definition_list'''
    t[0] = {'type_definition_part': t[2]}


def p_type_definition_list(t):
    '''type_definition_list : type_definition SEMICOLON
                          | schema_definition SEMICOLON
                          | type_definition_list type_definition SEMICOLON
                          | type_definition_list schema_definition SEMICOLON'''
    if len(t) == 3:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[2]]


def p_type_definition(t):
    '''type_definition : identifier EQUAL type_denoter'''
    t[0] = {'type_definition': [t[1], t[3]]}


def p_schema_definition(t):
    '''schema_definition : identifier formal_discriminant_part EQUAL '''\
        '''type_denoter''' # identifier EQUAL name будет в type_definition
    if len(t) == 4:
        t[0] = {'schema_definition': [t[1], t[3]]}


def p_formal_discriminant_part(t):
    '''formal_discriminant_part : LPAREN discriminant_specification_list '''\
        '''RPAREN'''
    t[0] = {'formal_discriminant_part':
            {'discriminant_specification_list': t[2]}}


def p_discriminant_specification_list(t):
    '''discriminant_specification_list : discriminant_specification
      | discriminant_specification_list SEMICOLON discriminant_specification'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_discriminant_specification(t):
    '''discriminant_specification : identifier_list COLON ordinal_type_name'''
    t[0] = {'discriminant_specification': [{'identifier_list': t[1]}, t[3]]}


def p_variable_declaration_part(t):
    '''variable_declaration_part : VAR variable_declaration_list'''
    t[0] = {'variable_declaration_part': t[2]}


def p_variable_declaration_list(t):
    '''variable_declaration_list : variable_declaration SEMICOLON
                  | variable_declaration_list variable_declaration SEMICOLON'''
    if len(t) == 3:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[2]]


def p_variable_declaration(t):
    '''variable_declaration : identifier_list COLON type_denoter'''
    t[0] = {'variable_declaration': [{'identifier_list': t[1]}, t[3]]}


def p_procedure_and_function_declaration_part(t):
    '''procedure_and_function_declaration_part : procedure_declaration '''\
            '''SEMICOLON
        | function_declaration SEMICOLON
        | procedure_and_function_declaration_part procedure_declaration '''\
            '''SEMICOLON
        | procedure_and_function_declaration_part function_declaration '''\
            '''SEMICOLON'''
    if len(t) == 3:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[2]]


def p_procedure_declaration(t):
    '''procedure_declaration : procedure_heading SEMICOLON remote_directive
                           | procedure_heading SEMICOLON procedure_block'''
    t[0] = {'procedure_declaration': [t[1], t[3]]}


def p_procedure_heading(t):
    '''procedure_heading : PROCEDURE name formal_parameter_list
                         | PROCEDURE name'''
    if len(t) == 3:
        t[0] = {'procedure_heading': t[2]}
    elif len(t) == 4:
        t[0] = {'procedure_heading': [t[2], t[3]]}


def p_formal_parameter_list(t):
    '''formal_parameter_list : LPAREN formal_parameter_section_list RPAREN'''
    t[0] = {'formal_parameter_list': t[2]}


def p_formal_parameter_section_list(t):
    '''formal_parameter_section_list : formal_parameter_section
          | formal_parameter_section_list SEMICOLON formal_parameter_section'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_formal_parameter_section(t):
    '''formal_parameter_section : value_parameter_specification
                                | variable_parameter_specification
                                | procedural_parameter_specification
                                | functional_parameter_specification
                                | conformant_array_parameter_specification'''
    t[0] = t[1]


def p_value_parameter_specification(t):
    '''value_parameter_specification : identifier_list COLON parameter_form
                            | PROTECTED identifier_list COLON parameter_form'''
    if len(t) == 4:
        t[0] = {'value_parameter_specification': [{'identifier_list': t[1]},
                                                  t[3]]}
    elif len(t) == 5:
        t[0] = {'value_parameter_specification': [t[1],
                                                  {'identifier_list': t[2]},
                                                  t[3]]}


def p_parameter_form(t):
    '''parameter_form : type_denoter_middle_part'''
    #'''parameter_form : name
    #                  | type_inquiry'''
    t[0] = {'parameter_form': t[1]}


def p_variable_parameter_specification(t):
    '''variable_parameter_specification : PROTECTED VAR identifier_list '''\
        '''COLON parameter_form
                                  | VAR identifier_list COLON parameter_form'''
    if len(t) == 5:
        t[0] = {'variable_parameter_specification': [{'identifier_list': t[2]},
                                                     t[4]]}
    elif len(t) == 6:
        t[0] = {'variable_parameter_specification': [t[1],
                                                     {'identifier_list': t[2]},
                                                     t[4]]}


def p_procedural_parameter_specification(t):
    '''procedural_parameter_specification : procedure_heading'''
    t[0] = {'procedural_parameter_specification': t[1]}


def p_functional_parameter_specification(t):
    '''functional_parameter_specification : function_heading'''
    t[0] = {'functional_parameter_specification': t[1]}


def p_function_heading(t):
    '''function_heading : FUNCTION identifier COLON result_type
        | FUNCTION identifier formal_parameter_list '''\
            '''result_variable_specification COLON result_type
        | FUNCTION identifier formal_parameter_list COLON result_type
        | FUNCTION identifier result_variable_specification COLON '''\
            '''result_type'''
    if len(t) == 5:
        t[0] = {'function_heading': [t[2], t[4]]}
    elif len(t) == 6:
        t[0] = {'function_heading': [t[2], t[3], t[5]]}
    elif len(t) == 7:
        t[0] = {'function_heading': [t[2], t[3], t[4], t[6]]}


def p_result_type(t):
    '''result_type : name'''
    t[0] = {'result_type': t[1]}


def p_result_variable_specification(t):
    '''result_variable_specification : EQUAL identifier'''
    t[0] = {'result_variable_specification': [t[1], t[2]]} # надо ли EQUAL?


def p_conformant_array_parameter_specification(t):
    '''conformant_array_parameter_specification : PROTECTED '''\
            '''value_conformant_array_specification
        | PROTECTED variable_conformant_array_specification
        | value_conformant_array_specification
        | variable_conformant_array_specification'''
    if len(t) == 2:
        t[0] = {'conformant_array_parameter_specification': t[1]}
    elif len(t) == 3:
        t[0] = {'conformant_array_parameter_specification': [t[1], t[2]]}


def p_value_conformant_array_specification(t):
    '''value_conformant_array_specification : identifier_list COLON '''\
        '''conformant_array_form'''
    t[0] = {'value_conformant_array_specification': [{'identifier_list': t[1]},
                                                     t[3]]}


def p_conformant_array_form(t):
    '''conformant_array_form : packed_conformant_array_form
                             | unpacked_conformant_array_form'''
    t[0] = {'conformant_array_form': t[1]}


def p_packed_conformant_array_form(t):
    '''packed_conformant_array_form : PACKED ARRAY LBRAC '''\
        '''index_type_specification RBRAC OF name'''
    t[0] = {'packed_conformant_array_form': [t[1], t[4], t[7]]} # так ли?


def p_index_type_specification(t):
    '''index_type_specification : identifier DOTDOT identifier COLON '''\
        '''ordinal_type_name'''
    t[0] = {'index_type_specification': [{'start': t[1]}, {'end': t[3]}, t[5]]}
    # тут может перед t[5] что-то поставить?


def p_unpacked_conformant_array_form(t):
    '''unpacked_conformant_array_form : ARRAY LBRAC '''\
            '''index_type_specification_list RBRAC OF name
        | ARRAY LBRAC index_type_specification_list RBRAC OF '''\
            '''conformant_array_form'''
    t[0] = {'unpacked_conformant_array_form':
            [{'index_type_specification_list': t[3]}, t[6]]}


def p_index_type_specification_list(t):
    '''index_type_specification_list : index_type_specification
          | index_type_specification_list SEMICOLON index_type_specification'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_variable_conformant_array_specification(t):
    '''variable_conformant_array_specification : VAR identifier_list COLON '''\
        '''conformant_array_form'''
    t[0] = {'variable_conformant_array_specification': [
                                                    {'identifier_list': t[2]},
                                                    t[4]]}


def p_remote_directive(t):
    '''remote_directive : directive'''
    t[0] = {'remote_directive': t[1]}


def p_directive(t):
    '''directive : ID'''
    t[0] = {'directive': t[1]}


def p_procedure_block(t):
    '''procedure_block : block'''
    t[0] = {'procedure_block': t[1]}


def p_function_declaration(t):
    '''function_declaration : function_heading SEMICOLON remote_directive
                            | function_identification SEMICOLON function_block
                            | function_heading SEMICOLON function_block'''
    t[0] = {'function_declaration': [t[1], t[3]]}


def p_function_identification(t):
    '''function_identification : FUNCTION identifier'''
    t[0] = {'function_identification': {'function_identifier': t[2]}}


def p_function_block(t):
    '''function_block : block'''
    t[0] = {'function_block': t[1]}


def p_statement_part(t):
    '''statement_part : compound_statement'''
    t[0] = {'statement_part': t[1]}


def p_compound_statement(t):
    '''compound_statement : BEGIN statement_sequence END'''
    t[0] = {'statement_sequence': t[2]}


def p_statement_sequence(t):
    '''statement_sequence : statement
                          | statement_sequence SEMICOLON statement'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_statement(t):
    '''statement : label COLON simple_statement
                 | label COLON structured_statement
                 | simple_statement
                 | structured_statement'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 4:
        #??? метки может не рассматривать вообще?
        t[0] = [t[1], t[3]]


def p_simple_statement(t):
    '''simple_statement : empty
                        | assignment_statement
                        | procedure_statement
                        | goto_statement'''
    t[0] = t[1]


def p_assignment_statement(t):
    '''assignment_statement : variable_access ASSIGNMENT expression'''
    t[0] = {t[2]: [t[1], t[3]]}


def p_procedure_statement(t):
    '''procedure_statement : name
                           | name actual_parameter_list'''
    if len(t) == 2:
        t[0] = {'procedure_statement': t[1]}
    elif len(t) == 3:
        t[0] = {'procedure_statement': [t[1], t[2]]}


def p_goto_statement(t):
    '''goto_statement : GOTO label'''
    t[0] = {'goto_statement': t[2]}


def p_structured_statement(t):
    '''structured_statement : compound_statement
                            | conditional_statement
                            | repetitive_statement
                            | with_statement'''
    t[0] = t[1]


def p_conditional_statement(t):
    '''conditional_statement : if_statement
                             | case_statement'''
    t[0] = t[1]


def p_if_statement(t):
    '''if_statement : IF boolean_expression THEN statement
                    | IF boolean_expression THEN statement else_part'''
    if len(t) == 5:
        t[0] = {'if_statement': [{t[1]: t[2]}, {t[3]: t[4]}]}
    elif len(t) == 6:
        t[0] = {'if_statement': [{t[1]: t[2]}, {t[3]: t[4]}, {'ELSE': t[5]}]}


def p_boolean_expression(t):
    '''boolean_expression : expression'''
    t[0] = t[1]


def p_else_part(t):
    '''else_part : ELSE statement'''
    t[0] = t[2]


def p_case_statement(t):
    '''case_statement : CASE case_index OF case_list_element_list END
                      | CASE case_index OF case_statement_completer END
        | CASE case_index OF case_list_element_list '''\
            '''case_statement_completer END
        | CASE case_index OF case_list_element_list SEMICOLON '''\
            '''case_statement_completer END
        | CASE case_index OF case_list_element_list SEMICOLON END
        | CASE case_index OF case_statement_completer SEMICOLON END
        | CASE case_index OF case_list_element_list '''\
            '''case_statement_completer SEMICOLON END
        | CASE case_index OF case_list_element_list SEMICOLON '''\
            '''case_statement_completer SEMICOLON END'''
    if len(t) == 6:
        if list(t[4])[0] == 'case_statement_completer':
            t[0] = {'case_statement': [{t[1]: t[2]}, {t[3]: t[4]}]}
        else:
            t[0] = {'case_statement': [{t[1]: t[2]},
                                     {t[3]: {'case_list_element_list': t[4]}}]}
    elif len(t) == 7:
        if list(t[5])[0] == 'case_statement_completer':
            t[0] = {'case_statement': [{t[1]: t[2]},
                             {t[3]: [{'case_list_element_list': t[4]}, t[5]]}]}
        else:
            if list(t[4])[0] == 'case_statement_completer':
                t[0] = {'case_statement': [{t[1]: t[2]}, {t[3]: t[4]}]}
            else:
                t[0] = {'case_statement': [{t[1]: t[2]},
                                     {t[3]: {'case_list_element_list': t[4]}}]}
    elif len(t) == 8:
        if list(t[6])[0] == 'case_statement_completer':
            t[0] = {'case_statement': [{t[1]: t[2]},
                             {t[3]: [{'case_list_element_list': t[4]}, t[6]]}]}
        else:
            t[0] = {'case_statement': [{t[1]: t[2]},
                             {t[3]: [{'case_list_element_list': t[4]}, t[5]]}]}
    elif len(t) == 9:
        t[0] = {'case_statement': [{t[1]: t[2]},
                             {t[3]: [{'case_list_element_list': t[4]}, t[6]]}]}


def p_case_list_element_list(t):
    '''case_list_element_list : case_list_element
                        | case_list_element_list SEMICOLON case_list_element'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_case_list_element(t):
    '''case_list_element : member_designator_list COLON statement'''
    t[0] = {'case_list_element': [{'member_designator_list': t[1]}, t[3]]}


def p_case_statement_completer(t):
    '''case_statement_completer : OTHERWISE statement_sequence'''
    t[0] = {'case_statement_completer': {t[1]: {'statement_sequence': t[2]}}}


def p_case_index(t):
    '''case_index : expression'''
    t[0] = {'case_index': t[1]}


def p_repetitive_statement(t):
    '''repetitive_statement : repeat_statement
                            | while_statement
                            | for_statement'''
    t[0] = t[1]


def p_repeat_statement(t):
    '''repeat_statement : REPEAT statement_sequence UNTIL boolean_expression'''
    t[0] = {'repeat_statement': [{t[1]: {'statement_sequence': t[2]}},
                                 {t[3]: t[4]}]}


def p_while_statement(t):
    '''while_statement : WHILE boolean_expression DO statement'''
    t[0] = {'while_statement': [{t[1]: t[2]}, {t[3]: t[4]}]}


def p_for_statement(t):
    '''for_statement : FOR entire_variable iteration_clause DO statement'''
    t[0] = {'for_statement': [{t[1]: [{'control_variable': t[2]}, t[3]]},
                              {t[4]: t[5]}]}


def p_iteration_clause(t):
    '''iteration_clause : sequence_iteration
                        | set_member_iteration'''
    t[0] = {'iteration_clause': t[1]}


def p_sequence_iteration(t):
    '''sequence_iteration : ASSIGNMENT initial_value TO final_value
                          | ASSIGNMENT initial_value DOWNTO final_value'''
    t[0] = {'sequence_iteration': [{'FROM': t[2]}, {t[3]: t[4]}]}


def p_initial_value(t):
    '''initial_value : expression'''
    t[0] = t[1]


def p_final_value(t):
    '''final_value : expression'''
    t[0] = t[1]


def p_set_member_iteration(t):
    '''set_member_iteration : IN set_expression'''
    t[0] = {'set_member_iteration': {t[1]: t[2]}}


def p_set_expression(t):
    '''set_expression : expression'''
    t[0] = {'set_expression': t[1]}


def p_with_statement(t):
    '''with_statement : WITH with_list DO statement'''
    t[0] = {'with_statement': [{t[1]: {'with_list': t[2]}}, {t[3]: t[4]}]}


def p_with_list(t):
    '''with_list : with_element
                 | with_list COMMA with_element'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_with_element(t):
    '''with_element : variable_access'''
    t[0] = {'with_element': t[1]}


def p_module_declaration(t):
    '''module_declaration : module_heading
                          | module_heading SEMICOLON module_block
                          | module_identification SEMICOLON module_block'''
    if len(t) == 2:
        t[0] = {'module_declaration': t[1]}
    elif len(t) == 4:
        t[0] = {'module_declaration': [t[1], t[3]]}


def p_module_heading(t):
    '''module_heading : MODULE identifier interface_directive '''\
            '''SEMICOLON interface_specification_part import_part '''\
            '''module_heading_middle_part END
        | MODULE identifier LPAREN module_parameter_list RPAREN SEMICOLON '''\
            '''interface_specification_part import_part '''\
            '''module_heading_middle_part END
        | MODULE identifier interface_directive LPAREN '''\
            '''module_parameter_list RPAREN SEMICOLON '''\
            '''interface_specification_part import_part '''\
            '''module_heading_middle_part END
        | MODULE identifier SEMICOLON interface_specification_part '''\
            '''import_part module_heading_middle_part END
        | MODULE identifier interface_directive '''\
            '''SEMICOLON interface_specification_part import_part END
        | MODULE identifier LPAREN module_parameter_list RPAREN SEMICOLON '''\
            '''interface_specification_part import_part END
        | MODULE identifier interface_directive LPAREN '''\
            '''module_parameter_list RPAREN SEMICOLON '''\
            '''interface_specification_part import_part END
        | MODULE identifier SEMICOLON interface_specification_part '''\
            '''import_part END'''
    if len(t) == 7:
        t[0] = {'module_heading': [t[2], t[4], t[5]]}
    if len(t) == 8:
        if list(t[6])[0] == 'import_part':
            t[0] = {'module_heading': [t[2], t[3], t[5], t[6]]}
        else:
            t[0] = {'module_heading': [t[2], t[4], t[5],
                                       {'module_heading_middle_part': t[6]}]}
    elif len(t) == 9:
        t[0] = {'module_heading': [t[2], t[3], t[5], t[6],
                                   {'module_heading_middle_part': t[7]}]}
    elif len(t) == 10:
        t[0] = {'module_heading': [t[2], t[4], t[7], t[8]]}
    elif len(t) == 11:
        if list(t[9])[0] == 'import_part':
            t[0] = {'module_heading': [t[2], t[3], t[5], t[8], t[9]]}
        else:
            t[0] = {'module_heading': [t[2], t[4], t[7], t[8],
                                       {'module_heading_middle_part': t[9]}]}
    elif len(t) == 12:
        t[0] = {'module_heading': [t[2], t[3], t[5], t[8], t[9],
                                   {'module_heading_middle_part': t[10]}]}


def p_module_heading_middle_part(t):
    '''module_heading_middle_part : constant_definition_part
            | type_definition_part
            | variable_declaration_part
            | procedure_and_function_heading_part
            | module_heading_middle_part constant_definition_part
            | module_heading_middle_part type_definition_part
            | module_heading_middle_part variable_declaration_part
            | module_heading_middle_part procedure_and_function_heading_part'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 3:
        t[0] = t[1] + [t[2]]


def p_procedure_and_function_heading_part(t):
    '''procedure_and_function_heading_part : procedure_heading SEMICOLON
                                           | function_heading SEMICOLON'''
    t[0] = {'procedure_and_function_heading_part': t[1]}


def p_interface_directive(t):
    '''interface_directive : directive'''
    t[0] = {'interface_directive': t[1]}


def p_interface_specification_part(t):
    '''interface_specification_part : EXPORT export_part_list'''
    t[0] = {'interface_specification_part': {t[1]: {'export_part_list': t[2]}}}


def p_export_part_list(t):
    '''export_part_list : export_part SEMICOLON
                        | export_part_list export_part SEMICOLON'''
    if len(t) == 3:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[2]]


def p_export_part(t):
    '''export_part : identifier EQUAL LPAREN export_list RPAREN'''
    t[0] = {'export_part': {t[2]: [t[1], {'export_list': t[4]}]}}


def p_export_list(t):
    '''export_list : export_clause
                   | export_range
                   | export_list COMMA export_clause
                   | export_list COMMA export_range'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 4:
        t[0] = t[1] + [t[3]]


def p_export_clause(t):
    '''export_clause : exportable_name
                     | export_renaming_clause'''
    t[0] = {'export_clause': t[1]}


def p_exportable_name(t):
    '''exportable_name : name
                       | PROTECTED name'''
    if len(t) == 2:
        t[0] = {'exportable_name': t[1]}
    elif len(t) == 3:
        t[0] = {'exportable_name': [t[1], t[2]]}


def p_export_renaming_clause(t):
    '''export_renaming_clause : exportable_name EG identifier'''
    t[0] = {'export_renaming_clause': [t[1], t[3]]}


def p_export_range(t):
    '''export_range : first_constant_name DOTDOT last_constant_name'''
    t[0] = {'export_range': [{'start': t[1]}, {'end': t[3]}]}


def p_first_constant_name(t):
    '''first_constant_name : name'''
    t[0] = {'first_constant_name': t[1]}


def p_last_constant_name(t):
    '''last_constant_name : name'''
    t[0] = {'last_constant_name': t[1]}


def p_module_parameter_list(t):
    '''module_parameter_list : identifier_list'''
    t[0] = {'module_parameter_list': {'identifier_list': t[1]}}


def p_module_block(t):
    '''module_block : import_part END
                 | import_part initialization_part END
                 | import_part finalization_part END
                 | import_part initialization_part finalization_part END
                 | import_part module_block_middle_part END
                 | import_part module_block_middle_part initialization_part END
                 | import_part module_block_middle_part finalization_part END
                 | import_part module_block_middle_part '''\
                    '''initialization_part finalization_part END'''
    if len(t) == 3:
        t[0] = {'module_block': t[1]}
    elif len(t) == 4:
        if list(t[2])[0] == 'initialization_part' or\
        list(t[2])[0] == 'finalization_part':
            t[0] = {'module_block': [t[1], t[2]]}
        else:
            t[0] = {'module_block': [t[1], {'module_block_middle_part': t[2]}]}
    elif len(t) == 5:
        if list(t[2])[0] == 'initialization_part':
            t[0] = {'module_block': [t[1], t[2], t[3]]}
        else:
            t[0] = {'module_block': [t[1], {'module_block_middle_part': t[2]},
                                     t[3]]}
    elif len(t) == 6:
        t[0] = {'module_block': [t[1], {'module_block_middle_part': t[2]},
                                 t[3], t[4]]}


def p_module_block_middle_part(t):
    '''module_block_middle_part : constant_definition_part
        | type_definition_part
        | variable_declaration_part
        | procedure_and_function_declaration_part
        | module_block_middle_part constant_definition_part
        | module_block_middle_part type_definition_part
        | module_block_middle_part variable_declaration_part
        | module_block_middle_part procedure_and_function_declaration_part'''
    if len(t) == 2:
        if  list(t[1])[0] == 'constant_definition_part' or\
            list(t[1])[0] == 'type_definition_part' or\
            list(t[1])[0] == 'variable_declaration_part':
                t[0] = [t[1]]
        else:
            t[0] = [{'procedure_and_function_declaration_part': t[1]}]
    elif len(t) == 3:
        if  list(t[2])[0] == 'constant_definition_part' or\
            list(t[2])[0] == 'type_definition_part' or\
            list(t[2])[0] == 'variable_declaration_part':
                t[0] = t[1] + [t[2]]
        else:
            t[0] = t[1] + [{'procedure_and_function_declaration_part': t[2]}]


def p_initialization_part(t):
    '''initialization_part : TO BEGIN DO statement SEMICOLON'''
    t[0] = {'to_begin_do': t[4]}


def p_finalization_part(t):
    '''finalization_part : TO END DO statement SEMICOLON'''
    t[0] = {'to_end_do': t[4]}


def p_module_identification(t):
    '''module_identification : MODULE module_identifier '''\
        '''implementation_directive'''
    t[0] = {'module_identification': [t[2], t[3]]}


def p_module_identifier(t):
    '''module_identifier : identifier'''
    t[0] = {'module_identifier': t[1]}


def p_implementation_directive(t):
    '''implementation_directive : directive'''
    t[0] = {'implementation_directive': t[1]}


def p_empty(t):
    '''empty :'''
    t[0] = {'empty': None}


def p_error(t):
    try:
        raise PascalSyntaxError(t.type, t.value, t.lineno)
    except AttributeError:
        raise PascalSyntaxError('EMPTY_FILE', '', 0)
