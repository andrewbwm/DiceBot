#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
A simple parser for arithmetic expressions, also adding
support for expressions having the form XdY, where X and Y
are numbers. The meaning is: roll X dies of Y sides.

The precedence of the d operator is the same as that of the
* operator.
"""

import shlex
import re,random

# parser class
# TODO: pStack
class diceparse(shlex.shlex):

    # constructor
    def __init__(self, s):
        s = s.replace(" ","")
        s = re.sub(r"\(.*\)", r"",s) # Strip comment
        s = re.sub(r"(\d+|[d+*-])", r"\1 ",s) # seperate tokens by spaces
        s = re.sub(r"(^|[+*] )d", r"\g<1>1 d",s) # e.g. change d6 to 1d6
        shlex.shlex.__init__(self,s)

    # eval function
    def dice_eval(self):
        # first term
        term_tok = self.__term_eval()

        # operator
        op_tok = self.get_token()

        if not op_tok:
            # simple expression
            return term_tok
        elif op_tok == '+':
            # next tokens
            expr_tok = self.dice_eval()
            return term_tok + expr_tok
        elif op_tok == '-':
            # next tokens
            expr_tok = self.dice_eval()
            return term_tok - expr_tok
        else:
            raise ParseException(str(op_tok) + ": unknown operator")

    # evaluate a term
    def __term_eval(self):
        # first factor
        tok = self.get_token()
        if not tok or (not tok.isdigit()):
            raise ParseException("missing operand")
        else:
            tok = int(tok) # really ugly, but does the job

        # maybe we have operators
        op_tok = self.get_token()
        if not op_tok or op_tok == '+' or op_tok == '-':
            # nothing
            self.push_token(op_tok)
            return tok
        elif op_tok == '*':
            # more factors
            term_tok = self.__term_eval()
            return tok * term_tok
        elif op_tok == 'd':
            # die
            sides = self.get_token()
            if not sides:
                raise ParseException("number of sides not specified")

            return self.__roll(tok, sides)
        else:
            raise ParseException(str(tok) + ": unknown operator")

    def __roll(self, dies, sides):
        return 42 # TODO

class ParseException(Exception):
    def __init__(self, s):
        self.s = s 
    def __str__(self):
        return repr(self,s)

# test
obj = diceparse("d42 + 3 - 2 * 5")
print obj.dice_eval()
