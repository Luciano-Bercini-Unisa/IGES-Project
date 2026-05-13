from pathlib import Path

import sb.cli

# Test CLI integration with Settings on the new flags (smart_select, feature_extractor, model_paths).
class TestCliIntegration:
    def test_cli_parses_smart_select_arguments(self, monkeypatch, tmp_path: Path) -> None:
        extractor_dir = tmp_path / "SCsVulLyzer-V2.0"
        extractor_dir.mkdir()

        model_pattern = str(tmp_path / "models" / "*" / "best_model.joblib")

        monkeypatch.setattr(
            "sys.argv",
            [
                "smartbugs",
                "--smart-select",
                "--feature-extractor",
                str(extractor_dir),
                "--model-paths",
                model_pattern,
                "-f",
                "samples/**/*.sol",
                "--continue-on-errors",
            ],
        )

        settings = sb.cli.cli(site_cfg=None)

        assert settings.smart_select is True
        assert settings.feature_extractor == str(extractor_dir)
        assert settings.model_paths == [model_pattern]
        assert settings.files == [(None, "samples/**/*.sol")]
        assert settings.continue_on_errors is True