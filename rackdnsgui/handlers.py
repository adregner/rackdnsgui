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

        email_address = self.get_cookie('rcloud_soa_email')
        
        # root request
        if len(url) < 2 or not url[1]:
            self.redirect('/zones/list')
        
        # SHOW ZONES
        elif url[1] == 'list':
            domains = conn.list_domains_info()
            tpl_args = {
                    'domains': domains,
                    'username': username,
                    'email': email_address,
                    }
            self.render('zones_list.py.html', **tpl_args)
        
        # EDIT RECORD
        elif len(url) > 2 and url[1].isdigit():
            domain = conn.get_domain(int(url[1]))
            record = domain.get_record(url[2])
            
            tpl_args = {
                    'domain': domain,
                    'record': record,
                    }
            self.render('record_show.py.html', **tpl_args)

        # EDIT ZONE (SHOW RECORDS)
        elif url[1].isdigit():
            domain = conn.get_domain(int(url[1]))
            records = domain.list_records_info()

            records_a_aaaa_cname = []
            records_mx_srv = []
            records_txt = []
            records_ns = []

            for r in records:
                if r['type'] in ('A', 'AAAA', 'CNAME'):
                    records_a_aaaa_cname.append(r)
                elif r['type'] in ('MX', 'SRV'):
                    records_mx_srv.append(r)
                elif r['type'] in ('TXT',):
                    records_txt.append(r)
                elif r['type'] in ('NS',):
                    records_ns.append(r)

            tpl_args = {
                    'domain': domain,
                    'records': records,
                    'email': email_address,
                    'records_a_aaaa_cname': records_a_aaaa_cname,
                    'records_mx_srv': records_mx_srv,
                    'records_txt': records_txt,
                    'records_ns': records_ns,
                    }

            self.render('zones_show.py.html', **tpl_args)

    def post(self, url):
        helpers.debug(__file__, url = url)
        url = url.split('/')

        username, key = self.get_secure_cookie('rcloud_login').split()
        conn = clouddns.connection.Connection(username, key)

        email_address = self.get_cookie('rcloud_soa_email')

        # save the email address to be entered later
        if self.get_argument('email', default=""):
            email_address = self.get_argument('email')
            self.set_cookie('rcloud_soa_email', email_address)

        if len(url) < 2 or not url[1]:
            # add a zone
            d_name = self.get_argument('name')
            d_ttl = self.get_argument('ttl')
            conn.create_domain(d_name, d_ttl, email_address)

        elif len(url) > 2 and url[1].isdigit():
            # edit a record
            domain = conn.get_domain(int(url[1]))
            record = domain.get_record(url[2])

            r = {}
            r['name'] = self.get_argument('name', None)
            r['data'] = self.get_argument('data', None)
            r['ttl'] = self.get_argument('ttl', None)
            r['comment'] = self.get_argument('comment', None)

            if record.type in ('MX', 'SRV'):
                r['priority'] = self.get_argument('priority', None)

            # unset things that don't change
            for field in r.keys():
                cur_val = record.__dict__[field]
                if cur_val and r[field] == cur_val:
                    del r[field]

            record.update(**r)

            # we don't want to go back to the same edit record page
            del url[2]

        elif url[1].isdigit():
            # add a record (edit a zone not really applicable?)
            domain = conn.get_domain(int(url[1]))

            r = {}
            r['name'] = self.get_argument('name')
            r['type'] = self.get_argument('type')
            r['data'] = self.get_argument('data')
            r['ttl'] = self.get_argument('ttl', None)
            r['comment'] = self.get_argument('comment', None)

            if r['type'] in ('MX', 'SRV'):
                r['priority'] = self.get_argument('priority', None)

            domain.create_record(**r)

        self.redirect('/zones%s' % "/".join(url))

class LoginHandler(tornado.web.RequestHandler):
    def get(self, url):
        helpers.debug(__file__, url = url)
        
        if not url:
            self.redirect('/login')
        elif url == 'login' and self.get_secure_cookie('rcloud_login'):
            if self._verify_api_key():
                self.redirect('/zones/list')
            else:
                self.render('login.py.html')
        elif url == 'logout':
            self.clear_cookie('rcloud_login')
            self.redirect('/login')
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

