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
class diceparse(shlex.shlex):

    # constructor
    def __init__(self, s):
        self.sCom = "" # default comment
        if re.search(r"\(.*\)", s):
            self.sCom = re.search(r"\(.*\)", s).group(0) # Take comment aside
        s = s.replace(" ","")
        s = re.sub(r"\(.*\)", r"",s) # Strip comment
        s = re.sub(r"^(\+|\-)", r"0\1",s)
        s = re.sub(r"(\d+|[d+*-])", r"\1 ",s) # separate tokens by spaces
        s = re.sub(r"(^|[-+*] )d", r"\g<1>1 d",s) # e.g. change d6 to 1d6
        shlex.shlex.__init__(self,s)

        # other class variables
        self.pStack = []

    # public eval function
    def dice_eval(self):
        total = self.__dice_eval()

        if len(self.pStack):
            self.pStack[-1] = self.pStack[-1][:-2] # remove last " + "
            self.pStack.append("= ")
        self.pStack.append(str(total)) # Append total
        self.pStack.append(" " + str(self.sCom)) # Append comment

        return (''.join(self.pStack), total)

    # eval function
    def __dice_eval(self):
        # first term
        term_tok = self.__term_eval()

        # operator
        op_tok = self.get_token()

        while op_tok:
            # normally another term follows
            term2_tok = self.__term_eval()

            if op_tok == '+':
                term_tok = term_tok + term2_tok
            elif op_tok == '-':
                term_tok = term_tok - term2_tok
            else:
                raise ParseException(op_tok + ": unknown operator")

            op_tok = self.get_token()

        return term_tok

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

            return self.__roll(tok, int(sides))
        else:
            raise ParseException(str(tok) + ": unknown operator")

    def __roll(self, dies, sides):
        # roll it
        tValue = 0
        for i in xrange(dies):
            if sides == 0:
                temp = 0
            else:
                temp = random.randint(1,sides)
            tValue += temp
            self.pStack.append("d" + str(sides) + ":" + str(temp)+" + ")
        return tValue

class ParseException(Exception):
    def __init__(self, s):
        self.s = s 
    def __str__(self):
        return repr(self,s)

# test
# obj = diceparse("3d3 - d10 + 2 * 4 - 2*3 + 5")
# print obj.dice_eval()
