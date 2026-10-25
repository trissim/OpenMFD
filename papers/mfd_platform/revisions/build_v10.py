"""Apply scoped V10 text edits to V9, then use the shared Word comparison."""

from copy import deepcopy
import argparse
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

from lxml import etree as E
from PIL import Image
from matplotlib import colormaps
from matplotlib.colors import TwoSlopeNorm, to_hex

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "build/mfd_draft_v9_alyson_version.docx"
CLEAN = ROOT / "build/mfd_draft_v10_plate_layouts_clean.docx"
TRACKED = ROOT / "build/mfd_draft_v10_changes_only_tracked.docx"
NOTES = Path(__file__).with_name("v10_notes.json")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
sys.path.insert(0, str(ROOT / "figures"))
from generate_validation_figure import DATA_DIR, OUTPUT_DIR, count_data, count_summaries, read_csv


def replace(paragraph, old, new):
    nodes = paragraph.findall(".//w:t", NS)
    text = "".join(node.text or "" for node in nodes)
    if text.count(old) != 1:
        raise ValueError(f"Edit must match exactly once: {old!r}")
    start = text.index(old)
    end = start + len(old)
    position = 0
    inserted = False
    for node in nodes:
        value = node.text or ""
        following = position + len(value)
        if following > start and position < end:
            prefix = value[:max(0, start - position)]
            suffix = value[max(0, end - position):]
            node.text = prefix + (new if not inserted else "") + suffix
            node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            inserted = True
        position = following


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notes-only", action="store_true",
                        help="Regenerate comment definitions without overwriting either DOCX")
    args = parser.parse_args()
    with ZipFile(BASE) as archive:
        entries = [(entry, archive.read(entry.filename)) for entry in archive.infolist()]
    document = E.fromstring(dict((entry.filename, data) for entry, data in entries)["word/document.xml"])
    paragraphs = document.findall("w:body/w:p", NS)
    original_text = {paragraph: "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))
                     for paragraph in paragraphs}
    notes = []
    def edit(number, replacements, anchor=None, reason=None):
        paragraph = paragraphs[number - 1]
        for old, new, *change_reason in replacements:
            if len(change_reason) > 1:
                raise ValueError("An individual replacement accepts one explanation")
            replace(paragraph, old, new)
            if change_reason:
                notes.append({"anchor": old.strip(), "text": change_reason[0], "source": "original"})
        if anchor is not None:
            if reason is None:
                raise ValueError("A comment needs an explanation")
            notes.append({"anchor": anchor, "text": reason})

    edit(11, [
        ("Microfluidic platforms enable spatially controlled neuronal culture and compartment-specific manipulation, but their adoption in medium-throughput assays is limited by fabrication methods that require labor-intensive processing and assembly.",
         "Microfluidic cell-culture platforms combine fine channels with pipette-accessible wells, but producing these features at different scales can require labor-intensive fabrication and assembly. This challenge is particularly relevant to neuronal assays, which use fine channels to connect spatially separated culture compartments."),
        ("enabling precise alignment", "enabling array-scale alignment"),
        ("Using this approach, we fabricated", "As an example application, we fabricated"),
        ("Devices supported multichannel liquid handling, automated high-content imaging, directional fluidic manipulation, and primary cortical neuron culture.",
         "Devices supported multichannel liquid handling, automated high-content imaging, directional tracer movement, primary cortical neuron culture and retrograde axonal labeling."),
        (" Compartmentalized axonal growth was demonstrated by retrograde cholera toxin B labeling establishing compatibility with parallel neuronal assays.", ""),
        ("Furthermore, the parametric design framework generated matched fabrication files for additional neuronal culture configurations, illustrating the adaptability of the approach.",
         "OpenMFD also generated matching fabrication files for alternative compartment layouts."),
        (" By combining high-resolution photolithography with scalable three-dimensional molding, this method provides an accessible and reusable fabrication platform for medium-throughput microfluidic assays.", "",
         "The abstract already describes the fabrication method and its demonstrated applications; this closing sentence repeats that summary.")
    ], "enabling array-scale",
       "'Precise' implies measured positioning accuracy. All 96 inserts were aligned in one operation, but positioning error was not measured; 'array-scale' describes what was demonstrated.")

    edit(13, [
        ("Microfluidic compartmentalization has transformed the study of neuronal cell biology by enabling independent access to cell bodies, axons and their local extracellular environments.",
         "Compartmentalized neuronal cultures enable independent access to cell bodies, axons and their local extracellular environments."),
        (" Together, these developments have established compartmentalized microfluidics as a versatile approach for investigating neuronal connectivity and responses to spatially defined perturbations.", "",
         "The examples already establish the neuronal uses. Removing this general summary lets the Introduction move directly to the need for parallel assays.")
    ], "Compartmentalized neuronal cultures enable independent access",
         "Starting with the neuronal need for fine channels preserves the biological motivation, then leads to the fabrication problem the platform solves across different compartment layouts.")

    edit(14, [(" These studies establish that parallelization and adaptable neuronal compartmentalization are feasible. Nevertheless, the fabrication workflow remains an important design consideration when laboratories need to reproduce, modify or manufacture custom arrays of devices.", "",
                "The next paragraph gives the specific fabrication problem, so this general transition is no longer needed.")])

    edit(15, [
        ("A persistent fabrication challenge is the integration", "A persistent fabrication challenge in microfluidic cell culture is the integration"),
        ("which control neurite access and local fluid movement", "which control access and local fluid movement between compartments"),
        ("culture reservoirs are often opened individually after casting.",
         "culture reservoirs are often opened individually after casting. Fine channel-forming features, such as the 10 µm widths designed here, can fall below the practical resolution of desktop resin printers. Photolithography provides these fine features, while printed structures form the larger wells (PMID: 40190179). Fabrication approaches differ in the equipment and operations required to combine these scales (Supplementary Table S2)."),
        ("Building on previous advances in multiscale molding and the elimination of manual reservoir punching, our approach introduces a customizable, parametric design strategy that enables the simultaneous alignment and assembly of large arrays of well-forming inserts onto reusable photolithographically patterned molds, facilitating reproducible, medium-throughput device fabrication.", "",
         "Stating our contribution before finishing the comparison with earlier methods interrupts that comparison. The final Introduction paragraph is the place to explain what OpenMFD adds.")
    ], "practical resolution of desktop resin printers",
         "The scale mismatch explains why the method combines photolithography with printed inserts. Table S2 compares fabrication routes, keeping the focus on how these devices are made rather than their neuronal features alone.")

    edit(16, [("Photopolymer-based 3D printing offers accessible fabrication",
               "For academic laboratories, access to a shared cleanroom for reusable mold fabrication can be more practical than acquiring dedicated precision molding or machining equipment (Supplementary Table S2). Photopolymer-based 3D printing offers accessible fabrication")],
         "access to a shared cleanroom for reusable mold fabrication",
         "Making a reusable mold at a shared facility separates the cleanroom requirement from repeat plate production on the bench. This explains how laboratories can use the method without owning cleanroom equipment.")

    edit(17, [("We demonstrate the approach using an array of 48 two-compartment neuronal devices containing 96 wells on a standard 9 mm plate grid.",
               "We demonstrate this combination of fine channels and pipette-accessible wells in an example neuronal application: an array of 48 two-compartment devices containing 96 wells on a standard 9 mm plate grid."),
              ("We further demonstrate that the parametric workflow generates coordinated fabrication files for alternative compartment geometries, providing a customizable strategy for manufacturing plate-format microfluidic devices.",
               "OpenMFD also arranges alternative compartment geometries into plate-format arrays and generates their matching fabrication files. Once a mold is made, further plates can be cast and assembled on the bench without repeating cleanroom processing.")],
         "an example neuronal application",
         "The workflow generates arrays and fabrication files for different compartment layouts. Describing the neuronal plate as an example preserves that wider contribution instead of narrowing the method to one assay.")

    paragraph = E.Element("{" + W + "}p")
    properties = paragraphs[24].find("w:pPr", NS)
    if properties is not None:
        paragraph.append(deepcopy(properties))
    run = E.SubElement(paragraph, "{" + W + "}r")
    E.SubElement(run, "{" + W + "}t").text = (
        "Supplementary Protocol S2 describes one-time hybrid mold fabrication; "
        "Supplementary Protocol S1 describes routine casting, assembly and assays.")
    paragraphs[23].addnext(paragraph)
    notes.append({"anchor": "".join(paragraph.xpath(".//w:t/text()", namespaces=NS)),
                  "text": "Separating the one-time mold protocol from routine casting makes clear which steps must be repeated to produce another plate."})

    edit(62, [("(Supplementary Note S1)", "(Supplementary Fig. S1; Supplementary Note S1)")])
    edit(63, [("(Supplementary Note S2)", "(Supplementary Fig. S2; Supplementary Note S2)")])

    for number, reason in (
        (73, "The pipetting and imaging results are already stated in the preceding two paragraphs."),
        (82, "Culture, labeling and imaging compatibility are already reported, together with the single-preparation limit. Repeating that limit here adds no new result; the separate biological experiments are discussed with the hydrogel paper."),
        (84, "Ristola combines SU-8 features with printed well-forming inserts, making it the direct comparison for our alignment method. Starting there brings out the added step: aligning and bonding the whole array together. The deleted opening repeats the Introduction."),
    ):
        paragraph = paragraphs[number - 1]
        notes.append({"anchor": original_text[paragraph], "text": reason, "source": "original"})
        paragraph.getparent().remove(paragraph)

    edit(70, [("These observations were qualitative, and systematic measurements of adhesive cytotoxicity or joint mechanical strength were not performed.",
               "Culture survival was assessed qualitatively; adhesive cytotoxicity was not quantified.")],
         "Culture survival was assessed qualitatively",
         "Removed the warning about unmeasured bond strength because no strength value is claimed.")
    edit(72, [("The Opera Phenix Plus was subsequently used for fluorescent tracer imaging and quantitative neuronal assays.",
               "The Opera Phenix Plus was subsequently used for fluorescent tracer imaging and quantitative neuronal assays because it was faster for these experiments.")],
         "because it was faster for these experiments",
         "Both microscopes worked. Speed was the reason for selecting Opera Phenix for these experiments; retaining that reason explains the instrument choice.")

    edit(85, [("Previous approaches have demonstrated the feasibility of combining micrometer- and millimeter-scale features using hybrid soft lithography, alternative molding strategies, and additive manufacturing (PMIDs: 20049640; 32832365). Particularly relevant to our approach, Ristola",
               "Ristola", "Ristola is the relevant comparison for insert alignment. The broader fabrication examples are already in the Introduction, so repeating them delays the comparison this paragraph needs to make."),
              ("Although these geometrical relationships provide tolerance for insert positioning, the actual alignment accuracy remains dependent on photolithographic registration and resin-printing precision and was not directly quantified.",
               "The chamber margin is 17 times the per-side pin clearance (Supplementary Table S3). Final alignment also depends on photolithographic registration and resin-printing precision.")],
         "The chamber margin is 17 times the per-side pin clearance",
         "The 1,275 µm chamber margin is 17 times the 75 µm pin clearance per side. This comparison explains how the layout accommodates positioning error without covering the channels.")
    edit(86, [("The combination of photolithography and resin printing also exploits the complementary capabilities of these fabrication technologies. Photolithography remains well suited to defining micrometer-scale structures, whereas resin printing provides an accessible means of producing larger three-dimensional features. Recent developments in printed molds and hybrid fabrication have expanded the range of structures that can be manufactured for biological microfluidic applications, although achievable resolution, PDMS curing compatibility, and surface treatment remain important considerations (PMIDs: 40190179; 40667579). ", "",
               "Repeating these fabrication-scale comparisons restarts the Introduction's background. This paragraph instead needs to explain why the resin stays in the mold rather than in the culture device."),
              (" This distinction is potentially advantageous for applications requiring conventional PDMS surface treatments and established neuronal culture protocols, although the biological compatibility of each assembled device configuration must still be established experimentally.", "",
               "Changing the compartment layout does not introduce new culture-contact materials. The qualification should concern what changes with the geometry or assay; the separate frame paragraph addresses the observed culture problem.")])
    edit(87, [("The fabrication results demonstrate the feasibility of repeated production using the hybrid molds.",
               "The hybrid molds supported repeated casting."),
              (" Nevertheless, the present study did not directly quantify manufacturing time, labor requirements, or cost savings relative to established alternatives, and these potential advantages should be evaluated in future comparisons.", "")],
         "Nevertheless, the present study did not directly quantify manufacturing time, labor requirements, or cost savings relative to established alternatives, and these potential advantages should be evaluated in future comparisons.",
         "Removed the warning about time and cost comparisons because the paragraph describes eliminated operations without claiming numerical savings.")
    notes[-1]["source"] = "original"
    edit(88, [("The compatibility of the resulting devices with conventional laboratory workflows is an important practical outcome. ", ""),
              ("Previous studies have demonstrated the value of parallelized and modular microfluidic systems for neuronal experimentation (PMIDs: 38150531; 35466333; 38841815). ", "",
               "These studies compare neuronal-platform capabilities, which the Introduction already covers. Repeating them here distracts from what the fabrication workflow adds."),
              ("Our approach complements these platforms by providing an alternative fabrication strategy rather than introducing neuronal compartmentalization or medium-throughput culture as new capabilities.",
               "Our approach extends existing compartmentalized device designs by carrying different layouts into multiwell plate arrays with matching fabrication files.")],
         "Our approach extends existing compartmentalized device designs",
         "The contribution is adapting existing compartment layouts for multiwell production. Stating that extension explains the method's value instead of listing neuronal capabilities that are not new.")
    edit(91, [("These designs have not yet been fabricated, and changes in insert geometry, well spacing, or compartment arrangement will require validation of alignment, casting, demolding, fluid transport, and biological compatibility.",
               "These designs have not yet been fabricated; changes beyond the demonstrated dimensions and clearances in Supplementary Table S3 require further validation.",
               "Table S3 records the dimensions and clearances used here. The qualification can focus on changes beyond that geometry instead of implying that every layout change requires repeating the material-compatibility work.")])
    edit(95, [("Experimental data supporting the findings, including mold fabrication and casting outcomes, resin-insert measurements, neuronal cell counts, and source images used for quantitative analyses, are provided in the Supplementary Information or associated repository.",
               "The Supplementary Information contains the resin-insert measurements, mold fabrication and casting outcomes, per-device neuronal counts and channel-width measurements. The count and width tables are also supplied as CSV files. The source images used for quantitative analyses will be deposited with the submission.")],
         "per-device neuronal counts and channel-width measurements",
         "The count and width results are now supplied, so readers can check the biological summaries and channel measurements without waiting for the planned repository deposit.")

    counts = count_data()
    summaries = count_summaries(counts)
    total = sum(row["n"] for row in summaries)
    excluded = [row for row in counts if row["included"] == "False"]
    n_excluded = len(excluded)
    sizes = ", ".join(str(row["n"]) for row in summaries)
    edit(48, [("Devices were excluded only when contamination or a technical failure prevented cell counting in the final image; high or low cell counts alone were not grounds for exclusion.",
               "Counts flagged for segmentation artifacts, including background falsely detected as cell bodies, were excluded from the plate summaries and retained as red crosses in Fig. 4C. High or low counts alone were not grounds for exclusion. Supplementary Table S7 lists every device count and identifies the exclusions.",
               "The saved exclusions are counting artifacts, not missing counts. Figure 4C and Table S7 retain their values while excluding them from the plate summaries.")])
    edit(51, [("Figure 4C shows the mean number of CTβ-positive cell bodies per device for each plate, with the standard deviation across the analyzed interior devices.",
               "Figure 4C shows individual device counts and each plate's mean and standard deviation after exclusion of the flagged counting artifacts.")],
         "Figure 4C shows individual device counts",
         "The plot now includes device-level dots, so the statistical description includes those observations alongside the plate summaries.")
    edit(50, [("These were baseline images collected before axotomy; Supplementary Protocol S1 describes the dataset.",
               "These were baseline images collected before axotomy in a dimethyl sulfoxide (DMSO)-only control experiment; Supplementary Protocol S1 describes the dataset.")])
    edit(79, [("Of the 72 interior devices across the three plates, three were excluded because contamination or technical failures prevented reliable cell counting, leaving 69 devices for analysis.",
               f"Of the 72 interior device counts, {n_excluded} were flagged for segmentation artifacts and excluded from the plate summaries, leaving {sizes} devices on Plates 1–3, respectively ({total} total; Supplementary Table S7).")],
         f"leaving {sizes} devices on Plates 1–3",
         "The saved dataset flags five counting artifacts, not three devices without counts. Applying those flags gives 67 included devices; retaining all 72 values allows the summaries to be checked.")
    summary_text = "; ".join(f"Plate {i+1}, {s['mean']:.1f} ± {s['sd']:.1f}"
                             for i, s in enumerate(summaries))
    edit(80, [("The mean number of labeled cell bodies per device and the corresponding within-plate standard deviations are presented for each of the three plates in Fig. 4C.",
               f"Counts per device were {summary_text} (mean ± SD; Fig. 4C).")])
    repeated_limits = (
        "However, the tracer experiment did not establish the duration of hydrostatic flow or quantitatively measure fluidic isolation. "
        "Similarly, neuronal experiments using 69 interior devices across three plates demonstrate assay feasibility but were performed using a single embryonic neuronal preparation. "
        "Validation across independent preparations and additional functional assays will be necessary to establish biological reproducibility and suitability for screening applications.")
    revised_limits = (
        "However, the tracer experiment did not establish the duration of hydrostatic flow or quantitatively measure fluidic isolation. "
        f"The neuronal count dataset reported here comprises {total} interior devices across three technical-replicate plates from one embryonic preparation. "
        "Chemical axotomy and drug-response studies using these devices are reported in the hydrogel paper.")
    edit(88, [(" " + repeated_limits, " " + revised_limits)],
         "reported in the hydrogel paper",
         "Chemical axotomy and drug-response experiments using these devices are already reported in the hydrogel paper. Pointing there separates the platform-compatibility example from that biological study, rather than presenting those assays as work still required.")
    edit(235, [(original_text[paragraphs[234]],
                "Inspect segmentation overlays for artifacts, including background detected as cell bodies, before summarizing counts. Retain excluded values in the count table, but omit them from the plate means and SDs. High or low counts alone are not exclusion criteria.",
                "The previous rule described contamination or an inability to count. The saved exclusions identify counting artifacts, so the protocol needs to state that actual basis for exclusion.")],
         "Inspect segmentation overlays for artifacts",
         "The saved DMSO flags identify counting artifacts. This rule ties exclusions to image review, rather than to the magnitude of a count.")
    edit(237, [(original_text[paragraphs[236]],
                f"Plate summaries used {total} of 72 interior device counts: {sizes} on Plates 1–3. The flagged devices were "
                + ", ".join(f"{r['plate'].upper()} {r['device']}" for r in excluded)
                + ". Supplementary Table S7 retains all 72 values and marks these five exclusions.",
                "The saved DMSO dataset excludes five counting artifacts, leaving 67 counts: 22, 21 and 24. The earlier description of three uncountable devices does not match that dataset.")],
         f"Plate summaries used {total} of 72 interior device counts",
         "Lists the five flagged devices explicitly so the 67-device summary can be reproduced from the 72 saved counts.")

    width_method = ("Apparent channel widths were measured in original brightfield fields from device R02C02 on each of three plates, using three transverse rulers per device. "
                    "Rulers joined the centres of opposing dark wall bands at the acquisition scale of 1.18675253 µm/pixel. "
                    "Supplementary Table S8 records the nine measurements; Supplementary Fig. S3 shows their positions.")
    edit(41, [("Microscopy was used to inspect the channels after coating and casting.",
               "Microscopy was used to inspect the channels after coating and casting. " + width_method)],
         width_method,
         "ChatGPT requested measurements of finished channels. These nine brightfield estimates help compare the cast channels with the 10 µm design width; Table S8 and Figure S3 show the measurements.")
    edit(65, [("However, the dimensional accuracy of the cast microchannels relative to their nominal photolithographic dimensions has not yet been quantitatively established.",
               "Nine brightfield ruler estimates from three devices spanned 9–11 pixels, equivalent to apparent widths of 10.7–13.1 µm (Supplementary Table S8; Supplementary Fig. S3).")],
         "Nine brightfield ruler estimates from three devices",
         "Finished-channel measurements were requested and are now available. The nine estimates address that request; defining the wall-band boundaries and noting the unmeasured depth prevents them being read as a complete measurement of channel geometry.")
    edit(89, [("but the dimensions of the finished microchannels have not been quantitatively characterized.",
               "and the examined finished channels had apparent brightfield widths of 10.7–13.1 µm."),
              ("Direct measurements of coated mold features and the resulting PDMS channels would establish dimensional fidelity and permit refinement of the scaling parameters.",
               "The brightfield estimates depend on wall-band placement: shifting each endpoint by one pixel changes a span by up to 2.37 µm. Channel depth remains unmeasured.",
               "The nine brightfield measurements are now supplied in Table S8 and Figure S3. This paragraph gives their optical limitations instead of proposing those measurements as future work.")])
    edit(322, [("Microscopy confirmed open channels after coating and casting.",
                "Microscopy confirmed open channels after coating and casting. Apparent brightfield widths are reported in Supplementary Table S8 and Fig. S3.")])

    edit(60, [("These examples establish the capacity of the design framework to generate coordinated fabrication files for distinct experimental configurations, although the additional designs were not physically fabricated or biologically evaluated.",
               "These additional designs were not fabricated or biologically tested.",
               "The preceding text already describes the coordinated fabrication files. This sentence only needs to distinguish those generated designs from devices that were actually fabricated and tested.")])
    edit(61, [(" A central requirement was the integration of micrometer-scale features with millimeter-scale structures while maintaining the integrity of the patterned wafer and enabling simultaneous positioning of the well-forming inserts.", "",
               "The Introduction explains the scale-integration problem. The next Results subsection shows the specific fabrication failures and solutions.")])
    edit(62, [("Several fabrication challenges were identified and addressed during process development. ", "")])
    edit(80, [(" These measurements demonstrate the feasibility of collecting quantitative retrograde labeling data across multiple compartmentalized neuronal cultures using an automated imaging workflow.", "",
               "Figure 4C and the explicit plate means give the quantitative result; this sentence repeats the subsection's compatibility finding.")])
    edit(89, [("Several design considerations remain important when adapting the platform to other experimental configurations. ", "")])
    edit(85, [("Importantly, the same array-transfer procedure", "The same array-transfer procedure")])

    for number, old, new in (
        (26, "nominal device, channel, pin, taper, and frame dimensions", "device, channel, pin, taper, and frame design dimensions"),
        (59, "nominal widths of 10 µm", "design widths of 10 µm"),
        (85, "In the present design, the nominal lateral clearance was 75 µm per side", "The design provides 75 µm clearance per side"),
        (89, "nominal widths of 10 µm", "design widths of 10 µm"),
    ):
        edit(number, [(old, new)])

    legend = ("Figure 4: Directional fluid movement and neuronal compatibility. "
              "(A) Twenty-four devices at loading and after 72 h without volume adjustment. "
              "Alexa Fluor 568-conjugated secondary antibody (red; 25 µL) was loaded into the left compartment and Alexa Fluor 488-conjugated secondary antibody (green; 50 µL) into the right, each at 1:1000 in PBS. Devices were incubated between images. "
              "Bars: approximately 5 mm, estimated from the known 9 mm well-centre spacing within one device. "
              "(B) Representative CTβ-647 images at DIV11, one device per plate, each beside the same image with segmentation outlines from the original count analysis (yellow). Signal is shown dark on white. Scale bars: 500 µm, calibrated using acquisition metadata. Background subtraction and contrast normalization are for display; all three plates use the same display window. "
              "(C) Individual CTβ-positive cell-body counts from three technical-replicate plates derived from one E18 rat embryo. "
              f"Coloured bars: means; black whiskers: SD across {sizes} included devices on Plates 1–3 ({total} total). "
              "Red crosses: five flagged counting artifacts, excluded from the summaries. Supplementary Table S7 gives all 72 counts.")
    edit(106, [(original_text[paragraphs[105]], legend)],
         "Individual CTβ-positive cell-body counts from three technical-replicate plates",
         "Device dots show variability that plate means hide. A stronger shared display window makes faint cell bodies visible beside their yellow counting outlines, without changing counts or segmentation. The scale-bar descriptions distinguish tracer estimates from acquisition-calibrated CTβ views.")

    def paragraph(text, template):
        result = E.Element("{" + W + "}p")
        props = template.find("w:pPr", NS)
        if props is not None:
            result.append(deepcopy(props))
        E.SubElement(E.SubElement(result, "{" + W + "}r"), "{" + W + "}t").text = text
        return result

    def data_table(rows):
        table = E.Element("{" + W + "}tbl")
        props = E.SubElement(table, "{" + W + "}tblPr")
        E.SubElement(props, "{" + W + "}tblW", {"{" + W + "}w": "0", "{" + W + "}type": "auto"})
        borders = E.SubElement(props, "{" + W + "}tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            E.SubElement(borders, "{" + W + "}" + edge,
                         {"{" + W + "}val": "single", "{" + W + "}sz": "4", "{" + W + "}color": "D0D0D0"})
        grid = E.SubElement(table, "{" + W + "}tblGrid")
        for _ in rows[0]:
            E.SubElement(grid, "{" + W + "}gridCol", {"{" + W + "}w": str(8400 // len(rows[0]))})
        for i, values in enumerate(rows):
            tr = E.SubElement(table, "{" + W + "}tr")
            if i == 0:
                E.SubElement(E.SubElement(tr, "{" + W + "}trPr"), "{" + W + "}tblHeader")
            for value in values:
                cell = E.SubElement(tr, "{" + W + "}tc")
                p = E.SubElement(cell, "{" + W + "}p")
                pp = E.SubElement(p, "{" + W + "}pPr")
                E.SubElement(pp, "{" + W + "}spacing", {"{" + W + "}after": "0"})
                r = E.SubElement(p, "{" + W + "}r")
                rp = E.SubElement(r, "{" + W + "}rPr")
                E.SubElement(rp, "{" + W + "}sz", {"{" + W + "}val": "20"})
                if i == 0:
                    E.SubElement(rp, "{" + W + "}b")
                E.SubElement(r, "{" + W + "}t").text = str(value)
        return table

    count_rows = [["Device", "Plate 1", "Plate 2", "Plate 3"]]
    by_device = {(r["plate"], r["device"]): r for r in counts}
    for device in sorted({r["device"] for r in counts}):
        values = [by_device[(p, device)] for p in ("p1", "p2", "p3")]
        count_rows.append([device] + [f"{float(r['ctb_positive_cells']):g}" + ("*" if r["included"] == "False" else "") for r in values])
    count_rows.append(["Included n"] + [str(s["n"]) for s in summaries])
    count_rows.append(["Mean ± SD"] + [f"{s['mean']:.1f} ± {s['sd']:.1f}" for s in summaries])
    anchor = paragraphs[140]
    counts_heading = paragraph("Supplementary Table S7. DMSO-only CTβ-positive cell-body counts", paragraphs[109])
    E.SubElement(counts_heading.find("w:pPr", NS), "{" + W + "}pageBreakBefore")
    anchor.addprevious(counts_heading)
    anchor.addprevious(paragraph("Baseline counts from the February 2026 experiment. * marks the five counting-artifact exclusions; their values remain listed. Means and SDs use unflagged devices. All three plates came from one E18 rat embryo.", paragraphs[110]))
    notes.append({"anchor": "Baseline counts from the February 2026 experiment.",
                  "text": "Provides every saved device count, including the flagged artifacts, so Figure 4C's means and sample sizes can be checked."})
    anchor.addprevious(data_table(count_rows))
    width_rows = [["Ruler", "Plate / device", "Endpoints (x, y), pixels", "Pixels", "Width (µm)"]]
    for row in read_csv(DATA_DIR / "channel_widths.csv"):
        endpoints = f"({float(row['x0_px']):g}, {float(row['y0_px']):g})–({float(row['x1_px']):g}, {float(row['y1_px']):g})"
        width_rows.append([row["measurement_id"], row["plate"] + " / " + row["device"], endpoints,
                           f"{float(row['width_px']):g}", f"{float(row['width_um']):.1f}"])
    widths_heading = paragraph("Supplementary Table S8. Apparent connecting-microchannel widths", paragraphs[109])
    E.SubElement(widths_heading.find("w:pPr", NS), "{" + W + "}pageBreakBefore")
    anchor.addprevious(widths_heading)
    anchor.addprevious(paragraph("Three rulers per device in original field 1, brightfield channel 1. Widths span opposing dark wall-band centres at 1.18675253 µm/pixel from each acquisition's Index.xml. Moving both endpoints by one pixel changes the span by up to 2.37 µm; blur also affects boundary placement. No channel depth was measured.", paragraphs[110]))
    notes.append({"anchor": "Three rulers per device in original field 1, brightfield channel 1.",
                  "text": "Provides the ruler endpoints and acquisition scale needed to check the nine channel-width estimates requested in the ChatGPT discussion."})
    anchor.addprevious(data_table(width_rows))

    package = {entry.filename: data for entry, data in entries}
    relationships = E.fromstring(package["word/_rels/document.xml.rels"])
    relation_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    drawing_ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
                  "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}
    embed = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"

    def set_picture(p, path, relationship_id=None):
        blip = p.find(".//a:blip", drawing_ns)
        if relationship_id is None:
            relationship_id = blip.get(embed)
            relation = next(r for r in relationships if r.get("Id") == relationship_id)
            target = "word/" + relation.get("Target")
        else:
            target = "word/media/" + path.name
            E.SubElement(relationships, "{" + relation_ns + "}Relationship",
                         Id=relationship_id, Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                         Target="media/" + path.name)
            blip.set(embed, relationship_id)
        package[target] = path.read_bytes()
        with Image.open(path) as im:
            width, height = im.size
        cx = 5334000
        cy = round(cx * height / width)
        for node in p.findall(".//wp:extent", drawing_ns) + p.findall(".//a:xfrm/a:ext", drawing_ns):
            node.set("cx", str(cx))
            node.set("cy", str(cy))

    set_picture(paragraphs[104], OUTPUT_DIR / "draft_figure.png")
    for node in paragraphs[104].findall(".//wp:docPr", drawing_ns):
        node.set("descr", legend)
    width_picture = deepcopy(paragraphs[149])
    for node in width_picture.findall(".//wp:docPr", drawing_ns):
        node.set("id", "100")
        node.set("descr", "Supplementary Figure S3. Original brightfield crops with channel-width rulers.")
    set_picture(width_picture, OUTPUT_DIR / "channel_widths.png", "rIdChannelWidths")
    anchor.addprevious(width_picture)
    anchor.addprevious(paragraph("Supplementary Figure S3. Brightfield channel-width measurements. Yellow rulers M01–M09 join opposing dark wall-band centres in the three original field-1 crops listed in Table S8. Images are contrast-stretched for display; measurements use original pixel coordinates. White bars: 20 µm.", paragraphs[150]))
    notes.append({"anchor": "Supplementary Figure S3. Brightfield channel-width measurements.",
                  "text": "Shows which visible wall bands were used for each width estimate, allowing boundary placement to be assessed."})
    package["word/_rels/document.xml.rels"] = E.tostring(relationships, encoding="UTF-8", xml_declaration=True, standalone=True)

    edit(11, [
        ("3D-printed structures", "structures produced by three-dimensional (3D) printing"),
        ("SU-8/SUEX-patterned wafers", "wafers patterned with SU-8 and SUEX photoresists"),
    ])
    edit(13, [
        ("controlled axon-guidance gradients, localized neuron–glia interactions and more complex neuronal networks (PMIDs: 26000554; 22828584; 35466333)",
         "controlled axon-guidance gradients (PMID: 26000554), localized neuron–glia interactions (PMID: 22828584) and modular neuronal culture models (PMID: 35466333)"),
    ])
    edit(14, [
        ("modular microfluidic units that can be combined into customizable neuronal culture configurations, whereas fluid-walled chambers support human neuronal microcircuits and moderate-throughput axotomy assays (PMIDs: 35466333; 38841815)",
         "modular microfluidic units that can be combined into customizable neuronal culture configurations (PMID: 35466333), whereas fluid-walled chambers support human neuronal microcircuits and moderate-throughput axotomy assays (PMID: 38841815)"),
    ])
    edit(25, [
        ("two-dimensional DXF mask drawings for each layer and three-dimensional STL models",
         "two-dimensional Drawing Exchange Format (DXF) mask drawings for each layer and three-dimensional stereolithography (STL) models"),
    ])
    edit(28, [("HMDS adhesion-promoter", "hexamethyldisilazane (HMDS) adhesion-promoter")])
    edit(31, [("ultraviolet light", "ultraviolet (UV) light")])
    edit(33, [("An EPDM rubber sheet", "An ethylene propylene diene monomer (EPDM) rubber sheet")])
    edit(46, [
        ("Harris et al.\u00a0(2007)", "Harris et al. (2007; PMID: 18989412)"),
        ("Clément et al.\u00a0(2022)", "Clément et al. (2022; PMID: 35023760)"),
    ])
    edit(48, [
        ("11 days in vitro (DIV11)", "11 days in vitro (DIV)"),
        ("Alexa Fluor-conjugated cholera toxin subunit B (CTβ-647)",
         "cholera toxin subunit B (CTβ) conjugated to Alexa Fluor 647 (CTβ-647)"),
    ])
    edit(50, [("XML format", "Extensible Markup Language (XML) format")])
    edit(69, [("high-impact polystyrene (HIPS)", "HIPS")])
    edit(77, [("11 days in vitro (DIV11)", "11 DIV")])
    edit(78, [("fluorescently conjugated cholera toxin subunit B (CTβ-647)", "CTβ-647")])
    edit(98, [
        ("filament-extrusion (FDM)", "fused deposition modeling (FDM)"),
        ("AEF is funded", "Alyson Fournier is funded"),
    ])
    edit(119, [
        ("The comparison emphasizes the operations and equipment each strategy adds to conventional PDMS soft lithography.",
         "The comparison emphasizes the operations and equipment each strategy adds to conventional PDMS soft lithography. Abbreviations: poly(methyl methacrylate) (PMMA); cyclic olefin copolymer (COC); computer numerical control (CNC); American National Standards Institute (ANSI); Society for Laboratory Automation and Screening (SLAS)."),
    ], "Abbreviations: poly(methyl methacrylate) (PMMA)",
       "These abbreviations were undefined in the supplementary comparison. Expanding them lets readers follow the table without looking up its terminology.")
    edit(168, [("RTV silicone sealant", "room-temperature-vulcanizing silicone sealant")])
    edit(169, [("Dendritic polyglycerol amine (dPGA; DendroTEK Biosciences)",
                "dPGA (DendroTEK Biosciences)")])
    edit(173, [("Alexa Fluor-conjugated cholera toxin subunit B (CTβ-647)", "CTβ-647")])
    edit(208, [("phosphate-buffered saline (PBS)", "PBS")])
    edit(218, [("Clément et al.\u00a0(2022)", "Clément et al. (2022; PMID: 35023760)")])
    edit(223, [
        ("11 days in vitro (DIV11)", "11 DIV"),
        ("Harris et al.\u00a0(2007)", "Harris et al. (2007; PMID: 18989412)"),
    ])

    tables = document.findall("w:body/w:tbl", NS)
    height_rows = tables[0].findall("w:tr", NS)[1:]
    heights = [[float("".join(cell.xpath(".//w:t/text()", namespaces=NS)))
                for cell in row.findall("w:tc", NS)[1:]] for row in height_rows]
    centre = sum(sum(row) for row in heights) / 96
    deviations = [[(value - centre) * 1000 for value in row] for row in heights]
    limit = max(abs(value) for row in deviations for value in row)
    colour = TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit)
    for table in tables[:2]:
        for run in table.findall(".//w:r", NS):
            properties = run.find("w:rPr", NS)
            if properties is None:
                properties = E.Element("{" + W + "}rPr")
                run.insert(0, properties)
            for name, value in (("sz", "18"), ("szCs", "18"), ("i", "0"), ("iCs", "0")):
                setting = properties.find("w:" + name, NS)
                if setting is None:
                    setting = E.SubElement(properties, "{" + W + "}" + name)
                setting.set("{" + W + "}val", value)
        for row, values in zip(table.findall("w:tr", NS)[1:], deviations, strict=True):
            for cell, value in zip(row.findall("w:tc", NS)[1:], values, strict=True):
                properties = cell.find("w:tcPr", NS)
                if properties is None:
                    properties = E.SubElement(cell, "{" + W + "}tcPr")
                shade = properties.find("w:shd", NS)
                if shade is None:
                    shade = E.SubElement(properties, "{" + W + "}shd")
                rgba = colormaps["coolwarm"](colour(value))
                # Pale cells keep the measurements readable in print.
                rgb = tuple(.55 + .45 * component for component in rgba[:3])
                shade.set("{" + W + "}val", "clear")
                shade.set("{" + W + "}fill", to_hex(rgb)[1:].upper())
    edit(111, [("Values are reported in millimeters (mm) and as deviations from the mean in micrometers (µm).",
                "Values are reported in millimeters (mm) and as deviations from the mean in micrometers (µm). Cell colour shows height relative to the mean: blue is lower, white is the mean and red is higher; both tables use the same scale.")],
         "Cell colour shows height relative to the mean",
         "Height variation prevented rigid clamping from seating the whole array uniformly. Showing its spatial pattern explains the need for compressible backing alongside the individual measurements.")
    for table in tables:
        for p in table.findall(".//w:p", NS):
            if "nominal channel width" in "".join(p.xpath(".//w:t/text()", namespaces=NS)):
                replace(p, "nominal channel width", "design channel width")
    comparison_rows = tables[2].findall("w:tr", NS)
    laser_approach = comparison_rows[2].findall("w:tc", NS)[0].find("w:p", NS)
    replace(laser_approach, "CO2 laser micromachining", "Carbon dioxide (CO2) laser micromachining")
    light_control = tables[7].findall("w:tr", NS)[1].findall("w:tc", NS)[0].find("w:p", NS)
    replace(light_control, "Bottom light PWM", "Bottom light pulse-width modulation (PWM)")

    text = "\n".join("".join(p.xpath(".//w:t/text()", namespaces=NS))
                     for p in document.findall("w:body/w:p", NS))
    for note in notes:
        source = "\n".join(original_text.values()) if note.get("source") == "original" else text
        if source.count(note["anchor"]) != 1:
            raise ValueError(f"Comment anchor must occur once: {note['anchor']!r}")

    NOTES.write_text(json.dumps(notes, indent=2) + "\n")
    if args.notes_only:
        return

    payload = E.tostring(document, encoding="UTF-8", xml_declaration=True, standalone=True)
    package["word/document.xml"] = payload
    with ZipFile(CLEAN, "w") as archive:
        for entry, data in entries:
            archive.writestr(entry, package.pop(entry.filename))
        for name, data in package.items():
            archive.writestr(name, data)
    comparison = Path("/home/ts/code/projects/papers/paper_build/compare.py")
    subprocess.run(["/usr/bin/python3", str(comparison), str(BASE), str(CLEAN), str(TRACKED),
                    "--author", "Tristan Simas", "--notes", str(NOTES)], check=True)


if __name__ == "__main__":
    main()
