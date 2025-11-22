# Brazilian Funds Database Schema

DuckDB database containing Brazilian fund data from CVM (Comissão de Valores Mobiliários).

**Database Path:** `src/infrastructure/db/br_funds.db`

## Database Statistics

- **Total Tables:** 5
- **Total Rows:** 14,721,961
- **Date Range:** 2024-01-01 to 2025-08-11

---

## Tables Overview

| Table | Rows | Columns | Description |
|-------|------|---------|-------------|
| **funds** | 67,928 | 33 | Fund master data (registration, metadata, fees) |
| **fund_snapshots** | 10,318,810 | 10 | Daily fund snapshots (prices, NAV, flows) |
| **positions** | 2,598,373 | 10 | Fund holdings linking funds to assets |
| **assets** | 1,224,402 | 17 | Asset details (stocks, bonds, derivatives) |
| **fund_performance_indicators** | 512,448 | 11 | Monthly fund performance metrics |

---

## Table: `funds`

**Description:** Master data for investment funds including registration details, fees, and metadata.

**Row Count:** 67,928

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `fund_id` | STRUCT(type VARCHAR, value VARCHAR) | Unique fund identifier (INTERNAL_HASH) |
| `timestamp` | VARCHAR | Data snapshot timestamp (ISO 8601) |
| `identifiers` | STRUCT(type VARCHAR, value VARCHAR)[] | Array of identifiers (CNPJ, CVM_CODE) |
| `legal_name` | VARCHAR | Full legal name of the fund |
| `fund_type` | VARCHAR | Fund type (FI, FIP, FIDC, FII, etc.) |
| `investment_class` | VARCHAR | Investment class (Multimercado, Ações, Renda Fixa, etc.) |
| `anbima_classification` | VARCHAR | ANBIMA classification |
| `performance_benchmark` | VARCHAR | Performance benchmark |
| `structure` | VARCHAR | Fund structure (OPEN, CLOSED, UNSPECIFIED) |
| `status` | VARCHAR | Fund status (ACTIVE, CANCELLED, etc.) |
| `target_audience` | VARCHAR | Target audience type |
| `manager_type` | VARCHAR | Manager type (CORPORATE, etc.) |
| `service_providers` | STRUCT[] | Array of service providers (admin, auditor, custodian) |
| `is_investment_entity` | BOOLEAN | Investment entity flag |
| `is_fund_of_funds` | BOOLEAN | Fund of funds flag |
| `is_exclusive_fund` | BOOLEAN | Exclusive fund flag |
| `can_invest_abroad_100_pct` | BOOLEAN | Can invest 100% abroad |
| `has_long_term_taxation` | BOOLEAN | Long-term taxation flag |
| `registration_date` | VARCHAR | CVM registration date |
| `constitution_date` | VARCHAR | Fund constitution date |
| `status_start_date` | VARCHAR | Status effective date |
| `activity_start_date` | VARCHAR | Activity start date |
| `class_start_date` | VARCHAR | Investment class start date |
| `fiscal_year_start_date` | VARCHAR | Fiscal year start |
| `fiscal_year_end_date` | VARCHAR | Fiscal year end |
| `cancellation_date` | VARCHAR | Cancellation date (if applicable) |
| `net_asset_value_date` | VARCHAR | NAV reference date |
| `management_fee` | DOUBLE | Management fee percentage |
| `performance_fee` | DOUBLE | Performance fee percentage |
| `net_asset_value` | STRUCT(value DOUBLE, currency VARCHAR) | Net asset value with currency |
| `management_fee_additional_info` | VARCHAR | Additional management fee info |
| `performance_fee_additional_info` | VARCHAR | Additional performance fee info |
| `data_version` | STRUCT | Data version and ingestion metadata |

### Fund Type Enum Values (Top 10)

| Value | Count | Description |
|-------|-------|-------------|
| FI | 32,609 | Fundo de Investimento |
| CLASSES - FIF | 22,858 | Investment Classes |
| FACFIF | 2,734 | Fund of Credit Rights |
| FIP | 2,633 | Private Equity Fund |
| FIF | 2,612 | Financial Investment Fund |
| FIDC | 1,768 | Receivables Investment Fund |
| CLASSES - FIP | 692 | Private Equity Classes |
| FII | 536 | Real Estate Investment Fund |
| FITVM | 343 | Securities and Capital Markets Fund |
| FMIA-CL | 340 | Agribusiness Investment Fund |

### Investment Class Enum Values (Top 10)

| Value | Count |
|-------|-------|
| Multimercado | 19,732 |
| Ações | 4,523 |
| Renda Fixa | 4,016 |
| FIDC | 1,128 |
| FIP | 789 |
| Referenciado | 637 |
| FIP Multi | 613 |
| FII | 524 |
| FIDC-NP | 508 |
| Curto Prazo | 147 |

---

## Table: `fund_snapshots`

**Description:** Daily snapshots of fund metrics including prices, NAV, and flows.

**Row Count:** 10,318,810

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `snapshot_id` | STRUCT(type VARCHAR, value VARCHAR) | Unique snapshot identifier |
| `fund_id` | STRUCT(type VARCHAR, value VARCHAR) | Foreign key to funds table |
| `timestamp` | VARCHAR | Snapshot date (ISO 8601) |
| `share_price` | STRUCT(value DOUBLE, currency VARCHAR) | Share price with currency |
| `total_portfolio_value` | STRUCT(value DOUBLE, currency VARCHAR) | Total portfolio value |
| `net_assets_value` | STRUCT(value DOUBLE, currency VARCHAR) | Net asset value |
| `daily_inflow_value` | STRUCT(value DOUBLE, currency VARCHAR) | Daily inflows |
| `daily_outflow_value` | STRUCT(value DOUBLE, currency VARCHAR) | Daily outflows |
| `number_of_holders` | DOUBLE | Number of fund holders |
| `data_version` | STRUCT | Data version metadata |

