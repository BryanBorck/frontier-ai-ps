import json
import os
import re


class EntityMapper:
    """
    Maps user-friendly names to standardized keys found in database correlations.
    """

    _entity_map = None

    @classmethod
    def _load_map(cls):
        if cls._entity_map is None:
            map_path = "src/infrastructure/database/extracted/entity_correlations.json"
            if os.path.exists(map_path):
                try:
                    with open(map_path, encoding="utf-8") as f:
                        data = json.load(f)
                        cls._entity_map = data.get("groups", {})
                except Exception as e:
                    print(f"Warning: Failed to load entity map: {e}")
                    cls._entity_map = {}
            else:
                cls._entity_map = {}

    @classmethod
    def _load_managers(cls):
        if not hasattr(cls, "_managers_set"):
            cls._managers_set = set()
            path = "src/infrastructure/database/extracted/managers.jsonl"
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        for line in f:
                            data = json.loads(line)
                            # Add primary and variations to set for fast lookup
                            cls._managers_set.add(data["primary_name"].upper())
                            for v in data.get("name_variations", []):
                                cls._managers_set.add(v.upper())
                except Exception as e:
                    print(f"Error loading managers: {e}")

    @classmethod
    def normalize_provider(cls, name: str) -> str | None:
        """
        Normalize a service provider name to its standardized key.
        """
        if not name:
            return None

        cls._load_map()
        name_upper = name.upper().strip()

        # 1. Direct match in groups
        if name_upper in cls._entity_map:
            return name_upper

        # 2. Check regex patterns (hardcoded fallbacks for common aliases)
        # These map aliases to the KEYS in entity_correlations.json
        PROVIDER_PATTERNS = {
            # Banks and Major Platforms
            r"\b(ita[uú])\b": "ITAU",
            r"\b(bradesco|bram)\b": "BRADESCO",
            r"\b(santander)\b": "SANTANDER",
            r"\b(xp)\b": "XP",
            r"\b(btg(?:\s+pactual)?)\b": "BTG",
            r"\b(banco\s+do\s+brasil|bb)\b": "BB",
            r"\b(safra)\b": "SAFRA",
            r"\b(credit\s+suisse|cshg)\b": "CREDIT SUISSE",
            r"\b(bny(?:\s+mellon)?)\b": "BNY MELLON",
            r"\b(daycoval)\b": "DAYCOVAL",
            r"\b(citibank|citi)\b": "CITIBANK",
            r"\b(bnp(?:\s+paribas)?)\b": "BNP",
            # Top Independent Asset Managers
            r"\b(vinci)\b": "VINCI",
            r"\b(arx)\b": "ARX",
            r"\b(kinea)\b": "KINEA",
            r"\b(spx)\b": "SPX",
            r"\b(jgp)\b": "JGP",
            r"\b(adam)\b": "ADAM",
            r"\b(kapitalo)\b": "KAPITALO",
            r"\b(g[aá]vea)\b": "GAVEA",
            r"\b(verde)\b": "VERDE",
            r"\b(genial)\b": "GENIAL",
            r"\b(occam)\b": "OCCAM",
            r"\b(truxt)\b": "TRUXT",
            r"\b(pátria|patria)\b": "PATRIA",
            r"\b(absoluto)\b": "ABSOLUTO",
            r"\b(bahia)\b": "BAHIA",
            r"\b(ip(?:\s+capital)?)\b": "IP CAPITAL",
            r"\b(dynamo)\b": "DYNAMO",
            r"\b(constellation)\b": "CONSTELLATION",
            r"\b(bogari)\b": "  BOGARI",
            r"\b(valet)\b": "VALET",
            r"\b(navi)\b": "NAVI",
            r"\b(jpmorgan|jp\s+morgan)\b": "JPMORGAN",
            r"\b(votorantim|bv)\b": "VOTORANTIM",
            r"\b([óo]rama)\b": "ORAMA",
            r"\b(legacy)\b": "LEGACY CAPITAL",
        }

        name_lower = name.lower()
        for pattern, key in PROVIDER_PATTERNS.items():
            if re.search(pattern, name_lower):
                return key

        # 3. Fuzzy / Partial match against keys in entity_map
        for key in cls._entity_map:
            if key in name_upper:
                return key
            if name_upper in key:
                pass

        # 4. Search in managers.jsonl (Dynamic validation of user term)
        cls._load_managers()

        # Filter generic terms that shouldn't match on their own
        GENERIC_TERMS = {
            "ASSET",
            "MANAGEMENT",
            "GESTORA",
            "RECURSOS",
            "CAPITAL",
            "INVESTIMENTOS",
            "FUNDO",
            "FUNDOS",
            "FINANCEIRO",
            "LTDA",
            "S.A.",
            "SA",
            "BANC0",
            "BANCO",
            "DTVM",
            "CORRETORA",
            "DISTRIBUIDORA",
            "WEALTH",
            "GLOBAL",
            "PARTICIPACOES",
            "PARTICIPAÇÕES",
        }

        if name_upper in GENERIC_TERMS:
            return None

        # Check if name_upper appears in any known manager name
        for mgr_name in cls._managers_set:
            # Check for exact token match (e.g. "LEGACY" in "LEGACY CAPITAL")
            tokens = set(mgr_name.split())
            if name_upper in tokens:
                return name_upper

            # Or check for phrase match if it's substantial
            if len(name_upper) > 3 and name_upper in mgr_name:
                return name_upper

        return None


