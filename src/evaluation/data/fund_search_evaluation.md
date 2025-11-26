# Fund Search Evaluation Dataset Summary

**Total Queries:** 300

## Evaluation Types

| Type | Description | Count |
|------|-------------|-------|
| `intent_match` | Check if intents list is correct | - |
| `extraction_match` | Check if extracted criteria match | - |
| `response_type_match` | Check if response_type is correct | - |
| `ambiguity_detection` | Check is_potentially_ambiguous flag | - |

## Categories


### Tier 1: Basic


### Tier 2: Intermediate


### Tier 3: Advanced


### Tier 4: Edge Cases


## Sample Queries by Category

### fund_type
**Query:** `FIP funds`

**Why Tricky:** Direct fund type filter

**Expected Intents:** `['find_by_criteria']`

---

### investment_class
**Query:** `Equity funds`

**Why Tricky:** English to Portuguese class translation

**Expected Intents:** `['find_by_criteria']`

---

### audience
**Query:** `Funds for qualified investors`

**Why Tricky:** Qualified investor filter

**Expected Intents:** `['find_by_criteria']`

---

### boolean
**Query:** `Exclusive funds`

**Why Tricky:** Boolean flag extraction

**Expected Intents:** `['find_by_criteria']`

---

### fund_name
**Query:** `Alaska Black`

**Why Tricky:** Famous fund name - should NOT interpret as strategy

**Expected Intents:** `['find_by_name']`

---

### manager
**Query:** `Itau funds`

**Why Tricky:** Major bank manager

**Expected Intents:** `['find_by_criteria']`

---

### exposure
**Query:** `Funds holding Petrobras`

**Why Tricky:** Brazilian blue chip

**Expected Intents:** `['find_by_exposure']`

---

### dual_criteria
**Query:** `Equity funds from Itau`

**Why Tricky:** Class + manager combination

**Expected Intents:** `['find_by_criteria']`

---

### ranking
**Query:** `Top 10 equity funds`

**Why Tricky:** Class + ranking

**Expected Intents:** `['find_by_criteria', 'has_numeric_filter']`

---

### numeric
**Query:** `Funds with fee less than 1%`

**Why Tricky:** Fee threshold

**Expected Intents:** `['has_numeric_filter']`

---

### thematic
**Query:** `Crypto funds`

**Why Tricky:** Thematic search - crypto

**Expected Intents:** `['find_by_strategy']`

---

### manager_theme
**Query:** `bradesco gold fund`

**Why Tricky:** Bradesco + Gold = Bradesco Ouro FI, NOT literal 'Bradesco Gold'

**Expected Intents:** `['find_by_strategy']`

---

### generic_manager
**Query:** `legacy funds`

**Why Tricky:** Legacy Capital is a manager - NOT 'old' funds

**Expected Intents:** `['find_by_name']`

---

### complex_semantic
**Query:** `funds that invest in latam tech`

**Why Tricky:** Complex theme: Latin America + technology intersection

**Expected Intents:** `['find_by_strategy']`

---

### ambiguous_word
**Query:** `Dollar funds`

**Why Tricky:** Dollar = Cambial class or USD exposure strategy?

**Expected Intents:** `['find_by_strategy', 'find_by_criteria']`

---

### too_vague
**Query:** `Show me funds`

**Why Tricky:** No criteria - should ask for clarification

**Expected Intents:** `['general_browse']`

---

### typo
**Query:** `Eqity funds`

**Why Tricky:** Typo: Eqity → Equity

**Expected Intents:** `['find_by_criteria']`

---

### greeting
**Query:** `Hello`

**Why Tricky:** Greeting - no fund search

**Expected Intents:** `['informational']`

---

### closing
**Query:** `Thank you`

**Why Tricky:** Gratitude - no fund search

**Expected Intents:** `['informational']`

---

### informational
**Query:** `What is a FII?`

**Why Tricky:** Definition question - informational

**Expected Intents:** `['informational']`

---

