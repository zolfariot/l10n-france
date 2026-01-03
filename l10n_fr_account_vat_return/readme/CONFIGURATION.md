# Configuration Guide

## Fiscal Position Configuration for VAT Return

### Overview

The French VAT return module requires proper configuration of **fiscal positions** to correctly calculate untaxed operations that must be reported on the CA3 form. This includes:

- **Intra-EU B2B sales** (livraisons intracommunautaires)
- **Intra-EU B2C sales**
- **Extra-EU exports** (exportations)
- **France exempt operations** (opérations exonérées)

### Why Account Mappings are Required

The module uses the fiscal position's **account mapping table** (table de correspondance des comptes) to identify which revenue accounts correspond to each type of untaxed operation. This is necessary because:

1. Different types of untaxed operations must be reported in different boxes on the CA3
2. The module analyzes the account balances during the period to calculate amounts
3. Account mappings allow the module to distinguish between different types of operations

### Error: "La table de correspondance des comptes est vide"

If you see the error **"La table de correspondance des comptes est vide sur la position fiscale 'Intra-EU B2B'"** (or similar), it means the fiscal position lacks the required account mappings.

### How to Configure Account Mappings

#### Step 1: Access Fiscal Position Configuration

1. Go to **Accounting > Configuration > Fiscal Positions**
2. Find and open the fiscal position mentioned in the error (e.g., "Intra-EU B2B")

#### Step 2: Add Account Mappings

In the fiscal position form, go to the **Account Mapping** tab and add mappings for revenue accounts:

**Example for Intra-EU B2B:**
- **Source Account**: 701100 (Ventes de produits finis France)
- **Destination Account**: 701200 (Ventes de produits finis Intra-EU)

**Example for Extra-EU Exports:**
- **Source Account**: 701100 (Ventes de produits finis France)
- **Destination Account**: 701400 (Ventes de produits finis Export)

**Example for France Exempt:**
- **Source Account**: 701100 (Ventes de produits finis France)
- **Destination Account**: 701500 (Ventes de produits finis Exonérées)

#### Step 3: Important Rules

1. **Map all revenue account types**: Map accounts for products (701xxx), services (706xxx), etc.
2. **Both accounts must be income accounts**: The source and destination must both have `account_type` starting with "income"
3. **Unique destination accounts**: Each fiscal position type should use different destination accounts
4. **Purchase-only positions**: For fiscal positions used only for purchases (e.g., Auto-entrepreneur), account mappings are optional

### Common Fiscal Position Account Mappings

#### Intra-EU B2B (`fr_vat_type = "intracom_b2b"`)
```
701100 → 701200 (Products)
706100 → 706200 (Services)
707100 → 707200 (Merchandise)
708510 → 708520 (Accessories)
```

#### Extra-EU Exports (`fr_vat_type = "extracom"`)
```
701100 → 701400 (Products)
706100 → 706400 (Services)
707100 → 707400 (Merchandise)
708510 → 708540 (Accessories)
```

#### France Exempt (`fr_vat_type = "france_exo"`)
```
701100 → 701500 (Products)
706100 → 706500 (Services)
707100 → 707500 (Merchandise)
708510 → 708550 (Accessories)
```

### Verification

After configuring the account mappings:

1. Create a test invoice with the fiscal position
2. Verify that the revenue account on the invoice lines is the **destination account** from the mapping
3. Generate a VAT return and verify that untaxed operations are correctly calculated

### Technical Note

The `_generate_operation_untaxed()` function is **still required** after migrating to native tax exigibility. It handles:

- Calculating untaxed operations from account balances during the period
- Grouping operations by fiscal position type
- Validating account mapping configuration

This function is **independent of tax exigibility** settings and relates to operations that have **no VAT** (either exempt, out-of-scope, or reverse charge).

### Related Error Messages

- **"La table de correspondance des comptes est vide sur la position fiscale 'X'"**
  - Solution: Add revenue account mappings to fiscal position X

- **"Missing account mapping on fiscal position 'X'"**
  - Solution: Add revenue account mappings to fiscal position X (unless it's purchase-only)

- **"Account 'X' is present in the mapping of several fiscal positions"**
  - Solution: Use different destination accounts for each fiscal position type

### Need Help?

If you need to create the destination accounts:
1. Go to **Accounting > Configuration > Chart of Accounts**
2. Create new accounts with appropriate codes (701200, 701400, etc.)
3. Set the **Account Type** to the same as the source account (Income)
4. Configure the account mappings as described above