---

## Table: `positions`

**Description:** Fund holdings/positions linking funds to their underlying assets.

**Row Count:** 2,598,373

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `position_id` | STRUCT(type VARCHAR, value VARCHAR) | Unique position identifier |
| `timestamp` | VARCHAR | Position date (ISO 8601) |
| `fund_id` | STRUCT(type VARCHAR, value VARCHAR) | Foreign key to funds table |
| `asset_id` | STRUCT(type VARCHAR, value VARCHAR) | Foreign key to assets table |
| `quantity` | DOUBLE | Quantity/units held |
| `current_market_value` | STRUCT(value DOUBLE, currency VARCHAR) | Current market value |
| `cost_basis` | STRUCT(value DOUBLE, currency VARCHAR) | Original cost basis |
| `related_party_issuer` | BOOLEAN | Related party transaction flag |
| `application_date` | VARCHAR | Application/purchase date |
| `data_version` | STRUCT | Data version metadata |

---

## Table: `assets`

**Description:** Asset master data including stocks, bonds, derivatives, and funds.

**Row Count:** 1,224,402

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `asset_id` | STRUCT(type VARCHAR, value VARCHAR) | Unique asset identifier |
| `timestamp` | VARCHAR | Data snapshot timestamp |
| `asset_class` | VARCHAR | Asset class (INVESTMENT_FUND, DERIVATIVES, EQUITY, etc.) |
| `financial_instrument` | VARCHAR | Instrument type (FUND, OPTION, STOCK, etc.) |
| `financial_instrument_description` | VARCHAR | Instrument description |
| `status` | VARCHAR | Asset status (ACTIVE, DELISTED, etc.) |
| `issuer` | STRUCT | Issuer information (name, type, id) |
| `name` | VARCHAR | Asset name |
| `short_name` | VARCHAR | Short/display name |
| `currency` | VARCHAR | Currency code (BRL, USD, etc.) |
| `country` | VARCHAR | Country code (BRA, USA, etc.) |
| `issued_at` | VARCHAR | Issuance date |
| `valid_until` | VARCHAR | Expiration/maturity date |
| `identifiers` | STRUCT(type VARCHAR, value VARCHAR)[] | Asset identifiers (ISIN, TICKER, etc.) |
| `listing` | STRUCT | Exchange listing information |
| `financial_instrument_raw` | VARCHAR | Raw instrument type |
| `data_version` | STRUCT | Data version metadata |

### Asset Class Distribution

| Asset Class | Count |
|-------------|-------|
| INVESTMENT_FUND | 565,792 |
| DERIVATIVES | 453,646 |
| FIXED_INCOME | 113,465 |
| UNSPECIFIED | 69,463 |
| EQUITY | 16,822 |

---

## Table: `fund_performance_indicators`

**Description:** Monthly aggregated performance metrics for funds.

**Row Count:** 512,448

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | STRUCT(type VARCHAR, value VARCHAR) | Unique indicator record ID |
| `fund_id` | STRUCT(type VARCHAR, value VARCHAR) | Foreign key to funds table |
| `year` | INTEGER | Year |
| `month` | INTEGER | Month (1-12) |
| `month_name` | VARCHAR | Month name (January, February, etc.) |
| `first_price` | DOUBLE | First trading price of month |
| `last_price` | DOUBLE | Last trading price of month |
| `return_pct` | DOUBLE | Monthly return percentage |
| `first_date` | VARCHAR | First trading date of month |
| `last_date` | VARCHAR | Last trading date of month |
| `data_version` | STRUCT | Data version metadata |

---

## Relationships

```
funds (1) ──< (M) fund_snapshots
           └──< (M) positions ──> (1) assets
           └──< (M) fund_performance_indicators
```

- A **fund** has many **snapshots** (daily)
- A **fund** has many **positions** (holdings)
- A **position** links a **fund** to an **asset**
- A **fund** has many **performance indicators** (monthly)

---

## Common Query Patterns

### Get fund by CNPJ
```sql
SELECT * FROM funds 
WHERE list_filter(identifiers, x -> x.type = 'CNPJ')[1].value = '12.345.678/0001-90';
```

### Search funds by name
```sql
SELECT * FROM funds 
WHERE LOWER(legal_name) LIKE LOWER('%bradesco%');
```

### Get fund with latest snapshot
```sql
SELECT f.*, s.share_price, s.net_assets_value
FROM funds f
JOIN fund_snapshots s ON f.fund_id = s.fund_id
WHERE s.timestamp = (
    SELECT MAX(timestamp) FROM fund_snapshots WHERE fund_id = f.fund_id
);
```

### Get fund holdings
```sql
SELECT f.legal_name, a.name, p.quantity, p.current_market_value
FROM funds f
JOIN positions p ON f.fund_id = p.fund_id
JOIN assets a ON p.asset_id = a.asset_id
WHERE f.fund_id.value = 'some-fund-id';
```

---

## Notes

- All IDs use STRUCT format: `{type: "INTERNAL_HASH", value: "uuid"}`
- Monetary values use STRUCT: `{value: amount, currency: "BRL"}`
- Timestamps are ISO 8601 format strings
- Data source: CVM (Brazilian Securities Commission)
- Most funds are cancelled (57.4%) or unspecified (41.2%), only 0.7% active
