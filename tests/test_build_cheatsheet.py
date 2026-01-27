from pathlib import Path

import astranotes.build_cheatsheet as bc


def test_generate_latex_writes_tex_to_tempdir(tmp_path: Path, monkeypatch):
    # Redirect build outputs to a temp directory
    monkeypatch.setattr(bc, "BUILD_DIR", str(tmp_path))
    monkeypatch.setattr(bc, "TEX_FILENAME", "test_cheatsheet.tex")
    monkeypatch.setattr(bc, "TEX_PATH", str(tmp_path / "test_cheatsheet.tex"))

    # Ensure dir exists and generate
    bc.ensure_build_dir()
    bc.generate_latex()

    out_path = tmp_path / "test_cheatsheet.tex"
    assert out_path.exists()

    text = out_path.read_text(encoding="utf-8")
    assert r"\documentclass" in text
    assert r"\begin{document}" in text
    assert r"\end{document}" in text
    assert r"\section*{Sources}" in text
