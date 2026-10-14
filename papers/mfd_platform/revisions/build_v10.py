"""Apply scoped V10 text edits to V9, then use the shared Word comparison."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "build/mfd_draft_v9_alyson_version.docx"
CLEAN = ROOT / "build/mfd_draft_v10_plate_layouts_clean.docx"
TRACKED = ROOT / "build/mfd_draft_v10_changes_only_tracked.docx"
NOTES = Path(__file__).with_name("v10_notes.json")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


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
    with ZipFile(BASE) as archive:
        entries = [(entry, archive.read(entry.filename)) for entry in archive.infolist()]
    document = E.fromstring(dict((entry.filename, data) for entry, data in entries)["word/document.xml"])
    paragraphs = document.findall("w:body/w:p", NS)
    original_text = {paragraph: "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))
                     for paragraph in paragraphs}
    notes = []
    explained = set()

    def edit(number, replacements, anchor, reason):
        paragraph = paragraphs[number - 1]
        for old, new in replacements:
            replace(paragraph, old, new)
        notes.append({"anchor": anchor, "text": reason})
        explained.add(paragraph)

    edit(11, [
        ("Microfluidic platforms enable spatially controlled neuronal culture and compartment-specific manipulation, but their adoption in medium-throughput assays is limited by fabrication methods that require labor-intensive processing and assembly.",
         "Microfluidic cell-culture platforms combine fine channels with pipette-accessible wells, but producing these features at different scales can require labor-intensive fabrication and assembly. This challenge is particularly relevant to neuronal assays, which use fine channels to connect spatially separated culture compartments."),
        ("enabling precise alignment", "enabling array-scale alignment"),
        ("Using this approach, we fabricated", "As an example application, we fabricated"),
        ("Devices supported multichannel liquid handling, automated high-content imaging, directional fluidic manipulation, and primary cortical neuron culture.",
         "Devices supported multichannel liquid handling, automated high-content imaging, directional tracer movement, primary cortical neuron culture and retrograde axonal labeling."),
        (" Compartmentalized axonal growth was demonstrated by retrograde cholera toxin B labeling establishing compatibility with parallel neuronal assays.", ""),
        ("matched fabrication files for additional neuronal culture configurations", "matched fabrication files for additional compartment geometries")
    ], "enabling array-scale",
       "We aligned all inserts together, but did not measure positioning error. I changed 'precise alignment' to describe the operation we performed.")
    notes.extend([
        {"anchor": "This challenge is particularly relevant to neuronal assays",
         "text": "The opening now states the fabrication problem first, then explains why neuronal assays need fine channels between compartments."},
        {"anchor": "directional tracer movement, primary cortical neuron culture and retrograde axonal labeling",
         "text": "Condensed the biological-validation summary into one sentence."},
        {"anchor": "additional compartment geometries",
         "text": "'Additional compartment geometries' describes what OpenMFD varies without limiting the fabrication method to neuronal assays."},
    ])

    edit(13, [
        ("Microfluidic compartmentalization has transformed the study of neuronal cell biology by enabling independent access to cell bodies, axons and their local extracellular environments.",
         "Neuronal culture is a particularly useful application of this multiscale fabrication capability. Microfluidic compartmentalization enables independent access to cell bodies, axons and their local extracellular environments."),
        ("Together, these developments have established compartmentalized microfluidics as a versatile approach for investigating neuronal connectivity and responses to spatially defined perturbations.",
         "Fine channel-forming features, such as the nominal 10 µm widths used here, can fall below the practical resolution of desktop resin printers. Photolithography provides these fine features, while printed structures form the larger wells (PMID: 40190179).")
    ], "practical resolution of desktop resin printers",
         "Moved the neuronal context after the fabrication problem. The added resolution explanation connects these applications to the need for photolithography for fine channels alongside printing for larger wells.")

    edit(14, [("These studies establish that parallelization and adaptable neuronal compartmentalization are feasible. Nevertheless, the fabrication workflow remains an important design consideration when laboratories need to reproduce, modify or manufacture custom arrays of devices.",
               "Our approach builds on existing compartmentalized device designs by arranging a chosen device layout into a multiwell plate array and generating matching photomasks, well-forming inserts and plate components.")],
         "Our approach builds on existing compartmentalized device designs",
         "The revised closing sentence explains how OpenMFD extends earlier work: arranging existing device layouts into multiwell arrays and generating their matching masks, inserts and plate components.")

    edit(15, [
        ("A persistent fabrication challenge is the integration", "A persistent fabrication challenge in microfluidic cell culture is the integration"),
        ("which control neurite access and local fluid movement", "which control access and local fluid movement between compartments"),
        ("culture reservoirs are often opened individually after casting.",
         "culture reservoirs are often opened individually after casting. Fabrication approaches differ in the equipment and operations required to combine these scales (Supplementary Table S2)."),
        ("Building on previous advances in multiscale molding and the elimination of manual reservoir punching, our approach introduces a customizable, parametric design strategy that enables the simultaneous alignment and assembly of large arrays of well-forming inserts onto reusable photolithographically patterned molds, facilitating reproducible, medium-throughput device fabrication.", "")
    ], "Fabrication approaches differ in the equipment and operations required to combine these scales",
         "Moved the fine-channel/large-well paragraph to the start and removed the duplicated method summary. The Table S2 link from V7 restores the broader fabrication comparison.")

    paragraphs[11].addnext(paragraphs[14])

    edit(16, [("Photopolymer-based 3D printing offers accessible fabrication",
               "For academic laboratories, access to a shared cleanroom for reusable mold fabrication can be more practical than acquiring dedicated precision molding or machining equipment (Supplementary Table S2). Photopolymer-based 3D printing offers accessible fabrication")],
         "access to a shared cleanroom for reusable mold fabrication",
         "Restored V7's shared-cleanroom explanation and Table S2 citation: a lab can obtain a reusable mold from a facility, then cast plates on the bench.")

    edit(17, [("We demonstrate the approach using an array of 48 two-compartment neuronal devices containing 96 wells on a standard 9 mm plate grid.",
               "We demonstrate this combination of fine channels and pipette-accessible wells in an example neuronal application: an array of 48 two-compartment devices containing 96 wells on a standard 9 mm plate grid."),
              ("providing a customizable strategy for manufacturing plate-format microfluidic devices.",
               "providing a customizable strategy for manufacturing plate-format microfluidic devices. Once a mold is made, further plates can be cast and assembled on the bench without repeating cleanroom processing.")],
         "an example neuronal application",
         "Described the plate as an example neuronal application and restored V7's practical benefit: later plates can be made without repeating cleanroom processing.")

    paragraph = E.Element("{" + W + "}p")
    properties = paragraphs[24].find("w:pPr", NS)
    if properties is not None:
        paragraph.append(deepcopy(properties))
    run = E.SubElement(paragraph, "{" + W + "}r")
    E.SubElement(run, "{" + W + "}t").text = (
        "Supplementary Protocol S2 describes one-time hybrid mold fabrication; "
        "Supplementary Protocol S1 describes routine casting, assembly and assays.")
    paragraphs[23].addnext(paragraph)
    explained.add(paragraph)
    notes.append({"anchor": "Supplementary Protocol S2 describes one-time hybrid mold fabrication",
                  "text": "Added protocol links to distinguish one-time mold fabrication from routine casting and assays."})

    edit(62, [("(Supplementary Note S1)", "(Supplementary Fig. S1; Supplementary Note S1)")],
         "Supplementary Fig. S1",
         "Added the Figure S1 citation because those images show the raised edges and the effect of the filter.")
    edit(63, [("(Supplementary Note S2)", "(Supplementary Fig. S2; Supplementary Note S2)")],
         "Supplementary Fig. S2",
         "Added the Figure S2 citation because the image shows the SU-8 peeling from the wafer.")

    edit(70, [("These observations were qualitative, and systematic measurements of adhesive cytotoxicity or joint mechanical strength were not performed.",
               "Culture survival was assessed qualitatively; adhesive cytotoxicity was not quantified.")],
         "Culture survival was assessed qualitatively",
         "Removed the warning about unmeasured bond strength because no strength value is claimed.")
    edit(72, [("The Opera Phenix Plus was subsequently used for fluorescent tracer imaging and quantitative neuronal assays.",
               "The Opera Phenix Plus was subsequently used for fluorescent tracer imaging and quantitative neuronal assays because it was faster for these experiments.")],
         "because it was faster for these experiments",
         "Restored V7's reason for choosing the Opera Phenix: it was faster for these experiments.")

    edit(85, [("Although these geometrical relationships provide tolerance for insert positioning, the actual alignment accuracy remains dependent on photolithographic registration and resin-printing precision and was not directly quantified.",
               "The chamber margin is 17 times the nominal per-side clearance (Supplementary Table S3). Final alignment also depends on photolithographic registration and resin-printing precision.")],
         "The chamber margin is 17 times the nominal per-side clearance",
         "Restored V7's 17-fold comparison between the 1,275 micrometer chamber margin and 75 micrometer pin clearance, which explains how the layout accommodates positioning error without covering the channels.")
    edit(86, [("conventional PDMS surface treatments and established neuronal culture protocols, although the biological compatibility of each assembled device configuration must still be established experimentally.",
               "conventional PDMS surface treatments and established cell-culture protocols.")],
         "established cell-culture",
         "Changed 'neuronal culture protocols' to 'cell-culture protocols' because the PDMS/glass culture surfaces are useful beyond neurons. Removed the repeated warning about validating each configuration.")
    edit(87, [(" Nevertheless, the present study did not directly quantify manufacturing time, labor requirements, or cost savings relative to established alternatives, and these potential advantages should be evaluated in future comparisons.", "")],
         "Nevertheless, the present study did not directly quantify manufacturing time, labor requirements, or cost savings relative to established alternatives, and these potential advantages should be evaluated in future comparisons.",
         "Removed the warning about time and cost comparisons because the paragraph describes eliminated operations without claiming numerical savings.")
    notes[-1]["source"] = "original"
    edit(88, [("Our approach complements these platforms by providing an alternative fabrication strategy rather than introducing neuronal compartmentalization or medium-throughput culture as new capabilities.",
               "Our approach extends existing compartmentalized device designs by carrying different layouts into multiwell plate arrays with matching fabrication files.")],
         "Our approach extends existing compartmentalized device designs",
         "Replaced the statement about what the work does not introduce with its contribution: adapting device layouts into multiwell plate arrays with matching fabrication files.")
    edit(91, [("These designs have not yet been fabricated, and changes in insert geometry, well spacing, or compartment arrangement will require validation of alignment, casting, demolding, fluid transport, and biological compatibility.",
               "These additional designs have not yet been fabricated or biologically tested.")],
         "These additional designs have not yet been fabricated or biologically tested",
         "Shortened the validation warning to the actual status: these layouts have not been fabricated or biologically tested.")
    edit(93, [("The resulting platform accommodates", "The demonstrated plate accommodates"),
              ("Although further optimization is required to improve peripheral culture performance and establish quantitative fabrication reproducibility, this approach provides an adaptable and accessible framework for producing customized microfluidic platforms for neuroscience and other applications requiring spatially controlled cell culture.",
               "Peripheral culture performance remains a target for improvement. The coordinated design and array-transfer workflow provides an adaptable framework for integrating fine microfeatures with well-forming inserts in reusable molds for spatially controlled cell culture.")],
         "The coordinated design and array-transfer workflow provides an adaptable framework",
         "The closing sentence now emphasizes coordinated design, collective insert transfer and reusable molds for spatially controlled cell culture. Removed the demand to establish quantitative fabrication reproducibility, which the paper does not claim.")
    edit(95, [("Experimental data supporting the findings, including mold fabrication and casting outcomes, resin-insert measurements, neuronal cell counts, and source images used for quantitative analyses, are provided in the Supplementary Information or associated repository.",
               "The Supplementary Information contains the resin-insert measurements and mold fabrication and casting outcomes. The per-device neuronal count table and source images used for quantitative analyses will be deposited with the submission.")],
         "The per-device neuronal count table and source images used for quantitative analyses",
         "The supplied supplement has pin heights and mold/cast totals. The individual neuronal counts and analysis images need their own data files for submission. I changed the statement so it does not say those files are already supplied.")

    changed = {p for p in document.findall("w:body/w:p", NS)
               if p not in original_text or original_text[p] != "".join(p.xpath(".//w:t/text()", namespaces=NS))}
    if changed - explained:
        raise ValueError("Every changed paragraph must have an explanatory comment")
    text = "\n".join("".join(p.xpath(".//w:t/text()", namespaces=NS))
                     for p in document.findall("w:body/w:p", NS))
    for note in notes:
        source = "\n".join(original_text.values()) if note.get("source") == "original" else text
        if source.count(note["anchor"]) != 1:
            raise ValueError(f"Comment anchor must occur once: {note['anchor']!r}")

    payload = E.tostring(document, encoding="UTF-8", xml_declaration=True, standalone=True)
    with ZipFile(CLEAN, "w") as archive:
        for entry, data in entries:
            archive.writestr(entry, payload if entry.filename == "word/document.xml" else data)
    NOTES.write_text(json.dumps(notes, indent=2) + "\n")
    comparison = Path("/home/ts/code/projects/papers/paper_build/compare.py")
    subprocess.run(["/usr/bin/python3", str(comparison), str(BASE), str(CLEAN), str(TRACKED),
                    "--author", "Tristan Simas", "--notes", str(NOTES)], check=True)


if __name__ == "__main__":
    main()
