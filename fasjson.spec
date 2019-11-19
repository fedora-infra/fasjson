%global debug_package %{nil}
%global ipa_version 4.8.0

Name:           fasjson
Version:        0.0.1
Release:        1%{?dist}
Summary:        JSON REST API for Fedora Account System

BuildArch:      noarch

License:        GPL
URL:            https://github.com/fedora-infra/fasjson
Source0:        https://github.com/fedora-infra/fasjson/archive/%{version}.tar.gz

BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: systemd

Requires:  python3-fasjson
Requires:  gssproxy
Requires:  httpd
Requires:  mod_auth_gssapi
Requires:  mod_session
Requires:  python3-mod_wsgi
%if 0%{?rhel}
Conflicts: ipa-server
Requires:  ipa-client >= %{ipa_version}
%else
Conflicts: freeipa-server
Requires:  freeipa-client  >= %{ipa_version}
%endif
%{?systemd_requires}


%description
JSON REST API for Fedora Account System


%package -n python3-fasjson
Summary: FAS JSON REST API server implementation
Requires: python3-dns
Requires: python3-flask
Requires: python3-gssapi
Requires: python3-ldap


%description -n python3-fasjson
Python 3 flask app for fasjson


%prep
%autosetup


%build
%py3_build
touch debugfiles.list


%install
rm -rf $RPM_BUILD_ROOT
%py3_install

%__mkdir_p %{buildroot}%{_usr}/share/fasjson
cp fasjson.wsgi %{buildroot}%{_usr}/share/fasjson

%__mkdir_p %{buildroot}%{_sysconfdir}/gssproxy
cp config/gssproxy-fasjson.conf %{buildroot}%{_sysconfdir}/gssproxy/99-fasjson.conf

%__mkdir_p %{buildroot}%{_unitdir}/httpd.service.d
cp config/systemd-httpd-service-fasjson.conf  %{buildroot}/%{_unitdir}/httpd.service.d/fasjson.conf

%__mkdir_p %{buildroot}%{_sysconfdir}/httpd/conf.d
cp config/httpd-fasjson.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/fasjson.conf

%__mkdir_p %{buildroot}%{_tmpfilesdir}
cp config/tmpfiles-fasjson.conf %{buildroot}%{_tmpfilesdir}/fasjson.conf


%post
%tmpfiles_create %{_tmpfilesdir}/fasjson.conf
%systemd_post gssproxy.service httpd.service


%preun
%systemd_preun gssproxy.service httpd.service


%postun
%systemd_postun gssproxy.service httpd.service


%posttrans
systemctl daemon-reload
systemctl enable --now gssproxy.service
systemctl restart gssproxy.service
systemctl try-restart httpd.service


%files
%config %{_sysconfdir}/gssproxy/99-fasjson.conf
%config %{_unitdir}/httpd.service.d/fasjson.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/fasjson.conf
%config %{_tmpfilesdir}/fasjson.conf
%dir %{_usr}/share/fasjson
%{_usr}/share/fasjson/fasjson.wsgi


%files -n python3-fasjson
%license COPYING
%doc README.md
%{python3_sitelib}/fasjson
%{python3_sitelib}/fasjson*.egg-info


%changelog
* Tue Nov 19 2019 Christian Heimes <cheimes@redhat.com> - 0.0.1-1
- Initial release
