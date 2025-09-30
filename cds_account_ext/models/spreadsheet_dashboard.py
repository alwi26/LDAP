from odoo import _, fields, models

class SpreadsheetDashboard(models.Model):
    _inherit = 'spreadsheet.dashboard'

    cds_json_converted = fields.Char(string="JSON Converted")
