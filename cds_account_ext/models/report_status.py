from odoo import models, fields, api, _

class CdsReportStatus(models.Model):
    _name = "cds.report.status"
    _description = "Report Status"

    cds_name = fields.Char(string="Name")
    
    @api.depends("cds_name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.cds_name