# Migration to Native Tax Exigibility (Version 18.0.2.0.0)

## Important Changes

Starting from version **18.0.2.0.0**, this module now uses **Odoo's native tax exigibility system** instead of a custom implementation.

### What Changed

The module previously:
- Blocked the use of Odoo's native `tax_exigibility = "on_payment"` setting
- Implemented a custom VAT on payment calculation system
- Required configuring VAT exigibility at the **company level** (via `fr_vat_exigibility` field)
- Disabled Odoo's automatic cash basis journal entries

Now the module:
- **Supports** Odoo's native `tax_exigibility` setting on taxes
- Uses **account balances** that automatically reflect tax exigibility
- Calculates VAT returns directly from account balances (which include cash basis entries)
- Configures VAT exigibility at the **tax level** (standard Odoo way)

### Migration Steps

After upgrading to version 18.0.2.0.0:

1. **Configure Tax Exigibility on Each Tax**:
   - Go to **Accounting > Configuration > Taxes**
   - For each tax that should be "sur encaissement" (on payment):
     - Edit the tax
     - Set **Tax Exigibility** to `Based on Payment`
     - Configure the **Cash Basis Transition Account** (usually 445670 for France)
   
2. **For taxes that are due on invoice** (immediate exigibility):
   - Set **Tax Exigibility** to `Based on Invoice` (default)

3. **Remove the deprecated wizard**:
   - The "Change VAT Exigibility" wizard is now deprecated
   - It will show an error message if you try to use it

### Benefits

- **Standard Odoo functionality**: Uses the built-in tax grid and cash basis system
- **Automatic calculations**: Cash basis journal entries are created automatically when invoices are paid
- **More flexible**: Each tax can have its own exigibility setting
- **Better integration**: Works seamlessly with Odoo's accounting engine

### Technical Details

The VAT return calculation now:
- Uses account balances at the end of the period
- These balances automatically include only paid amounts for taxes with `tax_exigibility = "on_payment"`
- Odoo creates transitional journal entries when payments are made
- No manual adjustment needed for unpaid invoices

### Backward Compatibility

- Existing VAT returns are not affected
- The custom `fr_vat_exigibility` company field has been removed
- The custom `out_vat_on_payment` invoice field has been removed
- Users must manually configure `tax_exigibility` on their taxes after upgrade
