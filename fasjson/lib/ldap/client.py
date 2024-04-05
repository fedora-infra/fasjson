import re

import ldap
from ldap.controls.pagedresults import SimplePagedResultsControl

from .models import AgreementModel, GroupModel, SponsorModel, UserModel


GROUP_DN_RE = re.compile("^cn=([^,]+)")
USER_DN_RE = re.compile("^uid=([^,]+)")


class LDAPResult:
    def __init__(
        self, items=None, total=None, page_size=None, page_number=None
    ):
        self.items = items or []
        self.total = total or len(self.items)
        self.page_size = page_size
        self.page_number = page_number

    def __repr__(self):
        return f"<LDAPResult items=[{len(self.items)} items] page={self.page_number}>"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise ValueError("Unsupported operation")
        return all(
            [
                getattr(self, attr) == getattr(other, attr)
                for attr in ["items", "total", "page_size", "page_number"]
            ]
        )


def _get_filter_string(attribute, value, substring_match):
    value = ldap.filter.escape_filter_chars(value, 0)
    if substring_match:
        value = f"*{value}*"
    return f"({attribute}={value})"


class LDAP:
    def __init__(
        self, uri, basedn, login="", timeout=ldap.NO_LIMIT, trace_level=0
    ):
        self.basedn = basedn
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        self.conn = ldap.ldapobject.ReconnectLDAPObject(
            uri, retry_max=3, trace_level=trace_level
        )
        self.conn.protocol_version = 3
        self.conn.timeout = timeout
        self.conn.sasl_gssapi_bind_s(authz_id=login)

    def whoami(self):
        raw = self.conn.whoami_s()
        dn = raw[4:]
        result = {"dn": dn}
        for part in dn.split(","):
            key, value = part.split("=")
            if key == "uid":
                result["username"] = value
            if key == "krbprincipalname":
                result["service"] = value.split("@")[0]
        return result

    def get_groups(self, attrs, page_size, page_number):
        return self.search(
            model=GroupModel,
            attrs=GroupModel.attrs_to_ldap(attrs),
            scope=ldap.SCOPE_SUBTREE,
            page_size=page_size,
            page_number=page_number,
        )

    def get_group(self, groupname, attrs=None):
        dn = GroupModel.get_sub_dn_for(groupname)
        result = self.search(
            model=GroupModel,
            sub_dn=dn,
            attrs=GroupModel.attrs_to_ldap(attrs),
            scope=ldap.SCOPE_BASE,
        )
        if not result.items:
            return None
        return result.items[0]

    def get_group_members(self, groupname, attrs, page_size, page_number):
        group_dn = GroupModel.get_sub_dn_for(groupname)
        filters = (
            "(&"
            f"(memberOf={group_dn},{self.basedn})"
            f"{UserModel.filters}"
            ")"
        )
        return self.search(
            model=UserModel,
            filters=filters,
            attrs=UserModel.attrs_to_ldap(attrs) or ["uid"],
            scope=ldap.SCOPE_SUBTREE,
            page_size=page_size,
            page_number=page_number,
        )

    def get_group_sponsors(self, groupname, attrs=None):
        group_dn = GroupModel.get_sub_dn_for(groupname)
        filters = f"(&(objectClass=fasGroup)(cn={groupname}))"
        sponsors_result = self.search(
            model=SponsorModel,
            sub_dn=group_dn,
            attrs=["memberManager"],
            filters=filters,
            scope=ldap.SCOPE_SUBTREE,
        )
        if (
            not sponsors_result.items
            or "sponsors" not in sponsors_result.items[0]
        ):
            return []
        return self._sponsors_to_users(sponsors_result, attrs)

    def _list_sponsors_uid(self, sponsors_dn, attrs):
        for sponsor in sponsors_dn.items[0]["sponsors"]:
            group_match = GROUP_DN_RE.match(sponsor)
            if group_match:
                members = self.get_group_members(
                    group_match.group(1), ["uid"], page_size=0, page_number=1
                )
                for member in members.items:
                    yield member["username"]
            user_match = USER_DN_RE.match(sponsor)
            if user_match:
                yield user_match.group(1)

    def _sponsors_to_users(self, sponsors_dn, attrs):
        sponsors = []

        for username in self._list_sponsors_uid(sponsors_dn, attrs):
            uid = f"uid={username}"
            sponsors.append(uid)

        if not sponsors:
            return []

        filters = ["(&(objectClass=fasUser)(|"]
        for uid in set(sponsors):
            filters.append(f"({uid})")
        filters.append("))")
        filters = "".join(filters)

        result = self.search(
            model=UserModel,
            filters=filters,
            attrs=UserModel.attrs_to_ldap(attrs) or ["uid"],
        )
        return result.items

    def check_membership(self, groupname, username):
        group_dn = GroupModel.get_sub_dn_for(groupname)
        filters = (
            "(&"
            f"(memberOf={group_dn},{self.basedn})"
            f"{UserModel.filters}"
            f"(uid={username})"
            ")"
        )
        result = self.search(
            model=UserModel,
            filters=filters,
            attrs=["uid"],
            scope=ldap.SCOPE_SUBTREE,
        )
        if not result.items:
            return False
        if len(result.items) == 1:
            return True
        raise ValueError(f"Unexpected result length: {len(result.items)}")

    def get_users(self, attrs, page_size, page_number):
        return self.search(
            model=UserModel,
            attrs=UserModel.attrs_to_ldap(attrs),
            scope=ldap.SCOPE_SUBTREE,
            page_size=page_size,
            page_number=page_number,
        )

    def get_user(self, username, attrs=None):
        dn = UserModel.get_sub_dn_for(username)
        result = self.search(
            model=UserModel,
            sub_dn=dn,
            attrs=UserModel.attrs_to_ldap(attrs),
            scope=ldap.SCOPE_BASE,
        )
        if not result.items:
            return None
        return result.items[0]

    def get_user_groups(self, username, attrs, page_size, page_number):
        user = self.get_user(username, ["memberof"])
        groups_filters = [
            f"({dn.split(',')[0]})"
            for dn in user.get("groups", [])
            if dn.endswith(f"{GroupModel.sub_dn},{self.basedn}")
        ]
        if not groups_filters:
            return LDAPResult(
                items=[],
                page_size=page_size,
                page_number=page_number,
                total=0,
            )
        filters = f"(&{GroupModel.filters}(|{''.join(groups_filters)}))"
        return self.search(
            model=GroupModel,
            attrs=GroupModel.attrs_to_ldap(attrs),
            filters=filters,
            page_number=page_number,
            page_size=page_size,
        )

    def get_user_agreements(self, username, page_size, page_number):
        dn = UserModel.get_sub_dn_for(username)
        filters = (
            f"(&(memberUser={dn},{self.basedn}){AgreementModel.filters})"
        )
        return self.search(
            model=AgreementModel,
            filters=filters,
            page_number=page_number,
            page_size=page_size,
        )

    def search_users(
        self,
        attrs,
        page_number,
        page_size,
        **filters,
    ):
        filter_string = ["(&", UserModel.filters, "(&"]
        attrs_map = UserModel.get_search_attrs_map()
        for term, filter in filters.items():
            if not filter:
                continue

            substring_match = True
            if term.endswith("__exact"):
                term = term[:-7]
                substring_match = False
            if term in UserModel.always_exact_match:
                substring_match = False
            if term == "group":
                filter = [
                    f"{GroupModel.get_sub_dn_for(name)},{self.basedn}"
                    for name in filter
                ]

            try:
                attribute = attrs_map[term]
            except KeyError:
                continue

            # the group filter is a list, handle them all as lists
            if not isinstance(filter, list):
                filter = [filter]
            for filter_item in filter:
                filter_string.append(
                    _get_filter_string(
                        attribute, filter_item, substring_match
                    )
                )

        if filters.get("creation__before"):
            filter_value = ldap.filter.escape_filter_chars(
                filters["creation__before"].strftime("%Y%m%d%H%M%SZ"), 0
            )
            filter_string.append(f"(fasCreationTime<={filter_value})")

        filter_string.append("))")
        filter_string = "".join(filter_string)

        return self.search(
            model=UserModel,
            filters=filter_string,
            attrs=UserModel.attrs_to_ldap(attrs),
            page_size=page_size,
            page_number=page_number,
        )

    def search(
        self,
        model,
        sub_dn=None,
        base_dn=None,
        filters=None,
        attrs=None,
        scope=ldap.SCOPE_SUBTREE,
        page_size=0,
        page_number=1,
    ):
        """Perform an LDAP query with pagination support.

        LDAP's pagination system is not web-compatible, because the pagination cursor is
        connection-specific and webservers typically have multiple processes, and therefore multiple
        LDAP connections.
        As a result, to implement pagination we proceed as such:

          1. query the primary keys for the whole result set (this is rather fast because only
             the primary keys are queried)
          2. slice this list into pages
          3. make a second query including only the primary keys that are in the requested page,
             but requesting all attributes
          4. build a ``LDAPResult`` object that takes into account the total number of entries to
             provide pagination information

        Args:
            model (Model): The object model that is being queried
            sub_dn (str, optional): The DN of the subtree to query (no ``base_dn`` suffix).
                Defaults to the ``sub_dn`` provided by the model.
            filters (str): The LDAP filters to use (in LDAP syntax)
            attrs (list, optional): The list of attributes to request. Defaults to the
                model's attributes list.
            scope (int, optional): The LDAP scope to use. Defaults to ldap.SCOPE_SUBTREE.
            page_size (int, optional): The number of items per page. If this is zero, disable
                pagination and request all items. Defaults to 0.
            page_number (int, optional): The requested page number. Defaults to 1.

        Returns:
            LDAPResult: The query result, with pagination information if appropriate.
        """
        base_dn = f"{sub_dn or model.sub_dn},{self.basedn}"
        filters = filters or model.filters
        total = None
        if page_size:
            # Get all primary keys regardless of paging
            pkeys = self._do_search(
                base_dn=base_dn,
                filters=filters,
                model=model,
                attrs=[model.primary_key],
                scope=scope,
            )
            total = len(pkeys)
            # Find out which items we need for this page
            first = (page_number - 1) * page_size
            last = first + page_size
            pkeys_page = [
                item[model.primary_key][0].decode("utf-8")
                for item in pkeys[first:last]
            ]
            if not pkeys_page:
                return LDAPResult(
                    items=[],
                    page_size=page_size,
                    page_number=page_number,
                    total=total,
                )
            # Now adjust the filters to only get items on this page
            entries_filters = [
                f"({model.primary_key}={item})" for item in pkeys_page
            ]
            filters = f"(&{filters}(|{''.join(entries_filters)}))"
        items = self._do_search(
            base_dn=base_dn,
            filters=filters,
            model=model,
            attrs=attrs,
            scope=scope,
        )
        return LDAPResult(
            items=[model.convert_ldap_result(item) for item in items],
            page_size=page_size,
            page_number=page_number,
            total=total,
        )

    def _do_search(
        self,
        base_dn,
        filters,
        model,
        attrs=None,
        scope=ldap.SCOPE_SUBTREE,
        # maximum=None,
    ):
        """Perform a single LDAP query

        Args:
            base_dn (str): The base DN for the query
            filters (str): The LDAP filters to use (in LDAP syntax)
            model (Model): The object model that is being queried
            attrs (list, optional): The list of attributes to request. Defaults to the
                model's attributes list.
            scope (int, optional): The LDAP scope to use. Defaults to ldap.SCOPE_SUBTREE.

        In the implementation, SimplePagedResultControl is used to buffer results and save
        memory, but it is not usable as a web-compatible paging system.

        Returns:
            list(dict): a list of dictionaries keyed by attributes.
        """
        attrs = attrs or model.get_ldap_attrs()
        page_size = 1000
        # if maximum:
        #     page_size = min(maximum, page_size)
        page_cookie = ""
        results = []
        while True:
            page_control = SimplePagedResultsControl(
                criticality=False, size=page_size, cookie=page_cookie
            )
            msgid = self.conn.search_ext(
                base_dn,
                scope,
                filters,
                attrlist=attrs,
                serverctrls=[page_control],
            )
            rtype, rdata, rmsgid, serverctrls = self.conn.result3(msgid)
            results.extend(obj for dn, obj in rdata)
            for ctrl in serverctrls:
                if isinstance(ctrl, SimplePagedResultsControl):
                    page_cookie = ctrl.cookie
                    break
            if not page_cookie:
                break
            # if maximum and len(results) >= maximum:
            #     break
        return results
