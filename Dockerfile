FROM quay.io/fedora/fedora:41
LABEL \
  name="fasjson" \
  vendor="Fedora Infrastructure" \
  license="GPLv3+"
ENV HOME=/opt
RUN dnf install -y \
        openldap-clients \
        vim \
        git \
        ipa-client \
        gcc \
        redhat-rpm-config \
        python-devel \
        krb5-devel \
        openldap-devel \
        httpd \
        mod_auth_gssapi \
        mod_session \
        policycoreutils-python-utils \
	poetry \
        python3-mod_wsgi \
        python3-pip && \
    dnf autoremove -y && \
    dnf clean all -y
RUN python3 -m venv /opt/venv
RUN poetry config virtualenvs.create false
COPY ./ /opt/fasjson
ENV VIRTUAL_ENV=/opt/venv
RUN cd /opt/fasjson && poetry install --only main
RUN rm -f /etc/krb5.conf && ln -sf /etc/krb5/krb5.conf /etc/krb5.conf && \
    rm -f /etc/openldap/ldap.conf && ln -sf /etc/ipa/ldap.conf /etc/openldap/ldap.conf
EXPOSE 8080
ENTRYPOINT bash /opt/fasjson/deploy/start.sh
