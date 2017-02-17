#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__name__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Posting(db.Model):
    title = db.StringProperty(required = True)
    posting = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def render_submission(self, title="", posting="", error=""):
        self.render("submission.html", title=title, posting=posting, error=error)

    def get(self):
        self.render_submission()

    def post(self):
        title = self.request.get("title")
        posting = self.request.get("posting")

        if title and posting:
            a = Posting(title = title, posting = posting)
            a.put()

            self.redirect("/blog/" + str(a.key().id()))
            return
        else:
            error = "We need both a title and some text to work!"
            self.render_submission(title, posting, error)

class ListingsHandler(Handler):
        def render_listings(self):
            postings = db.GqlQuery("SELECT * FROM Posting "
                                    "ORDER BY created DESC "
                                    "LIMIT 5 ")

            self.render("listings.html", postings=postings)

        def get(self):
            self.render_listings()
    #
    #     def get_posts(limit, offset):
    # # TODO: query the database for posts, and return them


class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        single = Posting.get_by_id( int(id) )
        self.response.out.write( single.posting )


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/listings', ListingsHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
