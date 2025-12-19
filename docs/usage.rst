Usage
-----

FasJSON provides a REST API to query user and group information from FreeIPA. All endpoints require GSSAPI (Kerberos) authentication.

Authentication
~~~~~~~~~~~~~~

All API requests require Kerberos authentication. Before making requests, obtain a Kerberos ticket::

   $ kinit
   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/me/

Interactive Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~

The API can be interactively viewed and explored using the Swagger documentation interface:

- **Production:** https://fasjson.fedoraproject.org/docs/v1/
- **Local/Development:** http://$(hostname)/fasjson/docs/v1/

The Swagger UI provides a comprehensive, interactive view of all API endpoints, request/response schemas, and allows you to try out API calls directly from your browser. Please note however that at the moment the example ``curl`` commands displayed by this documentation lack the necessary ``-u : --negotiate`` options, you'll have to remember to add them when using curl from the command line.


Pagination
~~~~~~~~~~

All list and search endpoints support pagination. Responses include pagination metadata:

- ``page``: Current page number
- ``page_size``: Number of results per page
- ``total_results``: Total number of results across all pages

**Example paginated response:**

::

   {
     "result": [...],
     "page": 1,
     "page_size": 40,
     "total_results": 150
   }


API Endpoints
~~~~~~~~~~~~~

.. contents:: Table of Contents
   :local:
   :depth: 2

Me Endpoint
^^^^^^^^^^^

