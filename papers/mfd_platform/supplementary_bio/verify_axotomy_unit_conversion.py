"""Audit original pixel measurements against saved SVG graph bar heights."""

import argparse
import csv
import json
import math
import re
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path


def svg_bar_values(path):
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.parse(path, parser=parser).getroot()
    ns = {"s": "http://www.w3.org/2000/svg"}
    ticks = []
    for group in root.findall(".//s:g", ns):
        if not group.get("id", "").startswith("ytick_"):
            continue
        label = next(e.text.strip() for e in group.iter() if e.tag is ET.Comment)
        marker = next(e for e in group.findall(".//s:use", ns) if "y" in e.attrib)
        ticks.append((float(label.replace(",", "")), float(marker.get("y"))))
    (v0, y0), (v1, y1) = ticks[:2]
    values = []
    for index in (3, 4, 5):
        path_element = root.find(f".//s:g[@id='patch_{index}']/s:path", ns)
        coordinates = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", path_element.get("d"))]
        top = min(coordinates[1::2])
        values.append(v0 + (top - y0) * (v1 - v0) / (y1 - y0))
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.figure_dir / "figure_manifest.json").read_text())
    with Path(manifest["authoritative_data"]).open(newline="") as handle:
        records = list(csv.DictReader(handle))
    summaries = []
    details = []
    rendered = {panel: svg_bar_values(args.figure_dir / "panels" / f"panel_{panel}.svg")
                for panel in ("C", "E")}
    for index, plate in enumerate(("p1", "p2", "p3")):
        acquisition = next(args.dataset_root.glob(f"TS_MFD_POST_{plate.upper()}_*-Measurement *"))
        raw_xml = acquisition / "Images/Index.xml"
        tree = ET.parse(raw_xml)
        calibration = {float(e.text) * 1e6 for e in tree.iter()
                       if e.tag.rsplit("}", 1)[-1] in ("ImageResolutionX", "ImageResolutionY")}
        assert len(calibration) == 1, calibration
        pixel_size = calibration.pop()
        analysis = next((args.dataset_root / "Stitched_Plates/Post").glob(f"*_{plate.upper()}_*_analysis"))
        rows = [r for r in records if r["plate"] == plate]
        assert len(rows) == 24
        for row in rows:
            raw = float(row["total_axon_count"])
            matches = []
            for source in (analysis / "images_results").glob(f'{row["well"].lower()}*ch3*axon_analysis*.json'):
                data = json.loads(source.read_text())
                if isinstance(data, str):
                    data = json.loads(data)
                if not math.isclose(data["summary"]["total_axon_length"], raw, rel_tol=1e-10):
                    continue
                assert data["metadata"]["voxel_spacing"] == [1.0, 1.0, 1.0]
                assert math.isclose(sum(b["branch_distance"] for b in data["branch_data"]), raw, rel_tol=1e-10)
                matches.append(str(source))
            assert matches, f'No original pixel-length match for {plate} {row["well"]}'
            details.append(dict(plate=plate, well=row["well"], axon_length_pixels=raw,
                                pixel_size_um=pixel_size, axon_length_um=raw * pixel_size,
                                ctb_positive_cells=float(row["pre_cell_count"]),
                                axon_length_um_per_cell=raw * pixel_size / float(row["pre_cell_count"]),
                                excluded_ctb=row["pre_outlier"], original_analysis=matches[0],
                                calibration_source=str(raw_xml)))
        retained = [r for r in rows if r["pre_outlier"].lower() != "true"]
        for panel, selected in (("C", rows), ("E", retained)):
            raw_mean = statistics.mean(float(r["total_axon_count"]) /
                                       (float(r["pre_cell_count"]) if panel == "E" else 1)
                                       for r in selected)
            expected = raw_mean * pixel_size
            actual = rendered[panel][index]
            # SVG positions are rounded to six decimal places by Matplotlib.
            assert math.isclose(actual, expected, abs_tol=0.002), (panel, plate, actual, expected)
            summaries.append(dict(panel=panel, plate=plate, n=len(selected),
                                  original_mean_pixels=raw_mean, converted_mean_um=expected,
                                  mean_decoded_from_saved_svg=actual))
    for filename, rows in (("unit_conversion_per_device.csv", details),
                           ("unit_conversion_graph_audit.csv", summaries)):
        with (args.figure_dir / filename).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print("PASS: 72 original branch-length sums; raw pixel spacing; acquisition calibration; 6 exported bar heights.")
    for row in summaries:
        print(row)


if __name__ == "__main__":
    main()
