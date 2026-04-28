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
    contract = Path(contract_path).resolve()
    extractor = Path(extractor_dir).resolve()
    main_file = extractor / "main.py"
    if not contract.exists():
        raise FeatureExtractionError(f"Contract file not found: {contract}")
    if not main_file.exists():
        raise FeatureExtractionError(f"SCsVulLyzer main.py not found: {main_file}")
    result = subprocess.run(
        [sys.executable, "main.py", str(contract)],
        cwd=str(extractor),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise FeatureExtractionError(
            f"SCsVulLyzer failed with exit code {result.returncode} "
            f"using Python interpreter {sys.executable}: {result.stderr}"
        )
    return parse_feature_output(result.stdout)


def parse_feature_output(output: str) -> dict[str, Any]:
    """Parse SCsVulLyzer stdout into a feature dictionary."""
    text = output.strip()
    if not text:
        raise FeatureExtractionError("SCsVulLyzer produced empty output.")
    if "{" in text and "}" in text:
        return _parse_dictionary_output(text)
    return _parse_key_value_output(text)


def _parse_dictionary_output(output: str) -> dict[str, Any]:
    start = output.find("{")
    end = output.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise FeatureExtractionError("SCsVulLyzer output does not contain a feature dictionary.")
    dictionary_text = output[start : end + 1]
    try:
        features = ast.literal_eval(dictionary_text)
    except (SyntaxError, ValueError) as exc:
        raise FeatureExtractionError("Unable to parse SCsVulLyzer output.") from exc
    if not isinstance(features, dict):
        raise FeatureExtractionError("SCsVulLyzer output is not a dictionary.")
    return features


def _parse_key_value_output(output: str) -> dict[str, Any]:
    features: dict[str, Any] = {}
    for line in output.splitlines():
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        features[key] = _parse_feature_value(value)
    if not features:
        raise FeatureExtractionError("SCsVulLyzer output does not contain parseable features.")
    return features


def _parse_feature_value(value: str) -> Any:
    if value == "":
        return value
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value