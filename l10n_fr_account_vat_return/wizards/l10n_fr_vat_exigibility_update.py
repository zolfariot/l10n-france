# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class L10nFrVatExigibilityUpdate(models.TransientModel):
    _name = "l10n.fr.vat.exigibility.update"
    _description = "Change Company VAT Exigibility (Deprecated)"

    # This wizard is deprecated and no longer functional
    # VAT exigibility should now be configured directly on individual taxes
    # using the native 'tax_exigibility' field in account.tax

    def run(self):
        raise UserError(
            _(
                "This wizard is deprecated.\n\n"
                "To configure VAT exigibility, please use the native Odoo functionality:\n"
                "1. Go to Accounting > Configuration > Taxes\n"
                "2. Edit each tax individually\n"
                "3. Set the 'Tax Exigibility' field to 'Based on Invoice' or "
                "'Based on Payment'\n\n"
                "When 'Based on Payment' is selected, Odoo will automatically create "
                "cash basis journal entries when invoices are paid, and the VAT return "
                "will correctly calculate VAT based on payment status."
            )
        )
