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
from diceparse import diceparse, ParseException
from collections import OrderedDict
import re, random
import operator
import sys

import config

# "constants"
PARSE_ERROR = "couldn't parse input"
def parse_error_message(name):
    print name + " inputted some garbage"

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
            return (None, 0)
        else:
            return (None, 0)

    assert len(stack) == 1
    if len(pStack):
        pStack[-1] = pStack[-1][:-2]
        pStack.append("= ")

    total = stack.pop()
    pStack.append(str(total)) # Append total
    pStack.append(" " + str(sCom)) # Append comment

    return (''.join(pStack), total)

def do_roll(user, s):
    if s == "":
         return ""
    try:
        (output, value) = diceparse(s).dice_eval()
    except ParseException:
        parse_error_message(user)
        return PARSE_ERROR
    return user + " rolled: " + output

# Initiative dictionary: (name, initiative) pairs
initiative = {}

def initiative_add(name, dice_string, monster = False):
    try:
        (output, value) = diceparse(dice_string).dice_eval()
    except ParseException:
        parse_error_message(name)
        return PARSE_ERROR
    if monster:
        value = value + 0.1 # On equal values, monsters have priority
    if value >= 1:
        if name == "Velten":
            if name not in initiative or initiative[name] < value:
                initiative[name] = value
        else:
            initiative[name] = value

    return name + " rolled: " + output

def initiative_query(name):
    if name not in initiative:
        return "No initiative value for " + name
    value = str(int(initiative[name]))
    return "Initiative value for " + name + ": " + value

def do_initiative(user, args):
    global initiative

    if len(args) == 0: # Query
        sorted_pairs = sorted(initiative.items(), key = lambda x : x[1],
                                                 reverse = True)
        formatted_pairs = map(lambda(name, value):
                            name + "(" + str(int(value)) + ") ", sorted_pairs)
        return reduce(operator.add, formatted_pairs, "")

    if len(args) == 2 and args[0].strip() == "reset":
        del initiative[args[1]]
        return "Initiative score reset for " + args[1]
    if len(args) == 1 and args[0].strip() == "reset":
        initiative = {}
        return "Initiative scores reset"

    if len(args) == 1 and not args[0].isdigit(): # Single-value query
        return initiative_query(name = args[0])

    if len(args) >= 1:
        if args[0].isdigit():  # Player initiative roll
            return initiative_add(name = user,
                dice_string = "d20 + " + reduce(operator.add, args, ""))

    if len(args) >= 2: # Monster initiative roll
        return initiative_add(name = args[0],
            dice_string = "d20 + " + reduce(operator.add, args[1:], ""),
            monster = True)

    return "Cats are not cool"

damage = {}
def damage_add(name, dice_string, monster = False):
    try:
        (output, value) = diceparse(dice_string).dice_eval()
    except ParseException:
        parse_error_message(name)
        return PARSE_ERROR
    if name in damage:
        damage[name] += value
    else:
        damage[name] = value
    return name + " has " + str(damage[name]) + " damage"

def damage_query(name):
    if name not in damage:
        return "No damage value for " + name
    value = str(int(damage[name]))
    return "Damage value for " + name + ": " + value

def do_damage(user, args):
    global damage

    if len(args) == 0: # Query
        sorted_pairs = sorted(damage.items(), key = lambda x : x[1],
                                                 reverse = True)
        formatted_pairs = map(lambda(name, value):
                            name + "(" + str(int(value)) + ") ", sorted_pairs)
        return reduce(operator.add, formatted_pairs, "")

    if len(args) == 1 and args[0][0] == "-":
        return damage_add(name = user,
            dice_string = reduce(operator.add, args, ""))
    if len(args) == 2 and args[0].strip() == "reset":
            del damage[args[1]]
            return "Damage score reset for " + args[1]
    if len(args) == 1 and args[0].strip() == "reset":
            damage = {}
            return "Damage scores reset"
    if len(args) == 1 and not args[0].isdigit(): # Single-value query
        return damage_query(name = args[0])

    if len(args) >= 1:
        if args[0].isdigit():  # Player damage roll
            return damage_add(name = user,
                dice_string = reduce(operator.add, args, ""))

    if len(args) >= 2: # Monster damage roll
        return damage_add(name = args[0],
            dice_string = reduce(operator.add, args[1:], ""),
            monster = True)

    return "W00T"

entities = {}

def do_status(user, args):
	global entities
	for i in initiative:
		if i in damage:
			entities[i] = (int(initiative[i]), damage[i])
		else:
			entities[i] = (int(initiative[i]), 0)
	sorted_ent = OrderedDict(sorted(entities.items(), key=lambda t: t[1][0], reverse=True))
	status = []
	i = 0
	for x in sorted_ent:
		i += 1
		status.append(str(i) + ". " + x + "\t\t" + str(sorted_ent[x][0]) + "\t\t" + str(sorted_ent[x][1]))
	return status

def do_command(user, cmd, arg):
    if cmd == "roll":
        return do_roll(user, arg)
    if cmd == "initiative":
        return do_initiative(user, arg.split())
    if cmd == "damage":
        return do_damage(user, arg.split())
    if cmd == "status":
        return do_status(user, arg.split())
    if cmd == "begin":
        return "**********Begin Session**********"
    if cmd == "pause":
        return "**********Pause Session**********"
    if cmd == "end":
        return "**********End Session**********"
    if cmd == "miau":
        return "**********Miau Session**********"
    if cmd == "tpk":
        return "Roll new characters"
    return "Cats are not cool"

class DiceBot(bot.SimpleBot):
    def on_channel_message(self, event):
        if event.message[0] != "!":
            return

        # input_str = string without the leading '!'
        input_str = event.message[1:].strip()
        if len(input_str) < 1:
            return

        # command = first word of input string
        command = input_str.split()[0]

        out_str = do_command(event.source, command,  input_str[len(command):])

        if isinstance(out_str, list):
            for s in out_str:
                self.send_message(event.target, s)
        if isinstance(out_str, str):
            self.send_message(event.target, out_str)

if __name__ == "__main__":
    if config.DEBUG:
        while True:
            split_str = sys.stdin.readline().split()
            if len(split_str) < 1:
                continue
            print do_command("miau", split_str[0], split_str[1:])
    dice = DiceBot(config.name)
    dice.connect(config.server, channel=[config.channel])
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
