import ast
import csv
from pathlib import Path

ROOT = Path("sb")

CORE_MODULES = [
    "cli",
    "settings",
    "smartbugs",
    "tools",
    "tasks",
    "analysis",
    "docker",
    "solidity",
]


def count_dependencies(py_file: Path, core_modules: list[str]) -> dict[str, int]:
    counts = {m: 0 for m in core_modules}
    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_file))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("sb."):
                    mod = name.split(".")[1]
                    if mod in counts:
                        counts[mod] += 1

        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("sb."):
                mod = node.module.split(".")[1]
                if mod in counts:
                    counts[mod] += 1

    return counts


def main():
    matrix = {}
    for mod in CORE_MODULES:
        py_file = ROOT / f"{mod}.py"
        if not py_file.exists():
            continue
        matrix[mod] = count_dependencies(py_file, CORE_MODULES)

    csv_path = Path("dependency_matrix.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Module"] + CORE_MODULES)
        for row_mod in CORE_MODULES:
            row = [row_mod]
            for col_mod in CORE_MODULES:
                row.append(matrix.get(row_mod, {}).get(col_mod, 0))
            writer.writerow(row)

    print(f"Dependency matrix written to {csv_path}")
    print()

    header = ["Module"] + CORE_MODULES
    print("\t".join(header))
    for row_mod in CORE_MODULES:
        values = [str(matrix.get(row_mod, {}).get(col_mod, 0)) for col_mod in CORE_MODULES]
        print("\t".join([row_mod] + values))


if __name__ == "__main__":
    main()