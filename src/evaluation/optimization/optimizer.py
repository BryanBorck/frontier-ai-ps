import dspy

import mlflow
from src.evaluation.config import settings


class GepaOptimizer:
    """
    Wrapper for DSPy GEPA Optimizer with MLflow integration.
    """

    def __init__(self, metric_fn, teacher_module=None, auto_level="medium", num_threads=4):
        self.metric_fn = metric_fn
        self.teacher_module = teacher_module  # Optional teacher for distillation/bootstrapping
        self.auto_level = auto_level
        self.num_threads = num_threads

        # Initialize reflection LM
        self.reflection_lm = dspy.LM(
            model=settings.REFLECTION_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=1.0,
            max_tokens=4000,
        )

        # Check for GEPA availability
        try:
            from dspy.teleprompt import GEPA

            self.optimizer_class = GEPA
        except ImportError:
            raise ImportError("dspy.teleprompt.GEPA not found. Ensure DSPy is updated.")

    def optimize(self, module, trainset, valset, experiment_name_suffix=""):
        """
        Run the optimization loop.
        """
        print(f"\nInitializing GEPA (Auto={self.auto_level}, Threads={self.num_threads})...")

        optimizer = self.optimizer_class(
            metric=self.metric_fn,
            teacher=self.teacher_module,
            reflection_lm=self.reflection_lm,
            auto=self.auto_level,
            num_threads=self.num_threads,
            use_mlflow=settings.MLFLOW_ENABLED,
            track_stats=True,
        )

        # Compile/Optimize
        print("\nStarting optimization run...")
        if settings.MLFLOW_ENABLED:
            mlflow.set_experiment(f"{settings.MLFLOW_EXPERIMENT_NAME}-{experiment_name_suffix}")

        compiled_module = optimizer.compile(student=module, trainset=trainset, valset=valset)

        return compiled_module
