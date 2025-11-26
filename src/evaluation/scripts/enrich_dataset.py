"""
Enrich Evaluation Dataset with Ground Truth CNPJs
=================================================
Adds expected CNPJs to queries where we can verify exact matches.
"""

import json
import os
import sys

# Add the parent directory to sys.path to allow importing from known_funds_ground_truth
# Assuming this script is run from project root or src/evaluation/scripts/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from known_funds_ground_truth import (
    KNOWN_FUNDS, 
    MANAGER_FUNDS, 
    FUND_TYPE_SAMPLES,
    INVESTMENT_CLASS_SAMPLES,
    TARGET_AUDIENCE_SAMPLES,
)

# Mapping of query IDs to ground truth data
# Format: query_id → {"ground_truth_cnpjs": [...], "ground_truth_note": "..."}
GROUND_TRUTH_MAP = {
    # === TIER 1: FUND NAME SEARCHES ===
    
    # Query ID 21: "Alaska Black"
    21: {
        "ground_truth_cnpjs": ["23.517.757/0001-34", "28.443.404/0001-10"],
        "ground_truth_note": "Alaska Black funds",
        "must_include_any": True,  # At least one of these CNPJs should be in results
    },
    
    # Query ID 22: "Verde Scena"
    22: {
        "ground_truth_cnpjs": ["35.688.927/0001-74"],
        "ground_truth_note": "Verde Scena FIC FIM",
        "must_include_any": True,
    },
    
    # Query ID 23: "Dynamo Cougar"  
    23: {
        "ground_truth_cnpjs": ["73.232.530/0001-39"],
        "ground_truth_note": "Dynamo Cougar FIA - one of Brazil's oldest and most famous equity funds",
        "must_include_any": True,
    },
    
    # Query ID 24: "SPX Nimitz"
    24: {
        "ground_truth_cnpjs": ["23.243.147/0001-55"],
        "ground_truth_note": "SPX Nimitz Feeder FIC FIM",
        "must_include_any": True,
    },
    
    # Query ID 25: "Kapitalo Kappa"
    25: {
        "ground_truth_cnpjs": ["25.068.790/0001-08"],
        "ground_truth_note": "Kapitalo Kappa FIN FIC FIM",
        "must_include_any": True,
    },
    
    # Query ID 26: "Ibiuna Hedge"
    26: {
        "ground_truth_cnpjs": ["11.017.946/0001-26"],
        "ground_truth_note": "Ibiuna Hedge STH FIC FIM",
        "must_include_any": True,
    },
    
    # Query ID 27: "Occam Retorno Absoluto"
    27: {
        "ground_truth_cnpjs": ["14.609.319/0001-17"],
        "ground_truth_note": "Occam Retorno Absoluto FIC FIM",
        "must_include_any": True,
    },
    
    # Query ID 28: "JGP Strategy"
    28: {
        "ground_truth_cnpjs": ["11.225.860/0001-02"],
        "ground_truth_note": "JGP Strategy FIC FIM",
        "must_include_any": True,
    },
    
    # === TIER 1: MANAGER SEARCHES ===
    
    # Query ID 36: "Itau funds"
    36: {
        "ground_truth_cnpjs": MANAGER_FUNDS.get("itau", []),
        "ground_truth_note": "Itau Asset Management funds",
        "must_include_any": True,
        "min_results": 5,  # Should return at least 5 Itau funds
    },
    
    # Query ID 37: "Bradesco funds"  
    37: {
        "ground_truth_cnpjs": MANAGER_FUNDS.get("bradesco", []),
        "ground_truth_note": "Bradesco Asset Management funds",
        "must_include_any": True,
        "min_results": 5,
    },
    
    # === TIER 1: FUND TYPE FILTERS ===
    
    # Query ID 1: "FIP funds"
    1: {
        "ground_truth_cnpjs": FUND_TYPE_SAMPLES.get("FIP", []),
        "ground_truth_note": "Private Equity funds (FIP)",
        "must_include_any": True,
        "min_results": 3,
    },
    
    # Query ID 2: "Show me FII funds"
    2: {
        "ground_truth_cnpjs": FUND_TYPE_SAMPLES.get("FII", []),
        "ground_truth_note": "Real Estate Investment Funds (FII)",
        "must_include_any": True,
        "min_results": 10,
    },
    
    # Query ID 4: "ETF funds"
    4: {
        "ground_truth_cnpjs": FUND_TYPE_SAMPLES.get("ETF", []),
        "ground_truth_note": "Exchange Traded Funds",
        "must_include_any": True,
        "min_results": 3,
    },
    
    # === TIER 1: INVESTMENT CLASS FILTERS ===
    
    # Query ID 5: "Equity funds"
    5: {
        "ground_truth_cnpjs": INVESTMENT_CLASS_SAMPLES.get("Ações", []),
        "ground_truth_note": "Equity (Ações) funds",
        "must_include_any": True,
        "min_results": 10,
    },
    
    # Query ID 7: "Fixed income funds"
    7: {
        "ground_truth_cnpjs": INVESTMENT_CLASS_SAMPLES.get("Renda Fixa", []),
        "ground_truth_note": "Fixed Income (Renda Fixa) funds",
        "must_include_any": True,
        "min_results": 10,
    },
    
    # Query ID 9: "Multimarket funds"
    9: {
        "ground_truth_cnpjs": INVESTMENT_CLASS_SAMPLES.get("Multimercado", []),
        "ground_truth_note": "Multimarket (Multimercado) funds",
        "must_include_any": True,
        "min_results": 10,
    },
    
    # === TIER 3: TRICKY MANAGER NAME QUERIES ===
    
    # Query ID 166: "legacy funds" - Legacy Capital is a real manager!
    166: {
        "ground_truth_cnpjs": ["29.679.575/0001-33"],
        "ground_truth_note": "Legacy Capital FIC FIM - should recognize 'Legacy' as manager name",
        "must_include_any": True,
    },
    
    # Query ID 167: "verde funds" - Verde Asset is a famous manager
    167: {
        "ground_truth_cnpjs": ["35.688.927/0001-74", "04.892.108/0001-06"],
        "ground_truth_note": "Verde Asset funds - should return Verde manager funds",
        "must_include_any": True,
    },
    
    # Query ID 168: "opportunity funds" - Opportunity Asset is a manager
    168: {
        "ground_truth_cnpjs": ["04.206.024/0001-02"],
        "ground_truth_note": "Opportunity Total FIC FIM",
        "must_include_any": True,
    },
    
    # Query ID 171: "constellation funds" - Constellation Asset is a manager
    171: {
        "ground_truth_cnpjs": ["29.516.363/0001-75"],
        "ground_truth_note": "Constellation Compounders FIC FIA",
        "must_include_any": True,
    },
    
    # Query ID 173: "brasil capital funds" - Brasil Capital is a manager
    173: {
        "ground_truth_cnpjs": ["19.077.409/0001-71"],
        "ground_truth_note": "Brasil Capital 30 FIC FIA",
        "must_include_any": True,
    },
    
    # Query ID 174: "patria funds" - Patria Investimentos is a manager
    174: {
        "ground_truth_cnpjs": ["37.521.238/0001-73"],
        "ground_truth_note": "Patria Infraestrutura Core FIP-IE",
        "must_include_any": True,
    },
}

