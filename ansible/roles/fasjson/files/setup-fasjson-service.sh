#!/bin/sh

set -e

PRINCIPAL="HTTP/fasjson.example.test"
DELEGATION="fasjson-delegation"

ipa service-find $PRINCIPAL &> /dev/null || ipa service-add $PRINCIPAL --force

ipa servicedelegationrule-find $DELEGATION &> /dev/null || ipa servicedelegationrule-add $DELEGATION

ipa servicedelegationrule-show $DELEGATION | grep "Member principals:" | grep -qs $PRINCIPAL || (
	ipa servicedelegationrule-add-member --principals=$PRINCIPAL $DELEGATION
)
ipa servicedelegationrule-show $DELEGATION | grep "Allowed Target:" | grep -qs ipa-ldap-delegation-targets || (
	ipa servicedelegationrule-add-target --servicedelegationtargets=ipa-ldap-delegation-targets $DELEGATION
)
