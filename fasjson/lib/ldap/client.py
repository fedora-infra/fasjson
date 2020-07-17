import re
import ldap
from ldap.controls.pagedresults import SimplePagedResultsControl

from .models import UserModel, GroupModel, SponsorModel


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

    def get_groups(self, page_size, page_number):
        return self.search(
            model=GroupModel,
            scope=ldap.SCOPE_SUBTREE,
            page_size=page_size,
            page_number=page_number,
        )

    def get_group(self, groupname, attrs=None):
        dn = GroupModel.get_sub_dn_for(groupname)
        result = self.search(
            model=GroupModel, sub_dn=dn, attrs=attrs, scope=ldap.SCOPE_BASE
        )
        if not result.items:
            return None
        return result.items[0]

    def get_group_members(self, groupname, page_size, page_number):
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
            attrs=["uid"],
            scope=ldap.SCOPE_SUBTREE,
            page_size=page_size,
            page_number=page_number,
        )

    def get_group_sponsors(self, groupname):
        group_dn = GroupModel.get_sub_dn_for(groupname)
        filters = f"(&(objectClass=fasGroup)(cn={groupname}))"
        sponsors_result = self.search(
            model=SponsorModel,
            sub_dn=group_dn,
            attrs=["memberManager"],
            filters=filters,
            scope=ldap.SCOPE_SUBTREE,
        )
        if not sponsors_result.items:
            return []
        return self._sponsors_to_users(sponsors_result)

    def _sponsors_to_users(self, sponsors_dn):
        sponsors = []

        for sponsor in sponsors_dn.items[0]["sponsors"]:
            username = re.findall("(?<=uid=)([^,]+)", sponsor)[0]
            uid = f"uid={username}"
            sponsors.append(uid)

        filters = ["(&(objectClass=fasUser)(|"]
        for uid in sponsors:
            filters.append(f"({uid})")
        filters.append("))")
        filters = "".join(filters)

        result = self.search(model=UserModel, filters=filters)
        return result.items

    def get_users(self, page_size, page_number):
        return self.search(
            model=UserModel,
            scope=ldap.SCOPE_SUBTREE,
            page_size=page_size,
            page_number=page_number,
        )

    def get_user(self, username, attrs=None):
        dn = UserModel.get_sub_dn_for(username)
        result = self.search(
            model=UserModel, sub_dn=dn, attrs=attrs, scope=ldap.SCOPE_BASE
        )
        if not result.items:
            return None
        return result.items[0]

    def get_user_groups(self, username, page_size, page_number):
        dn = UserModel.get_sub_dn_for(username)
        filters = f"(&(member={dn},{self.basedn}){GroupModel.filters})"
        return self.search(
            model=GroupModel,
            filters=filters,
            page_number=page_number,
            page_size=page_size,
        )

    def search_users(
        self,
        page_number,
        page_size,
        username,
        email,
        ircnick,
        givenname,
        surname,
    ):
        filter_fields = {
            "uid": username,
            "mail": email,
            "fasIRCNick": ircnick,
            "givenName": givenname,
            "sn": surname,
        }

        filter_string = ["(&", UserModel.filters, "(&"]
        for attribute, filter in filter_fields.items():
            if filter:
                filter_value = ldap.filter.escape_filter_chars(filter, 0)
                if attribute == "mail":
                    filter_string.append(f"({attribute}={filter_value})")
                else:
                    filter_string.append(f"({attribute}=*{filter_value}*)")
        filter_string.append("))")
        filter_string = "".join(filter_string)

        return self.search(
            model=UserModel,
            filters=filter_string,
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
