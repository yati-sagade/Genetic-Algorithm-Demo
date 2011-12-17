#===============================================================#
# expr.py                                                       #
#   routines to evaluate simple arithmetic expressions.         #
# Author: Yati Sagade (yati [dot] sagade [at] gmail [dot] com)  #
#===============================================================#
OPERATORS = ['+', '-', '/', '*']
PRECEDENCE = {'+': 0, 
              '-': 0, 
              '/': 1, 
              '*': 1}

EVAL_OPERATOR =  {  '+': lambda x, y: x + y,
                    '-': lambda x, y: x - y,
                    '*': lambda x, y: x * y,
                    '/': lambda x, y: x / y
                 }

DIGITS = range(10)
DIGITS_STR = map(str, DIGITS)
#----------------------------------------------------------------
def is_digit(c):
    return c in DIGITS_STR
#----------------------------------------------------------------
def is_numeral(x):
    for d in str(x):
        if not is_digit(d):
            return False

    return True
#----------------------------------------------------------------
def is_operator(x):
    return x in OPERATORS
#----------------------------------------------------------------
def prec(op):
    return PRECEDENCE[op]
#----------------------------------------------------------------
def infix_to_postfix(expr):
    '''expr is a LIST of tokens, i.e., numerals, variable names and 
       operator symbols.
    '''
    postfix = []
    stack = []

    for token in expr:
        if is_numeral(token):
            postfix.append(token)

        elif is_operator(token):
            if not len(stack):
                stack.append(token)
            
            else:
                while len(stack) and prec(stack[-1]) >= prec(token):
                    top = stack.pop()
                    postfix.append(top)

                stack.append(token)

        elif token == '(':
            stack.append(token)

        elif token == ')':
            top = stack.pop()
            while top != '(':
                postfix.append(top)
                top = stack.pop()

        else:
            raise NameError('unrecognized symbol: {symbol}'.format(symbol=token))

    while len(stack):
        postfix.append(stack.pop())

    return postfix
#----------------------------------------------------------------
def evaluate_postfix(expr):
    stack = ['(']
    my_expr = expr[:]
    my_expr.append(')')

    for token in my_expr:
        if token not in OPERATORS:
            if token == ')': # right sentinel
                return stack.pop()

            stack.append(token)
        else:
            y = stack.pop()
            x = stack.pop()
            result = EVAL_OPERATOR[token](x, y)
            stack.append(result)
#----------------------------------------------------------------
def evaluate(expr):
    postfix = infix_to_postfix(expr)
    return evaluate_postfix(postfix)
#----------------------------------------------------------------




