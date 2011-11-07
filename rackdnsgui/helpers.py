# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Andrew Regner <andrew@aregner.com>
#
# This program is free software; you can redistribute it and#or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA  02111-1307, USA.

"""Corky helper functions.

Simple things like printing common errors, verbose, and debugging output.

"""

__all__ = [
        "error",
        "debug",
        "verbose",
        ]

import sys

from inspect import stack

from colors import TerminalController

TERMINAL = TerminalController()

COLORIZE = "none"

def colorize(color, message, out = sys.stdout):
    """Colorize the given message with the given color.

    If COLOR is "none" we shall simply bypass colorizing otherwise we will try
    to add the requested appropriate color.

    """
    if COLORIZE == "none":
        print >> out, message
    else:
        print >> out, TERMINAL.render('${%s}%s${NORMAL}' % (color, message))

def debug(file_, message = None, *args, **kwargs):
    """Print a debugging message to the standard error."""

    output = []

    if message and len(args):
        output.append(message % args)
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([ 
            "%s -> %s" % (key, val) for key, val in kwargs.items() ])

    for line in output:
        colorize("YELLOW", "D: %s:%s %s" % (file_, unicode(stack()[1][2]),
            line), sys.stderr)

def verbose(message = None, *args, **kwargs):
    """Print a verbose message to the standard error."""

    output = []

    if message and len(args):
        output.append(message % args)
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([
            "%s -> %s" % (key, val) for key, val in kwargs.items() ])

    for line in output:
        colorize("BLUE", "V: %s" % line, sys.stderr)

def error(message = None, *args, **kwargs):
    """Print an error message to the standard error."""

    output = []

    if message and len(args):
        output.append(message % args)
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([
            "%s -> %s" % (key, val) for key, val in kwargs.items() ])

    for line in output:
        colorize("RED", "E: %s" % line, sys.stderr)

