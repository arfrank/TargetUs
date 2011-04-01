# -*- coding: utf-8 -*-
"""App configuration."""
config = {}

# Configurations for the 'tipfy' module.
config['tipfy'] = {
    'auth_store_class': 'tipfy.auth.MultiAuthStore',
}

config['tipfy.sessions'] = {
    'secret_key': 'hasjdkfhakljsdfhiluhi2ufh32uhfb2h3f97p2bfyg23ifuyhkjg23hjf23gf2g3f8i2y3fkuj23gfhkj23gf',
}

config['tipfy.auth.facebook'] = {
    'api_key':    'XXXXXXXXXXXXXXX',
    'app_secret': 'XXXXXXXXXXXXXXX',
}

config['tipfy.auth.friendfeed'] = {
    'consumer_key':    'XXXXXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXXXXX',
}

config['tipfy.auth.twitter'] = {
    'consumer_key':    'XXXXXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXXXXX',
}

config['tipfyext.jinja2'] = {
    'environment_args': {
        'autoescape': True,
        'extensions': [
            'jinja2.ext.autoescape',
            'jinja2.ext.i18n',
            'jinja2.ext.with_'
        ],
    },
}
config['site'] = {
'appspot_id':'target-us',
'main_url':'http://target-us.appspot.com/',
'title': 'TargetUs',
'subdomain':'target-us.appspot.com/',
}
