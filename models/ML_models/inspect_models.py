from pathlib import Path
from joblib import load

root = Path(".")

for folder in sorted(root.iterdir()):
    if not folder.is_dir():
        continue

    print(f"\n=== {folder.name} ===")

    joblibs = list(folder.glob("*.joblib"))
    if not joblibs:
        print("No .joblib files found")
        continue

    for model_path in joblibs:
        print(f"\nModel file: {model_path.name}")
        try:
            model = load(model_path)
            print("Type:", type(model))

            if hasattr(model, "n_features_in_"):
                print("n_features_in_:", model.n_features_in_)

            if hasattr(model, "feature_names_in_"):
                print("feature_names_in_:", list(model.feature_names_in_))

            if hasattr(model, "classes_"):
                print("classes_:", list(model.classes_))

        except Exception as e:
            print("Error loading model:", e)