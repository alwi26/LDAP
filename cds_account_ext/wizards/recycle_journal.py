from odoo import models, fields, api
from odoo.exceptions import UserError


class WizardRecycleJournal(models.TransientModel):
    _name = "wizard.recycle.journal"
    _description = "Wizard to Delete Journal Data"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_delete(self):
        if self.date_from > self.date_to:
            raise UserError("Tanggal awal tidak boleh lebih besar dari tanggal akhir.")

        pre_journals = self.env["cds_pre_account.move.line"].search(
            [
                ("cds_date", ">=", self.date_from),
                ("cds_date", "<=", self.date_to),
            ]
        )
        pre_journals.unlink()
        moves = self.env["account.move"].search(
            [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
            ]
        )
        for move in moves:
            move.button_draft()

        moves.unlink()
        
        return {"type": "ir.actions.act_window_close"}
