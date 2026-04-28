from pathlib import Path
from unittest.mock import MagicMock

import pytest

from sb.features import FeatureExtractionError, extract_features, parse_feature_output


def test_parse_feature_output_dictionary() -> None:
    output = "{'Number of total_lines': 10, 'Solidity call': 2}"

    features = parse_feature_output(output)

    assert features["Number of total_lines"] == 10
    assert features["Solidity call"] == 2


def test_parse_feature_output_with_extra_text() -> None:
    output = "Some log\n{'Number of total_lines': 10}\nDone"

    features = parse_feature_output(output)

    assert features == {"Number of total_lines": 10}


def test_parse_feature_output_empty() -> None:
    with pytest.raises(FeatureExtractionError):
        parse_feature_output("")


def test_parse_feature_output_invalid_dictionary() -> None:
    with pytest.raises(FeatureExtractionError):
        parse_feature_output("not a dictionary")


def test_extract_features_missing_contract(tmp_path: Path) -> None:
    extractor_dir = tmp_path / "SCsVulLyzer"
    extractor_dir.mkdir()
    (extractor_dir / "main.py").write_text("print({})", encoding="utf-8")

    with pytest.raises(FeatureExtractionError):
        extract_features(tmp_path / "missing.sol", extractor_dir)


def test_extract_features_missing_extractor(tmp_path: Path) -> None:
    contract = tmp_path / "Test.sol"
    contract.write_text("pragma solidity ^0.8.0; contract Test {}", encoding="utf-8")

    with pytest.raises(FeatureExtractionError):
        extract_features(contract, tmp_path / "missing_extractor")


def test_extract_features_success(tmp_path: Path, mocker) -> None:
    contract = tmp_path / "Test.sol"
    contract.write_text("pragma solidity ^0.8.0; contract Test {}", encoding="utf-8")

    extractor_dir = tmp_path / "SCsVulLyzer"
    extractor_dir.mkdir()
    (extractor_dir / "main.py").write_text("", encoding="utf-8")

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="{'Number of total_lines': 10, 'Solidity call': 1}",
        stderr="",
    )

    features = extract_features(contract, extractor_dir)

    assert features["Number of total_lines"] == 10
    assert features["Solidity call"] == 1


def test_extract_features_command_failure(tmp_path: Path, mocker) -> None:
    contract = tmp_path / "Test.sol"
    contract.write_text("pragma solidity ^0.8.0; contract Test {}", encoding="utf-8")

    extractor_dir = tmp_path / "SCsVulLyzer"
    extractor_dir.mkdir()
    (extractor_dir / "main.py").write_text("", encoding="utf-8")

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout="",
        stderr="Compilation failed",
    )

    with pytest.raises(FeatureExtractionError):
        extract_features(contract, extractor_dir)