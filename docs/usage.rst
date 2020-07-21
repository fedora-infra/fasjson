Usage
-----

::

   $ kinit
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/
   {"result": [{"name": "test-group", "uri": "http://$(hostname)/fasjson/v1/groups/test-group/"}]}
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/admins/
   {"result": {"name": "test-group", "uri": "http://fasjson.example.test/fasjson/v1/groups/test-group/"}}
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/admins/sponsors/
   {"result": [{"username": "admin", [...]}, {"username": "user123", [...]}]}
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/admins/members/
   {"result": [{"username": "admin", [...]}, {"username": "user123", [...]}]}
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/admin/
   {"result": {"username": "admin", "surname": "Administrator", "givenname": "", "emails": ["admin@$(domain)"], "ircnicks": null, "locale": "fr_FR", "timezone": null, "gpgkeyids": null, "creation": "2020-04-23T10:16:35", "locked": false, "uri": "http://$(hostname)/fasjson/v1/users/admin/"}}
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/admin/groups/
   {"result": [{"name": "test-group", "uri": "http://$(hostname)/fasjson/v1/groups/test-group/"}]}
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/search/users/?username=admin&ircnick=admin&surname=admin&givenname=admin&email=admin@example.test
   {"result": [{"username": "admin", [...]}, {"username": "badminton", [...]}]}
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/me/
   {"result": {"dn": "uid=admin,cn=users,cn=accounts,dc=$(domain)", "username": "admin", "uri": "http://$(hostname)/fasjson/v1/users/admin/"}}