class AssetMapper:
    """
    Maps asset names to tickers and IDs using extracted database correlations.
    """

    _asset_map = None  # Structured Dictionary: Category -> Normalized Name -> Data

    @classmethod
    def _load_map(cls):
        if cls._asset_map is None:
            map_path = "src/infrastructure/database/extracted/asset_correlations.json"
            if os.path.exists(map_path):
                try:
                    with open(map_path, encoding="utf-8") as f:
                        cls._asset_map = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to load asset map: {e}")
                    cls._asset_map = {}
            else:
                cls._asset_map = {}

    @classmethod
    def get_tickers(cls, name: str, category_filter: str | None = None) -> list[str]:
        """
        Get tickers for a given asset name.
        Uses extracted correlations and hardcoded fallbacks.
        """
        if not name:
            return []

        cls._load_map()
        name_clean = name.lower().strip()

        # 1. Hardcoded common aliases (fast path for very popular stocks)
        COMMON_MAPPINGS = {
            "petrobras": ["PETR3", "PETR4"],
            "vale": ["VALE3"],
            "itau": ["ITUB3", "ITUB4"],
            "bradesco": ["BBDC3", "BBDC4"],
            "banco do brasil": ["BBAS3"],
            "ambev": ["ABEV3"],
            "magalu": ["MGLU3"],
            "magazine luiza": ["MGLU3"],
            "rede d'or": ["RDOR3"],
            "rede dor": ["RDOR3"],
        }
        if name_clean in COMMON_MAPPINGS and (not category_filter or category_filter == "EQUITY"):
            return COMMON_MAPPINGS[name_clean]

        # 2. Normalize input
        norm_name = re.sub(r"[^\w\s]", "", name_clean).upper()

        # 3. Search in map
        tickers = []
        categories_to_search = [category_filter] if category_filter else cls._asset_map.keys()

        for cat in categories_to_search:
            if cat in cls._asset_map:
                cat_data = cls._asset_map[cat]
                # Direct match
                if norm_name in cat_data:
                    tickers.extend(cat_data[norm_name].get("tickers", []))
                # If not direct match, we might want partial match, but for now strict normalized match

        return list(set(tickers))

    @classmethod
    def get_asset_ids(cls, name: str, category_filter: str | None = None) -> list[str]:
        """
        Get asset IDs for a given asset name.
        """
        if not name:
            return []

        cls._load_map()
        name_clean = name.lower().strip()
        norm_name = re.sub(r"[^\w\s]", "", name_clean).upper()

        asset_ids = []
        categories_to_search = [category_filter] if category_filter else cls._asset_map.keys()

        for cat in categories_to_search:
            if cat in cls._asset_map:
                cat_data = cls._asset_map[cat]
                if norm_name in cat_data:
                    asset_ids.extend(cat_data[norm_name].get("asset_ids", []))

        return list(set(asset_ids))
