#!/usr/bin/env python3
"""Materialize the three-plate no-drug PRE/POST comparison asset package."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlateSources:
    pre: str
    post: str
    axon_crop: str
    post_fallback: str | None = None


PLATES = {
    "p1": PlateSources(
        pre=(
            "Pre/TS_MFD_PRE_P1_20260203__2026-02-03T19_23_43-Measurement 1_stitched_analysis_final"
        ),
        post=("Post/TS_MFD_POST_P1_20260203__2026-02-06T19_37_50-Measurement 2_stiched_axons"),
        axon_crop=(
            "Pre/TS_MFD_PRE_P1_20260203__2026-02-03T19_23_43-Measurement 1_stitched_axon-crop"
        ),
    ),
    "p2": PlateSources(
        pre=(
            "Pre/TS_MFD_PRE_P2_20260203__2026-02-03T19_50_17-Measurement 1_stiched_analysis_final"
        ),
        post=("Post/TS_MFD_POST_P2_20260203__2026-02-06T20_27_24-Measurement 1_stiched_axons"),
        axon_crop=(
            "Pre/TS_MFD_PRE_P2_20260203__2026-02-03T19_50_17-Measurement 1_stiched_axon-crop"
        ),
        post_fallback=(
            "Post/TS_MFD_POST_P2_20260203__2026-02-06T20_27_24-Measurement 1_stiched_openhcs"
        ),
    ),
    "p3": PlateSources(
        pre=(
            "Pre/TS_MFD_PRE_P3_20260203__2026-02-03T20_12_32-Measurement 1_stitched_analysis_final"
        ),
        post=("Post/TS_MFD_POST_P3_20260203__2026-02-06T21_17_22-Measurement 1_stitched_axons"),
        axon_crop=(
            "Pre/TS_MFD_PRE_P3_20260203__2026-02-03T20_12_32-Measurement 1_stitched_axon-crop"
        ),
    ),
}

FIGURE_DATA_FIELDS = (
    "plate",
    "well",
    "row",
    "col",
    "pre_cell_count",
    "dapi_count",
    "total_axon_count",
    "pre_outlier",
    "outlier_reason",
)

PRE_OUTLIER_OVERRIDES = {
    ("p1", "R03C02"): "PRE segmentation artifact identified by plate-mosaic review",
    ("p1", "R06C02"): "PRE segmentation artifact identified by plate-mosaic review",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-root",
        type=Path,
        required=True,
        help="Stitched_Plates directory containing Pre, Post, and figure_handoff.",
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--plates", nargs="+", choices=PLATES, default=list(PLATES))
    parser.add_argument("--wells", nargs="+")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--skip-existing", action="store_true")
    return parser.parse_args()


def write_figure_data(source: Path, destination: Path, plates: list[str]) -> list[str]:
    """Write the PRE-CTB figure table and apply reviewed PRE exclusions."""
    selected_rows = []
    with source.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["plate"] not in plates:
                continue
            reason = PRE_OUTLIER_OVERRIDES.get((row["plate"], row["well"]))
            if reason:
                row["pre_outlier"] = "True"
                row["outlier_reason"] = reason
            selected_rows.append({field: row.get(field, "") for field in FIGURE_DATA_FIELDS})

    expected = 24 * len(plates)
    if len(selected_rows) != expected:
        raise ValueError(f"Expected {expected} figure-data rows; found {len(selected_rows)}")

    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIGURE_DATA_FIELDS)
        writer.writeheader()
        writer.writerows(selected_rows)

    return [
        f"{row['plate']}_{row['well']}"
        for row in selected_rows
        if row["pre_outlier"].strip().lower() == "true"
    ]


def main() -> int:
    args = parse_args()
    generator = Path(__file__).with_name("generate_pre_post_comparison_v3.py")
    source_data = args.dataset_root / "figure_handoff/reference/aggregated_data.csv"
    if not generator.exists():
        raise FileNotFoundError(generator)
    if not source_data.exists():
        raise FileNotFoundError(source_data)

    args.output_root.mkdir(parents=True, exist_ok=True)
    commands = []
    expected_wells = {f"R{row:02d}C{column:02d}" for row in range(2, 8) for column in range(2, 6)}
    target_wells = expected_wells if not args.wells else {well.upper() for well in args.wells}
    for plate in args.plates:
        sources = PLATES[plate]
        for variant in ("overlay", "no_overlay"):
            command = [
                sys.executable,
                str(generator),
                "--pre-dir",
                str(args.dataset_root / sources.pre),
                "--post-dir",
                str(args.dataset_root / sources.post),
                "--pre-axon-dir",
                str(args.dataset_root / sources.axon_crop),
                "--inset-label",
                "0 h",
                "--output-dir",
                str(args.output_root / plate / variant),
                "--pre-roi-step",
                "2",
                "--post-channel",
                "3",
                "--post-roi-step",
                "2",
                "--post-subdir",
                "images",
                "--workers",
                str(args.workers),
            ]
            if variant == "no_overlay":
                command.append("--no-overlays")
            if args.wells:
                command.extend(["--wells", *args.wells])
            if args.skip_existing:
                command.append("--skip-existing")
            print("Running:", " ".join(command), flush=True)
            subprocess.run(command, check=True)
            commands.append(command)

            output_dir = args.output_root / plate / variant
            primary_wells = {
                f"R{int(path.name[1:3]):02d}C{int(path.name[4:6]):02d}"
                for path in (args.dataset_root / sources.post / "images").glob(
                    "r??c??f001p001-ch3sk1fk1fl1.tiff"
                )
            }
            missing_wells = sorted(target_wells - primary_wells)
            if missing_wells and sources.post_fallback:
                fallback_command = command.copy()
                post_index = fallback_command.index("--post-dir") + 1
                fallback_command[post_index] = str(args.dataset_root / sources.post_fallback)
                if "--wells" in fallback_command:
                    wells_index = fallback_command.index("--wells")
                    fallback_command = fallback_command[:wells_index]
                fallback_command.extend(["--wells", *missing_wells])
                print("Running fallback:", " ".join(fallback_command), flush=True)
                subprocess.run(fallback_command, check=True)
                commands.append(fallback_command)

            rendered_wells = {
                path.name.split("_", maxsplit=1)[0]
                for path in output_dir.glob("*_pre_post_comparison.tiff")
            }
            missing_wells = sorted(target_wells - rendered_wells)
            if missing_wells:
                raise RuntimeError(
                    f"{plate}/{variant} is missing {len(missing_wells)} wells: {missing_wells}"
                )

    pre_exclusions = write_figure_data(
        source_data,
        args.output_root / "data.csv",
        args.plates,
    )
    code_dir = args.output_root / "code"
    code_dir.mkdir(exist_ok=True)
    shutil.copy2(generator, code_dir / generator.name)
    shutil.copy2(Path(__file__), code_dir / Path(__file__).name)
    for companion_name in (
        "generate_axotomy_control_supplementary_figure.py",
        "generate_axotomy_supplementary_figure.py",
        "generate_combined_axotomy_supplementary_figure.py",
        "AXOTOMY_CONTROL_REPRODUCIBILITY_FIGURE.md",
        "AXOTOMY_COMBINED_SUPPLEMENTARY_FIGURE.md",
    ):
        companion = Path(__file__).with_name(companion_name)
        if companion.exists():
            shutil.copy2(companion, code_dir / companion.name)

    manifest = {
        "dataset_root": str(args.dataset_root.resolve()),
        "cohort": "three-plate all-DMSO/no-drug reproducibility experiment",
        "plates": {plate: asdict(PLATES[plate]) for plate in args.plates},
        "primary_post_missing_wells": {
            plate: sorted(
                expected_wells
                - {
                    f"R{int(path.name[1:3]):02d}C{int(path.name[4:6]):02d}"
                    for path in (args.dataset_root / PLATES[plate].post / "images").glob(
                        "r??c??f001p001-ch3sk1fk1fl1.tiff"
                    )
                }
            )
            for plate in args.plates
        },
        "pre_channel": 2,
        "pre_roi_step": 2,
        "ctb_measurement": "PRE CTB-647 channel 2 only",
        "post_axon_channel": 3,
        "post_roi_step": 2,
        "inset": "0 h post-axotomy axon-compartment crop",
        "contrast_stretch": "2nd-98th percentile independently per microscopy image",
        "pre_exclusions": pre_exclusions,
        "text": "Arial 11 pt",
        "wells_filter": args.wells,
        "commands": commands,
    }
    (args.output_root / "asset_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote portable asset package to {args.output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
