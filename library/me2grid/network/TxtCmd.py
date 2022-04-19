"""!
@file  TxtCmd.py
@brief Library for textual command interpretation

@section Description

This Library contains the stack opbjects for evaluating textual command strings.

Von Nutzer an Bad Heizung an der Wand setze Temperatur auf 15 °C
From user to bath wall heater set temperature to 15 °C

The command string starts with either
a structural word,
an address string (may contain several words)
an optional command
or an parameter or process name

Structural words:
Von ... any      surounds the sending device


"""
