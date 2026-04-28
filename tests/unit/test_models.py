from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from sb.models import (
    ModelSelectionError,
    aggregate_predictions,
    load_model,
    predict_tool,
    predict_tools,
    select_required_features,
    select_tools_from_models,
    REQUIRED_FEATURES
)


def test_select_required_features_success() -> None:
    features = {
        "feature_a": 1,
        "feature_b": 2,
        "feature_c": 3,
    }
    required_features = ["feature_a", "feature_c"]

    feature_row = select_required_features(features, required_features)

    assert isinstance(feature_row, pd.DataFrame)
    assert list(feature_row.columns) == required_features
    assert feature_row.iloc[0]["feature_a"] == 1
    assert feature_row.iloc[0]["feature_c"] == 3


def test_select_required_features_missing_feature() -> None:
    features = {
        "feature_a": 1,
    }
    required_features = ["feature_a", "feature_b"]

    with pytest.raises(ModelSelectionError):
        select_required_features(features, required_features)


def test_load_model_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ModelSelectionError):
        load_model(tmp_path / "missing.joblib")


def test_load_model_success(tmp_path: Path, mocker) -> None:
    model_file = tmp_path / "model.joblib"
    model_file.write_text("fake model", encoding="utf-8")

    fake_model = MagicMock()
    mock_load = mocker.patch("sb.models.joblib.load")
    mock_load.return_value = fake_model

    model = load_model(model_file)

    assert model is fake_model
    mock_load.assert_called_once_with(model_file)


def test_load_model_failure(tmp_path: Path, mocker) -> None:
    model_file = tmp_path / "model.joblib"
    model_file.write_text("fake model", encoding="utf-8")

    mock_load = mocker.patch("sb.models.joblib.load")
    mock_load.side_effect = RuntimeError("cannot load")

    with pytest.raises(ModelSelectionError):
        load_model(model_file)


def test_predict_tool_success() -> None:
    model = MagicMock()
    model.predict.return_value = ["slither"]
    feature_row = pd.DataFrame([{"feature_a": 1}])

    prediction = predict_tool(model, feature_row)

    assert prediction == "slither"


def test_predict_tool_empty_prediction() -> None:
    model = MagicMock()
    model.predict.return_value = []
    feature_row = pd.DataFrame([{"feature_a": 1}])

    with pytest.raises(ModelSelectionError):
        predict_tool(model, feature_row)


def test_predict_tool_failure() -> None:
    model = MagicMock()
    model.predict.side_effect = RuntimeError("prediction error")
    feature_row = pd.DataFrame([{"feature_a": 1}])

    with pytest.raises(ModelSelectionError):
        predict_tool(model, feature_row)


def test_predict_tools_multiple_models() -> None:
    model_a = MagicMock()
    model_a.predict.return_value = ["slither"]

    model_b = MagicMock()
    model_b.predict.return_value = ["mythril"]

    feature_row = pd.DataFrame([{"feature_a": 1}])

    predictions = predict_tools([model_a, model_b], feature_row)

    assert predictions == ["slither", "mythril"]


def test_aggregate_predictions_removes_duplicates() -> None:
    predictions = ["slither", "slither", "mythril"]

    selected_tools = aggregate_predictions(predictions)

    assert selected_tools == ["slither", "mythril"]


def test_aggregate_predictions_removes_no_tool() -> None:
    predictions = ["nessun_tool", "slither", "nessun_tool"]

    selected_tools = aggregate_predictions(predictions)

    assert selected_tools == ["slither"]


def test_aggregate_predictions_removes_unknown_tools() -> None:
    predictions = ["slither", "unknown_tool", "mythril"]
    supported_tools = {"slither", "mythril"}

    selected_tools = aggregate_predictions(predictions, supported_tools)

    assert selected_tools == ["slither", "mythril"]


def test_aggregate_predictions_returns_empty_list() -> None:
    predictions = ["nessun_tool", "", "unknown_tool"]
    supported_tools = {"slither", "mythril"}

    selected_tools = aggregate_predictions(predictions, supported_tools)

    assert selected_tools == []


def test_select_tools_from_models_success(tmp_path: Path, mocker) -> None:
    model_a_path = tmp_path / "model_a.joblib"
    model_b_path = tmp_path / "model_b.joblib"
    model_a_path.write_text("fake model", encoding="utf-8")
    model_b_path.write_text("fake model", encoding="utf-8")

    model_a = MagicMock()
    model_a.predict.return_value = ["slither"]

    model_b = MagicMock()
    model_b.predict.return_value = ["slither"]

    mock_load = mocker.patch("sb.models.joblib.load")
    mock_load.side_effect = [model_a, model_b]

    features = {
        "feature_a": 1,
        "feature_b": 2,
    }

    selected_tools = select_tools_from_models(
        features=features,
        model_paths=[model_a_path, model_b_path],
        supported_tools={"slither", "mythril"},
        required_features=["feature_a", "feature_b"],
    )

    assert selected_tools == ["slither"]


def test_required_features_contains_41_features() -> None:
    assert len(REQUIRED_FEATURES) == 41
    assert "AST Features_ast_id" in REQUIRED_FEATURES
    assert "Opcode Count Features_SWAP4" in REQUIRED_FEATURES