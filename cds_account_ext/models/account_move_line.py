from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    cds_pre_account_id = fields.Many2one(
        "cds_pre_account.move.line", string="Pre Journal Items"
    )
    cds_searchable_code = fields.Char(
        string="Searchable Code", related="account_id.cds_searchable_code"
    )
    cds_account_report_group_axis_1 = fields.Char(
        string="Account Report Group Axis1.1 - General",
        related="account_id.cds_account_report_group_axis_1",
    )
    cds_account_report_group_axis_2 = fields.Selection(
        [
            ("pv_ra", "PV & RA"),
            ("pv_cf", "PV_CF"),
            ("ra", "RA"),
            ("csm", "CSM"),
            ("pv_cf_vfa", "PV_CF_VFA"),
            ("ra_vfa", "RA_VFA"),
            ("csm_vfa", "CSM_VFA"),
            ("bel_uf_vfa", "BEL_UF_VFA"),
            ("pv_cf_lic", "PV_CF_LIC"),
            ("pv_cf_lic_vfa", "PV_CF_LIC_VFA"),
        ],
        string="Account Report Group Axis1.2 - Change",
        related="account_id.cds_account_report_group_axis_2",
    )
    cds_account_report_group_axis_3 = fields.Char(
        string="Account Report Group Axis1.3 - Claim",
        related="account_id.cds_account_report_group_axis_3",
    )
    cds_account_report_group_axis_4 = fields.Char(
        string="Account Report Group Axis1.4 - Other Dim",
        related="account_id.cds_account_report_group_axis_4",
    )
    cds_account_report_group_axis_5 = fields.Char(
        string="Account Report Group Axis2.1 - VFA & GMM",
        related="account_id.cds_account_report_group_axis_5",
    )
    cds_account_report_group_axis_6 = fields.Char(
        string="Account Report Group Axis2.2 - PV & RA",
        related="account_id.cds_account_report_group_axis_6",
    )
    cds_account_report_group_axis_7 = fields.Char(
        string="Account Report Group Axis2.3 - Acquisition & Moodys",
        related="account_id.cds_account_report_group_axis_7",
    )
    cds_account_report_group_axis_8 = fields.Selection(
        [("moodys", "Moodys"), ("deferred", "Deferred Acquisition Expenses")],
        string="Account Report Group Axis2.4 - Contract & Loss",
        related="account_id.cds_account_report_group_axis_8",
    )
