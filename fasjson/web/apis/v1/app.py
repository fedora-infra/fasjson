from flask import Blueprint

from . import resources


app = Blueprint('v1 api', __name__)

#root
app.add_url_rule('/', view_func=resources.root)
#me / whoami
app.add_url_rule('/me', view_func=resources.me)
#groups
app.add_url_rule('/groups', view_func=resources.groups)
app.add_url_rule('/groups/<name>/members', view_func=resources.group_members)
#users
app.add_url_rule('/users/<username>', view_func=resources.user)