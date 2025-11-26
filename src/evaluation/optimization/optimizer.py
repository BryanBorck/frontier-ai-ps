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

        # Initialize default/student LM
        self.task_lm = dspy.LM(
            model=settings.DEFAULT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.0,  # Lower temp for consistent evaluation
            max_tokens=2000,
        )

        # Configure global LM immediately upon initialization
        dspy.configure(lm=self.task_lm)

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

        # Re-configure just in case
        dspy.configure(lm=self.task_lm)

        optimizer = self.optimizer_class(
            metric=self.metric_fn,
            reflection_lm=self.reflection_lm,  # Fixed: use reflection_lm instead of prompt_model
            auto=self.auto_level,
            # verbose=True,
        )

        # Compile/Optimize
        print("\nStarting optimization run...")
        if settings.MLFLOW_ENABLED:
            mlflow.set_experiment(f"{settings.MLFLOW_EXPERIMENT_NAME}-{experiment_name_suffix}")

        compiled_module = optimizer.compile(
            student=module,
            trainset=trainset,
            valset=valset,
        )

        return compiled_module
