# -*- coding: utf-8 -*-
"""URL definitions."""
from tipfy import Rule

rules = [
	Rule('/', name='home', handler='content.handlers.MainHandler'),
#	Rule('/pretty', name='hello-world-pretty', handler='hello_world.handlers.PrettyHelloWorldHandler'),
#	Rule('/', endpoint='home', handler='auth.handlers.HomeHandler'),
	Rule('/auth/login', endpoint='auth/login', handler='auth.handlers.LoginHandler'),
	Rule('/auth/logout', endpoint='auth/logout', handler='auth.handlers.LogoutHandler'),
	Rule('/auth/signup', endpoint='auth/signup', handler='auth.handlers.SignupHandler'),
	Rule('/auth/register', endpoint='auth/register', handler='auth.handlers.RegisterHandler'),

	Rule('/auth/facebook/', endpoint='auth/facebook', handler='auth.handlers.FacebookAuthHandler'),
	Rule('/auth/friendfeed/', endpoint='auth/friendfeed', handler='auth.handlers.FriendFeedAuthHandler'),
	Rule('/auth/google/', endpoint='auth/google', handler='auth.handlers.GoogleAuthHandler'),
	Rule('/auth/twitter/', endpoint='auth/twitter', handler='auth.handlers.TwitterAuthHandler'),
	Rule('/auth/yahoo/', endpoint='auth/yahoo', handler='auth.handlers.YahooAuthHandler'),

	Rule('/content', endpoint='content/index', handler='auth.handlers.ContentHandler'),
	Rule('/r/<hash>', endpoint='redirect', handler='redirector.handlers.MainHandler'),
	Rule('/background/statistics', endpoint='redirect', handler='statistics.handlers.MainHandler'),
]
