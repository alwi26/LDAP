from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CdsMappingAnalyticPlan(models.Model):
    _name = "cds_mapping.account.account"
    _description = "Mapping Chart of account"

    cds_source_account = fields.Char("Source CoA")
    cds_account_code = fields.Char("Account Code")
    cds_account_name = fields.Char("Account Name")
    cds_account_id = fields.Many2one("account.account")
