# Evaluation & Optimization Package

This package contains tools for evaluating and optimizing the Fund Search Agent using DSPy and MLflow.

## Structure

- **`config/`**: Configuration settings.
- **`core/`**: Shared logic for metrics, pipelines, and dataset loading.
- **`optimization/`**: GEPA optimizer wrapper and target-specific optimization logic.
- **`scripts/`**: CLI entry points.

## Usage

### 1. Evaluation

Run evaluations on specific components:

```bash
# Evaluate Intent Classification
uv run python -m src.evaluation.scripts.evaluate intent

# Evaluate Extraction (Criteria Matching)
uv run python -m src.evaluation.scripts.evaluate extractor

# Evaluate Full Pipeline (Intent + Extractor)
uv run python -m src.evaluation.scripts.evaluate pipeline
```

### 2. Optimization (GEPA)

Optimize components using DSPy's GEPA optimizer. Ensure `MLFLOW_ENABLED=true` to track results.

```bash
# Optimize Intent Classifier
MLFLOW_ENABLED=true uv run python -m src.evaluation.scripts.optimize --target intent

# Optimize Extractor
MLFLOW_ENABLED=true uv run python -m src.evaluation.scripts.optimize --target extractor
```

### 3. Viewing Results

If MLflow is enabled, view the results UI:

   ```bash
uv run mlflow ui --backend-store-uri src/mlflow/mlflow.db
```
