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
    pStack[-1] = pStack[-1][:-2]
    pStack.append("= " + str(stack.pop())) # Append total
    pStack.append(" " + str(sCom)) # Append comment
    return ''.join(pStack)

def channelAnnounce(inString, boldText=False, underText=False, foreColor=None):
    if boldText:
        inString = format.bold(inString)
    if underText:
        inString = format.underline(inString)
    if foreColor == None:
        pass
    elif foreColor == "Black":
        inString = format.color(inString, format.BLACK)
    elif foreColor == "Navy Blue":
        inString = format.color(inString, format.NAVY_BLUE)
    elif foreColor == "Green":
        inString = format.color(inString, format.GREEN)
    elif foreColor == "Red":
        inString = format.color(inString, format.RED)
    elif foreColor == "Lime Green":
        inString = format.color(inString, format.LIME_GREEN)
    elif foreColor == "Teal":
        inString = format.color(inString, format.TEAL)
    elif foreColor == "Aqua":
        inString = format.color(inString, format.AQUA)
    elif foreColor == "Blue":
        inString = format.color(inString, format.BLUE)
    elif foreColor == "Brown":
        inString = format.color(inString, format.BROWN)
    elif foreColor == "Purple":
        inString = format.color(inString, format.PURPLE)
    elif foreColor == "Olive":
        inString = format.color(inString, format.OLIVE)
    elif foreColor == "Yellow":
        inString = format.color(inString, format.YELLOW)
    elif foreColor == "Pink":
        inString = format.color(inString, format.PINK)
    elif foreColor == "Dark Gray":
        inString = format.color(inString, format.DARK_GRAY)
    elif foreColor == "Light Gray":
        inString = format.color(inString, format.LIGHT_GRAY)
    elif foreColor == "White":
        inString = format.color(inString, format.WHITE)
    return inString
    
class DiceBot(bot.SimpleBot):
    def on_channel_message(self, event):
        if event.message[0] != "!":
            return
        if event.message[1:5] == "roll":
            dice_output = str(dice_eval(event.message[6:]))
            if len(dice_output)>400:
                while len(dice_output)>400:
                    self.send_message(event.target, event.source + " rolled: " + dice_output[:400])
                    dice_output = dice_output[400:]
                self.send_message(event.target, event.source + " rolled: " + dice_output)
            else:
                self.send_message(event.target, event.source + " rolled: " + dice_output)
        
        if event.message[1:6] == "begin":
            self.send_message(event.target, channelAnnounce("**********Begin Session**********",True, False,"Green"))
        if event.message[1:6] == "pause":
            self.send_message(event.target, channelAnnounce("**********Pause   Session**********",True, False,"Pause"))
        if event.message[1:4] == "end":
            self.send_message(event.target, channelAnnounce("**********End Session**********",True, False,"Red"))


if __name__ == "__main__":
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
