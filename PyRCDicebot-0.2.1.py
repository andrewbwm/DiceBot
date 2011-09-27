#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Custom IRC Dicebot.    
"""
"""
Copyright (c) 2010 David Ross

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from ircutils import bot, format
import re, random
import operator
import sys

def dice_eval(s):
    sCom = ""
    if re.search(r"\(.*\)", s):
        sCom = re.search(r"\(.*\)", s).group(0) # Take comment aside
    s = s.replace(" ","")
    s = re.sub(r"\(.*\)", r"", s) # Strip comment
    s = re.sub(r"(\d+|[d+*])", r"\1 ",s) # seperate tokens by spaces
    s = re.sub(r"(^|[+*] )d", r"\g<1>1 d",s) # e.g. change d6 to 1d6
    while "*" in s:
        s = re.sub(r"([^+]+) \* ([^+]+)", r"\1 \2mul ", s, 1)
    while "+" in s:
        s = re.sub(r"(.+) \+ (.+)", r"\1 \2add ", s, 1)
    s = re.sub(r"d (\d+) ", r"\1 roll ", s)

    stack = []
    pStack = []

    for token in s.split():
        if token == "mul":
            stack.append(stack.pop() * stack.pop())
        elif token == "add":
            stack.append(stack.pop() + stack.pop())
#        elif token == "sub": # Implement
#            stack.append(stack.pop() - stack.pop())
        elif token == "roll":
            tValue = 0
            dice = stack.pop()
            for i in xrange(stack.pop()):
                if dice == 0:
                    temp = 0
                else:
                    temp = random.randint(1,dice)
                tValue += temp
                pStack.append("d" + str(dice) + ":" + str(temp)+" + ")
            stack.append(tValue)
        elif token.isdigit():
            stack.append(int(token))
        elif token == "(":
            return
        else:
            return

    assert len(stack) == 1
    if len(pStack):
        pStack[-1] = pStack[-1][:-2]
        pStack.append("= ")
    pStack.append(str(stack.pop())) # Append total
    pStack.append(" " + str(sCom)) # Append comment
    return ''.join(pStack)

def do_roll(user, s):
    if s == "":
         return ""
    return user + " rolled: " + str(dice_eval(s))

def do_command(user, cmd, args):
    if cmd == "roll":
        return do_roll(user, reduce(operator.add, args, ""))
    if cmd == "begin":
        return "**********Begin Session**********"
    if cmd == "pause":
        return "**********Pause Session**********"
    if cmd == "end":
        return "**********End Session**********"
    if cmd == "miau":
        return "**********Miau Session**********"
    return ">^o^<"

class DiceBot(bot.SimpleBot):
    def on_channel_message(self, event):
        if event.message[0] != "!":
            return
        split_str = event.message[1:].split()
        if len(split_str) < 1:
            return
        out_str = do_command(event.source, split_str[0], split_str[1:])
        self.send_message(event.target, out_str)

DEBUG = 0

if __name__ == "__main__":
    if DEBUG:
        while True:
            split_str = sys.stdin.readline().split()
            if len(split_str) < 1:
                continue
            print do_command("miau", split_str[0], split_str[1:])
    dice = DiceBot("PyRC_Dicebot")
    dice.connect("irc.freenode.net", channel=["#thh-dnd"])
    dice.start()

'''
Feature requests:
Print results of each roll [x]
Subtraction [ ]
Error handling [x]
Auto-restart [ ]
Other commands [ ]
Multiline output past 444 characters [ ]
!begin and !end [ ]
'''

'''
Errors to check for:
1d0

'''
