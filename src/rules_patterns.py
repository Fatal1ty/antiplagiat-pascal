###############################################################################
'term = factor { multiplying_operator factor}'
def p_term(t):
    '''term : factor
            | term multiplying_operator factor'''
    if len(t) == 2:
        t[0] = {'term': t[1]}
    elif len(t) == 4:
        t[0] = {t[2]: (t[1], t[3])}
###############################################################################
'expression = simple_expression [ relational_operator simple_expression]'
def p_expression(t):
    '''expression : simple_expression
                  | relational_operator simple_expression'''
    if len(t) == 2:
        t[0] = {'expression': t[1]}
    elif len(t) == 3:
        t[0] = {'expression': {t[1]: t[2]}}
###############################################################################
# да, когда правило:     a | ba
# нет, когда правило:    a | bc 
def p_enumerated_type(t):
    '''enumerated_type : '(' identifier_list ')\''''
    t[0] = {'enumerated-type': {'identifier-list': t[1]}}

#если есть правило в стандарте, то его имя пишем в правиле, использующем его
def p_identifier_list(t):
    '''identifier_list : identifier
                       | identifier_list ',' identifier'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 4:
        if isinstance(t[1], tuple):
            t[0] = t[1] + (t[3],)
        else:
            t[0] = (t[1], t[3])
###############################################################################
# как поступать с sign, NOT (унарные операции)
def p_scale_factor(t):
    '''scale_factor : digit_sequence
                    | sign digit_sequence'''
    if len(t) == 2:
        t[0] = {'scale_factor': t[1]}
    elif len(t) == 3:
        t[0] = {'scale_factor': {t[1]: t[2]}}
###############################################################################