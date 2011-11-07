# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Andrew Regner <andrew@aregner.com>             
#                                                                    
# This program is free software; you can redistribute it andor modify it under
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

"""RackDNSGui Main Application Module
"""

import os
import random
import argparse
import tornado.web
import tornado.ioloop

import helpers
import handlers

class RackDNSGuiApplication(object):
    """Main Application class for rackdnsgui."""

    def __init__(self):
        self._debug = False
        self._verbose = False
        self._quiet = False

        arguments = RackDNSGuiOptions("rackdnsgui").parsed_args

        self._quiet = arguments.quiet
        self._debug = arguments.debug

        # If we have debugging turned on we should also have verbose.
        if self._debug: 
            self._verbose = True
        else: 
            self._verbose = arguments.verbose

        # If we have verbose we shouldn't be quiet.
        if self._verbose: 
            self._quiet = False

        # Other option handling ...
        helpers.COLORIZE = arguments.color

        self._port = arguments.port

    def run(self):
        """Run the application ... """
        cookie_secret = "testingtestingtestingtesting" if self._debug else \
            "".join([chr(random.randint(0,254)) for n in xrange(40)])
        options = {
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'cookie_secret': cookie_secret,
            'debug': self._debug,
        }
        helpers.debug(__file__, repr(options))
        webapp = tornado.web.Application([
            (r"/(login)?", handlers.LoginHandler),
            (r"/zones(.*)", handlers.ZoneHandler),
            ("/favicon.ico", handlers.NullHandler),
            ], **options)
        webapp.listen(self._port)
        tornado.ioloop.IOLoop.instance().start()

class RackDNSGuiOptions(object):
    """Options for the rackdnsgui application."""

    def __init__(self, name):
        """Create the option parser."""
        self._parser = argparse.ArgumentParser(prog = name)
        self._parser = self._add_args()

    @property
    def parser(self):
        """Return the option parser."""
        return self._parser

    @property
    def parsed_args(self):
        """Return the parsed arguments."""
        return self._parser.parse_args()

    def _add_args(self):
        """Add the options to the parser."""

        self._parser.add_argument('--version', action = "version", 
                version = "%(prog)s 0.1")
       
        # --verbose, -v
        help_list = [
                "Specifies verbose output from the application.",
                ]
        self._parser.add_argument('--verbose', '-v', action = 'store_true', 
                default = False, help = ''.join(help_list))

        # --debug, -D
        help_list = [
                "Specifies debugging output from the application.  Implies verbose ",
                "output from the application.",
                ]
        self._parser.add_argument('--debug', '-D', action = 'store_true', 
                default = False, help = ''.join(help_list))

        # --quiet, -q
        help_list = [
                "Specifies quiet output from the application.  This is ",
                "superceded by verbose output.",
                ]
        self._parser.add_argument('--quiet', '-q', action = 'store_true', 
                default = False, help = ''.join(help_list))

        # --color=[none,light,dark,auto]
        help_list = [
                "Specifies whether output should use color and which type of ",
                "background to color for (light or dark).  This defaults to ",
                "the value of system.color in the configuration file.",
                ]
        self._parser.add_argument('--color', 
                choices = [ "none", "light", "dark", "auto", ], 
                default = "none", help = ''.join(help_list))

        # --port, -p
        help_list = [
                "Specifies the port for RackDNSGui to listen on.",
                ]
        self._parser.add_argument('--port', '-p', default = 5051, type = int, 
                help = ''.join(help_list))

        return self._parser

