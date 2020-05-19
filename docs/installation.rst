Installation
------------

Install dependencies::

   dnf install ipa-client httpd mod_auth_gssapi mod_session python3-mod_wsgi python3-poetry

Install WSGI app::

   poetry config virtualenvs.create false
   poetry install
   cp ansible/roles/fasjson/files/fasjson.wsgi /srv/

Enroll the system as an IPA client::

   $ ipa-client-install

Get service keytab for HTTPd::

   ipa service-add HTTP/$(hostname)
   ipa servicedelegationrule-add-member --principals=HTTP/$(hostname) fasjson-delegation
   ipa-getkeytab -p HTTP/$(hostname) -k /var/lib/gssproxy/httpd.keytab
   chown root:root /var/lib/gssproxy/httpd.keytab
   chmod 640 /var/lib/gssproxy/httpd.keytab

Configure GSSProxy for Apache::

   cp ansible/roles/fasjson/files/config/gssproxy-fasjson.conf /etc/gssproxy/99-fasjson.conf
   systemctl enable gssproxy.service
   systemctl restart gssproxy.service

Configure temporary files::

   cp ansible/roles/fasjson/files/config/tmpfiles-fasjson.conf /etc/tmpfiles.d/fasjson.conf
   systemd-tmpfiles --create

Tune SELinux Policy::

   setsebool -P httpd_can_connect_ldap=on

Configure Apache::

   mkdir mkdir -p /etc/systemd/system/httpd.service.d
   cp ansible/roles/fasjson/files/config/systemd-httpd-service-fasjson.conf /etc/systemd/system/httpd.service.d/fasjson.conf
   cp ansible/roles/fasjson/files/config/httpd-fasjson.conf /etc/httpd/conf.d/fasjson.conf
   systemctl daemon-reload
   systemctl enable httpd.service
   systemctl restart httpd.service