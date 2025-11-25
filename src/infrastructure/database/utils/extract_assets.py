import duckdb
import json
import re
import os
from collections import defaultdict

DB_PATH = "src/infrastructure/database/br_funds.db"
OUTPUT_DIR = "src/infrastructure/database/extracted"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "asset_correlations.json")

def normalize_name(name):
    if not name:
        return ""
    name = name.lower()
    # Remove common legal suffixes
    name = re.sub(r"\bs\.?a\.?\b", "", name)
    name = re.sub(r"\bltda\.?\b", "", name)
    name = re.sub(r"\bcompanhia\b", "", name)
    name = re.sub(r"\bcia\b", "", name)
    name = re.sub(r"\bbanco\b", "", name)
    name = re.sub(r"[^\w\s]", "", name)
    return name.strip().upper()

def categorize_asset_class(raw_class, raw_instrument):
    """
    Map raw database asset_class/instrument to high-level categories.
    """
    raw_class = (raw_class or "").upper()
    raw_instrument = (raw_instrument or "").upper()
    
    if "EQUITY" in raw_class or "STOCK" in raw_class or "ACOES" in raw_class or "AÇÕES" in raw_class:
        return "EQUITY"
    if "DERIVATIVE" in raw_class or "OPTION" in raw_class or "FUTURE" in raw_class or "SWAP" in raw_class:
        return "DERIVATIVES"
    if "FUND" in raw_class or "COTA" in raw_class:
        return "INVESTMENT_FUND"
    if "FIXED" in raw_class or "BOND" in raw_class or "DEBENTURE" in raw_class or "TESOURO" in raw_class:
        return "FIXED_INCOME"
    
    # Fallbacks based on instrument
    if "OPTION" in raw_instrument:
        return "DERIVATIVES"
    if "FUND" in raw_instrument:
        return "INVESTMENT_FUND"
        
    return "OTHER"

def extract_assets():
    conn = duckdb.connect(DB_PATH, read_only=True)
    
    query = """
    SELECT 
        asset_id, 
        name, 
        issuer.issuer_name as issuer_name,
        asset_class,
        financial_instrument,
        identifiers,
        listing
    FROM assets
    WHERE status = 'ACTIVE'
    """
    
    try:
        rows = conn.execute(query).fetchall()
    except Exception as e:
        print(f"Error querying assets: {e}")
        return

    # Grouping structure:
    # {
    #   "EQUITY": {
    #       "PETROBRAS": { ... data ... }
    #   },
    #   ...
    # }
    grouped_data = defaultdict(lambda: defaultdict(list))
    
    print(f"Processing {len(rows)} assets...")

    for row in rows:
        asset_id, name, issuer_name, asset_class, financial_instrument, identifiers, listing = row
        
        # Determine high-level category
        category = categorize_asset_class(asset_class, financial_instrument)
        
        # Extract Ticker
        ticker = None
        if identifiers:
            for ident in identifiers:
                if ident.get("type") == "TICKER":
                    ticker = ident.get("value")
        
        if not ticker and listing:
            listing_ticker = listing.get("ticker")
            if listing_ticker:
                ticker = listing_ticker.get("value")

        # Determine grouping key (Normalized Name)
        # Use issuer name if available (better for aggregation), else asset name
        raw_group_name = issuer_name if issuer_name else name
        if not raw_group_name:
            continue
            
        norm_key = normalize_name(raw_group_name)
        if not norm_key:
            continue

        # Extract UUID string from struct if needed
        if isinstance(asset_id, dict) and "value" in asset_id:
            aid_str = asset_id["value"]
        else:
            aid_str = str(asset_id)

        asset_obj = {
            "id": aid_str,
            "name": name,
            "ticker": ticker
        }
        
        grouped_data[category][norm_key].append(asset_obj)

    # Final formatting
    final_output = {}
    
    for category, groups in grouped_data.items():
        final_output[category] = {}
        for key, assets in groups.items():
            tickers = set(a["ticker"] for a in assets if a["ticker"])
            ids = [a["id"] for a in assets]
            # Keep a few sample names for display/verification
            sample_names = list(set(a["name"] for a in assets))[:5]
            
            final_output[category][key] = {
                "tickers": list(tickers),
                "asset_ids": ids,
                "sample_names": sample_names,
                "count": len(assets)
            }

    print(f"Extracted categories: {list(final_output.keys())}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_FILE}")
    conn.close()

if __name__ == "__main__":
    extract_assets()
