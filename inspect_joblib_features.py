from pathlib import Path
import joblib

MODELS_DIR = Path("models/ML_models")

def print_attrs(obj, prefix=""):
    interesting_attrs = [
        "feature_names_in_",
        "n_features_in_",
        "classes_",
        "steps",
        "named_steps",
    ]

    for attr in interesting_attrs:
        if hasattr(obj, attr):
            value = getattr(obj, attr)
            print(f"{prefix}{attr}: {value}")

def inspect_model(path: Path):
    print("=" * 100)
    print(f"MODEL: {path}")
    print("=" * 100)

    model = joblib.load(path)

    print(f"Type: {type(model)}")
    print_attrs(model)

    if hasattr(model, "steps"):
        print("\nPipeline steps:")
        for name, step in model.steps:
            print(f"\nStep: {name}")
            print(f"Type: {type(step)}")
            print_attrs(step, prefix="  ")

    if hasattr(model, "named_steps"):
        print("\nNamed steps:")
        for name, step in model.named_steps.items():
            print(f"\nNamed step: {name}")
            print(f"Type: {type(step)}")
            print_attrs(step, prefix="  ")

    print("\n")

def main():
    model_paths = sorted(MODELS_DIR.rglob("*.joblib"))

    if not model_paths:
        print(f"No .joblib files found in {MODELS_DIR.resolve()}")
        return

    for path in model_paths:
        inspect_model(path)

if __name__ == "__main__":
    main()