def enrich_dataset(input_file: str, output_file: str):
    """Add ground truth data to evaluation dataset"""
    
    enriched = []
    enriched_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                query = json.loads(line.strip())
                query_id = query.get("id")
                
                # Check if we have ground truth for this query
                if query_id in GROUND_TRUTH_MAP:
                    gt = GROUND_TRUTH_MAP[query_id]
                    query["ground_truth_cnpjs"] = gt.get("ground_truth_cnpjs", [])
                    query["ground_truth_note"] = gt.get("ground_truth_note", "")
                    query["must_include_any"] = gt.get("must_include_any", False)
                    if "min_results" in gt:
                        query["min_results"] = gt["min_results"]
                    enriched_count += 1
                
                enriched.append(query)
        
        # Write enriched dataset
        with open(output_file, 'w', encoding='utf-8') as f:
            for query in enriched:
                f.write(json.dumps(query, ensure_ascii=False) + "\n")
        
        print(f"Enriched {enriched_count} queries with ground truth CNPJs")
        print(f"Output saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def print_ground_truth_summary():
    """Print summary of ground truth mappings"""
    print("\n" + "="*60)
    print("GROUND TRUTH CNPJ MAPPINGS")
    print("="*60)
    
    for query_id, gt in sorted(GROUND_TRUTH_MAP.items()):
        print(f"\nQuery ID {query_id}:")
        print(f"  Note: {gt.get('ground_truth_note', 'N/A')}")
        print(f"  CNPJs: {gt.get('ground_truth_cnpjs', [])[:3]}...")
        if gt.get("min_results"):
            print(f"  Min Results: {gt['min_results']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print_ground_truth_summary()
    else:
        enrich_dataset(
            "src/evaluation/data/fund_search_evaluation.jsonl",
            "src/evaluation/data/fund_search_evaluation_enriched.jsonl"
        )

