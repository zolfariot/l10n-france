# Copyright 2026 Akretion France (http://www.akretion.com/)
# @author: Lorenzo Battistini <lorenzo.battistini@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.tools.misc import format_date


CATEGORY_LABELS = {
    "product": "Biens",
    "service": "Services",
    "mixed": "Mixte (biens + services)",
}


class DeductibleVatDetailXlsx(models.AbstractModel):
    _name = "report.l10n_fr_account_vat_return.deductible_vat_detail_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Detailed Deductible VAT XLSX Report"

    def generate_xlsx_report(self, workbook, data, wizards):
        for wizard in wizards:
            rows = wizard._collect_report_data()
            vat_return = wizard.return_id
            sheet_name = _("TVA déductible %s") % vat_return.name
            # Worksheet names limited to 31 chars
            sheet = workbook.add_worksheet(sheet_name[:31])
            currency = vat_return.company_id.currency_id
            styles = self._prepare_styles(workbook, currency)

            self._write_header_block(sheet, styles, vat_return)
            header_row = 4
            self._write_column_headers(sheet, styles, header_row)
            self._write_data_rows(sheet, styles, rows, header_row + 1, wizard)
            self._write_totals(sheet, styles, rows, header_row + 1 + len(rows))

    def _prepare_styles(self, workbook, currency):
        decimals = "0" * currency.decimal_places
        currency_fmt = f"# ##0.{decimals}"
        return {
            "title": workbook.add_format(
                {"bold": True, "font_size": 14}
            ),
            "subtitle": workbook.add_format(
                {"bold": True, "font_size": 11}
            ),
            "col_header": workbook.add_format(
                {
                    "bold": True,
                    "font_size": 10,
                    "bg_color": "#4472C4",
                    "font_color": "#FFFFFF",
                    "text_wrap": True,
                    "align": "center",
                    "valign": "vcenter",
                    "border": 1,
                }
            ),
            "text": workbook.add_format(
                {"font_size": 10, "text_wrap": True, "border": 1}
            ),
            "text_bold": workbook.add_format(
                {"font_size": 10, "bold": True, "border": 1}
            ),
            "date": workbook.add_format(
                {"font_size": 10, "num_format": "dd/mm/yyyy", "border": 1}
            ),
            "currency": workbook.add_format(
                {"font_size": 10, "num_format": currency_fmt, "border": 1}
            ),
            "currency_bold": workbook.add_format(
                {
                    "font_size": 10,
                    "num_format": currency_fmt,
                    "bold": True,
                    "border": 1,
                    "bg_color": "#D9E2F3",
                }
            ),
            "percent": workbook.add_format(
                {"font_size": 10, "num_format": "0.00%", "border": 1}
            ),
            "total_label": workbook.add_format(
                {
                    "font_size": 10,
                    "bold": True,
                    "border": 1,
                    "bg_color": "#D9E2F3",
                }
            ),
        }

    def _write_header_block(self, sheet, styles, vat_return):
        company = vat_return.company_id
        sheet.write(
            0,
            0,
            _("État détaillé de la TVA déductible"),
            styles["title"],
        )
        sheet.write(
            1,
            0,
            _("Société : %s") % company.name,
            styles["subtitle"],
        )
        period_label = _("Période : %s – %s") % (
            format_date(self.env, vat_return.start_date),
            format_date(self.env, vat_return.end_date),
        )
        sheet.write(2, 0, period_label, styles["subtitle"])

    def _get_columns(self):
        """Return list of (header_label, width, field_key) tuples."""
        return [
            (_("Date facture"), 12, "invoice_date"),
            (_("N° facture"), 15, "invoice_number"),
            (_("Fournisseur"), 30, "partner_name"),
            (_("Adresse"), 40, "partner_address"),
            (_("SIRET"), 18, "partner_siret"),
            (_("Nature de l'opération"), 40, "operation_nature"),
            (_("Type"), 12, "category"),
            (_("Taux TVA"), 10, "tax_rate"),
            (_("Montant HT"), 15, "amount_ht"),
            (_("TVA déductible"), 15, "amount_vat"),
            (_("Montant TTC"), 15, "amount_ttc"),
            (_("Date(s) de paiement\n(prestations de services)"), 22, "payment_dates"),
            (
                _("Date de livraison\n(livraison de biens)"),
                18,
                "delivery_date",
            ),
            (_("Case"), 12, "box_label"),
        ]

    def _write_column_headers(self, sheet, styles, row):
        columns = self._get_columns()
        for col_idx, (label, width, _key) in enumerate(columns):
            sheet.write(row, col_idx, label, styles["col_header"])
            sheet.set_column(col_idx, col_idx, width)
        sheet.set_row(row, 30)  # Taller header row for wrapped text

    def _write_data_rows(self, sheet, styles, rows, start_row, wizard):
        for i, row_data in enumerate(rows):
            r = start_row + i
            col = 0
            columns = self._get_columns()
            for _label, _width, key in columns:
                value = row_data.get(key)
                if key == "invoice_date":
                    if value:
                        sheet.write_datetime(r, col, value, styles["date"])
                    else:
                        sheet.write(r, col, "", styles["text"])
                elif key == "delivery_date":
                    if value:
                        sheet.write_datetime(r, col, value, styles["date"])
                    else:
                        sheet.write(r, col, "", styles["text"])
                elif key in ("amount_ht", "amount_vat", "amount_ttc"):
                    sheet.write_number(r, col, value or 0.0, styles["currency"])
                elif key == "tax_rate":
                    sheet.write_number(
                        r, col, (value or 0.0) / 100.0, styles["percent"]
                    )
                elif key == "category":
                    sheet.write(
                        r, col, CATEGORY_LABELS.get(value, value), styles["text"]
                    )
                elif key == "payment_dates":
                    if value:
                        formatted = ", ".join(
                            format_date(self.env, d) for d in value
                        )
                        sheet.write(r, col, formatted, styles["text"])
                    else:
                        sheet.write(r, col, "", styles["text"])
                else:
                    sheet.write(r, col, value or "", styles["text"])
                col += 1

    def _write_totals(self, sheet, styles, rows, total_row):
        if not rows:
            return
        total_ht = sum(r["amount_ht"] for r in rows)
        total_vat = sum(r["amount_vat"] for r in rows)
        total_ttc = sum(r["amount_ttc"] for r in rows)

        columns = self._get_columns()
        col_keys = [c[2] for c in columns]

        # Write "TOTAL" label in the operation_nature column
        nature_col = col_keys.index("operation_nature")
        sheet.write(total_row, nature_col, _("TOTAL"), styles["total_label"])

        # Fill empty cells before total with the total_label style
        for c in range(nature_col):
            sheet.write(total_row, c, "", styles["total_label"])

        # Fill category and tax_rate columns
        cat_col = col_keys.index("category")
        sheet.write(total_row, cat_col, "", styles["total_label"])
        rate_col = col_keys.index("tax_rate")
        sheet.write(total_row, rate_col, "", styles["total_label"])

        ht_col = col_keys.index("amount_ht")
        sheet.write_number(total_row, ht_col, total_ht, styles["currency_bold"])
        vat_col = col_keys.index("amount_vat")
        sheet.write_number(total_row, vat_col, total_vat, styles["currency_bold"])
        ttc_col = col_keys.index("amount_ttc")
        sheet.write_number(total_row, ttc_col, total_ttc, styles["currency_bold"])

        # Fill remaining columns with total_label style
        for c in range(ttc_col + 1, len(columns)):
            sheet.write(total_row, c, "", styles["total_label"])
