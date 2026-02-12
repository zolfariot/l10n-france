# Copyright 2026 Akretion France (http://www.akretion.com/)
# @author: Lorenzo Battistini <lorenzo.battistini@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, fields, models
from odoo.exceptions import UserError


class L10nFrAccountVatReturnDeductibleDetail(models.TransientModel):
    _name = "l10n.fr.account.vat.return.deductible.detail"
    _description = "Detailed Deductible VAT Report Wizard"

    return_id = fields.Many2one(
        "l10n.fr.account.vat.return",
        string="VAT Return",
        required=True,
    )
    box_choice = fields.Selection(
        [
            ("deductible_vat_other", "Box 20 – Other Goods and Services"),
            ("deductible_vat_asset", "Box 19 – Assets"),
            ("both", "Both (Box 19 + Box 20)"),
        ],
        string="Boxes to Include",
        default="deductible_vat_other",
        required=True,
    )

    def _get_tag_names_for_choice(self):
        """Return list of (tag_names, box_label) tuples for the selected choice."""
        self.ensure_one()
        result = []
        if self.box_choice in ("deductible_vat_other", "both"):
            result.append(
                (["+20", "-20"], _("Box 20 – TVA déductible autres biens et services"))
            )
        if self.box_choice in ("deductible_vat_asset", "both"):
            result.append(
                (["+19", "-19"], _("Box 19 – TVA déductible sur immobilisations"))
            )
        return result

    def _get_move_lines_for_tags(self, tag_names):
        """Query account.move.line records matching the given tax tag names
        within the VAT return period."""
        vat_return = self.return_id
        tags = self.env["account.account.tag"].search(
            [
                ("country_id", "=", self.env.ref("base.fr").id),
                ("applicability", "=", "taxes"),
                ("name", "in", tag_names),
            ]
        )
        if not tags:
            return self.env["account.move.line"]
        domain = [
            ("company_id", "=", vat_return.company_id.id),
            ("parent_state", "=", "posted"),
            ("date", ">=", vat_return.start_date),
            ("date", "<=", vat_return.end_date),
            ("tax_tag_ids", "in", tags.ids),
        ]
        return self.env["account.move.line"].search(domain)

    def _resolve_source_invoice(self, move_line):
        """Given a move line (possibly from a CABA entry), resolve the original
        source invoice.

        Returns:
            tuple: (source_move, is_caba)
                - source_move: the original vendor bill (account.move)
                - is_caba: True if the move_line comes from a cash-basis entry
        """
        move = move_line.move_id
        origin = move.tax_cash_basis_origin_move_id
        if origin:
            return origin, True
        return move, False

    def _get_line_category(self, move_line, source_move):
        """Determine if a tagged tax line relates to 'product' (goods) or
        'service' by finding matching base lines on the source invoice and
        calling _fr_is_product_or_service() on them.

        For mixed invoices (same tax applied to both goods and service lines),
        returns 'mixed'.
        """
        tax = move_line.tax_line_id
        if not tax:
            # Fallback: if no tax_line_id, cannot determine
            return "service"
        # Find base lines on the source invoice that use this tax
        base_lines = source_move.line_ids.filtered(
            lambda l: l.display_type == "product" and tax in l.tax_ids
        )
        if not base_lines:
            # Fallback using tax_exigibility as proxy
            if tax.tax_exigibility == "on_payment":
                return "service"
            return "product"
        categories = set()
        for base_line in base_lines:
            categories.add(base_line._fr_is_product_or_service())
        if len(categories) > 1:
            return "mixed"
        return categories.pop()

    def _format_partner_address(self, partner):
        """Format a partner's address as a single string."""
        parts = []
        if partner.street:
            parts.append(partner.street)
        if partner.street2:
            parts.append(partner.street2)
        city_parts = []
        if partner.zip:
            city_parts.append(partner.zip)
        if partner.city:
            city_parts.append(partner.city)
        if city_parts:
            parts.append(" ".join(city_parts))
        if partner.country_id and partner.country_id.code != "FR":
            parts.append(partner.country_id.name)
        return ", ".join(parts)

    def _get_operation_nature(self, source_move, tax):
        """Get a description of the operation from the source invoice's base
        lines that use the given tax."""
        base_lines = source_move.line_ids.filtered(
            lambda l: l.display_type == "product" and tax in l.tax_ids
        )
        descriptions = []
        for line in base_lines:
            if line.product_id:
                descriptions.append(line.product_id.name)
            elif line.name:
                descriptions.append(line.name)
        if descriptions:
            return ", ".join(dict.fromkeys(descriptions))  # Deduplicate preserving order
        return source_move.ref or source_move.name or ""

    def _collect_report_data(self):
        """Collect and aggregate all data for the report.

        Returns a list of dicts, one per (source_invoice, tax_rate) group:
        {
            'invoice_date': date,
            'invoice_number': str,
            'partner_name': str,
            'partner_address': str,
            'partner_siret': str,
            'operation_nature': str,
            'tax_rate': float,
            'amount_vat': float,
            'amount_ht': float,
            'amount_ttc': float,
            'category': 'product' | 'service' | 'mixed',
            'payment_dates': [date, ...],
            'delivery_date': date or False,
            'box_label': str,
        }
        """
        self.ensure_one()
        vat_return = self.return_id
        if vat_return.state == "manual":
            raise UserError(
                _(
                    "Please generate the automatic lines first "
                    "before producing the detailed report."
                )
            )

        tag_groups = self._get_tag_names_for_choice()
        # Key: (source_move_id, tax_id, box_label) → aggregated data
        grouped = defaultdict(
            lambda: {
                "amount_vat": 0.0,
                "payment_dates": [],
            }
        )

        for tag_names, box_label in tag_groups:
            move_lines = self._get_move_lines_for_tags(tag_names)
            for ml in move_lines:
                source_move, is_caba = self._resolve_source_invoice(ml)
                tax = ml.tax_line_id
                tax_rate = tax.amount if tax else 0.0
                key = (source_move.id, tax.id if tax else 0, box_label)

                entry = grouped[key]
                entry["amount_vat"] += ml.balance
                entry["source_move"] = source_move
                entry["tax"] = tax
                entry["tax_rate"] = tax_rate
                entry["box_label"] = box_label
                entry["is_caba"] = is_caba or entry.get("is_caba", False)
                # Collect payment dates from CABA entries
                if is_caba:
                    pay_date = ml.move_id.date
                    if pay_date and pay_date not in entry["payment_dates"]:
                        entry["payment_dates"].append(pay_date)

        # Build final rows
        rows = []
        currency = vat_return.company_id.currency_id
        for key, entry in grouped.items():
            source_move = entry["source_move"]
            tax = entry["tax"]
            tax_rate = entry["tax_rate"]
            amount_vat = currency.round(entry["amount_vat"])
            if currency.is_zero(amount_vat):
                continue

            # Compute HT from VAT amount and rate
            if tax_rate:
                amount_ht = currency.round(amount_vat / (tax_rate / 100.0))
            else:
                amount_ht = 0.0
            amount_ttc = currency.round(amount_ht + amount_vat)

            partner = source_move.partner_id.commercial_partner_id
            category = "service"
            if tax:
                # We need a representative move_line to call _get_line_category
                # but since we've aggregated, we re-derive from tax properties
                # Find base lines on source invoice matching this tax
                base_lines = source_move.line_ids.filtered(
                    lambda l, t=tax: l.display_type == "product" and t in l.tax_ids
                )
                if base_lines:
                    categories = set()
                    for bl in base_lines:
                        categories.add(bl._fr_is_product_or_service())
                    if len(categories) > 1:
                        category = "mixed"
                    else:
                        category = categories.pop()
                else:
                    # Fallback: use tax exigibility
                    if tax.tax_exigibility == "on_payment":
                        category = "service"
                    else:
                        category = "product"

            payment_dates = sorted(entry["payment_dates"])
            # Delivery date: for goods, use delivery_date or invoice_date
            delivery_date = False
            if category in ("product", "mixed"):
                delivery_date = (
                    getattr(source_move, "delivery_date", False)
                    or source_move.invoice_date
                )

            rows.append(
                {
                    "invoice_date": source_move.invoice_date or source_move.date,
                    "invoice_number": source_move.ref or source_move.name or "",
                    "partner_name": partner.name or "",
                    "partner_address": self._format_partner_address(partner),
                    "partner_siret": getattr(partner, "siret", "") or "",
                    "operation_nature": self._get_operation_nature(source_move, tax),
                    "tax_rate": tax_rate,
                    "amount_ht": amount_ht,
                    "amount_vat": amount_vat,
                    "amount_ttc": amount_ttc,
                    "category": category,
                    "payment_dates": payment_dates,
                    "delivery_date": delivery_date,
                    "box_label": entry["box_label"],
                }
            )

        # Sort by invoice date then partner name
        rows.sort(key=lambda r: (r["invoice_date"] or "", r["partner_name"]))
        return rows

    def generate_xlsx(self):
        """Launch the XLSX report generation."""
        self.ensure_one()
        return self.env.ref(
            "l10n_fr_account_vat_return"
            ".action_report_deductible_vat_detail_xlsx"
        ).report_action(self)
