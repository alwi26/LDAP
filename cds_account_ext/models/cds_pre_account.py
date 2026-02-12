from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import string
import json
import base64
import copy
from dateutil.relativedelta import relativedelta
import calendar
import io
from datetime import datetime, timedelta, date
from openpyxl import Workbook
from xlcalculator import ModelCompiler, Evaluator, xltypes

_logger = logging.getLogger(__name__)


class CdsPreAccountMoveLine(models.Model):
    _name = "cds_pre_account.move.line"
    _description = "Pre Journal Items"

    cds_amount_in_functional_currency = fields.Float(
        string="Amount in Functional Currency",
        compute="_compute_convert_transaction_currency",
        store=True,
    )
    cds_amount_in_transaction_currency = fields.Float(
        string="Amount in Transaction Currency"
    )
    cds_run_description = fields.Char(string="Run Description")
    cds_date = fields.Date(string="Date")
    cds_entity_name = fields.Char(string="Entity Name")
    cds_group_type = fields.Char(string="Group Type")
    cds_insurance_contract_type_at_opening = fields.Char(
        string="Insurance Contract Type at Opening"
    )
    cds_insurance_contract_type_at_closing = fields.Char(
        string="Insurance Contract Type at Closing"
    )
    cds_portfolio = fields.Char(string="Portfolio")
    cds_transaction_currency = fields.Char(string="Transaction Currency")
    cds_account_code = fields.Char(string="Account Code")
    cds_account_name = fields.Char(string="Account Name")
    cds_balance_type = fields.Selection(
        [("cr", "CR"), ("dr", "DR")], string="Debit/Credit"
    )
    cds_debit = fields.Float(
        string="Debit", compute="_compute_debit_credit", store=True
    )
    cds_credit = fields.Float(
        string="Credit", compute="_compute_debit_credit", store=True
    )
    cds_amount_in_currency_conversion = fields.Float(
        string="Amount in Currency Conversion",
        related="cds_amount_in_functional_currency",
    )
    cds_distribution_channel = fields.Char(string="Distribution Channel")
    cds_product = fields.Char(string="Product")
    cds_campaign_code = fields.Char(string="Campaign Code")
    cds_branch_code = fields.Char(string="Branch Office")
    cds_cost_center = fields.Char(string="Cost Center")
    cds_ifrs_group = fields.Char(string="IFRS Group")
    cds_valuation_method_of_master_account = fields.Char(
        string="Valuation Method of Master Account"
    )
    cds_accounting_policy = fields.Char(string="Accounting Policy")
    cds_calculation_step = fields.Char(string="Calculation Step")
    cds_hierarchy_node = fields.Char(string="Hierarchy Node")
    cds_journal_type = fields.Char(string="Journal Type")
    cds_loss_recovery_component_method = fields.Char(
        string="Loss Recovery Component Method"
    )
    cds_modified_gmm = fields.Char(string="Modified GMM")
    cds_onerosity_at_soa = fields.Char(string="Onerosity at SOA")
    cds_onerosity_at_eoa = fields.Char(string="Onerosity at EOA")
    cds_onerosity_at_nb_recog = fields.Char(string="Onerosity at NB Recog")
    cds_at_opening = fields.Char(string="Onerosity at Opening")
    cds_lrecc_new_business_recognition = fields.Char(
        string="LRECC New Business Recognition"
    )
    cds_reinsurance_held = fields.Char(string="Reinsurance Held")
    cds_source_of_business = fields.Char(string="Source of Business")
    cds_transition_method = fields.Char(string="Transition Method")
    cds_underlying_ifrs17_group = fields.Char(string="Underlying IFRS 17 Group")
    cds_valuation_method = fields.Char(string="Valuation Method")
    cds_vfa_approach = fields.Char(string="VFA Approach")
    cds_variable = fields.Char(string="Variable")
    cds_variable_definition = fields.Char(string="Variable Definition")
    cds_component_of_master_account = fields.Char(string="Component of Master Account")
    cds_direct_rch_of_master_account = fields.Char(
        string="Direct / RCH of Master Account"
    )
    cds_lrc_lic_and_onerousness_of_master_account = fields.Char(
        string="LRC/LIC and Onerousness of Master Account"
    )
    cds_movement_of_master_account = fields.Char(string="Movement of Master Account")
    cds_section_of_master_account = fields.Char(string="Section of Master Account")
    cds_sub_component_of_master_account = fields.Char(
        string="Sub-Component of Master Account"
    )
    cds_sub_movement1_of_master_account = fields.Char(
        string="Sub-Movement 1 of Master Account"
    )
    cds_sub_movement2_of_master_account = fields.Char(
        string="Sub-Movement 2 of Master Account"
    )
    cds_package_name = fields.Char("Package Name")
    cds_generate_done = fields.Boolean()
    pre_journal_items_bkey = fields.Char(string="Data Warehouse IFRS ID")
    cds_input_name = fields.Char("Input Name")
    cds_status = fields.Many2one("cds.report.status", string="Status")

    @api.depends("cds_transaction_currency", "cds_amount_in_transaction_currency")
    def _compute_convert_transaction_currency(self):
        for rec in self:
            if (
                rec.cds_transaction_currency
                and rec.cds_transaction_currency.upper() != "IDR"
            ):
                idr = self.env.ref("base.IDR")
                convert_currency = self.env["res.currency"].search(
                    [("name", "=", rec.cds_transaction_currency.upper())], limit=1
                )
                convert = convert_currency._convert(
                    rec.cds_amount_in_transaction_currency,
                    idr,
                    self.env.company,
                    rec.cds_date,
                )
                rec.cds_amount_in_functional_currency = convert
            else:
                rec.cds_amount_in_functional_currency = (
                    rec.cds_amount_in_transaction_currency
                )

    @api.depends("cds_date")
    def _compute_display_name(self):
        for rec in self:
            date_str = rec.cds_date.strftime("%y%m%d") if rec.cds_date else ""
            rec.display_name = f"Pre-{date_str}"

    @api.depends(
        "cds_amount_in_currency_conversion",
        "cds_balance_type",
        "cds_amount_in_transaction_currency",
    )
    def _compute_debit_credit(self):
        for rec in self:
            if (
                rec.cds_amount_in_currency_conversion < 0
                and rec.cds_movement_of_master_account == "Movement"
            ):
                rec.cds_debit = 0
                rec.cds_credit = -1 * rec.cds_amount_in_currency_conversion
            elif (
                rec.cds_amount_in_currency_conversion < 0
                and rec.cds_movement_of_master_account != "Movement"
            ):
                rec.cds_debit = (
                    rec.cds_amount_in_currency_conversion
                    if rec.cds_amount_in_currency_conversion > 0
                    else 0.0
                )
                rec.cds_credit = (
                    -1 * rec.cds_amount_in_currency_conversion
                    if rec.cds_amount_in_currency_conversion < 0
                    else 0.0
                )
            else:
                rec.cds_debit = (
                    rec.cds_amount_in_currency_conversion
                    if rec.cds_balance_type == "dr"
                    else 0.0
                )
                rec.cds_credit = (
                    rec.cds_amount_in_currency_conversion
                    if rec.cds_balance_type == "cr"
                    else 0.0
                )

    def action_generate_journal_entries(self):
        journal = self.env["account.journal"].search(
            [("type", "=", "general")], limit=1
        )
        if not journal:
            raise UserError("Journal type 'general' not found.")

        pre_lines = self.search([("cds_generate_done", "=", False)])
        if not pre_lines:
            return True

        pre_lines_by_group = {}
        for line in pre_lines:
            month_key = line.cds_date.strftime("%Y-%m")
            group_key = (line.cds_package_name, line.cds_status.id, month_key)
            pre_lines_by_group.setdefault(group_key, []).append(line)

        created_moves = self.env["account.move"]

        for (category, status, date), lines in pre_lines_by_group.items():
            move_date = f"{date}-01"
            status_report = self.env["cds.report.status"].browse(status) or ""
            move = self.env["account.move"].create(
                {
                    "journal_id": journal.id,
                    "date": move_date,
                    "ref": f"Auto Journal {category or ''} | {status_report.cds_name or ''} - {move_date}",
                    "cds_status": status,
                }
            )

            move_lines_vals = []
            for pre_line in lines:
                mapping_account = self.env["cds_mapping.account.account"].search(
                    [("cds_account_code", "=", pre_line.cds_account_code)], limit=1
                )
                mapping_account_account = self.env["account.account"].search(
                    [("code", "=", pre_line.cds_account_code)], limit=1
                )
                if not mapping_account and not mapping_account_account:
                    raise UserError(f"Account {pre_line.cds_account_code} not found.")
                account = mapping_account.cds_account_id or mapping_account_account
                analytic_distribution = {}
                mappings = self.env["cds_mapping.analyitc.plan"].search([])
                for mapping in mappings:
                    field_name = mapping.cds_column_name.name
                    plan = mapping.cds_analytic_plan
                    if not field_name or not plan:
                        continue

                    val = getattr(pre_line, field_name, False)
                    if val:
                        acc = self.env["account.analytic.account"].search(
                            [("name", "=", val), ("plan_id", "=", plan.id)],
                            limit=1,
                        )
                        if acc:
                            analytic_distribution[acc.id] = 100
                            pre_line.cds_package_name = category

                move_lines_vals.append(
                    (
                        0,
                        0,
                        {
                            "name": pre_line.cds_run_description,
                            "account_id": account.id,
                            "debit": round(pre_line.cds_debit, 0),
                            "credit": round(pre_line.cds_credit, 0),
                            "analytic_distribution": analytic_distribution,
                            "cds_pre_account_id": pre_line.id,
                        },
                    )
                )

                pre_line.write({"cds_generate_done": True})
            total_debit = sum(
                line_val[2].get("debit", 0.0) for line_val in move_lines_vals
            )
            total_credit = sum(
                line_val[2].get("credit", 0.0) for line_val in move_lines_vals
            )
            diff = round(total_debit - total_credit, 2)

            if diff != 0:
                _logger.warning(f"Balancing diff detected (before write): {diff}")
                move_lines_vals.append(
                    (
                        0,
                        0,
                        {
                            "name": "Auto Balancing",
                            "account_id": 811,
                            "debit": 0.0 if diff > 0 else abs(diff),
                            "credit": diff if diff > 0 else 0.0,
                        },
                    )
                )

            # # Tulis semua line termasuk balancing line ke move
            move.write({"line_ids": move_lines_vals})
            move.action_post()
            created_moves |= move
        return True

    def _shift_year_safe(self, d, years_back=1):
        """Geser tahun ke belakang, fallback ke last day of month jika tanggal tidak ada (misalnya 29 Feb)."""
        try:
            return d.replace(year=d.year - years_back)
        except ValueError:
            last_day = calendar.monthrange(d.year - years_back, d.month)[1]
            return date(d.year - years_back, d.month, last_day)

    def _unlink_dashboard_last_year(self, dashboard_ids):
        Dashboard = self.env["spreadsheet.dashboard"]
        DashboardGroup = self.env["spreadsheet.dashboard.group"]

        dashboards_to_unlink = Dashboard
        groups_to_unlink = DashboardGroup

        for dashboard in dashboard_ids:
            if not dashboard.cds_dashboard_date or not dashboard.cds_dashboard_date_end:
                continue

            last_year_start = self._shift_year_safe(dashboard.cds_dashboard_date)
            last_year_end = self._shift_year_safe(dashboard.cds_dashboard_date_end)

            # 🟡 Cari dashboard tahun lalu dengan rentang yang SAMA persis, bukan overlap
            last_year_dashboards = Dashboard.search(
                [
                    ("cds_dashboard_date", "=", last_year_start),
                    ("cds_dashboard_date_end", "=", last_year_end),
                    ("dashboard_group_id", "ilike", "IFRS"),
                ]
            )

            if not last_year_dashboards:
                last_year_dashboards = Dashboard.search(
                    [
                        ("cds_dashboard_date", ">=", last_year_start),
                        ("cds_dashboard_date_end", "<=", last_year_end),
                        ("dashboard_group_id", "ilike", "IFRS"),
                    ]
                )

            if last_year_dashboards:
                dashboards_to_unlink |= last_year_dashboards
                groups_to_unlink |= last_year_dashboards.mapped("dashboard_group_id")

        # 🧹 Unlink batch
        if dashboards_to_unlink:
            dashboards_to_unlink.mapped("cds_sdic_ids").unlink()
            dashboards_to_unlink.unlink()

        if groups_to_unlink:
            groups_to_unlink.unlink()

    def next_date_range(self, start_date, end_date, period_type=False):
        if not period_type:
            period_type = self.env.company.period_type or "month"

        if period_type == "month":
            next_start = (end_date + relativedelta(months=1)).replace(day=1)
            last_day = calendar.monthrange(next_start.year, next_start.month)[1]
            next_end = next_start.replace(day=last_day)

        elif period_type == "quarter":
            next_start = (end_date + relativedelta(months=1)).replace(day=1)
            quarter = ((next_start.month - 1) // 3) + 1
            quarter_start_month = 3 * (quarter - 1) + 1
            quarter_end_month = quarter_start_month + 2
            next_start = next_start.replace(month=quarter_start_month, day=1)
            last_day = calendar.monthrange(next_start.year, quarter_end_month)[1]
            next_end = next_start.replace(month=quarter_end_month, day=last_day)

        elif period_type == "year":
            if end_date.month == 12:
                next_start = date(end_date.year + 1, 1, 1)
            else:
                next_start = date(end_date.year, end_date.month + 1, 1)

            end_month = next_start.month - 1 or 12
            end_year = next_start.year

            if end_month == 12 and end_date.month == 1:
                end_year = end_date.year + 1

            last_day = calendar.monthrange(end_year, end_month)[1]
            next_end = date(end_year, end_month, last_day)

        else:
            raise ValueError(f"Unknown period_type: {period_type}")
        return next_start, next_end

    def get_header(self, cells):
        headers = []
        for cell, data in cells.items():
            formula = data.get("content", "")
            if formula.startswith("=ODOO.LIST.HEADER"):
                # ambil argumen terakhir di dalam tanda kurung
                arg = formula.split(",")[-1].replace(")", "").replace('"', "").strip()
                headers.append(arg)
        return headers

    def _recycle_dashboard_json(self, template_id=False):
        if not template_id:
            raise UserError("Dashboard Template is not define")

        base_group = self.env["spreadsheet.dashboard.group"].browse(template_id)

        if not base_group:
            raise UserError(_("No dashboard template found!"))

        status = base_group.cds_status
        if not status:
            raise UserError(_("Status is not defined in the dashboard template!"))

        dashboard = base_group.dashboard_ids and base_group.dashboard_ids[0]
        start, end = self.next_date_range(
            dashboard.cds_dashboard_date,
            dashboard.cds_dashboard_date_end,
            base_group.period_type,
        )

        s_str = start.strftime("%d %B %Y")
        e_str = end.strftime("%d %B %Y")
        if end > fields.Date.today():
            raise UserError(
                _(f"Cannot Generate Dashboard in date range {s_str} - {e_str}")
            )

        account_moves = self.env["account.move"].search(
            [
                ("cds_status_generate_dashboard", "=", False),
                ("cds_status", "=", base_group.cds_status.id),
                ("date", ">=", start),
                ("date", "<=", end),
            ]
        )

        if account_moves:
            _logger.info(f"🔄 PROCESS: {status.cds_name}")

            dashboard_name = f"IFRS ({s_str} - {e_str}) - {status.cds_name}"

            new_group = base_group.copy(
                default={
                    "name": dashboard_name,
                    "cds_dashboard_date": start,
                    "cds_dashboard_date_end": end,
                    "dashboard_ids": False,
                }
            )

            for dashboard in base_group.dashboard_ids:
                # ============================================================
                # 3. VALIDASI DUPLICATE (CEGAH GANDA)
                # ============================================================
                existing_dashboard = self.env["spreadsheet.dashboard"].search(
                    [
                        ("cds_dashboard_date", "=", start),
                        ("cds_dashboard_date_end", "=", end),
                        ("cds_status", "=", status.id),
                        ("name", "=", dashboard.name),
                        ("dashboard_group_id.name", "ilike", "IFRS"),
                    ],
                    limit=1,
                )

                if existing_dashboard:
                    _logger.info(
                        f"⚠️ SKIPPED — Dashboard already exists: {dashboard.name}"
                    )
                    continue

                dashboard.copy(
                    default={
                        "dashboard_group_id": new_group.id,
                        "name": dashboard.name,
                        "spreadsheet_binary_data": dashboard.spreadsheet_binary_data,
                    }
                )

            # ============================================================
            # 5. Update dashboard baru (inject data IFRS + balance calc)
            # ============================================================
            for new_dashboard in new_group.dashboard_ids:
                new_dashboard.write(
                    {
                        "cds_status": status.id,
                        "cds_dashboard_date": start,
                        "cds_dashboard_date_end": end,
                    }
                )

                new_dashboard.generate_all_balance()

                all_lines = new_dashboard.cds_sdic_ids
                binary_data = new_dashboard.spreadsheet_binary_data
                if not binary_data:
                    continue

                decoded_bytes = base64.b64decode(binary_data)
                json_data = json.loads(decoded_bytes.decode("utf-8"))

                sheets = json_data.get("sheets")[1]
                cells = sheets.get("cells", {})
                headers = self.get_header(cells)
                cells.clear()

                for i, field in enumerate(headers):
                    letter = string.ascii_uppercase[i]
                    cells[f"{letter}1"] = {"content": f'=ODOO.LIST.HEADER(1,"{field}")'}

                    for row_idx, ifrs in enumerate(all_lines, start=2):
                        cells[f"{letter}{row_idx}"] = {
                            "content": f'=ODOO.LIST(1,{row_idx-1},"{field}")'
                        }

                json_data["sheets"][1]["cells"] = cells
                check_domain = next(iter(json_data.get("lists")), None)
                json_data["lists"]["1"] = json_data.get("lists").pop(check_domain)
                json_data["lists"]["1"].update(
                    {
                        "domain": [("id", "in", all_lines.ids)],
                        "model": "spreadsheet.dashboard.ifrs.calculator",
                    }
                )

                new_dashboard.spreadsheet_binary_data = base64.b64encode(
                    json.dumps(json_data).encode("utf-8")
                )

            account_moves.write({"cds_status_generate_dashboard": True})

            _logger.info(f"✅ DASHBOARD GENERATED: {dashboard_name}")

            # Update Dashboard template date
            base_group.write(
                {
                    "cds_dashboard_date": start,
                    "cds_dashboard_date_end": end,
                }
            )
            base_group.calculate()
