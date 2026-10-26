# OpenMFD platform manuscript

Read the latest successful [manuscript PDF](current/openmfd_manuscript.pdf),
[supplement PDF](current/openmfd_supplement.pdf), or
[combined review PDF](current/openmfd_review.pdf). DOCX files, input/output/tool
provenance and complete build logs are beside them. All three switch together.

Edit [manuscript.md](manuscript.md) for the main text and files in
[supplementary](supplementary/) for supplementary text. The single ordered
supplement declaration is in [build_paper.py](build_paper.py); the combined
review derives these same two declarations and parsed inputs. Missing sections
fail rather than being silently omitted. The old paper.md path is only a pointer.

## Supplementary text and data

The supplement declaration includes three tables, two illustrated fabrication
notes, the apparent-channel-width note, and the two final protocols. Individual
pin heights, printer profiles, apparent widths and retained per-device counts
are separate data files, listed in
[supplementary/Supplementary_data.md](supplementary/Supplementary_data.md).
The data index also links the width-image crops and native crop bounds, both
saved count-flag sets, the frame-printing G-code and microscope XML file. The
count source and final inclusion decisions for Figure 4 remain unresolved.
Supply these linked files with the supplement when preparing submission files;
the build records and retains them as supporting inputs rather than typesetting
every measurement and setting.

## Build a reading copy

Use a build-only environment, not the OpenMFD runtime environment. Install
Pandoc, LibreOffice and Poppler on Linux, then install the pinned shared package:

```sh
python -m venv /path/to/paper-build-env
/path/to/paper-build-env/bin/python -m pip install -r papers/mfd_platform/requirements-build.txt
/path/to/paper-build-env/bin/python papers/mfd_platform/build_paper.py build
/path/to/paper-build-env/bin/python papers/mfd_platform/build_paper.py status
/path/to/paper-build-env/bin/python papers/mfd_platform/build_paper.py snapshot --label pi-review
/path/to/paper-build-env/bin/python papers/mfd_platform/build_paper.py history
```

To generate a tracked Word copy from two DOCX versions:

```sh
python /home/ts/code/projects/papers/paper_build/compare.py original.docx revised.docx tracked.docx --author "Tristan Simas"
```

The shared package's new `compare` command provides the same operation through
`build_paper.py` once installed from the updated shared source. Generate the
revised DOCX from Markdown first; the source needs no revision markup. This is
a native text comparison, retaining the revised layout, rather than exhaustive
formatting comparison. The system Python needs LibreOffice's UNO bridge.
With the updated shared package, `build --track-against original.docx
--track-role review --author "Tristan Simas"` regenerates the clean documents
and tracked comparison together; `review` includes the supplement.

The requirement pins the tested shared package's exact remote Git revision.
There is one imported shared implementation, not vendored code to synchronise.
No sibling papers checkout is required. Shared-code development can instead
install an editable papers checkout in this build-only environment.
Absolute script paths also work from any directory. `build --candidate` validates
without switching current; failures/interruption retain the previous complete
combined and separate copies. LibreOffice is the only PDF route, not a silent
fallback to a different engine.

## Figures, history and retention

Canonical figure references remain stable PDFs in figures/rendered. The local
preparation owner projects them to existing rendered_docx PNGs for Word; missing
projections fail, without launching a renderer. The figure receipts check the declared PDF/PNG pairs. The apparent-width pair
is published from its existing authored files without invoking the CTB renderer. This is reused presentation evidence, not
fresh biological analysis or proof of regenerated figure sources.

Existing scientific/authoring workflows remain in figures/ and are separate
explicit operations. Automatic `--refresh-figures` fails: current generators can
consume external evidence and clean outputs, so no safe automatic refresh is
declared. Ordinary builds do not call generators, image analysis or OpenSCAD.

The legacy `build_docx.py --skip-figures` command delegates to the same complete
three-output build and reports current/; it never silently rerenders figures.
Earlier build/paper_review copies and the 45-page baseline are retained, not latest.
[History](review/INDEX.md) is generated from new build/snapshot records and labels
[older reviews](reviews/) whose provenance predates this system. Existing report
folders are physically unchanged. Snapshots copy one resolved package and linked
support with unique names; they are frozen reading copies, not editable sources.

Track scientific text, figure generators, required small receipts/results and
intentional main assets only. Generated current/build runs/profiles/review
snapshots remain ignored. Do not newly track raw microscopy data, biology-paper
archives, intermediate renders or old output variants. Current and previous
successful runs, newer review candidates, frozen snapshots and unmanaged folders
are protected. `python build_paper.py cleanup` is a read-only exact candidate and
owned-byte report. Optional `cleanup --archive` moves older owned runs into a
journalled recoverable archive and preserves old URLs with relative symlinks;
it organises live runs rather than reclaiming disk space. A multi-run interruption
can leave a partial but recoverable archive. No archive is executed automatically
or during this migration; legacy/raw/review directories are never cleanup targets.

Status rederives current preparation/source inputs and active tool/dependency
identities. Defining-file hashes are not arbitrary helper-import closure proofs;
owners must observe additional helper/configuration inputs explicitly. Use a
fresh CLI process after code edits. No whole-filesystem lock, reverted-edit
detection, same-version dependency-patch proof or journal-readiness claim.
