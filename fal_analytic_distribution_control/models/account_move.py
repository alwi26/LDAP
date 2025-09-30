from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        AnalyticAccount = self.env["account.analytic.account"]

        for record in self:
            for line in record.invoice_line_ids:
                if line.analytic_distribution:
                    summary = {}
                    for acc_id, value in line.analytic_distribution.items():
                        # Handle the case of "1,90" by splitting account ID
                        acc_ids = acc_id.split(",")
                        for single_acc_id in acc_ids:
                            single_acc_id = single_acc_id.strip()  # Remove any whitespace

                            # Search for the analytic account and get the plan_id
                            analytic_account = AnalyticAccount.browse(int(single_acc_id))
                            if analytic_account:
                                plan_id = analytic_account.plan_id.id
                                if plan_id not in summary:
                                    summary[plan_id] = 0
                                summary[plan_id] += value

                    # Check if any plan's total distribution per line exceeds 100%
                    for plan_id, total in summary.items():
                        if total > 100:
                            raise UserError("Analytic Distribution Plan More Than 100%")

        return res
