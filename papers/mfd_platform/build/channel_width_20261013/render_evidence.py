"""Render returned MCP pixel samples and native measurements; no image analysis."""
import json
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
decoder = json.JSONDecoder()
text = (OUT / 'paired_mcp.log').read_text()
position = 0
samples = []
measurements = []
while position < len(text):
    start = text.find('{', position)
    if start < 0:
        break
    try:
        data, length = decoder.raw_decode(text[start:])
    except json.JSONDecodeError:
        position = start + 1
        continue
    position = start + length
    if not isinstance(data, dict) or 'results' not in data:
        continue
    for result in data['results']:
        if result['tool'] == 'openhcs_sample_viewer_window_image':
            samples.extend(result['payloads'])
        if result['tool'] == 'openhcs_measure_viewer_polyline':
            measurements.extend(result['payloads'])
accepted = [r for r in measurements if not r['errors'] and r['measurement']['line_width'] == 1]
identities = {samples[0]['route_key']: ('P1', 1), samples[2]['route_key']: ('P2', 3),
    samples[3]['route_key']: ('P3', 4)} if len(samples) >= 4 else {}
calibration = json.loads((OUT / 'calibration.json').read_text())
rows = []
for number, result in enumerate(accepted, 1):
    c, m = result['coordinates'], result['measurement']
    plate, sample_id = identities[c['route_key']]
    source = next(r for r in calibration if r['plate'] == plate and r['field'] == c['components']['site'])
    assert c['source_domain']['origin_yx'] == [0, 0]
    assert c['source_domain']['source_shape_yx'] == source['shape']
    assert c['source_spacing']['values_zyx'] == [source['pixel_size_y_um'], source['pixel_size_x_um']]
    (y0, x0), (y1, x1) = m['vertices_yx']
    assert abs(m['world_length'] - m['data_length'] * source['pixel_size_x_um']) < 1e-10
    rows.append(dict(measurement_id=f'M{number:02d}', plate=plate, device='R02C02', field=1, channel=1,
        source=source['source'], acquisition_xml=source['acquisition_xml'], route_key=c['route_key'],
        y0_px=y0, x0_px=x0, y1_px=y1, x1_px=x1, width_px=m['data_length'],
        pixel_size_um=source['pixel_size_x_um'], width_um=m['world_length'],
        feature='connecting microchannel; apparent opposing dark wall-band spacing',
        method='manual visible wall-band centres supported by native 5-pixel-band profiles',
        sample_json=f'raw_sample_{sample_id:02d}.json', overlay=f'{plate}_R02C02_microchannels_overlay.png',
        boundary_placement_sensitivity_px=2, physical_accuracy='optical boundary bias unquantified'))
if rows:
    with (OUT / 'measurements.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / 'accepted_width_measurements.json').write_text(json.dumps(accepted, indent=2) + '\n')
for index, sample in enumerate(samples):
    if sample['errors']:
        continue
    assert sample['returned_record_count'] == 1 and sample['records_truncated_count'] == 0
    record = sample['records'][0]
    summary = record['array_value_summary']
    assert summary['included'] and summary['size'] == np.prod(summary['shape'])
    pixels = np.array(record['array_values'], dtype=np.uint16)
    assert list(pixels.shape) == summary['shape']
    (y0, y1), (x0, x1) = sample['array_slices']
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(pixels, cmap='gray', vmin=summary['min'], vmax=summary['max'],
        extent=(x0-.5, x1-.5, y1-.5, y0-.5), interpolation='nearest')
    ax.set(xlabel='Original source x (pixels)', ylabel='Original source y (pixels)',
        title=f'Native MCP raw sample {index+1}; no resampling')
    fig.tight_layout()
    fig.savefig(OUT / f'raw_sample_{index+1:02d}.png', dpi=160)
    if sample['route_key'] in identities:
        plate, _ = identities[sample['route_key']]
        selected = [r for r in rows if r['plate'] == plate]
        for color, row in zip(('cyan', 'yellow', 'magenta'), selected):
            ax.plot([row['x0_px'], row['x1_px']], [row['y0_px'], row['y1_px']],
                color=color, linewidth=1.5, marker='o', markersize=3)
            ax.text(row['x1_px']+7, (row['y0_px']+row['y1_px'])/2,
                f"{row['measurement_id']}: {row['width_px']:.0f} px / {row['width_um']:.1f} um",
                color=color, fontsize=9, va='center', bbox=dict(facecolor='black', alpha=.65, pad=2))
        ax.set_title(f'{plate} R02C02 field 1: apparent connecting microchannel widths')
        if selected:
            fig.savefig(OUT / f'{plate}_R02C02_microchannels_overlay.png', dpi=160)
    plt.close(fig)
    (OUT / f'raw_sample_{index+1:02d}.json').write_text(json.dumps(sample) + '\n')
(OUT / 'native_measurements.json').write_text(json.dumps(measurements, indent=2) + '\n')
for route, (plate, _) in identities.items():
    profiles = [r for r in measurements if not r['errors'] and r['coordinates']['route_key'] == route
        and r['measurement']['line_width'] == 5]
    if not profiles:
        continue
    fig, axes = plt.subplots(1, len(profiles), figsize=(12, 3.8))
    selected = [r for r in rows if r['plate'] == plate]
    for ax, result, row in zip(np.atleast_1d(axes), profiles, selected):
        m = result['measurement']
        ax.plot(np.array(m['profile_distance_data']) + m['vertices_yx'][0][0], m['profile_values'], '.-')
        for y in (row['y0_px'], row['y1_px']):
            ax.axvline(y, color='red', linewidth=1)
        ax.set(xlabel='Original y (pixels)', ylabel='Raw intensity (5-pixel band mean)',
            title=f"{row['measurement_id']}: {row['width_px']:.0f} px")
    fig.suptitle(f'{plate} R02C02: native transverse profiles and selected wall bands')
    fig.tight_layout()
    fig.savefig(OUT / f'{plate}_R02C02_profiles.png', dpi=160)
    plt.close(fig)
print(f'{len(samples)} raw samples, {len(measurements)} native measurements')
for plate in ('P1', 'P2', 'P3'):
    widths = [r['width_um'] for r in rows if r['plate'] == plate]
    if widths:
        print(plate, 'um', widths, 'mean', sum(widths)/len(widths))
