from odoo import _, fields, models

class SpreadsheetDashboard(models.Model):
    _inherit = 'spreadsheet.dashboard'

    cds_json_converted = fields.Char(string="JSON Converted")
    cds_dashboard_date = fields.Date(string="Dashboard Date")


    def action_open_dashboard(self):
        self.ensure_one()
        url = "/odoo/dashboards?dashboard_id=%s" % self.id
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

