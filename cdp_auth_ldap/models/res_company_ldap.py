# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ldap
from odoo import _, fields, models, tools
import logging

_logger = logging.getLogger(__name__)


class ResCompanyLdap(models.Model):
    _inherit = "res.company.ldap"

    # override odoo
    def _query(self, conf, filter, retrieve_attributes=None):
        """
        Query an LDAP server with the filter argument and scope subtree.

        Allow for all authentication methods of the simple authentication
        method:

        - authenticated bind (non-empty binddn + valid password)
        - anonymous bind (empty binddn + empty password)
        - unauthenticated authentication (non-empty binddn + empty password)

        .. seealso::
           :rfc:`4513#section-5.1` - LDAP: Simple Authentication Method.

        :param dict conf: LDAP configuration
        :param filter: valid LDAP filter
        :param list retrieve_attributes: LDAP attributes to be retrieved. \
        If not specified, return all attributes.
        :return: ldap entries
        :rtype: list of tuples (dn, attrs)

        """

        results = []
        try:
            _logger.info("try Connecting to Active Directory")
            # change odoo method to connect LDAP
            uri = 'ldap://%s' % (conf['ldap_server'])
            conn = ldap.initialize(uri)
            if conf['ldap_tls']:
                conn.start_tls_s()
            ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)
            ldap_password = conf["ldap_password"] or ""
            ldap_binddn = conf["ldap_binddn"] or ""
            conn.simple_bind_s(ldap_binddn, ldap_password)
            _logger.info("Bind Successful")
            results = conn.search_st(
                conf["ldap_base"],
                ldap.SCOPE_SUBTREE,
                filter,
                attrlist=["cn", "mail"],
                timeout=60
            )
            conn.unbind()
        except ldap.INVALID_CREDENTIALS:
            _logger.error("LDAP bind failed.")
        except ldap.LDAPError as e:
            _logger.error("An LDAP exception occurred: %s", e)
        return results

    def test_ldap_connection(self):
        """
        Test the LDAP connection using the current configuration.
        Returns a dictionary with notification parameters indicating success or failure.
        """
        conf = {
            "ldap_server": self.ldap_server,
            "ldap_server_port": self.ldap_server_port,
            "ldap_binddn": self.ldap_binddn,
            "ldap_password": self.ldap_password,
            "ldap_base": self.ldap_base,
            "ldap_tls": self.ldap_tls,
        }

        bind_dn = self.ldap_binddn or ""
        bind_passwd = self.ldap_password or ""

        try:
            conn = self._connect(conf)
            conn.simple_bind_s(bind_dn, bind_passwd)
            conn.unbind()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "title": _("Connection Test Successful!"),
                    "message": _(
                        "Successfully connected to LDAP server at %(server)s:%(port)d",
                        server=self.ldap_server,
                        port=self.ldap_server_port,
                    ),
                    "sticky": False,
                },
            }

        except ldap.SERVER_DOWN:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "danger",
                    "title": _("Connection Test Failed!"),
                    "message": _(
                        "Cannot contact LDAP server at %(server)s:%(port)d",
                        server=self.ldap_server,
                        port=self.ldap_server_port,
                    ),
                    "sticky": False,
                },
            }

        except ldap.INVALID_CREDENTIALS:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "danger",
                    "title": _("Connection Test Failed!"),
                    "message": _(
                        "Invalid credentials for bind DN %(binddn)s",
                        binddn=self.ldap_binddn,
                    ),
                    "sticky": False,
                },
            }

        except ldap.TIMEOUT:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "danger",
                    "title": _("Connection Test Failed!"),
                    "message": _(
                        "Connection to LDAP server at %(server)s:%(port)d timed out",
                        server=self.ldap_server,
                        port=self.ldap_server_port,
                    ),
                    "sticky": False,
                },
            }

        except ldap.LDAPError as e:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "danger",
                    "title": _("Connection Test Failed!"),
                    "message": _("An error occurred: %(error)s", error=e),
                    "sticky": False,
                },
            }
