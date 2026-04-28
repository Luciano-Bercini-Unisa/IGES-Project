"""Machine learning utilities for intelligent SmartBugs tool selection."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import joblib
import pandas as pd

REQUIRED_FEATURES = [
    "AST Features_ast_id",
    "AST Features_ast_len_exportedSymbols",
    "AST Features_ast_len_nodes",
    "Opcode Count Features_ADD",
    "Opcode Count Features_AND",
    "Opcode Count Features_CALLCODE",
    "Opcode Count Features_CALLDATALOAD",
    "Opcode Count Features_CALLDATASIZE",
    "Opcode Count Features_CALLER",
    "Opcode Count Features_DIV",
    "Opcode Count Features_DUP1",
    "Opcode Count Features_DUP2",
    "Opcode Count Features_DUP3",
    "Opcode Count Features_DUP4",
    "Opcode Count Features_DUP5",
    "Opcode Count Features_DUP6",
    "Opcode Count Features_DUP7",
    "Opcode Count Features_EQ",
    "Opcode Count Features_EXP",
    "Opcode Count Features_EXTCODECOPY",
    "Opcode Count Features_ISZERO",
    "Opcode Count Features_JUMP",
    "Opcode Count Features_JUMPDEST",
    "Opcode Count Features_JUMPI",
    "Opcode Count Features_MLOAD",
    "Opcode Count Features_MSTORE",
    "Opcode Count Features_POP",
    "Opcode Count Features_PUSH1",
    "Opcode Count Features_PUSH2",
    "Opcode Count Features_PUSH20",
    "Opcode Count Features_PUSH4",
    "Opcode Count Features_RETURN",
    "Opcode Count Features_REVERT",
    "Opcode Count Features_SLOAD",
    "Opcode Count Features_SSTORE",
    "Opcode Count Features_STOP",
    "Opcode Count Features_SUB",
    "Opcode Count Features_SWAP1",
    "Opcode Count Features_SWAP2",
    "Opcode Count Features_SWAP3",
    "Opcode Count Features_SWAP4",
]

NO_TOOL = "nessun_tool"


class ModelSelectionError(RuntimeError):
    """Raised when model-based tool selection fails."""


def select_required_features(
    features: dict[str, Any],
    required_features: list[str],
) -> pd.DataFrame:
    """Select the subset of features required by the ML models.

    Args:
        features: Dictionary produced by the feature extraction module.
        required_features: Ordered list of feature names expected by the models.

    Returns:
        A single-row pandas DataFrame containing only the required features.

    Raises:
        ModelSelectionError: If one or more required features are missing.
    """
    missing_features = [
        feature for feature in required_features
        if feature not in features
    ]
    if missing_features:
        raise ModelSelectionError(
            f"Missing required features: {', '.join(missing_features)}"
        )
    selected_features = {
        feature: features[feature]
        for feature in required_features
    }
    return pd.DataFrame([selected_features], columns=required_features)


def load_model(model_path: str | Path) -> Any:
    """Load a serialized machine learning model.

    Args:
        model_path: Path to a .joblib model file.

    Returns:
        Loaded model object.

    Raises:
        ModelSelectionError: If the model file does not exist or cannot be loaded.
    """
    path = Path(model_path)
    if not path.exists():
        raise ModelSelectionError(f"Model file not found: {path}")
    try:
        return joblib.load(path)
    except Exception as exc:
        raise ModelSelectionError(f"Unable to load model: {path}") from exc


def predict_tool(model: Any, feature_row: pd.DataFrame) -> str:
    """Predict the most suitable SmartBugs tool using one model.

    Args:
        model: Loaded ML model.
        feature_row: Single-row DataFrame with the required features.

    Returns:
        Predicted tool name.

    Raises:
        ModelSelectionError: If prediction fails or has an invalid shape.
    """
    try:
        prediction = model.predict(feature_row)
    except Exception as exc:
        raise ModelSelectionError("Model prediction failed.") from exc
    if prediction is None or len(prediction) == 0:
        raise ModelSelectionError("Model returned an empty prediction.")
    return str(prediction[0])


def predict_tools(
    models: Iterable[Any],
    feature_row: pd.DataFrame,
) -> list[str]:
    """Execute multiple models and collect their predicted tools."""
    return [
        predict_tool(model, feature_row)
        for model in models
    ]


def aggregate_predictions(
    predictions: Iterable[str],
    supported_tools: set[str] | None = None,
) -> list[str]:
    """Aggregate and filter model predictions.

    This function removes:
    - empty predictions;
    - 'nessun_tool';
    - unknown tools, if supported_tools is provided;
    - duplicates, preserving prediction order.

    Args:
        predictions: Tool names predicted by the ML models.
        supported_tools: Optional set of valid SmartBugs tool identifiers.

    Returns:
        Ordered list of selected tools.
    """
    selected_tools: list[str] = []
    seen_tools: set[str] = set()
    for prediction in predictions:
        tool = str(prediction).strip()
        if not tool:
            continue
        if tool == NO_TOOL:
            continue
        if supported_tools is not None and tool not in supported_tools:
            continue
        if tool in seen_tools:
            continue
        selected_tools.append(tool)
        seen_tools.add(tool)
    return selected_tools


def select_tools_from_models(
    features: dict[str, Any],
    model_paths: Iterable[str | Path],
    supported_tools: set[str] | None = None,
    required_features: list[str] | None = None,
) -> list[str]:
    """Select SmartBugs tools using extracted features and ML models.

    Args:
        features: Extracted feature dictionary.
        required_features: Ordered list of features expected by the models.
        model_paths: Paths to .joblib model files.
        supported_tools: Optional set of supported SmartBugs tools.

    Returns:
        Final list of selected tools.
    """
    feature_names = required_features or REQUIRED_FEATURES
    feature_row = select_required_features(features, feature_names)
    models = [
        load_model(path)
        for path in model_paths
    ]
    predictions = predict_tools(models, feature_row)
    return aggregate_predictions(predictions, supported_tools)