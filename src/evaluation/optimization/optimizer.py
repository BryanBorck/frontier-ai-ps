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

        # NOTE: teacher argument removed from init as it caused TypeError in recent DSPy versions
        optimizer = self.optimizer_class(
            metric=self.metric_fn,
            # teacher=self.teacher_module, 
            reflection_lm=self.reflection_lm,
            # auto=self.auto_level, # 'auto' might also be specific to MIPRO/MIPROv2 or deprecated in GEPA init
            # num_threads=self.num_threads, # Moved to compile usually or depends on version
            # use_mlflow=settings.MLFLOW_ENABLED, # Not standard arg for base GEPA
            # track_stats=True,
        )
        
        # NOTE: The GEPA signature varies by version. 
        # Standard DSPy optimizers often take metric in init and trainset in compile.
        # Let's try a minimal init first if the previous one failed.
        # If GEPA follows the new standard, it might just be `GEPA(metric=...)`
        
        # Re-instantiating with likely correct args based on error `TypeError: GEPA.__init__() got an unexpected keyword argument 'teacher'`
        # This suggests 'teacher' was wrong. 'auto' and 'num_threads' might be valid if it's like MIPRO.
        # Let's try passing just metric and prompt_model (reflection_lm).
        
        optimizer = self.optimizer_class(
            metric=self.metric_fn,
            prompt_model=self.reflection_lm,
            verbose=True
        )

        # Compile/Optimize
        print("\nStarting optimization run...")
        if settings.MLFLOW_ENABLED:
            mlflow.set_experiment(f"{settings.MLFLOW_EXPERIMENT_NAME}-{experiment_name_suffix}")

        # num_threads usually goes into compile if supported, or init. 
        # auto might be part of compile config.
        compiled_module = optimizer.compile(
            student=module, 
            trainset=trainset, 
            valset=valset,
            # config=dict(num_threads=self.num_threads) # Try passing config if supported
        )

        return compiled_module
