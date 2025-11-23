## Evaluation and Optimization Setup

This directory contains the evaluation dataset and optimization scripts for the fund search system using DSPy's GEPA optimizer.

## What's Included

### 1. Evaluation Dataset (`fund_search_eval_dataset.py`)

A curated dataset of **17 evaluation examples** covering:
- **Basic queries**: Company names, fund types, investment classes
- **Combined queries**: Multiple criteria in one query
- **Boolean filters**: Fund of funds, exclusive funds
- **Enum filters**: Target audience (qualified/professional/retail investors)
- **Complex queries**: Multiple filters combined

### 2. Evaluation Script (`evaluate.py`)

Evaluates the current system using custom metrics:
- **`criteria_match_score`**: Measures how well parsed criteria matches expected output
- Logs results to MLflow for tracking
- Shows detailed per-example results

### 3. Optimization Script (`optimize.py`)

Runs GEPA optimization to improve system prompts:
- Compares baseline vs optimized performance
- Saves optimized module
- Logs everything to MLflow

## Setup

### 1. Install GEPA (Optional, for optimization)

```bash
pip install gepa
# or with uv:
uv pip install gepa
```

### 2. Enable MLflow (Optional)

In your `.env` file:
```
MLFLOW_ENABLED=true
MLFLOW_TRACKING_URI=http://127.0.0.1:5001
```

Start MLflow UI:
```bash
uv run mlflow ui --port 5001
```

## Usage

### Step 1: Evaluate Current System

Start by evaluating your current system to establish a baseline:

```bash
uv run python src/evaluation/evaluate.py
```

This will:
1. Split dataset into train (80%) and test (20%)
2. Evaluate parser on test set
3. Calculate average score
4. Show detailed per-example results
5. Log results to MLflow (if enabled)

**Expected Output:**
```
EVALUATING FUND SEARCH SYSTEM
================================================================================

Dataset split:
  Training examples: 13
  Test examples: 4

Initializing parser...
Evaluating parser on test set...

================================================================================
RESULTS
================================================================================
Average Score: 95%+  (varies based on prompts)
Total Examples: 4
Total Score: 3.8/4

================================================================================
DETAILED RESULTS
================================================================================

1. give me itau funds
   Score: 100%

2. bradesco FIP multimercado
   Score: 100%

3. exclusive fund of funds from btg for qualified investors
   Score: 100%

4. fund for qualified investors
   Score: 50%
   Expected: {'target_audience': 'QUALIFIED', ...}
   Predicted: {'target_audience': None, ...}

================================================================================
Perfect matches: 3/4
================================================================================
```

### Step 2: Optimize with GEPA (Optional)

Once you're comfortable with evaluation results, optimize with GEPA:

```bash
uv run python src/evaluation/optimize.py
```

This will:
1. Evaluate baseline performance
2. Run GEPA optimization (breadth=3, depth=2)
3. Evaluate optimized prompts
4. Compare before/after
5. Save optimized module
6. Log everything to MLflow

**What GEPA Does:**
- Samples system trajectories (reasoning, tool calls, outputs)
- Reflects on them in natural language to diagnose problems
- Proposes and tests prompt updates
- Combines complementary lessons from Pareto frontier
- **Can improve performance by 10-20%** based on research

**Note:** GEPA optimization can take 5-15 minutes depending on dataset size

## Evaluation Metrics

### `criteria_match_score(predicted, expected) -> float`

Compares predicted vs expected criteria field-by-field:
- Returns score between 0.0 and 1.0
- Only compares fields that are set in expected
- Ignores None values (don't care)

**Example:**
```python
expected = {
    "fund_legal_name": "btg",
    "fund_type": "FIP",
    "investment_class": None,  # Don't care
}

predicted = {
    "fund_legal_name": "btg",
    "fund_type": "FIP",
    "investment_class": "Multimercado",
}

score = criteria_match_score(predicted, expected)
# Returns: 1.0 (100% match on fields we care about)
```

## Adding More Examples

To expand the evaluation dataset:

1. Open `fund_search_eval_dataset.py`
2. Add new `FundSearchExample` to `FUND_SEARCH_EXAMPLES` list:

```python
FundSearchExample(
    query="your query here",
    expected_criteria={
        "fund_legal_name": "expected value or None",
        "fund_type": "expected value or None",
        # ... other fields
    },
    description="What this example tests",
),
```

## GEPA Configuration

You can tune GEPA parameters in `evaluate_and_optimize.py`:

```python
gepa_optimizer = GEPA(
    metric=metric,
    breadth=3,      # Number of prompt variations to try (higher = more exploration)
    depth=2,        # Number of optimization rounds (higher = more refinement)
    num_threads=1,  # Parallel threads (higher = faster but more API calls)
)
```

**Recommendations:**
- Start with `breadth=3, depth=2` (default)
- Increase for better results (but slower & more expensive)
- Monitor MLflow to track improvement over iterations

## MLflow Tracking

When MLflow is enabled, you'll see:

**Experiments:**
- `FundSearch-Evaluation` - evaluation runs

**Metrics:**
- `avg_score` - Average criteria match score
- `num_test_examples` - Number of test examples

**Parameters:**
- `model` - LLM model used
- `optimizer` - Optimizer used (baseline vs GEPA)
- `breadth`, `depth` - GEPA parameters (if optimizing)

**Artifacts:**
- `eval_results.json` - Detailed results for each example

## Recommended Workflow

1. **Start with evaluation**
   ```bash
   uv run python src/evaluation/evaluate.py
   ```
   - Review baseline performance
   - Identify failing examples
   - Check MLflow UI for detailed results

2. **Get comfortable with the metrics**
   - Understand which queries fail and why
   - Add more test examples if needed
   - Run evaluation again after adding examples

3. **When ready, optimize**
   ```bash
   uv run python src/evaluation/optimize.py
   ```
   - GEPA will improve your prompts
   - Compare before/after in MLflow
   - Review which examples improved

4. **Iterate**
   - Add more examples to evaluation dataset as you discover edge cases
   - Re-evaluate periodically
   - Re-optimize when you make significant system changes

## Research Paper

GEPA is based on:
- **Paper**: "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning"
- **Authors**: Agrawal et al., 2025
- **ArXiv**: https://arxiv.org/abs/2507.19457
- **Key Result**: Outperforms GRPO by 10% on average, MIPROv2 by 10%+, using 35x fewer rollouts
