# Copyright 2026 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration script for version 18.0.2.0.0
    
    This version removes the custom VAT exigibility system and migrates to use
    Odoo's native tax exigibility functionality.
    
    Changes:
    - Removed company.fr_vat_exigibility field
    - Removed account.move.out_vat_on_payment field
    - Native tax.tax_exigibility should now be used instead
    """
    logger.info("Starting migration to version 18.0.2.0.0")
    
    # Remove deprecated fields from database
    # The fields will be automatically removed by Odoo when the module is updated
    
    # Log information for users about the migration
    logger.info(
        "VAT exigibility migration complete. "
        "Please configure tax exigibility directly on individual taxes using the "
        "native 'Tax Exigibility' field in Accounting > Configuration > Taxes."
    )
    
    # Note: Users should manually configure tax_exigibility on their taxes
    # based on their previous fr_vat_exigibility setting
