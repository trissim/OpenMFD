# Rendered Figures

These are stable figure assets referenced by `papers/mfd_platform/manuscript.md`
and its supplementary sources. Ordinary document builds reuse these PDFs and
the retained PNGs in rendered_docx; they do not regenerate figures.

Workflow:

1. Edit the source `.odp` files in `papers/mfd_platform/figures/final_drop/`
2. Run:

```bash
python papers/mfd_platform/build_paper.py build
```

or, if you only want to refresh the figures:

```bash
python papers/mfd_platform/figures/render_figures.py
```

3. The script prefers `draft_figure.pdf` from each figure folder. If only `draft_figure.odp` is present, it exports a fresh PDF first and then copies that PDF into this folder.
4. The manuscript keeps referencing the stable files here

Stable output selection is declared by FigureRenderSpec in render_figures.py;
the actual document dependencies are derived from canonical Markdown references.

Note: the paper points to the stable outputs in this folder. Live auto-refresh on every save is not configured; re-run the render script after editing an `.odp`.
