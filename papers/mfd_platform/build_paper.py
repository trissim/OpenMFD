#!/usr/bin/env python3
"""OpenMFD declares scientific sources locally and imports shared build owners."""
from dataclasses import dataclass
from pathlib import Path

from paper_build.artifacts import InputObservations
from paper_build.cli import main
from paper_build.declarations import DocumentDefinition, DocumentRole, PaperDefinition, Preparation
from paper_build.evidence import ReceiptCoverage
from paper_build.word import CaptionedFiguresLayout, EndTextFiguresLayout

ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class MfdRetainedFigures(Preparation):
    def image_resource(self, root: Path, path: Path) -> Path:
        if path.suffix.lower() != '.pdf':
            return path
        if path.parent != root / 'figures/rendered':
            raise ValueError(f'No retained document projection is declared for {path}')
        return root / 'figures/rendered_docx' / (path.stem + '.png')

    def resolve(self, root: Path, figures: tuple[Path, ...], observations: InputObservations) -> tuple[str, ...]:
        for path in (root / 'build_docx.py', root / 'requirements-build.txt',
                     root / 'figures/render_figures.py', *sorted((root / 'figures').glob('generate_*.py'))):
            observations.read(path)
        coverage = ReceiptCoverage.discover(root / 'figures', figures, root, observations)
        return (*coverage.validate(observations),
                'Existing PDF/PNG document assets are reused; no scientific analysis or figure regeneration was launched.')

    def refresh(self, root: Path) -> None:
        raise RuntimeError('OpenMFD figure generators consume authoring/external evidence and may clean rendered outputs. No safe automatic refresh is declared; follow README.md separately.')


SUPPLEMENT = DocumentDefinition(
    DocumentRole.SUPPLEMENT,
    sources=(
        Path('supplementary/Supplementary_Table_S1_pin_z_variability.md'),
        Path('supplementary/Supplementary_Table_S2_fabrication_strategies.md'),
        Path('supplementary/Supplementary_Table_S3_design_limits.md'),
        Path('supplementary/Supplementary_Table_S4_resin_insert_printing_settings.md'),
        Path('supplementary/Supplementary_Table_S5_process_qc.md'),
        Path('supplementary/Supplementary_Table_S6_FDM_frame_printing_settings.md'),
        Path('supplementary/Supplementary_Note_S1_LP360_filter.md'),
        Path('supplementary/Supplementary_Note_S2_base_layer_adhesion.md'),
        Path('supplementary/Supplementary_Protocol_S1_device_assembly_culture_and_CTB.md'),
        Path('supplementary/Supplementary_Protocol_S2_hybrid_mold_fabrication.md'),
    ),
    layout=CaptionedFiguresLayout(), markdown_format='markdown', citeproc=False,
    section_heading='Supplementary Information',
)

PAPER = PaperDefinition(
    identity='openmfd-platform', root=ROOT, declaration=Path(__file__).resolve(),
    documents=(DocumentDefinition(DocumentRole.MANUSCRIPT, (Path('manuscript.md'),),
                                  layout=EndTextFiguresLayout(boundary_heading=SUPPLEMENT.section_heading),
                                  markdown_format='markdown', citeproc=False), SUPPLEMENT),
    preparation=MfdRetainedFigures(), combined_review=True,
)

if __name__ == '__main__':
    raise SystemExit(main(PAPER))
