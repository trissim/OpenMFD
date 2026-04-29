# Rendered Figures

These are the stable figure assets referenced by `papers/mfd_platform/paper.md`.

Workflow:

1. Edit the source `.odp` files in `papers/mfd_platform/figures/final_drop/`
2. Run:

```bash
python papers/mfd_platform/build_paper.py
```

or, if you only want to refresh the figures:

```bash
python papers/mfd_platform/figures/render_figures.py
```

3. The script prefers `draft_figure.pdf` from each figure folder. If only `draft_figure.odp` is present, it exports a fresh PDF first and then copies that PDF into this folder.
4. The manuscript keeps referencing the stable files here

Current stable outputs:

- `openmfd_design.pdf`
- `insert_bonding.pdf`
- `mold_casts_package.pdf`
- `validation.pdf`
- `generalizability.pdf`

Note: the paper points to the stable outputs in this folder. Live auto-refresh on every save is not configured; re-run the render script after editing an `.odp`.
