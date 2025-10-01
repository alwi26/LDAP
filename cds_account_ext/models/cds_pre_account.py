from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import string
import json
import base64
import copy
from dateutil.relativedelta import relativedelta
import re

_logger = logging.getLogger(__name__)


class CdsPreAccountMoveLine(models.Model):
    _name = "cds_pre_account.move.line"
    _description = "Pre Journal Items"

    cds_amount_in_functional_currency = fields.Float(
        string="Amount in Functional Currency",
        compute="_compute_convert_transaction_currency",
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
    cds_loss_recovery_component_method = fields.Char(string="Loss Recovery Component Method")
    cds_modified_gmm = fields.Char(string="Modified GMM")
    cds_onerosity_at_soa = fields.Char(string="Onerosity at SOA")
    cds_onerosity_at_eoa = fields.Char(string="Onerosity at EOA")
    cds_onerosity_at_nb_recog = fields.Char(string="Onerosity at NB Recog")
    cds_at_opening = fields.Char(string="Onerosity at Opening")
    cds_lrecc_new_business_recognition = fields.Char(string="LRECC New Business Recognition")
    cds_reinsurance_held = fields.Char(string="Reinsurance Held")
    cds_source_of_business = fields.Char(string="Source of Business")
    cds_transition_method = fields.Char(string="Transition Method")
    cds_underlying_ifrs17_group = fields.Char(string="Underlying IFRS 17 Group")
    cds_valuation_method = fields.Char(string="Valuation Method")
    cds_vfa_approach = fields.Char(string="VFA Approach")
    cds_variable = fields.Char(string="Variable")
    cds_variable_definition = fields.Char(string="Variable Definition")
    cds_component_of_master_account = fields.Char(string="Component of Master Account")
    cds_direct_rch_of_master_account = fields.Char(string="Direct / RCH of Master Account")
    cds_lrc_lic_and_onerousness_of_master_account = fields.Char(string="LRC/LIC and Onerousness of Master Account")
    cds_movement_of_master_account = fields.Char(string="Movement of Master Account")
    cds_section_of_master_account = fields.Char(string="Section of Master Account")
    cds_sub_component_of_master_account = fields.Char(string="Sub-Component of Master Account")
    cds_sub_movement1_of_master_account = fields.Char(string="Sub-Movement 1 of Master Account")
    cds_sub_movement2_of_master_account = fields.Char(string="Sub-Movement 2 of Master Account")
    cds_category_column = fields.Char("Category Column")
    cds_generate_done = fields.Boolean()
    pre_journal_items_bkey = fields.Integer(string="Data Warehouse IFRS ID")

    @api.depends("cds_transaction_currency")
    def _compute_convert_transaction_currency(self):
        for rec in self:
            if rec.cds_transaction_currency == "USD":
                idr = rec.env["res.currency"].browse(12)
                usd = rec.env["res.currency"].browse(1)
                convert = usd._convert(
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

    @api.depends("cds_amount_in_currency_conversion", "cds_balance_type", "cds_amount_in_transaction_currency")
    def _compute_debit_credit(self):
        for rec in self:
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
            group_key = (line.cds_category_column, month_key)
            pre_lines_by_group.setdefault(group_key, []).append(line)

        created_moves = self.env["account.move"]

        for (category, date), lines in pre_lines_by_group.items():
            move_date = f"{date}-01"
            move = self.env["account.move"].create(
                {
                    "journal_id": journal.id,
                    "date": move_date,
                    "ref": f"Auto Journal {category or ''} - {move_date}",
                }
            )

            move_lines_vals = []
            for pre_line in lines:
                account = self.env["account.account"].search(
                    [("code", "=", pre_line.cds_account_code)], limit=1
                )
                if not account:
                    raise UserError(f"Account {pre_line.cds_account_code} not found.")

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
                            pre_line.cds_category_column = category

                move_lines_vals.append(
                    (
                        0,
                        0,
                        {
                            "name": pre_line.cds_run_description,
                            "account_id": account.id,
                            "debit": pre_line.cds_debit,
                            "credit": pre_line.cds_credit,
                            "analytic_distribution": analytic_distribution,
                            "cds_pre_account_id": pre_line.id,
                        },
                    )
                )

                pre_line.write({"cds_generate_done": True})
            move.write({"line_ids": move_lines_vals})
            created_moves |= move

        if created_moves:
            self._recycle_dashboard_json(created_moves)

        return True

    def _unlink_dashboard_last_year(self, date):
        last_year_date = date.replace(year=date.year - 1)
        # format it for last year
        month_year = last_year_date.strftime("%b %Y")
        dashboard_name = f"IFRS ({month_year})"
        last_year_dashboard_group = self.env["spreadsheet.dashboard.group"].search(
            [("name", "=", dashboard_name)], limit=1
        )
        if last_year_dashboard_group:
            last_year_dashboard_group.dashboard_ids.unlink()
            last_year_dashboard_group.unlink()

    def _recycle_dashboard_json(self, moves):
        for move in moves:
            dashboard_group = self.env["spreadsheet.dashboard.group"].search(
                [("create_date", "<", fields.Date.today()), ("name", "ilike", "IFRS")],
                order="create_date desc",
                limit=1,
            )
    
            if not moves:
                return
    
            date = move.date
            month_year = date.strftime("%b %Y")
            dashboard_name = f"IFRS ({month_year})"
            start_month = date.replace(day=1)
            end_month = (start_month + relativedelta(months=1))
    
            existing_dashboard_group = self.env["spreadsheet.dashboard.group"].search(
                [("name", "=", dashboard_name)], limit=1
            )
            if existing_dashboard_group:
                raise UserError(_(f"Already has existing dashboard {dashboard_name}"))
    
            if dashboard_group:
                new_group = dashboard_group.copy(default={"name": dashboard_name})
                for dashboard in dashboard_group.dashboard_ids:
                    dashboard.copy(
                        default={
                            "dashboard_group_id": new_group.id,
                            "name": dashboard.name,
                            "spreadsheet_binary_data": dashboard.spreadsheet_binary_data,
                        }
                    )
    
                # semua line_ids digabung
                all_move_lines = moves.mapped("line_ids")
    
                for new_dashboard in new_group.dashboard_ids:
                    binary_data = new_dashboard.spreadsheet_binary_data
                    if not binary_data:
                        continue
    
                    decoded_bytes = base64.b64decode(binary_data)
                    json_data = json.loads(decoded_bytes.decode("utf-8"))
    
                    headers = json_data["lists"]["1"]["columns"]
                    sheets = json_data.get("sheets")[1]
                    cells = sheets.get("cells", {})
    
                    # Copy json untuk simpan text version
                    json_data_text = copy.deepcopy(json_data)
                    sheets_text = json_data_text.get("sheets")[1]
                    cells_text = sheets_text.get("cells", {})
    
                    # clear cell value
                    cells.clear()
                    cells_text.clear()
    
                    # rewrite the cells
                    for i, field in enumerate(headers):
                        field_obj = self.env["account.move.line"]._fields.get(field)
                        if not field_obj:
                            continue
    
                        field_label = field_obj.string
                        letter = string.ascii_uppercase[i]
                        no = 1
    
                        # Keep Odoo format
                        cells[f"{letter}{no}"] = {
                            "content": f'=ODOO.LIST.HEADER(1,"{field}")'
                        }
                        cells_text[f"{letter}{no}"] = {"content": f"{field_label}"}
    
                        for move_line in all_move_lines:
                            no += 1
                            cells[f"{letter}{no}"] = {
                                "content": f'=ODOO.LIST(1,{no-1},"{field}")'
                            }
    
                            value = getattr(move_line, field, "")
                            if field_obj.type == "many2one":
                                value = value.display_name if value else ""
                            elif field_obj.type in ("one2many", "many2many"):
                                value = ", ".join(value.mapped("display_name"))
                            value = value or ""
    
                            cells_text[f"{letter}{no}"] = {"content": f"{value}"}
    
                    
                    # Convert amount formula
                    cells1 = json_data_text.get("sheets")[0].get("cells")
                    sheet1_backup = copy.deepcopy(json_data_text.get("sheets")[0])
    
                    # Backup Data Formula to sheet 3
                    json_data_text.get("sheets").append(sheet1_backup)
                    json_data_text["sheets"][2].update(
                        {"id": "backupsheetformula", "name": "Backup Sheet Formula"}
                    )
    
                    pattern = re.compile(
                        r"""(?ix)           # ignore case, verbose
                        ([+\-]?)\s*         # optional sign
                        (?:                 # start big non-capture group
                            sumifs\(
                                [^!]+!([A-Z]+):[A-Z]+\s*,\s*
                                [^!]+!([A-Z]+):[A-Z]+\s*,\s*
                                ([A-Z]+\d+)
                            \)
                          |                # OR
                            sum\(\s*
                                ([A-Z]+\d+):([A-Z]+\d+)
                            \)
                        )"""
                    )
    
                    # calculate sumifs first
                    for cell_id, cell_data in cells1.items():
                        content = cell_data.get("content", "")
                        if isinstance(content, str) and "sumifs" in content.lower():
                            matches = pattern.findall(content)
                            sum_amount = 0
                            if matches:
                                for m in matches:
                                    (
                                        sign,
                                        sum_col,
                                        crit_col,
                                        crit_cell,
                                        start_cell,
                                        end_cell,
                                    ) = m
                                    sign = sign or "+"
                                    if sum_col:  # it’s a SUMIFS
                                        crit_value = cells1.get(crit_cell, {}).get(
                                            "content"
                                        )
                                        # Step 2: search in the other sheet’s crit_col column for the same content
                                        found_cells = []
                                        for other_key, other_data in cells_text.items():
                                            if other_data.get("content") == crit_value:
                                                found_cells.append(
                                                    "".join(filter(str.isdigit, other_key))
                                                )
                                        total_amount = 0
                                        for key in found_cells:
                                            amount = cells_text.get(sum_col + str(key)).get("content") or 0
                                            total_amount += float(amount)
                                        sum_amount += total_amount if sign == "+" else -total_amount
    
                            cells1.get(cell_id).update({"content": abs(sum_amount)})
    
                    for cell_id, cell_data in cells1.items():
                        content = cell_data.get("content", "")
                        if isinstance(content, str) and "sum" in content.lower() and "sumifs" not in content.lower():
                            def val(cid):
                                v = str(cells1.get(cid, {}).get("content", "")).strip()
                                return float(v) if v else 0
                            total = 0
                            for arg in content[5:-1].split(','):          # ambil isi SUM(...)
                                arg = arg.strip()
                                if ':' in arg:                            # jika range
                                    start, end = arg.split(':')
                                    col = ''.join(filter(str.isalpha, start))
                                    r1 = int(''.join(filter(str.isdigit, start)))
                                    r2 = int(''.join(filter(str.isdigit, end)))
                                    for r in range(r1, r2 + 1):
                                        total += val(f"{col}{r}")
                                else:                                     # jika cell tunggal
                                    total += val(arg)
                            cells1.get(cell_id).update({"content": total})
    
                    last_col_letter = string.ascii_uppercase[len(headers) - 1]
                    last_row_number = len(all_move_lines) + 1
                    new_range = f"A1:{last_col_letter}{last_row_number}"
    
                    sheets.get("tables")[0].update({"range": new_range})
                    sheets_text.get("tables")[0].update({"range": new_range})
    
                    json_data.get("sheets")[1].update({"cells": cells})
                    json_data_text.get("sheets")[1].update({"cells": cells_text})
    
                    # update domain → semua moves
                    domain = json_data["lists"]["1"]["domain"]
                    domain = [("move_id", "in", moves.ids)]
                    json_data["lists"]["1"].update({"domain": domain})
                    json_data_text["lists"]["1"].update({"domain": domain})
    
                    # encode back to base64
                    updated_json_str = json.dumps(json_data)
                    updated_binary = base64.b64encode(updated_json_str.encode("utf-8"))
    
                    new_dashboard.spreadsheet_binary_data = updated_binary
                    new_dashboard.cds_json_converted = str(json_data_text)
                    new_dashboard.cds_dashboard_date = date
            self._unlink_dashboard_last_year(date)