**GET /v1/me/**

Fetch information about the currently authenticated user or service.

**Response fields:**

- ``dn``: Distinguished name in LDAP
- ``username``: Username (for user principals)
- ``service``: Service name (for service principals)
- ``uri``: URI to the user resource

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/me/
   {"result": {"dn": "uid=admin,cn=users,cn=accounts,dc=example,dc=com", "username": "admin", "uri": "http://$(hostname)/fasjson/v1/users/admin/"}}


User Endpoints
^^^^^^^^^^^^^^

**GET /v1/users/**

List all users with pagination support.

**Query parameters:**

- ``page_size``: Number of results per page (default: 40)
- ``page_number``: Page number (default: 1)

**Response fields:**

- ``username``: User's username
- ``surname``: Last name
- ``givenname``: First name
- ``human_name``: Full display name
- ``emails``: List of email addresses
- ``ircnicks``: List of IRC nicknames
- ``locale``: User's locale setting
- ``timezone``: User's timezone
- ``gpgkeyids``: List of GPG key IDs
- ``sshpubkeys``: List of SSH public keys
- ``certificates``: List of certificates (base64 encoded)
- ``creation``: Account creation timestamp
- ``locked``: Boolean indicating if account is locked
- ``github_username``: GitHub username
- ``gitlab_username``: GitLab username
- ``pronouns``: List of preferred pronouns
- ``rhbzemail``: Red Hat Bugzilla email
- ``websites``: List of website URLs
- ``rssurls``: List of RSS feed URLs
- ``uri``: URI to this user resource

**Note:** Some fields may be hidden if the user has marked their profile as private (``is_private``).

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/
   {"result": [{"username": "admin", "uri": "http://$(hostname)/fasjson/v1/users/admin/"}, ...]}


**GET /v1/users/<username>/**

Fetch detailed information about a specific user.

**Parameters:**

- ``username``: The user's username

**Response:** Same fields as the user list endpoint, but for a single user.

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/admin/
   {"result": {"username": "admin", "surname": "Administrator", "givenname": "", "emails": ["admin@example.com"], "ircnicks": null, "locale": "en_US", "timezone": null, "gpgkeyids": null, "creation": "2020-04-23T10:16:35", "locked": false, "uri": "http://$(hostname)/fasjson/v1/users/admin/"}}


**GET /v1/users/<username>/groups/**

Fetch the list of groups a user belongs to.

**Parameters:**

- ``username``: The user's username

**Query parameters:**

- ``page_size``: Number of results per page (default: 40)
- ``page_number``: Page number (default: 1)

**Response fields:**

- ``groupname``: Group name
- ``uri``: URI to the group resource

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/admin/groups/
   {"result": [{"groupname": "admins", "uri": "http://$(hostname)/fasjson/v1/groups/admins/"}]}


**GET /v1/users/<username>/agreements/**

Fetch the list of agreements a user has signed.

**Parameters:**

- ``username``: The user's username

**Query parameters:**

- ``page_size``: Number of results per page (default: 40)
- ``page_number``: Page number (default: 1)

**Response fields:**

- ``name``: Agreement name

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/admin/agreements/
   {"result": [{"name": "FPCA"}]}


Group Endpoints
^^^^^^^^^^^^^^^

**GET /v1/groups/**

List all groups with pagination support.

**Query parameters:**

- ``page_size``: Number of results per page (default: 40)
- ``page_number``: Page number (default: 1)

**Response fields:**

- ``groupname``: Group name
- ``description``: Group description
- ``mailing_list``: Mailing list address
- ``url``: Group URL
- ``irc``: List of IRC channels
- ``discussion_url``: Discussion forum URL
- ``uri``: URI to this group resource

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/
   {"result": [{"groupname": "admins", "uri": "http://$(hostname)/fasjson/v1/groups/admins/"}]}


**GET /v1/groups/<groupname>/**

Fetch detailed information about a specific group.

**Parameters:**

- ``groupname``: The group's name

**Response:** Same fields as the group list endpoint, but for a single group.

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/admins/
   {"result": {"groupname": "admins", "description": "Administrators group", "uri": "http://$(hostname)/fasjson/v1/groups/admins/"}}


**GET /v1/groups/<groupname>/members/**

Fetch the list of members in a group.

**Parameters:**

- ``groupname``: The group's name

**Query parameters:**

- ``page_size``: Number of results per page (default: 40)
- ``page_number``: Page number (default: 1)

**Response fields:**

- ``username``: Member's username
- ``uri``: URI to the user resource

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/admins/members/
   {"result": [{"username": "admin", "uri": "http://$(hostname)/fasjson/v1/users/admin/"}]}


**GET /v1/groups/<groupname>/sponsors/**

Fetch the list of sponsors for a group.

**Parameters:**

- ``groupname``: The group's name

**Response fields:**

- ``username``: Sponsor's username
- ``uri``: URI to the user resource

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/admins/sponsors/
   {"result": [{"username": "admin", "uri": "http://$(hostname)/fasjson/v1/users/admin/"}]}


**GET /v1/groups/<groupname>/is-member/<username>**

Check whether a user is a member of a group.

**Parameters:**

- ``groupname``: The group's name
- ``username``: The user's username

**Response:** Boolean value (true/false)

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/admins/is-member/admin
   {"result": true}


Search Endpoints
^^^^^^^^^^^^^^^^

**GET /v1/search/users/**

Search for users based on various criteria.

**Query parameters:**

All search terms support substring matching by default unless specified as exact match or listed in ``always_exact_match``.
Substring search terms must be at least 3 characters long.

- ``username``: Username to search for (substring)
- ``email``: Email address to search for (exact match)
- ``email__exact``: DEPRECATED: use ``email`` instead
- ``ircnick``: IRC nickname to search for (substring)
- ``givenname``: First name to search for (substring)
- ``surname``: Last name to search for (substring)
- ``human_name``: Full name to search for (substring)
- ``github_username``: GitHub username (exact match)
- ``gitlab_username``: GitLab username (exact match)
- ``rhbzemail``: Red Hat Bugzilla email (exact match)
- ``website``: Website URL to search for (exact match)
- ``rssurl``: RSS URL to search for (exact match)
- ``group``: Group name (exact match). Can be specified multiple times; users must be members of **all** specified groups
- ``creation__before``: Search for users created before this ISO 8601 date
- ``page_size``: Number of results per page (max: 40, default: 40)
- ``page_number``: Page number (default: 1)

**Presence match:** Use ``field=*`` to search for users who have a value set for that field. For example, ``ircnick=*`` returns all users with an IRC nickname defined.

**Exact match:** For fields that support substring matching, append ``__exact`` to the parameter name for exact matching (e.g., ``username__exact=admin``).

**Response:** Same fields as the user list endpoint.

**Validation:**

- At least one search term must be provided
- Substring search terms must be at least 3 characters long
- Page size must be between 1 and 40

**Examples:**

Search by username::

   $ curl --negotiate -u : "http://$(hostname)/fasjson/v1/search/users/?username=admin"
   {"result": [{"username": "admin", ...}, {"username": "badminton", ...}]}

Search by multiple fields::

   $ curl --negotiate -u : "http://$(hostname)/fasjson/v1/search/users/?username=admin&email=admin@example.com"
   {"result": [{"username": "admin", ...}]}

Search by multiple groups (users in ALL groups)::

   $ curl --negotiate -u : "http://$(hostname)/fasjson/v1/search/users/?group=packager&group=nodejs-sig"
   {"result": [{"username": "user1", ...}]}

Search for users with IRC nick set::

   $ curl --negotiate -u : "http://$(hostname)/fasjson/v1/search/users/?ircnick=*"
   {"result": [{"username": "user1", "ircnicks": ["nick1"], ...}]}


Certificate Endpoints
^^^^^^^^^^^^^^^^^^^^^

**POST /v1/certs/**

Submit a Certificate Signing Request (CSR) and receive a signed certificate.

**Request parameters:**

- ``user``: Username for which to sign the certificate (required)
- ``csr``: Certificate Signing Request in PEM format (required)
- ``profile``: Certificate profile to use (optional, defaults to config value)

**Response fields:**

- ``cacn``: CA common name
- ``certificate``: Signed certificate in PEM format
- ``certificate_chain``: List of certificates in the chain
- ``issuer``: Certificate issuer DN
- ``revoked``: Boolean indicating if certificate is revoked
- ``san_other``: List of Subject Alternative Names (other)
- ``san_other_kpn``: List of SAN Kerberos Principal Names
- ``san_other_upn``: List of SAN User Principal Names
- ``serial_number``: Certificate serial number (integer)
- ``serial_number_hex``: Certificate serial number (hexadecimal)
- ``sha1_fingerprint``: SHA1 fingerprint
- ``sha256_fingerprint``: SHA256 fingerprint
- ``subject``: Certificate subject DN
- ``valid_not_after``: Expiration date (RFC822 format)
- ``valid_not_before``: Valid from date (RFC822 format)
- ``uri``: URI to this certificate resource

**Example:**

::

   $ curl --negotiate -u : -X POST -d "user=admin&csr=-----BEGIN CERTIFICATE REQUEST-----..." http://$(hostname)/fasjson/v1/certs/
   {"result": {"certificate": "-----BEGIN CERTIFICATE-----...", "serial_number": 123, ...}}


**GET /v1/certs/<serial_number>/**

Fetch detailed information about a certificate by its serial number.

**Parameters:**

- ``serial_number``: The certificate's serial number (integer)

**Response:** Same fields as the certificate creation endpoint.

**Example:**

::

   $ curl --negotiate -u : http://$(hostname)/fasjson/v1/certs/123/
   {"result": {"certificate": "-----BEGIN CERTIFICATE-----...", "serial_number": 123, ...}}
