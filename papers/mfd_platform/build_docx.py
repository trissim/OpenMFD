#!/usr/bin/env python3
"""Temporary legacy command: delegate to the one paired/combined build owner."""
import argparse

from paper_build.cli import main as shared_main
from paper_build.declarations import DocumentRole
from paper_build.word import CAPTION_FONT_SIZE_PT, WORD_DOCUMENT_XML, WORD_NAMESPACE, fit_docx_figures, word_tag
from build_paper import PAPER

# Compatibility is a bound reference to the actual declared layout owner.
move_main_figures_after_text = PAPER.document(DocumentRole.MANUSCRIPT).layout.move_figures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Compatibility build; outputs now live in current/.')
    parser.add_argument('--skip-figures', action='store_true', help='Retained for compatibility; ordinary builds always reuse retained figures.')
    args = parser.parse_args(argv)
    return shared_main(PAPER, ['build'])


if __name__ == '__main__':
    raise SystemExit(main())
