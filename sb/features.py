"""Feature extraction utilities for the intelligent SmartBugs workflow."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import Any


class FeatureExtractionError(RuntimeError):
    """Raised when feature extraction fails."""


def extract_features(
    contract_path: str | Path,
    extractor_dir: str | Path = "external/SCsVulLyzer",
) -> dict[str, Any]:
    """Extract features from a Solidity contract using SCsVulLyzer.

    Args:
        contract_path: Path to the Solidity contract to analyze.
        extractor_dir: Path to the SCsVulLyzer project directory.

    Returns:
        A dictionary containing the extracted features.

    Raises:
        FeatureExtractionError: If the input file does not exist, SCsVulLyzer
        cannot be executed, or its output cannot be parsed.
    """
    contract = Path(contract_path)
    extractor = Path(extractor_dir)
    main_file = extractor / "main.py"
    if not contract.exists():
        raise FeatureExtractionError(f"Contract file not found: {contract}")
    if not main_file.exists():
        raise FeatureExtractionError(f"SCsVulLyzer main.py not found: {main_file}")
    result = subprocess.run(
        [sys.executable, str(main_file), str(contract)],
        cwd=str(extractor),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise FeatureExtractionError(
            f"SCsVulLyzer failed with exit code {result.returncode}: {result.stderr}"
        )
    return parse_feature_output(result.stdout)


def parse_feature_output(output: str) -> dict[str, Any]:
    """Parse SCsVulLyzer stdout into a feature dictionary."""
    text = output.strip()
    if not text:
        raise FeatureExtractionError("SCsVulLyzer produced empty output.")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise FeatureExtractionError("SCsVulLyzer output does not contain a feature dictionary.")
    dictionary_text = text[start : end + 1]
    try:
        features = ast.literal_eval(dictionary_text)
    except (SyntaxError, ValueError) as exc:
        raise FeatureExtractionError("Unable to parse SCsVulLyzer output.") from exc
    if not isinstance(features, dict):
        raise FeatureExtractionError("SCsVulLyzer output is not a dictionary.")
    return features