#!/bin/sh

set -e

PRINCIPAL="HTTP/fasjson.example.test"
DELEGATION="fasjson-delegation"

ipa service-find $PRINCIPAL &> /dev/null || ipa service-add $PRINCIPAL --force

# Create delegation rule

ipa servicedelegationrule-find $DELEGATION &> /dev/null || ipa servicedelegationrule-add $DELEGATION

ipa servicedelegationrule-show $DELEGATION | grep "Member principals:" | grep -qs $PRINCIPAL || (
	ipa servicedelegationrule-add-member --principals=$PRINCIPAL $DELEGATION
)

# Delegate for LDAP

ipa servicedelegationrule-show $DELEGATION | grep "Allowed Target:" | grep -qs ipa-ldap-delegation-targets || (
	ipa servicedelegationrule-add-target --servicedelegationtargets=ipa-ldap-delegation-targets $DELEGATION
)

# Delegate for HTTP

ipa servicedelegationtarget-find ipa-http-delegation-targets &> /dev/null || ipa servicedelegationtarget-add ipa-http-delegation-targets

ipa servicedelegationtarget-show ipa-http-delegation-targets | grep "Member principals:" | grep -qs HTTP/ipa.example.test || (
	ipa servicedelegationtarget-add-member ipa-http-delegation-targets --principals=HTTP/ipa.example.test@EXAMPLE.TEST
)

ipa servicedelegationrule-show $DELEGATION | grep "Allowed Target:" | grep -qs ipa-http-delegation-targets || (
	ipa servicedelegationrule-add-target --servicedelegationtargets=ipa-http-delegation-targets $DELEGATION
)