from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import pytest

from paper_build.artifacts import InputObservations, sha256_bytes
from paper_build.build import MarkdownDocumentBuilder, resolve_inputs
from paper_build.declarations import DocumentRole
from paper_build.process import BuildLog
from paper_build.word import fit_docx_figures
from build_paper import PAPER


def test_scientific_source_and_figure_bytes_preserved_after_rename():
    archive = PAPER.root / 'build/refactor-inputs-before-cutover-20260915'
    if not (archive / 'inputs.json').is_file():
        pytest.skip('Local frozen cutover evidence is not distributed; portable owner tests remain active')
    records = json.loads((archive / 'inputs.json').read_text())
    for relative, digest in records.items():
        if relative.endswith('.py'):
            continue
        path = PAPER.root / ('manuscript.md' if relative == 'paper.md' else relative)
        assert sha256_bytes(path.read_bytes()) == digest
    assert 'sole editable manuscript' in (PAPER.root / 'paper.md').read_text()


def test_combined_order_and_heading_have_one_authority(tmp_path):
    resolved, checks = resolve_inputs(PAPER, MarkdownDocumentBuilder(), BuildLog(tmp_path / 'log'), InputObservations())
    assert tuple(item.definition.role for item in resolved) == (DocumentRole.MANUSCRIPT, DocumentRole.SUPPLEMENT, DocumentRole.REVIEW)
    assert len(PAPER.documents) == 2
    assert resolved[-1].inputs.sections == resolved[0].inputs.sections + resolved[1].inputs.sections
    assert '7 document figures' in checks[0] and '14 retained outputs' in checks[0]
    assert PAPER.document(DocumentRole.MANUSCRIPT).layout.boundary_heading == PAPER.document(DocumentRole.SUPPLEMENT).section_heading


def test_missing_projected_asset_fails_without_renderer_fallback(tmp_path, monkeypatch):
    original = Path.read_bytes
    missing = PAPER.root / 'figures/rendered_docx/openmfd_design.png'
    def read(path):
        if path == missing:
            raise FileNotFoundError(path)
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', read)
    with pytest.raises(FileNotFoundError):
        resolve_inputs(PAPER, MarkdownDocumentBuilder(), BuildLog(tmp_path / 'log'), InputObservations())


def test_missing_supplement_fails_instead_of_silent_omission(tmp_path, monkeypatch):
    original = Path.read_bytes
    missing = PAPER.root / PAPER.document(DocumentRole.SUPPLEMENT).sources[-1]
    def read(path):
        if path == missing:
            raise FileNotFoundError(path)
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', read)
    with pytest.raises(FileNotFoundError):
        resolve_inputs(PAPER, MarkdownDocumentBuilder(), BuildLog(tmp_path / 'log'), InputObservations())


def test_compatibility_shim_imports_actual_owners():
    import build_docx
    assert build_docx.fit_docx_figures is fit_docx_figures
    assert build_docx.move_main_figures_after_text.__self__ is PAPER.document(DocumentRole.MANUSCRIPT).layout


def test_refresh_is_explicitly_unsupported():
    with pytest.raises(RuntimeError, match='No safe automatic refresh'):
        PAPER.preparation.refresh(PAPER.root)
