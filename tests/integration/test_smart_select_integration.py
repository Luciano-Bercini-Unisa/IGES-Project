from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import joblib
import pandas as pd

import sb.cfg
import sb.smartbugs
from sb.settings import Settings


class FakeModel:
    def __init__(self, prediction: str) -> None:
        self.prediction = prediction

    def predict(self, feature_row: pd.DataFrame) -> list[str]:
        return [self.prediction]


def make_required_features() -> dict[str, int]:
    return {
        "AST Features_ast_id": 1,
        "AST Features_ast_len_exportedSymbols": 1,
        "AST Features_ast_len_nodes": 1,
        "Opcode Count Features_ADD": 1,
        "Opcode Count Features_AND": 1,
        "Opcode Count Features_CALLCODE": 0,
        "Opcode Count Features_CALLDATALOAD": 1,
        "Opcode Count Features_CALLDATASIZE": 1,
        "Opcode Count Features_CALLER": 1,
        "Opcode Count Features_DIV": 0,
        "Opcode Count Features_DUP1": 1,
        "Opcode Count Features_DUP2": 1,
        "Opcode Count Features_DUP3": 1,
        "Opcode Count Features_DUP4": 1,
        "Opcode Count Features_DUP5": 1,
        "Opcode Count Features_DUP6": 1,
        "Opcode Count Features_DUP7": 1,
        "Opcode Count Features_EQ": 1,
        "Opcode Count Features_EXP": 0,
        "Opcode Count Features_EXTCODECOPY": 0,
        "Opcode Count Features_ISZERO": 1,
        "Opcode Count Features_JUMP": 1,
        "Opcode Count Features_JUMPDEST": 1,
        "Opcode Count Features_JUMPI": 1,
        "Opcode Count Features_MLOAD": 1,
        "Opcode Count Features_MSTORE": 1,
        "Opcode Count Features_POP": 1,
        "Opcode Count Features_PUSH1": 1,
        "Opcode Count Features_PUSH2": 1,
        "Opcode Count Features_PUSH20": 1,
        "Opcode Count Features_PUSH4": 1,
        "Opcode Count Features_RETURN": 1,
        "Opcode Count Features_REVERT": 1,
        "Opcode Count Features_SLOAD": 1,
        "Opcode Count Features_SSTORE": 1,
        "Opcode Count Features_STOP": 1,
        "Opcode Count Features_SUB": 1,
        "Opcode Count Features_SWAP1": 1,
        "Opcode Count Features_SWAP2": 1,
        "Opcode Count Features_SWAP3": 1,
        "Opcode Count Features_SWAP4": 1,
    }


class TestSmartSelectIntegration:
    def test_select_tools_intelligently_with_real_extractor_and_models(
        self,
        tmp_path: Path,
        monkeypatch,
    ) -> None:
        contract_file = tmp_path / "Test.sol"
        contract_file.write_text("pragma solidity ^0.8.0; contract Test {}", encoding="utf-8")

        features = make_required_features()

        extractor_dir = tmp_path / "extractor"
        extractor_dir.mkdir()

        main_py = extractor_dir / "main.py"
        main_py.write_text(
            "import sys\n"
            f"print({features!r})\n",
            encoding="utf-8",
        )

        models_root = tmp_path / "models" / "ML_models"
        swc1 = models_root / "swc_101"
        swc2 = models_root / "swc_107"
        swc1.mkdir(parents=True)
        swc2.mkdir(parents=True)

        joblib.dump(FakeModel("slither-0.10.4"), swc1 / "best_model.joblib")
        joblib.dump(FakeModel("smartcheck"), swc2 / "best_model.joblib")

        tools_home = tmp_path / "tools"
        (tools_home / "slither").mkdir(parents=True)
        (tools_home / "smartcheck").mkdir(parents=True)

        monkeypatch.setattr(sb.cfg, "TOOLS_HOME", str(tools_home))

        settings = Settings()
        settings.feature_extractor = str(extractor_dir)
        settings.model_paths = [str(models_root / "*" / "best_model.joblib")]

        selected_tools = sb.smartbugs.select_tools_intelligently(
            [(str(contract_file), "Test.sol")],
            settings,
        )

        assert selected_tools == ["slither", "smartcheck"]


class TestMainSmartSelectIntegration:
    @patch("sb.analysis.run")
    @patch("sb.smartbugs.collect_tasks")
    @patch("sb.tools.load")
    def test_main_runs_intelligent_selection_before_task_collection(
        self,
        mock_load_tools: MagicMock,
        mock_collect_tasks: MagicMock,
        mock_analysis_run: MagicMock,
        tmp_path: Path,
        monkeypatch,
    ) -> None:
        contract_file = tmp_path / "Test.sol"
        contract_file.write_text("pragma solidity ^0.8.0; contract Test {}", encoding="utf-8")

        features = make_required_features()

        extractor_dir = tmp_path / "extractor"
        extractor_dir.mkdir()
        (extractor_dir / "main.py").write_text(
            "import sys\n"
            f"print({features!r})\n",
            encoding="utf-8",
        )

        models_root = tmp_path / "models" / "ML_models"
        swc1 = models_root / "swc_101"
        swc1.mkdir(parents=True)
        joblib.dump(FakeModel("smartcheck"), swc1 / "best_model.joblib")

        tools_home = tmp_path / "tools"
        (tools_home / "smartcheck").mkdir(parents=True)
        monkeypatch.setattr(sb.cfg, "TOOLS_HOME", str(tools_home))

        mock_tool = MagicMock()
        mock_tool.id = "smartcheck"
        mock_load_tools.return_value = [mock_tool]

        mock_task = MagicMock()
        mock_collect_tasks.return_value = [mock_task]

        settings = Settings()
        settings.files = [(None, str(contract_file))]
        settings.smart_select = True
        settings.feature_extractor = str(extractor_dir)
        settings.model_paths = [str(models_root / "*" / "best_model.joblib")]
        settings.quiet = True

        sb.smartbugs.main(settings)

        assert settings.tools == ["smartcheck"]
        mock_load_tools.assert_called_once_with(["smartcheck"])
        mock_collect_tasks.assert_called_once()
        mock_analysis_run.assert_called_once_with([mock_task], settings)