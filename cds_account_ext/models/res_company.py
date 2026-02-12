# file: models/res_config_settings.py
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    period_type = fields.Selection(
        [
            ('month', 'Month'),
            ('quarter', 'Quarter'),
            ('year', 'Year'),
        ],
        string='Default Period Type',
    )
    maximum_unbalance = fields.Float(
        string="Maximum Unbalance"
    )
