# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    # Native Odoo tax cash basis journal entries are now enabled
    # The VAT return will use native tax exigibility to determine
    # which amounts should be included in the VAT calculation
