import json
import os
from collections import defaultdict

EXTRACTED_DIR = "src/infrastructure/db/extracted"
OUTPUT_FILE = os.path.join(EXTRACTED_DIR, "entity_correlations.json")

# Define keywords to group entities by parent company
# This maps a Keyword -> List of possible patterns in the name
ENTITY_GROUPS = {
    "ITAU": ["ITAU", "INTRAG", "UNIBANCO"],
    "BRADESCO": ["BRADESCO", "BRAM"],
    "SANTANDER": ["SANTANDER", "S3 CACEIS"], # S3 CACEIS is the custodian for Santander
    "BTG": ["BTG PACTUAL"],
    "XP": ["XP "], # Space to avoid partial matches
    "SAFRA": ["SAFRA"],
    "BB": ["BB ", "BANCO DO BRASIL"],
    "BNY": ["BNY MELLON"],
    "CREDIT SUISSE": ["CREDIT SUISSE", "CSHG"],
    "CITI": ["CITIBANK", "CITI "],
    "BNP": ["BNP PARIBAS"],
    "JPMORGAN": ["J.P. MORGAN", "JPMORGAN"],
    "VINCI": ["VINCI"],
    "KINEA": ["KINEA"],
    "SPX": ["SPX"],
    "ARX": ["ARX"],
    "ADAM": ["ADAM"],
    "GAVEA": ["GÁVEA", "GAVEA"],
    "VERDE": ["VERDE AM", "VERDE ASSET"],
    "OCCAM": ["OCCAM"],
    "TRUXT": ["TRUXT"],
    "KAPITALO": ["KAPITALO"],
    "JGP": ["JGP"],
    "PATRIA": ["PÁTRIA", "PATRIA"],
    "ABSOLUTO": ["ABSOLUTO"],
    "BAHIA": ["BAHIA AM", "BAHIA ASSET"],
    "IP": ["IP CAPITAL"],
    "DYNAMO": ["DYNAMO"],
    "CONSTELLATION": ["CONSTELLATION"],
    "BOGARI": ["BOGARI"],
    "VALET": ["VALET"],
    "NAVI": ["NAVI"],
    "DAYCOVAL": ["DAYCOVAL"],
    "VOTORANTIM": ["VOTORANTIM", "BV "],
    "ABC": ["ABC BRASIL"],
    "GENIAL": ["GENIAL", "PLURAL"],
    "GUIDE": ["GUIDE"],
    "ORAMA": ["ÓRAMA", "ORAMA"],
    "RICO": ["RICO"],
    "CLEAR": ["CLEAR"],
    "MODAL": ["MODAL"],
}

def build_correlations():
    print("=" * 80)
    print("BUILDING ENTITY CORRELATIONS")
    print("=" * 80)
    
    files_to_process = ["managers.jsonl", "administrators.jsonl", "custodians.jsonl"]
    
    # Structure: Group -> { Role -> List of Entities }
    correlation_map = defaultdict(lambda: defaultdict(list))
    
    # Also keep track of "Uncategorized" major players
    uncategorized = []

    for filename in files_to_process:
        filepath = os.path.join(EXTRACTED_DIR, filename)
        role = filename.split(".")[0].upper().rstrip("S") # MANAGER, ADMINISTRATOR, CUSTODIAN
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                entity = json.loads(line)
                name = entity['primary_name']
                tax_id = entity['tax_id']
                count = entity['count']
                
                matched = False
                for group, keywords in ENTITY_GROUPS.items():
                    # Check if ANY keyword matches ANY name variation
                    # But primary name is usually sufficient
                    if any(kw in name for kw in keywords):
                        correlation_map[group][role].append({
                            "name": name,
                            "tax_id": tax_id,
                            "count": count
                        })
                        matched = True
                        break
                
                if not matched and count > 50: # Only track significant uncategorized entities
                    uncategorized.append({
                        "name": name,
                        "role": role,
                        "count": count
                    })

    # Sort lists by count
    for group in correlation_map:
        for role in correlation_map[group]:
            correlation_map[group][role].sort(key=lambda x: x['count'], reverse=True)

    # Save output
    output = {
        "groups": correlation_map,
        "uncategorized_significant": sorted(uncategorized, key=lambda x: x['count'], reverse=True)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"Correlations saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nSummary of Top Groups:")
    for group, roles in sorted(correlation_map.items(), key=lambda x: sum(len(r) for r in x[1].values()), reverse=True)[:10]:
        print(f"\n{group}:")
        for role, entities in roles.items():
            total_count = sum(e['count'] for e in entities)
            print(f"  {role}: {len(entities)} entities (Total refs: {total_count})")
            print(f"    Top: {entities[0]['name']}")

if __name__ == "__main__":
    build_correlations()

