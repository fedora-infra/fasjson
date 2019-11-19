# Fedora Account System / IPA JSON gateway

**PROOF OF CONCEPT**

## Installation

Install dependencies

```
dnf install ipa-client httpd mod_auth_gssapi mod_session python3-mod_wsgi python3-dns python3-flask python3-gssapi python3-ldap python3-pip python3-wheel
```

Install WSGI app

```
pip-3 install .
cp fasjson.wsgi /srv/
```

Enroll the system as an IPA client

```
$ ipa-client-install
```

Get service keytab for HTTPd

```
ipa service-add HTTP/$(hostname)
ipa-getkeytab -p HTTP/$(hostname) -k /var/lib/gssproxy/httpd.keytab
chown root:root /var/lib/gssproxy/httpd.keytab
chmod 640 /var/lib/gssproxy/httpd.keytab
```

Configure GSSProxy for Apache

```
cp config/gssproxy-fasjson.conf /etc/gssproxy/99-fasjson.conf
systemctl enable gssproxy.service
systemctl restart gssproxy.service
```

Configure temporary files

```
cp config/tmpfiles-fasjson.conf /etc/tmpfiles.d/fasjson.conf
systemd-tmpfiles --create
```

Tune SELinux Policy

```
setsebool -P httpd_can_connect_ldap=on
```

Configure Apache

```
mkdir mkdir -p /etc/systemd/system/httpd.service.d
cp config/systemd-httpd-service-fasjson.conf /etc/systemd/system/httpd.service.d/fasjson.conf
cp config/httpd-fasjson.conf /etc/httpd/conf.d/fasjson.conf
systemctl daemon-reload
systemctl enable httpd.service
systemctl restart httpd.service
```

## Usage

```
$ kinit
$ curl --negotiate -u : http://$(hostname)/fasjson/groups
["admins","ipausers","editors","trust admins"]
$ curl --negotiate -u : http://$(hostname)/fasjson/group/admins
["admin"]
$ curl --negotiate -u : http://$(hostname)/fasjson/user/admin
{"gecos":"Administrator"}
```

## TODO

A lot!

* tests
* documentation
* CI
* error handling
* HTTPS
* JSON return value
