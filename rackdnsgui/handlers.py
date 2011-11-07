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

import tornado.web
import tornado.template
import sys
import os

import helpers

try:
    import clouddns
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "vendor", "python-clouddns"))
    import clouddns


class ZoneHandler(tornado.web.RequestHandler):
    def get(self, url):
        helpers.debug(__file__, url = url)
        url = url.split('/')
        
        username, key = self.get_secure_cookie('rcloud_login').split()
        conn = clouddns.connection.Connection(username, key)
        
        if len(url) < 2 or not url[1]:
            self.redirect('/zones/list')
        
        elif url[1] == 'list':
            domains = conn.list_domains_info()
            self.render('zones_list.py.html', domains=domains, username=username)
        
        elif url[1].isdigit():
            domain = conn.get_domain(int(url[1]))
            records = domain.list_records_info()
            self.render('zones_show.py.html', domain=domain, records=records)

class LoginHandler(tornado.web.RequestHandler):
    def get(self, url):
        helpers.debug(__file__, url = url)
        
        if not url or len(url) < 2 or not url[1]:
            self.redirect('/login')
        elif self.get_secure_cookie('rcloud_login'):
            if self._verify_api_key():
                self.redirect('/zones/list')
            else:
                self.render('login.py.html')
        else:
            self.render('login.py.html')

    def _verify_api_key(self, username=None, key=None):
        if not username or not key and self.get_secure_cookie('rcloud_login'):
            username, key = self.get_secure_cookie('rcloud_login').split()

        try:
            conn = clouddns.connection.Connection(username, key)
        except clouddns.errors.AuthenticationFailed:
            return False

        return True
        
    def post(self, url):
        helpers.debug(__file__, url = url)
        
        username = self.get_argument('username')
        key = self.get_argument('key')
        
        # verify the login information
        if not self._verify_api_key(username, key):
            self.set_status(403)
            self.write("Bad username or API key.")
            return

        # save it in a cookie on client
        self.set_secure_cookie('rcloud_login', "%s %s" % (username, key))

        self.redirect('/zones/list')

class NullHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(404)
        self.write("404 : Not Found")

