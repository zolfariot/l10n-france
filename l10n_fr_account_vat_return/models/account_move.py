# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Keep fiscal position type for compatibility with other features
    fiscal_position_fr_vat_type = fields.Selection(
        related="fiscal_position_id.fr_vat_type",
        store=True,
        string="Fiscal Position Type",
    )

    # Native Odoo tax cash basis journal entries are now enabled
    # The VAT return will use native tax exigibility to determine
    # which amounts should be included in the VAT calculation
