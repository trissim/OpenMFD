# Published document figures

The manuscript uses the PDFs in this directory and the matching PNGs in
`../rendered_docx/`. Ordinary document builds reuse these outputs; they do not
regenerate scientific figures.

`FigureRenderSpec` in `../render_figures.py` owns each published PDF/PNG pair.
Retained supplement pairs are verified in place.
`AuthoredFigure` owns the source basename and copying an existing authored pair.
`GeneratedFigure` inherits that behavior and additionally owns a producer script.
The apparent-width figure uses `AuthoredFigure`: publication never runs the
validation renderer. Shared
`publish()` requires both formats before writing either. The manuscript sequence
supplies the order; there is no separate generator roster.

Historical ODPs remain preserved as authoring history. They are not publication
inputs, and file timestamps never select or re-export them over a scripted PDF.
Publication does not delete unrelated files.

## Explicit authoring and publication

After reviewing the relevant scientific inputs, run the figure's declared
producer on the desktop. Then publish only the reviewed figure specification:

```python
from render_figures import FIGURE_SPECS

spec = next(s for s in FIGURE_SPECS if s.rendered_name == "openmfd_design.pdf")
spec.publish()
```

Update the figure's existing provenance receipt with the actual output/source
hashes and runtime versions, then rebuild and inspect the reading copies.

The full `python papers/mfd_platform/figures/render_figures.py` command runs every
declared producer. Figure 4's producer reads the original count/image/outline
files without new segmentation; the author-confirmed selection is 67 devices.
It redraws Figure 4 only, leaving the retained apparent-width pair untouched.
The restored source still needs its explicit render, publication and placed-page
inspection; exact historical analysis-run configuration and ethics remain open.
Automatic `build_paper.py --refresh-figures` remains unavailable: ordinary document
builds reuse the inspected assets rather than launching authoring workflows.
