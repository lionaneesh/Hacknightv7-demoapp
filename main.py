#!/usr/bin/env python
#
# Copyright (C) 2014 Aneesh Dogra <lionaneesh@gmail.com>
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

import webapp2
import logging
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from Template_Handler import Handler

#-- Database Classes

from Post import Post

#---- Webpage Handlers

class home(Handler):
    def get(self):
        poster = users.get_current_user()
        u = db.GqlQuery("SELECT * FROM Post WHERE user=:1 ORDER BY created DESC LIMIT 50", poster)
        recent = u.fetch(50)
        
        if poster:
            self.render('index.html', posts=recent)

        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        poster = users.get_current_user()
        content = self.request.get('content').strip()

        if poster:
            if content:
                u = Post(content = content, user = poster)
                u.put()
                self.redirect("/")
                # First update the recent posts
            else:
                self.redirect(users.create_login_url(self.request.uri))

class view_post(Handler):
    def get(self, id):
        poster = users.get_current_user()
        u = Post.get_by_id(int(id))
        if u == None:
            self.error(404);
        else:
            self.render("view_post.html",
                        post=u,
                        poster=poster)

class like_post(Handler):
    def get(self, id):
        poster = users.get_current_user()
        u = Post.get_by_id(int(id))
        if u == None:
            self.error(404);
        else:
            if poster.email() not in u.liked_by:
                u.liked_by.append(poster.email())
                u.likes += 1
                u.put()
            else:
                self.error(304)
            self.redirect("/post/" + id)


class view_user(Handler):
    def get(self, email):
        poster = users.get_current_user()
        viewing = users.User(email=email)
        u = db.GqlQuery("SELECT * FROM Post WHERE user=:1 ORDER BY created DESC LIMIT 50", viewing)
        posts = u.fetch(None)
        if not u or len(posts) == 0:
            self.error(404)
        else:
            self.render("view_user.html",
                        viewing=viewing,
                        posts=posts,
                        poster=poster)

app = webapp2.WSGIApplication([(r'/', home),
                               (r'/post/([0-9]+)', view_post),
                               (r'/post/like/([0-9]+)', like_post),
                               (r'/users/(.+)', view_user)], debug=True)
