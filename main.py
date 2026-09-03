"""
CLI Entrypoint for Daily AI News Intelligence.
"""
import sys
from src.pipeline import run_pipeline

if __name__ == "__main__":
    try:
        run_pipeline()
        sys.exit(0)
    except Exception as e:
        print(f"Pipeline failed with error: {e}", file=sys.stderr)
        sys.exit(1)
