# Published document figures

The manuscript uses the PDFs in this directory and the matching PNGs in
`../rendered_docx/`. Ordinary document builds reuse these outputs; they do not
regenerate scientific figures.

`FigureRenderSpec` in `../render_figures.py` owns each published PDF/PNG pair.
The frozen validation figure and retained supplement pairs are verified in place.
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

The full `python papers/mfd_platform/figures/render_figures.py` command runs the
four declared design/casting producers. Figure4 has no automatic producer: its
existing PDF/PNG pair is verified without regeneration or copying. This preserves
the frozen September composite; it does not accept its scientific content. The
October authored source, its measurement source and the intended69-device set
still need reconciliation before replacing that pair. Automatic
`build_paper.py --refresh-figures` remains deliberately unavailable.
