# Makefile for DiceBot

DICEBOT_SCRIPT=PyRCDicebot-0.2.1.py

.PHONY: build run clean
build:
	# nothing here, actually

run:
	python $(DICEBOT_SCRIPT)

clean:
	rm -rf *.pyc
