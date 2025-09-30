from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CdsMappingAnalyticPlan(models.Model):
    _name = "cds_mapping.analyitc.plan"
    _description = "Mapping Analytic Plan"

    cds_column_name = fields.Many2one(
        "ir.model.fields",
        domain=[("model", "=", "cds_pre_account.move.line")],
        string="Column",
    )
    cds_analytic_plan = fields.Many2one("account.analytic.plan", string="Analytic Plan")
