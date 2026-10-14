"""Declare bounded original fields through OpenHCS's native source projection."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from openhcs.constants import Microscope
from openhcs.core.runtime_image_values import ImagePayloadMetadata
from openhcs.core.source_metadata import SourceVoxelSpacing, SourceVoxelSpacingUnit
from openhcs.core.source_projection import OpenHCSPlaneAddress, SourcePlaneProjection, SourceProjectionSet
from openhcs.core.source_spatial_domain import SourceSpatialDomain
from openhcs.core.virtual_workspace_metadata import AtomicMetadataWriter
from openhcs.microscopes.source_schema import SourceSchemaFilenameParser
from polystore.virtual_workspace import SourcePixelRef
import tifffile

OUT = Path(__file__).resolve().parent
ROOT = Path('/run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03')
evidence = []
for plate in sorted(ROOT.glob('TS_MFD_PRE_P*-Measurement 1')):
    xml = plate / 'Images/Index.xml'
    tree = ET.parse(xml)
    values = {}
    for node in tree.iter():
        key = node.tag.rsplit('}', 1)[-1]
        if key in ('ImageResolutionX', 'ImageResolutionY', 'ImageSizeX', 'ImageSizeY'):
            values.setdefault(key, set()).add((node.text, node.attrib.get('Unit')))
    assert all(len(v) == 1 for v in values.values())
    sx, ux = next(iter(values['ImageResolutionX']))
    sy, uy = next(iter(values['ImageResolutionY']))
    assert ux == uy == 'm'
    spacing = (float(sy) * 1e6, float(sx) * 1e6)
    plate_id = plate.name.split('_')[3]
    workspace = OUT / ('sources_' + plate_id)
    workspace.mkdir(exist_ok=True)
    projections = []
    for site in range(1, 43 if plate_id == 'P3' else 36):
        filename = f'r02c02f{site:02d}p01-ch1sk1fk1fl1.tiff'
        source = plate / 'Images' / filename
        with tifffile.TiffFile(source) as tif:
            assert len(tif.pages) == 1
            shape = tif.pages[0].shape
            dtype = str(tif.pages[0].dtype)
        assert shape == (1080, 1080)
        metadata = ImagePayloadMetadata(
            source_voxel_spacing=SourceVoxelSpacing(spacing, unit=SourceVoxelSpacingUnit.MICROMETERS),
            source_spatial_domain=SourceSpatialDomain((0, 0), shape),
            source_path=str(source), source_dtype=dtype,
        )
        projections.append(SourcePlaneProjection(
            OpenHCSPlaneAddress.from_values('B02', site, 1, 1, 1),
            SourcePixelRef('disk', str(source)), image_metadata=metadata,
        ))
        evidence.append(dict(plate=plate_id, device='R02C02', field=site,
            source=str(source), acquisition_xml=str(xml), shape=shape, dtype=dtype,
            pixel_size_y_um=spacing[0], pixel_size_x_um=spacing[1],
            xml_resolution_x=sx, xml_resolution_y=sy, xml_unit='m',
            spatial_origin_yx=[0, 0], resampling='none; original single-field TIFF'))
    document = SourceProjectionSet(tuple(projections)).metadata_dict(
        parser=SourceSchemaFilenameParser(), microscope_handler_name=Microscope.SOURCE_BINDINGS.value,
        source_filename_parser_name='SourceSchemaFilenameParser', grid_dimensions=[],
        pixel_size=spacing[0], main=True,
    )
    AtomicMetadataWriter().replace_subdirectory_metadata(workspace / 'openhcs_metadata.json', '.', document)
    if plate_id == 'P1':
        context = ROOT / 'Stitched_Plates/Pre' / (plate.name + '_stitched') / 'images/r02c02f001p001-ch1sk1fk1fl1.tiff'
        with tifffile.TiffFile(context) as tif:
            shape = tif.pages[0].shape
            dtype = str(tif.pages[0].dtype)
        context_workspace = OUT / 'context_P1'
        context_workspace.mkdir(exist_ok=True)
        context_metadata = SourceProjectionSet((SourcePlaneProjection(
            OpenHCSPlaneAddress.from_values('B02', 1, 1, 1, 1),
            SourcePixelRef('disk', str(context)),
            image_metadata=ImagePayloadMetadata(
                source_spatial_domain=SourceSpatialDomain((0, 0), shape),
                source_path=str(context), source_dtype=dtype,
            ),
        ),)).metadata_dict(parser=SourceSchemaFilenameParser(),
            microscope_handler_name=Microscope.SOURCE_BINDINGS.value,
            source_filename_parser_name='SourceSchemaFilenameParser',
            grid_dimensions=[], pixel_size=1, main=True)
        AtomicMetadataWriter().replace_subdirectory_metadata(context_workspace / 'openhcs_metadata.json', '.', context_metadata)
(OUT / 'calibration.json').write_text(json.dumps(evidence, indent=2) + '\n')
print(json.dumps(evidence, indent=2))
