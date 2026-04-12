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


class UsageAnalyzer(ast.NodeVisitor):
    def __init__(self, current_module: str, core_modules: list[str]):
        self.current_module = current_module
        self.core_modules = core_modules
        self.import_aliases = {}
        self.from_imports = {}
        self.counts = {m: 0 for m in core_modules}

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.name
            asname = alias.asname or name
            if name.startswith("sb."):
                parts = name.split(".")
                if len(parts) >= 2:
                    mod = parts[1]
                    if mod in self.core_modules:
                        self.import_aliases[asname] = mod
                        self.counts[mod] += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.startswith("sb."):
            parts = node.module.split(".")
            if len(parts) >= 2:
                mod = parts[1]
                if mod in self.core_modules:
                    self.counts[mod] += 1
                    for alias in node.names:
                        asname = alias.asname or alias.name
                        self.from_imports[asname] = mod
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # e.g. sb.tools.load or alias.load
        if isinstance(node.value, ast.Name):
            base = node.value.id
            if base in self.import_aliases:
                mod = self.import_aliases[base]
                self.counts[mod] += 1
            elif base == "sb":
                # handles patterns like sb.tools.load
                pass
        elif isinstance(node.value, ast.Attribute):
            # handles sb.tools.load
            chain = []
            cur = node
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name) and cur.id == "sb":
                if chain:
                    mod = chain[-1]
                    if mod in self.core_modules:
                        self.counts[mod] += 1
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in self.from_imports:
            mod = self.from_imports[node.id]
            self.counts[mod] += 1
        self.generic_visit(node)


def analyze_file(py_file: Path, core_modules: list[str]) -> dict[str, int]:
    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_file))
    analyzer = UsageAnalyzer(py_file.stem, core_modules)
    analyzer.visit(tree)
    return analyzer.counts


def main():
    matrix = {}
    for mod in CORE_MODULES:
        py_file = ROOT / f"{mod}.py"
        if py_file.exists():
            matrix[mod] = analyze_file(py_file, CORE_MODULES)

    csv_path = Path("dependency_matrix_usage.csv")
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