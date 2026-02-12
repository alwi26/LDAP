# file: models/res_config_settings.py
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    period_type = fields.Selection(
        [
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        string="Default Period Type",
        related="company_id.period_type",
        readonly=False,
    )
    maximum_unbalance = fields.Float(
        string="Maximum Unbalance",
        related="company_id.maximum_unbalance",
        readonly=False,
    )
