from datetime import datetime, timezone
from copy import deepcopy
import argparse
import csv
import json
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
import re
import subprocess
import sys
from lxml import etree as E
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'reviews/alyson_feedback.md'
REPORT = ROOT / 'reviews/ALYSON_FEEDBACK_CHECK_20261013.md'
OUTPUT = ROOT / 'reviews/alyson_feedback_annotated.docx'
BASELINE = ROOT / 'build/mfd_draft_v8_alyson_feedback.docx'
WORKING = ROOT / 'build/mfd_draft_v9_working.docx'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
XML = '{http://www.w3.org/XML/1998/namespace}'
E.register_namespace('w', W)
E.register_namespace('r', R)

parser = argparse.ArgumentParser()
parser.add_argument('--refresh-comments', action='store_true')
parser.add_argument('--format-existing', action='store_true')
parser.add_argument('--prepend-decisions', action='store_true')
parser.add_argument('--lead-with-findings', action='store_true')
parser.add_argument('--label-destinations', action='store_true')
parser.add_argument('--cache-page-numbers', type=Path)
parser.add_argument('--granular-comments', action='store_true')
parser.add_argument('--source-document', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
ANNOTATED = OUTPUT
if args.output is not None:
    OUTPUT = args.output.resolve()
REVIEW_ROWS = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_decisions.json').read_text())
CHECK_ROWS = {key: row['id'] for row in REVIEW_ROWS for key in row['checks']}
KENNEDY_PAPERS = (
    (9, 'Bélisle et al. (2008): LAPAP',
     'Bélisle, J. M., Correia, J. P., Wiseman, P. W., Kennedy, T. E., and Costantino, S. '
     '[Patterning protein concentration using laser-assisted adsorption by photobleaching, LAPAP]'
     '(https://pubs.rsc.org/en/content/articlelanding/2008/lc/b813897d). '
     '*Lab on a Chip* **8**, 2164–2167. DOI: [10.1039/B813897D](https://doi.org/10.1039/B813897D).',
     'This Communication presents and characterizes a protein-patterning method, with axon guidance as biological proof of principle. '
     'That method-first framing is relevant to V7: fabrication is the contribution, and neuronal culture demonstrates its use.'),
    (10, 'Roy et al. (2013): engineered culture substrates',
     'Roy, J., Kennedy, T. E., and Costantino, S. '
     '[Engineered cell culture substrates for axon guidance studies: moving beyond proof of concept]'
     '(https://pubs.rsc.org/en/content/articlelanding/2013/lc/c2lc41002h). '
     '*Lab on a Chip* **13**, 498–508. DOI: [10.1039/C2LC41002H](https://doi.org/10.1039/C2LC41002H).',
     'This Critical Review examines biological insights from engineered substrates for axon guidance. '
     'It provides context for the neuronal application and for making engineered substrates useful in biological research.'),
)


def table_handles(text):
    def replace(match):
        first = match[1]
        if first not in CHECK_ROWS:
            return match[0]
        if first == 'E18' and re.match(r'\s+(?:rat|embryo)\b', text[match.end():]):
            return match[0]
        last = int(match[3]) if match[3] else int(first[1:])
        group = match[2] or first[0]
        if group != first[0]:
            raise ValueError('Check range crosses groups: ' + match[0])
        return ' / '.join(dict.fromkeys(CHECK_ROWS[f'{group}{i:02d}']
                                       for i in range(int(first[1:]), last + 1)))
    return re.sub(r'\b([A-F]\d{2})(?:[-–](?:([A-F])?(\d{2})))?\b', replace, text)


def link_checks_to_rows(document, comments):
    for tree in (document, comments):
        for link in tree.iter(w('hyperlink')):
            match = re.fullmatch(r'evidence_([A-F]\d{2})', link.get(w('anchor'), ''))
            if match is None:
                continue
            para = next(link.iterancestors(w('p')))
            style = para.find('./' + w('pPr') + '/' + w('pStyle'))
            if style is not None and style.get(w('val')) == 'SourceQuote':
                continue
            if match[1] == 'E18' and re.search(r'\bE18\s+(?:rat|embryo)\b', ''.join(para.itertext())):
                parent = link.getparent()
                index = parent.index(link)
                for run in list(link):
                    for prop in list(run.findall('./' + w('rPr') + '/*')):
                        if prop.tag in (w('u'), w('color'), w('rStyle')):
                            prop.getparent().remove(prop)
                    parent.insert(index, run)
                    index += 1
                parent.remove(link)
                continue
            row = CHECK_ROWS[match[1]]
            link.set(w('anchor'), 'change_' + row)
            texts = list(link.iter(w('t')))
            texts[0].text = row
            for node in texts[1:]:
                node.text = ''
            for color in link.iter(w('color')):
                color.set(w('val'), '222222')
        manuscript = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_comparison.json').read_text())['documents']
        quoted_texts = {text for draft in manuscript.values() for text in draft['paragraphs']}
        quoted_texts.update(item['text'] for item in json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_opening.json').read_text()) if item.get('quote'))
        for para in tree.iter(w('p')):
            style = para.find('./' + w('pPr') + '/' + w('pStyle'))
            if style is not None and style.get(w('val')) == 'SourceQuote':
                continue
            text = ''.join(para.xpath('.//w:t/text()', namespaces={'w': W}))
            # E18 is also an embryo age, and B27 is a culture supplement.
            if text in quoted_texts or re.search(r'\bE18\s+(?:rat|embryo)\b', text):
                continue
            for node in para.iter(w('t')):
                if node.text:
                    node.text = table_handles(node.text)
        for para in tree.iter(w('p')):
            previous = None
            between = []
            for child in list(para):
                if child.tag == w('hyperlink'):
                    if previous is not None and child.get(w('anchor')) == previous.get(w('anchor')):
                        for separator in between:
                            para.remove(separator)
                        para.remove(child)
                    else:
                        previous = child
                    between = []
                elif child.tag == w('r') and ''.join(child.itertext()).strip() in ('', '·', '/', '-', 'and'):
                    between.append(child)
                else:
                    previous = None
                    between = []


def w(name):
    return '{' + W + '}' + name


def xml(node):
    return E.tostring(node, encoding='utf-8', xml_declaration=True)


def sub(parent, tag, **attrs):
    return E.SubElement(parent, w(tag), {w(k): str(v) for k, v in attrs.items()})


def text_run(parent, text, small=False):
    run = sub(parent, 'r')
    if small:
        props = sub(run, 'rPr')
        sub(props, 'sz', val=16)
        sub(props, 'color', val='666666')
    pieces = text.split('\t')
    for index, piece in enumerate(pieces):
        item = sub(run, 't')
        item.set(XML + 'space', 'preserve')
        item.text = piece
        if index + 1 < len(pieces):
            sub(run, 'tab')
    return run


def paragraph(parent, text, style=None):
    item = sub(parent, 'p')
    props = sub(item, 'pPr')
    if style:
        sub(props, 'pStyle', val=style)
    sub(props, 'spacing', after=80, line=240, lineRule='auto')
    text_run(item, text)
    return item


def internal_link(parent, label, anchor, color='0563C1'):
    link = sub(parent, 'hyperlink', anchor=anchor)
    run = text_run(link, label)
    props = E.Element(w('rPr'))
    sub(props, 'u', val='single')
    sub(props, 'color', val=color)
    run.insert(0, props)


def page_reference(parent, anchor):
    sub(sub(parent, 'r'), 'fldChar', fldCharType='begin', dirty='true')
    instruction = sub(sub(parent, 'r'), 'instrText')
    instruction.set(XML + 'space', 'preserve')
    instruction.text = f' PAGEREF {anchor} \\h '
    sub(sub(parent, 'r'), 'fldChar', fldCharType='separate')
    text_run(parent, '1')
    sub(sub(parent, 'r'), 'fldChar', fldCharType='end')


def reference_anchor(name, number):
    if name == 'feedback':
        return f'src_L{number:03d}'
    if name in ('v7', 'v8'):
        return f'cmp_{name}_P{number}'
    if name == 'evidence':
        return 'change_' + CHECK_ROWS[number]
    if name == 'published':
        return f'published_paper_{number}' if number else 'published_comparisons'
    if name == 'measurement':
        return 'channel_measurements'
    if name == 'change':
        return 'change_' + number
    if name == 'source':
        return 'sources_' + number
    raise ValueError('Unknown reference kind: ' + name)


def reference_label(name, number):
    if name == 'feedback':
        return f'Feedback L{number}'
    if name in ('v7', 'v8'):
        return f'{name.upper()} P{number}'
    if name == 'evidence':
        return CHECK_ROWS[number]
    if name == 'published':
        return f'Paper {number}' if number else 'Published examples'
    if name == 'measurement':
        return 'Width data'
    if name == 'change':
        return number
    if name == 'source':
        return 'Sources ' + number
    raise ValueError('Unknown reference kind: ' + name)


def space_handles(tree):
    # Spaces are outside the underlined link; each short handle stays together.
    for link in list(tree.iter(w('hyperlink'))):
        if link.get(w('anchor')) is None:
            continue
        texts = list(link.iter(w('t')))
        if not texts:
            continue
        label = ''.join(node.text or '' for node in texts).strip()
        if re.fullmatch(r'(?:V[78] P\d+|Feedback L\d+|Sources R\d{2}|[A-FR]\d{2}|Width data|Published examples|Paper \d+)', label):
            texts[0].text = label.replace(' ', '\u00a0')
            for node in texts[1:]:
                node.text = ''
        parent = link.getparent()
        siblings = list(parent)
        position = siblings.index(link)
        next_link = next((i for i in range(position + 1, len(siblings))
                          if siblings[i].tag == w('hyperlink')), None)
        if next_link is None:
            continue
        between = siblings[position + 1:next_link]
        if any(node.tag != w('r') or ''.join(node.itertext()).strip() not in ('', '·') for node in between):
            continue
        for node in between:
            parent.remove(node)
        spacer = text_run(E.Element('holder'), '    ')
        source_props = link.find('./' + w('r') + '/' + w('rPr'))
        props = deepcopy(source_props) if source_props is not None else E.Element(w('rPr'))
        spacer.insert(0, props)
        underline = props.find(w('u'))
        if underline is None:
            underline = sub(props, 'u')
        underline.set(w('val'), 'none')
        parent.insert(parent.index(link) + 1, spacer)


def link_handles_in_prose(document, comments, compared):
    pattern = re.compile(r'\b(v[78])\s+P(\d+)\b|\bFeedback\s+L(\d+)\b|\bL(\d+)\b|\bP(\d+)\b|\b(R\d{2})\b|\b(Width data)\b|\bSources\s+(R\d{2})\b|\b(Pin-height CSV|Separate supplement(?: \(DOCX/PDF\))?)(?!\w)', re.I)
    names = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    templates = {}
    for tree in (document, comments):
        for link in tree.iter(w('hyperlink')):
            if link.get(w('anchor')):
                templates.setdefault(link.get(w('anchor')), link)
    changed = removed = 0
    for tree in (document, comments):
        for para in tree.iter(w('p')):
            style = para.find('./' + w('pPr') + '/' + w('pStyle'))
            if style is not None and style.get(w('val'), '').startswith('Heading'):
                continue
            quoted = style is not None and style.get(w('val')) == 'SourceQuote'
            if quoted:
                continue
            trailing = []
            for node in reversed(list(para)):
                if node.tag == w('hyperlink'):
                    trailing.append(node)
                elif node.tag == w('r') and not ''.join(node.itertext()).strip(' \u00a0\t\n·'):
                    continue
                elif node.tag in (w('bookmarkStart'), w('bookmarkEnd')):
                    continue
                else:
                    break
            local_templates = {link.get(w('anchor')): link for link in para.iter(w('hyperlink'))}
            linked = set()
            # Keep run formatting while turning handles split across runs into one link.
            groups, group = [], []
            for node in para:
                plain = node.tag == w('r') and node.findall(w('t')) and all(child.tag in (w('rPr'), w('t')) for child in node)
                if plain:
                    group.append(node)
                elif group:
                    groups.append(group)
                    group = []
            if group:
                groups.append(group)
            for group in groups:
                spans, cursor = [], 0
                for run in group:
                    value = ''.join(run.xpath('./w:t/text()', namespaces={'w': W}))
                    spans.append((cursor, cursor + len(value), run, value))
                    cursor += len(value)
                value = ''.join(span[3] for span in spans)
                matches = list(pattern.finditer(value))
                if not matches:
                    continue
                prefix = ''.join(text.text or '' for node in list(para)[:para.index(group[0])] for text in node.iter(w('t')))
                holder = E.Element('holder')
                def append_slice(parent, start, stop):
                    for left, right, run, text in spans:
                        begin, end = max(start, left), min(stop, right)
                        if begin >= end:
                            continue
                        clone = deepcopy(run)
                        for child in list(clone):
                            if child.tag != w('rPr'):
                                clone.remove(child)
                        node = sub(clone, 't')
                        node.text = text[begin - left:end - left]
                        node.set(XML + 'space', 'preserve')
                        parent.append(clone)
                cursor = 0
                for match in matches:
                    if match[5] and (quoted or match[0][0] != 'P'):
                        continue
                    if match[1]:
                        anchor = f'cmp_{match[1].lower()}_P{int(match[2])}'
                    elif match[3] or match[4]:
                        anchor = f'src_L{int(match[3] or match[4]):03d}'
                    elif match[6]:
                        anchor = 'change_' + match[6].upper()
                    elif match[7]:
                        anchor = 'channel_measurements'
                    elif match[8]:
                        anchor = reference_anchor('source', match[8].upper())
                    elif match[9]:
                        anchor = reference_anchor('source', 'R58')
                    else:
                        drafts = re.findall(r'\bv[78]\b', prefix + value[:match.start()], re.I)
                        if not drafts:
                            continue
                        anchor = f'cmp_{drafts[-1].lower()}_P{int(match[5])}'
                    # Labels at their own destination are not navigation links.
                    if anchor not in names or para.xpath('.//w:bookmarkStart[@w:name="' + anchor + '"]', namespaces={'w': W}):
                        continue
                    append_slice(holder, cursor, match.start())
                    template = local_templates.get(anchor)
                    if template is None:
                        template = templates.get(anchor)
                    color_node = template.find('.//' + w('color')) if template is not None else None
                    color = color_node.get(w('val')) if color_node is not None else '222222'
                    if match[1] and template is None:
                        color = wording_color(compared, match[1].lower(), int(match[2]))
                    link = sub(holder, 'hyperlink', anchor=anchor)
                    append_slice(link, match.start(), match.end())
                    for run in link:
                        props = run.find(w('rPr'))
                        if props is None:
                            props = E.Element(w('rPr'))
                            run.insert(0, props)
                        for tag, val in (('u', 'single'), ('color', color)):
                            node = props.find(w(tag))
                            if node is None:
                                node = sub(props, tag)
                            node.set(w('val'), val)
                    linked.add(anchor)
                    changed += 1
                    cursor = match.end()
                if not len(holder):
                    continue
                append_slice(holder, cursor, len(value))
                position = para.index(group[0])
                for run in group:
                    para.remove(run)
                for offset, node in enumerate(list(holder)):
                    para.insert(position + offset, node)
            for link in trailing:
                if link.get(w('anchor')) in linked:
                    para.remove(link)
                    removed += 1
            if linked:
                blanks = []
                for node in list(para) + [None]:
                    if node is not None and node.tag == w('r') and node.findall(w('t')) and not ''.join(node.itertext()).strip():
                        blanks.append(node)
                        continue
                    if blanks and sum(len(''.join(run.itertext())) for run in blanks) > 4:
                        blanks[0].find(w('t')).text = '    '
                        for run in blanks[1:]:
                            para.remove(run)
                    blanks = []
    for cell in document.iter(w('tc')):
        earlier = set()
        for para in list(cell.findall(w('p'))):
            links = list(para.iter(w('hyperlink')))
            plain = ''.join(node.text or '' for run in para.findall(w('r')) for node in run.iter(w('t')))
            if links and not plain.strip(' \u00a0\t\n·/'):
                for link in links:
                    if link.get(w('anchor')) in earlier:
                        para.remove(link)
                        removed += 1
                if not list(para.iter(w('hyperlink'))) and not list(para.iter(w('bookmarkStart'))):
                    cell.remove(para)
            earlier.update(link.get(w('anchor')) for link in para.iter(w('hyperlink')))
    for comment in comments:
        earlier = set()
        for para in list(comment):
            if ''.join(para.itertext()).startswith('Links: '):
                for link in list(para.iter(w('hyperlink'))):
                    if link.get(w('anchor')) in earlier:
                        para.remove(link)
                        removed += 1
                if not list(para.iter(w('hyperlink'))):
                    comment.remove(para)
                else:
                    links = list(para.iter(w('hyperlink')))
                    for child in list(para):
                        if child.tag != w('pPr'):
                            para.remove(child)
                    text_run(para, 'Links: ')
                    for index, link in enumerate(links):
                        if index:
                            text_run(para, '    ')
                        para.append(link)
            else:
                earlier.update(link.get(w('anchor')) for link in para.iter(w('hyperlink')))
    print('Linked', changed, 'handles in prose; removed', removed, 'repeated trailing links.')


def shade_comment_sources(document, comments):
    labels = {node.get(w('id')): ''.join(node.find(w('p')).itertext()).rstrip('.') for node in comments}
    active, spans, lengths = set(), [], {}
    for node in document.iter():
        if node.tag == w('commentRangeStart'):
            active.add(node.get(w('id')))
        elif node.tag == w('commentRangeEnd'):
            active.remove(node.get(w('id')))
        elif node.tag == w('r') and node.findall(w('t')) and active:
            spans.append((node, tuple(active)))
            length = sum(len(text.text or '') for text in node.findall(w('t')))
            for identifier in active:
                lengths[identifier] = lengths.get(identifier, 0) + length
    if active:
        raise ValueError('Unclosed comment ranges')
    for run, identifiers in spans:
        # A specific phrase can have a different answer from the surrounding sentence.
        shortest = min(lengths[identifier] for identifier in identifiers)
        kinds = {labels[identifier] for identifier in identifiers if lengths[identifier] == shortest}
        if len(kinds) != 1:
            raise ValueError('Same source span has conflicting comment colors')
        color, fill = COMMENT_PALETTES[next(iter(kinds))]
        props = run.find(w('rPr'))
        if props is None:
            props = E.Element(w('rPr'))
            run.insert(0, props)
        shade = props.find(w('shd'))
        if shade is None:
            shade = sub(props, 'shd')
        shade.set(w('val'), 'clear')
        shade.set(w('fill'), fill)
        foreground = props.find(w('color'))
        if foreground is None:
            foreground = sub(props, 'color')
        foreground.set(w('val'), color)
    print('Colored', len(spans), 'commented source runs from their comment types.')


COMMENT_PALETTES = {
    'In V7 only': ('175DA0', 'EAF2FB'),
    'In V7 and V8': ('246B40', 'EAF5ED'),
    'In V8 only': ('925400', 'FFF1D9'),
    'Not supplied in V7 or V8': ('555555', 'EEEEEE'),
    'Not a paper claim': ('555555', 'EEEEEE'),
}


def wording_color(compared, name, position, excerpt=None):
    source = compared[name]['paragraphs'][position - 1]
    whole_paragraph = excerpt is None
    excerpt = source if excerpt is None else excerpt
    if not excerpt or excerpt not in source:
        raise ValueError('Finding quote no longer matches its source')
    source_is_main = position <= compared[name]['paragraphs'].index('Supplementary Information')
    presence = []
    for document_name in ('v7', 'v8'):
        corpus = compared[document_name]['paragraphs']
        if source_is_main:
            corpus = corpus[:corpus.index('Supplementary Information')]
        presence.append(any(excerpt == text if whole_paragraph else excerpt in text for text in corpus))
    label = {(True, False): 'In V7 only', (True, True): 'In V7 and V8',
             (False, True): 'In V8 only'}.get(tuple(presence))
    if label is None:
        raise ValueError('Finding wording is absent from both sources')
    return COMMENT_PALETTES[label][0]


def matching_passage(compared, name, position):
    text = compared[name]['paragraphs'][position - 1]
    other = 'v8' if name == 'v7' else 'v7'
    boundary = compared[name]['paragraphs'].index('Supplementary Information')
    other_boundary = compared[other]['paragraphs'].index('Supplementary Information')
    matches = [index + 1 for index, value in enumerate(compared[other]['paragraphs'])
               if text and value == text and (index <= other_boundary) == (position - 1 <= boundary)]
    return (other, matches[0]) if len(matches) == 1 else None


def pair_shared_passage_links(document, comments, compared):
    names = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    count = 0
    for tree in (document, comments):
        for para in tree.iter(w('p')):
            targets = {link.get(w('anchor')) for link in para.iter(w('hyperlink'))}
            for link in list(para.iter(w('hyperlink'))):
                source = re.fullmatch(r'cmp_(v[78])_P(\d+)', link.get(w('anchor'), ''))
                if source is None:
                    continue
                match = matching_passage(compared, source[1], int(source[2]))
                if match is None:
                    continue
                anchor = reference_anchor(*match)
                if anchor in targets:
                    continue
                if anchor not in names:
                    raise ValueError('Shared passage is not embedded: ' + anchor)
                holder = E.Element('holder')
                text_run(holder, ' / ')
                internal_link(holder, reference_label(*match), anchor)
                index = para.index(link) + 1
                for offset, node in enumerate(list(holder)):
                    para.insert(index + offset, node)
                targets.add(anchor)
                count += 1
    print('Paired', count, 'unchanged passage links with their other draft.')


def color_source_links(document, comments, compared, source_categories):
    for tree in (document, comments):
        for link in tree.iter(w('hyperlink')):
            anchor = link.get(w('anchor'), '')
            source = re.fullmatch(r'cmp_(v[78])_P(\d+)', anchor)
            if source is not None:
                color = wording_color(compared, source[1], int(source[2]))
            else:
                categories = source_categories.get(anchor, set())
                color = COMMENT_PALETTES[next(iter(categories))][0] if len(categories) == 1 else '222222'
                if color == '555555':
                    color = '222222'
            for run in link.iter(w('r')):
                props = run.find(w('rPr'))
                if props is None:
                    props = E.Element(w('rPr'))
                    run.insert(0, props)
                node = props.find(w('color'))
                if node is None:
                    node = sub(props, 'color')
                node.set(w('val'), color)
                underline = props.find(w('u'))
                if underline is None:
                    underline = sub(props, 'u')
                underline.set(w('val'), 'single')


def order_reference_sections(parts):
    document = E.fromstring(parts['word/document.xml'])
    body = document.find(w('body'))
    nodes = list(body)
    def position(title):
        matches = [i for i, node in enumerate(nodes)
                   if node.tag == w('p') and ''.join(node.xpath('.//w:t/text()', namespaces={'w': W})) == title]
        if len(matches) != 1:
            raise ValueError('Reference section is missing or ambiguous: ' + title)
        return matches[0]
    exact = position('Cited V7 and V8 passages')
    feedback = position('Feedback suggestions and review comments')
    after = position('Additional source passages')
    if exact < feedback:
        if feedback >= after:
            raise ValueError('Unexpected end of the commented discussion')
        passages = nodes[exact:feedback]
        destination = nodes[after]
        for node in passages:
            body.remove(node)
        for node in passages:
            body.insert(body.index(destination), node)
    parts['word/document.xml'] = xml(document)


def extend_change_table(document, decisions):
    expected = [row['id'] for row in decisions]
    candidates = []
    for table in document.find(w('body')).findall(w('tbl')):
        rows = table.findall(w('tr'))
        ids = [''.join(row.find(w('tc')).xpath('.//w:t/text()', namespaces={'w': W})) for row in rows[1:]]
        if len(ids) >= 52 and ids == expected[:len(ids)]:
            candidates.append(table)
    if len(candidates) != 1:
        raise ValueError('The existing review table is missing or ambiguous')
    table = candidates[0]
    rows = table.findall(w('tr'))
    template = rows[-1]
    labels = {'remaining': 'Remaining: ', 'supplied': 'Supplied: ', 'optional': 'Optional: ', 'draft': ''}
    for decision in decisions[len(rows) - 1:]:
        row = sub(table, 'tr')
        props = template.find(w('trPr'))
        if props is not None:
            row.append(deepcopy(props))
        values = [decision['id'], labels[decision['kind']] + decision['title'], decision['decision'], decision['reason']]
        for original, value in zip(template.findall(w('tc')), values):
            cell = sub(row, 'tc')
            props = original.find(w('tcPr'))
            if props is not None:
                cell.append(deepcopy(props))
            para = paragraph(cell, value)
            props = original.find('./' + w('p') + '/' + w('pPr'))
            if props is not None:
                para.remove(para.find(w('pPr')))
                para.insert(0, deepcopy(props))


def link_change_rows(document, decisions):
    body = document.find(w('body'))
    def text_of(node):
        return ''.join(node.xpath('.//w:t/text()', namespaces={'w': W}))
    tables = [table for table in body.findall(w('tbl'))
              if [text_of(row.find(w('tc'))) for row in table.findall(w('tr'))[1:]] == [row['id'] for row in decisions]]
    if len(tables) != 1:
        raise ValueError('Change table is missing or ambiguous')
    table = tables[0]
    names = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    next_id = max(int(node.get(w('id'))) for node in document.iter(w('bookmarkStart'))) + 1
    def bookmark(para, name):
        nonlocal next_id
        if name in names:
            return
        start = E.Element(w('bookmarkStart'), {w('name'): name, w('id'): str(next_id)})
        end = E.Element(w('bookmarkEnd'), {w('id'): str(next_id)})
        first = next((i for i, node in enumerate(para) if node.tag != w('pPr')), len(para))
        para.insert(first, start)
        para.append(end)
        names.add(name)
        next_id += 1
    first_summary = {}
    for node in list(body)[:body.index(table)]:
        for link in node.iter(w('hyperlink')):
            target = link.get(w('anchor'), '')
            if target.startswith('change_'):
                row_id = target.removeprefix('change_')
                if row_id not in first_summary:
                    anchor = 'summary_change_' + row_id
                    bookmark(node, anchor)
                    first_summary[row_id] = anchor
    for row, decision in zip(table.findall(w('tr'))[1:], decisions):
        cell = row.findall(w('tc'))[3]
        for sources in list(cell.findall(w('p')))[1:]:
            links = list(sources.iter(w('hyperlink')))
            if links and all(re.fullmatch(r'cmp_v[78]_P\d+', link.get(w('anchor'), '')) for link in links):
                plain = ''.join(node.text or '' for run in sources.findall(w('r')) for node in run.iter(w('t')))
                if not plain.strip(' \u00a0\t\n·/'):
                    if sources.xpath('.//w:bookmarkStart|.//w:bookmarkEnd|.//w:commentRangeStart|.//w:commentRangeEnd', namespaces={'w': W}):
                        raise ValueError('Preserve annotations on table passages: ' + decision['id'])
                    cell.remove(sources)
        linked = {link.get(w('anchor')) for link in cell.iter(w('hyperlink'))}
        passages = [(draft, number) for draft in ('v7', 'v8') for number in decision[draft]
                    if reference_anchor(draft, number) not in linked]
        if passages:
            sources = paragraph(cell, '')
            for draft, number in passages:
                anchor = reference_anchor(draft, number)
                if anchor not in names:
                    raise ValueError('Table source passage is missing: ' + anchor)
                internal_link(sources, reference_label(draft, number), anchor)
                text_run(sources, '    ')
        if decision['id'] == 'R58':
            replacements = {
                'supplementary/pin_z_variability_raw_mm.csv': 'Pin-height CSV',
                'pi_review_20261002/openmfd_supplement.docx': 'Separate supplement (DOCX/PDF)',
            }
            for node in cell.iter(w('t')):
                for source, label in replacements.items():
                    if node.text:
                        node.text = node.text.replace(source, label)
        para = row.find(w('tc')).find(w('p'))
        row_id = decision['id']
        if row_id in first_summary and para.find(w('hyperlink')) is None:
            runs = para.findall(w('r'))
            if len(runs) != 1 or text_of(runs[0]) != row_id:
                raise ValueError('Preserve changed row label: ' + row_id)
            run = runs[0]
            position = para.index(run)
            para.remove(run)
            holder = E.Element('holder')
            internal_link(holder, row_id, first_summary[row_id], color='222222')
            para.insert(position, holder[0])
        bookmark(para, 'change_' + row_id)


def add_change_feedback(document, decisions):
    body = document.find(w('body'))
    def text_of(node):
        return ''.join(node.xpath('.//w:t/text()', namespaces={'w': W}))
    tables = [table for table in body.findall(w('tbl'))
              if [text_of(row.find(w('tc'))) for row in table.findall(w('tr'))[1:]] == [row['id'] for row in decisions]]
    if len(tables) != 1:
        raise ValueError('Change table is missing or ambiguous')
    names = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    next_id = max(int(node.get(w('id'))) for node in document.iter(w('bookmarkStart'))) + 1
    count = 0
    for row, decision in zip(tables[0].findall(w('tr'))[1:], decisions):
        cell = row.findall(w('tc'))[3]
        marker = 'change_feedback_' + decision['id']
        owned = [p for p in cell.findall(w('p'))
                 if p.xpath('.//w:bookmarkStart[@w:name="' + marker + '"]', namespaces={'w': W})]
        if len(owned) > 1:
            raise ValueError('Duplicate feedback block: ' + marker)
        for para in owned:
            if para.xpath('.//w:commentRangeStart', namespaces={'w': W}):
                raise ValueError('Preserve annotations on ' + marker)
            cell.remove(para)
        linked = {link.get(w('anchor')) for link in cell.iter(w('hyperlink'))}
        passages = [(draft, number) for draft in ('v7', 'v8') for number in decision[draft]
                    if reference_anchor(draft, number) not in linked]
        if passages:
            sources = paragraph(cell, '')
            for draft, number in passages:
                anchor = reference_anchor(draft, number)
                if anchor not in names:
                    raise ValueError('Table source passage is missing: ' + anchor)
                internal_link(sources, reference_label(draft, number), anchor)
                text_run(sources, '    ')
        if not decision.get('feedback'):
            continue
        para = paragraph(cell, 'Related feedback: ')
        sub(para, 'bookmarkStart', id=next_id, name=marker)
        sub(para, 'bookmarkEnd', id=next_id)
        next_id += 1
        for line in decision['feedback']:
            anchor = reference_anchor('feedback', line)
            if anchor not in names:
                raise ValueError('Feedback target is missing: ' + anchor)
            internal_link(para, reference_label('feedback', line), anchor)
            text_run(para, '    ')
        for run in para.iter(w('r')):
            props = run.find(w('rPr'))
            if props is None:
                props = E.Element(w('rPr'))
                run.insert(0, props)
            sub(props, 'sz', val=18)
        count += 1
    print('Added direct feedback links to', count, 'change-table rows.')


def add_contents(parts):
    document = E.fromstring(parts['word/document.xml'])
    body = document.find(w('body'))
    start = next((node for node in body if node.xpath('.//w:bookmarkStart[@w:name="review_contents"]', namespaces={'w': W})), None)
    stop = next((node for node in body if node.xpath('.//w:bookmarkStart[@w:name="review_contents_end"]', namespaces={'w': W})), None)
    if (start is None) != (stop is None):
        raise ValueError('Contents block has only one boundary')
    if start is not None:
        owned = list(body)[body.index(start):body.index(stop) + 1]
        if any(node.xpath('.//w:commentRangeStart', namespaces={'w': W}) for node in owned):
            raise ValueError('Preserve user annotations before rebuilding contents')
        for node in owned:
            body.remove(node)
    headings = {}
    for node in body.findall(w('p')):
        style = node.find('./' + w('pPr') + '/' + w('pStyle'))
        if style is not None and style.get(w('val')) == 'Heading1':
            headings.setdefault(''.join(node.xpath('.//w:t/text()', namespaces={'w': W})), []).append(node)
    groups = [
        ('Comparison', [
            ('Already covered in V7 (details)', '1. Points already covered in V7', 'nav_covered'),
            ('Useful V8 edits (details)', '2. Useful V8 edits', 'nav_useful'),
            ('Work still needed (details)', '3. Work still needed after combining V7 with useful V8 edits', 'nav_remaining'),
            ('Lost explanations and added warnings (details)', '4. V8 changes the feedback did not identify as losses or unnecessary additions', 'nav_losses'),
            ('Revision table (leave comments here)', 'Changes and remaining work', 'change_R01'),
        ]),
        ('Reference material (mostly accessed via links)', [
            ('Alyson’s ChatGPT discussion, with comments', 'Source transcript', 'nav_transcript'),
            ('Cited V7 and V8 passages', 'Cited V7 and V8 passages', 'nav_passages'),
            ('Additional sources and images', 'Additional sources and images', 'detailed_evidence'),
            ('Published Lab on a Chip comparisons', 'Published Lab on a Chip comparisons', 'published_comparisons'),
        ]),
    ]
    names = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    next_id = max(int(node.get(w('id'))) for node in document.iter(w('bookmarkStart'))) + 1
    def bookmark(node, name):
        nonlocal next_id
        sub(node, 'bookmarkStart', id=next_id, name=name)
        sub(node, 'bookmarkEnd', id=next_id)
        next_id += 1
    entries = [entry for _, group_entries in groups for entry in group_entries]
    nodes = list(body)
    for index, (_, target, anchor) in enumerate(entries):
        if len(headings.get(target, [])) != 1:
            raise ValueError('Contents target is missing or ambiguous: ' + target)
        end_anchor = anchor + '_end'
        if anchor == 'change_R01':
            first_row = next(node for node in document.iter(w('bookmarkStart'))
                             if node.get(w('name')) == anchor)
            table = next(first_row.iterancestors(w('tbl')))
            paragraphs = [p for p in table.iter(w('p'))
                          if p.xpath('.//w:t', namespaces={'w': W})]
            for old in list(document.iter(w('bookmarkStart'))):
                if old.get(w('name')) != end_anchor:
                    continue
                old_end = next(node for node in document.iter(w('bookmarkEnd'))
                               if node.get(w('id')) == old.get(w('id')))
                old_end.getparent().remove(old_end)
                old.getparent().remove(old)
        else:
            if end_anchor in names:
                continue
            first = body.index(headings[target][0])
            last = body.index(headings[entries[index + 1][1]][0]) if index + 1 < len(entries) else len(nodes)
            paragraphs = [p for node in nodes[first:last] for p in node.iter(w('p'))
                          if p.xpath('.//w:t', namespaces={'w': W})]
        para = paragraphs[-1]
        last_text = next(node for node in reversed(list(para))
                         if ''.join(node.xpath('.//w:t/text()', namespaces={'w': W})).strip())
        begin = E.Element(w('bookmarkStart'), {w('id'): str(next_id), w('name'): end_anchor})
        para.insert(para.index(last_text), begin)
        para.insert(para.index(last_text) + 1, E.Element(w('bookmarkEnd'), {w('id'): str(next_id)}))
        next_id += 1
        names.add(end_anchor)
    holder = E.Element('holder')
    title = paragraph(holder, 'Contents', 'Heading2')
    bookmark(title, 'review_contents')
    for group, entries in groups:
        heading = paragraph(holder, group)
        heading_run = heading.find(w('r'))
        props = E.Element(w('rPr'))
        heading_run.insert(0, props)
        sub(props, 'b')
        table = sub(holder, 'tbl')
        props = sub(table, 'tblPr')
        sub(props, 'tblW', w=9360, type='dxa')
        sub(props, 'tblLayout', type='fixed')
        margins = sub(props, 'tblCellMar')
        for edge in ('left', 'right', 'top', 'bottom'):
            sub(margins, edge, w=0, type='dxa')
        grid = sub(table, 'tblGrid')
        for width in (7200, 2160):
            sub(grid, 'gridCol', w=width)
        for label, target, anchor in entries:
            matches = headings.get(target, [])
            if len(matches) != 1:
                raise ValueError('Contents target is missing or ambiguous: ' + target)
            if anchor not in names:
                bookmark(matches[0], anchor)
                names.add(anchor)
            row = sub(table, 'tr')
            sub(sub(row, 'trPr'), 'cantSplit')
            cells = []
            for width in (7200, 2160):
                cell = sub(row, 'tc')
                sub(sub(cell, 'tcPr'), 'tcW', w=width, type='dxa')
                item = paragraph(cell, '')
                item.find(w('pPr')).find(w('spacing')).set(w('after'), '50')
                cells.append(item)
            internal_link(cells[0], label, anchor, color='222222')
            if anchor == 'change_R01':
                text_run(cells[0], '  \u2190')
            item = cells[1]
            sub(item.find(w('pPr')), 'jc', val='right')
            text_run(item, ('\u2192  ' if anchor == 'change_R01' else '') + 'p. ')
            page_reference(item, anchor)
            text_run(item, '–')
            page_reference(item, anchor + '_end')
            for cell in cells:
                for run in cell.iter(w('r')):
                    props = run.find(w('rPr'))
                    if props is None:
                        props = E.Element(w('rPr'))
                        run.insert(0, props)
                    sub(props, 'sz', val=22)
                    if anchor == 'change_R01':
                        sub(props, 'b')
    end = paragraph(holder, '')
    bookmark(end, 'review_contents_end')
    for node in list(holder)[:-2]:
        for para in node.iter(w('p')):
            sub(para.find(w('pPr')), 'keepNext')
    guide = next((node for node in body if ''.join(node.xpath('.//w:t/text()', namespaces={'w': W})) == 'Reading guide'), None)
    first_comparison = next((node for node in body if ''.join(node.xpath('.//w:t/text()', namespaces={'w': W})) == '1. Points already covered in V7'), None)
    key = next((node for node in body if node.xpath('.//w:bookmarkStart[@w:name="comment_color_key"]', namespaces={'w': W})), None)
    insertion = body.index(key if key is not None else first_comparison) if guide is not None and first_comparison is not None else 1
    for index, node in enumerate(list(holder), insertion):
        body.insert(index, node)
    parts['word/document.xml'] = xml(document)


def add_intro_links(parts):
    document = E.fromstring(parts['word/document.xml'])
    body = document.find(w('body'))
    names = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    opening = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_opening.json').read_text())
    for item in opening:
        links = item.get('links', [])
        if not links:
            continue
        matches = [para for para in body.findall(w('p'))
                   if ''.join(para.xpath('.//w:t/text()', namespaces={'w': W})) == item['text']]
        if len(matches) != 1:
            raise ValueError('Intro paragraph is missing or changed: ' + item['text'])
        para = matches[0]
        if para.xpath('.//w:commentRangeStart|.//w:bookmarkStart', namespaces={'w': W}):
            raise ValueError('Preserve annotations on the intro paragraph')
        for child in list(para):
            if child.tag != w('pPr'):
                para.remove(child)
        cursor = 0
        for link in links:
            label, anchor = link['text'], link['anchor']
            if anchor not in names:
                raise ValueError('Intro destination is missing: ' + anchor)
            position = item['text'].index(label, cursor)
            text_run(para, item['text'][cursor:position])
            internal_link(para, label, anchor, color='222222')
            text_run(para, ' (pp. ' if anchor == 'change_R01' else ' (p. ')
            page_reference(para, anchor)
            if anchor == 'change_R01':
                if anchor + '_end' not in names:
                    raise ValueError('Table-end destination is missing')
                text_run(para, '\u2013')
                page_reference(para, anchor + '_end')
            text_run(para, ')')
            cursor = position + len(label)
        text_run(para, item['text'][cursor:])
    parts['word/document.xml'] = xml(document)


def cache_page_numbers():
    source = args.source_document.resolve()
    if (OUTPUT.parent / ('.~lock.' + OUTPUT.name + '#')).exists():
        raise ValueError('Output is open; preserve unsaved work')
    opening = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_opening.json').read_text())
    rendered = subprocess.check_output(['pdftotext', '-layout', str(args.cache_page_numbers), '-'], text=True)
    contents_title = re.search(r'(?m)^Contents[ \t]*$', rendered)
    if contents_title is None:
        raise ValueError('Rendered contents heading is missing')
    linked_text = re.sub(r'\s+', ' ', rendered)
    pages = {}
    navigation_page_count = 0
    for item in opening:
        for link in item.get('links', []):
            table_link = link['anchor'] == 'change_R01'
            pattern = r'\s*\(pp\.\s*(\d+)\s*[\u2013-]\s*(\d+)\)' if table_link else r'\s*\(p\.\s*(\d+)\)'
            matches = re.findall(re.escape(link['text']) + pattern, linked_text)
            if len(matches) != 1:
                raise ValueError('Rendered page reference is missing or ambiguous: ' + link['text'])
            if table_link:
                pages[link['anchor']], pages[link['anchor'] + '_end'] = matches[0]
                navigation_page_count += 2
            else:
                pages[link['anchor']] = matches[0]
                navigation_page_count += 1
    with ZipFile(source) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    document = E.fromstring(parts['word/document.xml'])
    remaining = len(rendered.split('\f')) - 1 - int(pages['change_R01_end'])
    if remaining < 0:
        raise ValueError('Table end exceeds the rendered page count')
    marker = next(node for node in document.iter(w('bookmarkStart'))
                  if node.get(w('name')) == 'remaining_support_pages')
    value = marker.getnext().find(w('t'))
    if value is None or marker.getnext().getnext().tag != w('bookmarkEnd'):
        raise ValueError('Remaining-page count marker has changed')
    value.text = str(remaining)
    body = document.find(w('body'))
    nodes = list(body)
    start = next(i for i, node in enumerate(nodes)
                 if node.xpath('.//w:bookmarkStart[@w:name="review_contents"]', namespaces={'w': W}))
    stop = next(i for i, node in enumerate(nodes)
                if node.xpath('.//w:bookmarkStart[@w:name="review_contents_end"]', namespaces={'w': W}))
    contents = []
    for node in nodes[start:stop]:
        for para in node.iter(w('p')):
            refs = [match[1] for instruction in para.iter(w('instrText'))
                    if (match := re.fullmatch(r'\s*PAGEREF\s+(\S+)\s+\\h\s*', instruction.text or ''))]
            if not refs:
                continue
            if refs != [refs[0], refs[0] + '_end']:
                raise ValueError('Unexpected contents page fields')
            contents.append((para, refs[0]))
    contents_end = rendered.find('Comment colors:', contents_title.end())
    if contents_end < 0:
        raise ValueError('Rendered contents boundary is missing')
    spans = re.findall(r'p\.\s*(\d+)\s*[–-]\s*(\d+)', rendered[contents_title.end():contents_end])
    if len(spans) != len(contents):
        raise ValueError('Rendered contents section lengths are missing or ambiguous')
    for (para, anchor), (first, last) in zip(contents, spans):
        length = int(last) - int(first) + 1
        if (anchor in pages and pages[anchor] != first) or length < 1:
            raise ValueError('Contents and reading guide disagree: ' + anchor)
        pages[anchor] = first
        for child in list(para):
            if child.tag != w('pPr'):
                para.remove(child)
        text_run(para, ('\u2192  ' if anchor == 'change_R01' else '') + 'p. ')
        page_reference(para, anchor)
        text_run(para, f' ({length} pages)')
        for run in para.iter(w('r')):
            props = E.Element(w('rPr'))
            run.insert(0, props)
            sub(props, 'sz', val=22)
            if anchor == 'change_R01':
                sub(props, 'b')
    count = 0
    for para in document.iter(w('p')):
        runs = list(para)
        for index, node in enumerate(runs):
            instruction = node.find(w('instrText'))
            if instruction is None:
                continue
            match = re.fullmatch(r'\s*PAGEREF\s+(\S+)\s+\\h\s*', instruction.text or '')
            if match is None or match[1] not in pages:
                continue
            separated, cached = False, []
            for run in runs[index + 1:]:
                field = run.find(w('fldChar'))
                if field is not None:
                    if field.get(w('fldCharType')) == 'end':
                        break
                    if field.get(w('fldCharType')) == 'separate':
                        separated = True
                elif separated:
                    cached.extend(run.findall(w('t')))
            if len(cached) != 1:
                raise ValueError('Unexpected page-field result: ' + match[1])
            cached[0].text = pages[match[1]]
            count += 1
    if count != navigation_page_count + len(contents):
        raise ValueError('Expected matching intro and contents page fields')
    parts['word/document.xml'] = xml(document)
    temporary = OUTPUT.with_suffix('.pages.docx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    temporary.replace(OUTPUT)
    print('Cached', count, 'native page-field results from the rendered document; field codes retained.')


def add_section_footer(parts):
    document = E.fromstring(parts['word/document.xml'])
    in_transcript = False
    for node in document.find(w('body')):
        text = ''.join(node.xpath('.//w:t/text()', namespaces={'w': W}))
        if text == 'Source transcript':
            in_transcript = True
            continue
        if text in ('Cited V7 and V8 passages', 'Additional source passages'):
            in_transcript = False
        style = node.find('./' + w('pPr') + '/' + w('pStyle'))
        if in_transcript and style is not None and style.get(w('val')) == 'Heading1':
            style.set(w('val'), 'Heading2')
    relationships = E.fromstring(parts['word/_rels/document.xml.rels'])
    types = E.fromstring(parts['[Content_Types].xml'])
    target = 'footerReview.xml'
    relation = next((node for node in relationships if node.get('Type') == R + '/footer'
                     and node.get('Target') == target), None)
    if relation is None:
        ids = {node.get('Id') for node in relationships}
        number = 1
        while f'rId{number}' in ids:
            number += 1
        relation = E.SubElement(relationships, '{' + PKG + '}Relationship',
                                Id=f'rId{number}', Type=R + '/footer', Target=target)
    footer = E.Element(w('ftr'))
    para = sub(footer, 'p')
    props = sub(para, 'pPr')
    sub(props, 'spacing', before=100, after=0)
    sub(sub(props, 'tabs'), 'tab', val='right', pos=9360)
    sub(sub(props, 'pBdr'), 'top', val='single', sz=4, space=6, color='888888')
    def run(text=None):
        node = sub(para, 'r')
        style = sub(node, 'rPr')
        sub(style, 'rFonts', ascii='Arial', hAnsi='Arial')
        sub(style, 'sz', val=18)
        sub(style, 'color', val='222222')
        if text is not None:
            item = sub(node, 't')
            item.set(XML + 'space', 'preserve')
            item.text = text
        return node
    def field(instruction, cached):
        sub(run(), 'fldChar', fldCharType='begin', dirty='true')
        item = sub(run(), 'instrText')
        item.set(XML + 'space', 'preserve')
        item.text = instruction
        sub(run(), 'fldChar', fldCharType='separate')
        run(cached)
        sub(run(), 'fldChar', fldCharType='end')
    field(' STYLEREF "Heading 1" \\l ', 'Section')
    run('    ')
    internal_link(para, 'Contents', 'review_contents', color='222222')
    for node in para[-1].iter(w('rPr')):
        sub(node, 'rFonts', ascii='Arial', hAnsi='Arial')
        sub(node, 'sz', val=18)
    sub(run(), 'tab')
    run('Page ')
    field(' PAGE ', '1')
    for section in document.iter(w('sectPr')):
        references = section.findall(w('footerReference'))
        if any(node.get('{' + R + '}id') != relation.get('Id') for node in references):
            raise ValueError('Preserve existing user footers before adding the review footer')
        if not references:
            node = E.Element(w('footerReference'), {w('type'): 'default', '{' + R + '}id': relation.get('Id')})
            section.insert(0, node)
    part_name = '/word/' + target
    if not any(node.get('PartName') == part_name for node in types):
        E.SubElement(types, '{' + CT + '}Override', PartName=part_name,
                     ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml')
    settings = E.fromstring(parts['word/settings.xml'])
    update = settings.find(w('updateFields'))
    if update is None:
        update = sub(settings, 'updateFields')
    update.set(w('val'), 'true')
    parts['word/' + target] = xml(footer)
    parts['word/document.xml'] = xml(document)
    parts['word/_rels/document.xml.rels'] = xml(relationships)
    parts['word/settings.xml'] = xml(settings)
    parts['[Content_Types].xml'] = xml(types)


def add_review_header(parts):
    document = E.fromstring(parts['word/document.xml'])
    relationships = E.fromstring(parts['word/_rels/document.xml.rels'])
    types = E.fromstring(parts['[Content_Types].xml'])
    target = 'headerReview.xml'
    relation = next((node for node in relationships if node.get('Type') == R + '/header' and node.get('Target') == target), None)
    if relation is None:
        ids = {node.get('Id') for node in relationships}
        number = 1
        while f'rId{number}' in ids:
            number += 1
        relation = E.SubElement(relationships, '{' + PKG + '}Relationship', Id=f'rId{number}', Type=R + '/header', Target=target)
    header = E.Element(w('hdr'))
    def line(chunks, border=False):
        para = sub(header, 'p')
        props = sub(para, 'pPr')
        sub(props, 'spacing', before=0, after=35, line=200, lineRule='auto')
        if border:
            sub(sub(props, 'pBdr'), 'bottom', val='single', sz=4, space=4, color='888888')
        for text, color in chunks:
            node = text_run(para, text)
            props = node.find(w('rPr'))
            if props is None:
                props = sub(node, 'rPr')
                node.remove(props)
                node.insert(0, props)
            sub(props, 'rFonts', ascii='Arial', hAnsi='Arial')
            sub(props, 'sz', val=16)
            sub(props, 'color', val=color)
    line([('V7/V8 P = draft + paragraph  |  R = review row  |  L = ChatGPT line', '222222')])
    line([('Links: ', '222222'), ('blue = V7 only', '175DA0'), ('  |  ', '222222'), ('green = both', '246B40'), ('  |  ', '222222'), ('orange = V8 only', '925400'), ('  |  black = other/mixed  |  gray notes = absent in both drafts', '222222')], border=True)
    for section in document.iter(w('sectPr')):
        references = section.findall(w('headerReference'))
        if any(node.get('{' + R + '}id') != relation.get('Id') for node in references):
            raise ValueError('Preserve existing user headers before adding the review key')
        if not references:
            section.insert(0, E.Element(w('headerReference'), {w('type'): 'default', '{' + R + '}id': relation.get('Id')}))
    part_name = '/word/' + target
    if not any(node.get('PartName') == part_name for node in types):
        E.SubElement(types, '{' + CT + '}Override', PartName=part_name, ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml')
    parts['word/' + target] = xml(header)
    parts['word/document.xml'] = xml(document)
    parts['word/_rels/document.xml.rels'] = xml(relationships)
    parts['[Content_Types].xml'] = xml(types)


def granular_notes(notes):
    groups = {note[0]: note for note in notes}
    result = []

    def add(group, line, category, answer=None, details=None, needle=None):
        _, refs, status, existing_answer, existing_details = groups[group]
        if line == 477:
            answer = ('Figure S1 already shows the visible raised-edge defect and the filtered-exposure comparison. '
                      'The filter addresses the bonding problem. No ridge-height measurement is proposed; '
                      'the paper does not claim a measured height reduction.')
        result.append((line, refs, category,
                       answer or existing_answer, details or existing_details, needle))

    both = 'In V7 and V8'
    v7 = 'In V7 only'
    v8 = 'In V8 only'
    missing = 'Not supplied in V7 or V8'
    other = 'Not a paper claim'
    add(1, 7, both)
    add(1, 11, both, 'V7 P23 gives the rubber, clamps and adhesive procedure in Methods. V7 P52 gives the 116 µm spread and clamping outcome in Results. V8 P22 and V8 P40 retain that split.')
    add(13, 14, both)
    for line, answer, detail in (
        (19, 'V7 P49 already reports coordinated fabrication files and the plate-format design. V8 P34 retains these topics.', 'A06'),
        (20, 'V7 P50-P52 already report exposure, adhesion and clamping development in Results. V8 P37-P40 retain these topics.', 'A07'),
        (21, 'V7 P54 already reports repeated casting, mold losses and elapsed use. V8 P43 retains those outcomes.', 'A08; A16-A17'),
        (22, 'V7 P33 describes inspection; V7 P56 and V7 P60 report handling and imaging. V8 retains both the method and its observed outcomes.', 'A09'),
        (23, 'V7 P38 already describes the tracer method and V7 P61 reports redistribution and its limits. V8 retains both.', 'A10'),
        (24, 'V7 P40-P41 already describe neuron culture and CTβ treatment; V7 P63-P64 report labeling, device numbers and edge-growth limits. V8 retains those topics.', 'A11; A19'),
        (25, 'V7 P44 describes the counting images and V7 P64 reports the counts in neuronal Results. V8 does the same. R55 covers integrating the saved counting configuration from the supplementary-biology analysis.', 'A12; F03'),
        (26, 'V7 P46 already explains descriptive summaries and the one-embryo technical-replicate design; V7 P64 reports per-plate mean/SD. V8 P51 keeps those summaries in the neuronal Results.', 'A12'),
    ):
        add(13, line, both, answer, detail)
    add(29, 33, both, 'V7 P50 already reports raised SUEX edges and the flatter surfaces obtained with filtered exposure. V8 P38 retains the observation.', 'A14; E06')
    add(29, 34, both, 'V7 P51 already reports SU-8 detachment on bare silicon and the base layer that prevented it. V8 P38 retains both observations.', 'A14; E07')
    add(29, 35, both, 'V7 P52 reports the 116 µm pin-height spread and uneven pressure with rigid clamping. V8 P40 retains both.', 'A04; A14')
    add(29, 36, both, 'V7 P52 reports that the EPDM backing accommodated height differences and let all pins seat together. V8 P40 retains that result.', 'A04; A14')
    add(29, 39, both, 'V7 P18-P24 gives exposure, baking, solvents and bonding in Methods. The bake temperature in Results identifies the successful batch.', 'A15')
    add(43, 44, both, 'V7 P54 already reports three routinely used molds and more than 50 usable casts in Results. V8 P43 retains the total.', 'A16')
    add(43, 46, both, 'V7 P33 already describes mold/cast inspection in Methods and points to the usable-cast definition in Table S5. V8 P25 keeps that assessment in Methods.', 'A16; E22')
    add(43, 48, both)
    add(50, 51, both, 'V7 P40 gives the preparation and plating density; V7 P41 gives CTβ timing/concentration and exclusions; V7 P43 gives imaging conditions. Those procedures were already in Methods.', 'A18')
    add(50, 51, missing, 'V7 P241 and V8 P202 give a general counting instruction. R55 covers integrating the saved counting method from the recent supplementary-biology analysis; R53 covers the updated exclusions and totals.', 'F03', 'analysis criteria.')
    add(50, 53, both, 'V7 P63 reports axonal labeling; V7 P64 reports 69 analyzed devices, exclusions and the within-plate mean/SD. V8 P49-P51 retain these results.', 'A19')
    add(50, 55, both, 'V7 P64 already reports poorer edge growth in Results and explains the restriction to interior devices. V8 P49 and V8 P51 retain that observation.', 'A19')
    add(57, 58, v8, 'V7 has four Results groups at V7 P48, V7 P55, V7 P62 and V7 P65. V8 separates the same topics into six.', 'A06-A13; A21')
    for line, answer, detail in (
        (62, 'V7 P49 already reports coordinated fabrication files, the 48-device/96-well format and the shared design dimensions. V8 P34 retains those topics.', 'A06'),
        (66, 'V7 P50, V7 P51 and V7 P52 already report exposure, adhesion and clamping development. V8 P37-P40 retain those topics.', 'A07'),
        (70, 'V7 P54 already reports reuse and mold losses; V7 P56 describes complete casts without separate well punching. V8 P42-P44 cover the same topics.', 'A08'),
        (74, 'V7 P56 reports the 9 mm well grid and multichannel pipetting; V7 P60 reports imaging on both systems. V8 P45 and V8 P46 retain these results.', 'A09'),
        (78, 'V7 P61 already reports tracer redistribution and the limits of the two-time-point experiment. V8 P47-P48 cover the same findings.', 'A10'),
        (82, 'V7 P63 and V7 P64 already report CTβ labeling, 69 analyzed devices and the edge-growth limitation. V8 P49-P51 cover the same findings.', 'A11; A19'),
    ):
        add(57, line, both, answer, detail)
    add(72, 72, v8, 'V7 P56 reports manual multichannel pipetting. V8 P45 adds a warning about automated dispensing and processing rates.', 'A09')
    add(84, 84, both)
    add(1, 87, both, 'V7 P22 already points detailed printer settings to Table S4; V7 P26 points frame settings to Table S6; V7 P41 points the assay procedure to Protocol S1. V8 also retains the two protocols.', 'A20')
    add(1, 89, both, 'V7 Methods has 2,226 words; V8 has 1,266. V7 P23 gives the procedure and V7 P52 reports its outcome. Both drafts also supply detailed protocols.', 'A20-A21')
    add(1, 91, both, 'V7 P18-P24 already describe the layer stack, resin inserts, alignment, bonding and parylene coating in main Methods, with the full mold procedure in Protocol S2. V8 retains the same main-text/supplement division.', 'A20')
    add(1, 96, both, 'The Methods/Results separation is already present: V7 P23 gives the bonding procedure and V7 P52 its outcome; V8 P22 and V8 P40 retain that split. R25 separately covers the six Results groups. Shortening Methods should be revisited as an editorial change.', 'A21')
    add(1, 102, other, 'This describes a separate ChatGPT review session. The supplied discussion does not include a link to that session.', 'A22')
    add(106, 108, both, 'Figures 2 and 3 are unchanged and explain construction. Broeren also uses a main fabrication figure; the published comparison gives its exact location.', 'B01')
    add(106, 110, both, 'V7 Table S1 supplies all 96 pin heights. V7 P54 and Table S5 report mold use and more than 50 casts.', 'B02')
    add(106, 126, both, 'V7 P121 and Table S1 already supply all 96 positions and heights. A heatmap can display their differences from the mean for this one array.', 'B03')
    add(106, 127, both, 'The 96 heights already in V7 Table S1 give a mean of 5.551 mm, sample SD 26.7 µm and range 116 µm. Recalculation agrees with those rounded values.', 'B04')
    add(106, 128, both, 'V7 P54 already reports five assembled molds, three routinely used, one broken during demolding and one lost after a PDMS leak. Three out of five is not the assembly success rate: all five had been assembled.', 'B05')
    add(106, 131, both, 'V7 P52 reports the 116 µm height spread, uneven rigid clamping and successful EPDM seating.', 'B06')
    for line in (136, 149, 165, 345, 351):
        add(133, line, missing, 'V7 P53 and V8 P58 identify cast dimensions as unmeasured. The later width check uses existing brightfield images; its table and overlays are included in this review.', 'B07; B12')
    for line in (138, 522):
        add(43, line, missing, 'V7 P54 and V8 P43 give the combined total of more than 50 casts and more than eight months of use. Neither gives exact usable/attempted cast counts or first/last-use dates for each mold.', 'B08-B09; E21')
    add(133, 145, missing, 'The proposed panels show heights from one printed array and combined mold-use records. B11 gives a title matching those quantities.', 'B11')
    add(133, 346, missing, 'Neither draft supplies measured channel sizes across successive casts or molds. The proposed comparison would need actual widths/heights linked to mold, cast and channel position.', 'B10')
    add(133, 349, both, 'V7 P54 reports one broken wafer during demolding and one PDMS leak beneath a wafer. V8 P43 retains both reasons.', 'B05')
    add(133, 357, missing, 'Panels D/E require channel-size measurements and linked cast records. The later width check supplies one part of that material.', 'B13')
    add(106, 359, both, 'V7 Table S1 contains the heights. Plotting them is a possible use of existing data, not a proposed addition here (R62).', 'B14')
    add(180, 174, both, 'This compares the original figures with rewritten Results and Discussion. All five legends and seven image contents are unchanged between V7 and V8.', 'C01')
    add(180, 181, both)
    add(180, 191, both, 'Both drafts retain the same panel labels. Their placement, font and size can be standardized.', 'C05')
    add(180, 192, missing, 'Both drafts start their legends with descriptive titles. The suggested change is italic to bold.', 'C03')
    add(180, 193, both, 'V7 P116 already gives fluorophores, starting volumes, imaging times, replicate design, device count and error-bar meaning. V8 keeps the legend. F01-F04 identify the supplied DMSO counts and calculation; D23 identifies calibrated views. R53 must reconcile the five counting-artifact exclusions with the stated exclusion rule in Methods and Protocol S1, not only update counts and the legend. R54 covers the calibrated views.', 'C02; D23; F01')
    add(180, 196, both, 'V7 P112 titles Figure 2 “Insert transfer and wafer bonding for the hybrid mold.” V8 retains it. The suggested replacement changes the title\'s emphasis.', 'C02')
    add(199, 208, both, 'V7 P110 already titles Figure 1 around shared dimensions connecting photomask/insert design to assembly. V8 keeps that title and the same panels.', 'D01')
    add(199, 212, both, 'V7 Figure 1 shows design inputs, masks, inserts, frame and assembled plate. D02 locates the bonded-mold step in Figure 2.', 'D02')
    add(199, 214, both, 'Figure 1B already shows the two-well geometry (V7 P110; V8 P71). A larger view with compartment labels should be revisited (R62).', 'D03')
    add(199, 216, both, 'V7 P15 gives 48 devices, 96 wells and 9 mm well spacing, with 18 × 9 mm device spacing. V8 P18 retains those dimensions. D04 gives the proposed figure labels.', 'D04')
    add(199, 220, both, 'Current panel B is the single-device photomask, identified in V7 P110. The proposed legend assigns B to a replacement schematic.', 'D05')
    add(224, 231, both, 'V7 P112 identifies the existing array-alignment and bonding views in Figure 2. V8 keeps them.', 'D06')
    add(224, 237, both, 'V7 P112 already identifies Figure 2A as the wafer and insert array before clamping. The same view is retained in V8.', 'D06')
    add(224, 238, both, 'Figure 2B already shows the pin/opening interface, identified in V7 P112 and retained in V8. Its size and visual emphasis should be revisited (R62).', 'D07')
    add(224, 239, both, 'V7 P112 already identifies Figure 2D as the clamping-layer side view, including the compressible EPDM backing. V8 keeps it.', 'D09')
    add(224, 240, missing, 'V7 Figure 2E shows a bonded insert/wafer close-up. A whole-mold panel needs a full-wafer photograph after bonding.', 'D10')
    add(224, 241, both, 'V7 P22 gives a 1.85 mm pin and 2.00 mm hole: (2.00 - 1.85) / 2 = 0.075 mm per side. V8 retains those dimensions.', 'D08')
    add(224, 247, both, 'V7 P52 and Table S1 already supply the 116 µm spread. Adding it to Figure 2 would replot existing data. Feedback L390 repeats this suggestion.', 'D11; B14')
    add(249, 254, both, 'Both drafts retain the process figure. The published comparisons also contain main fabrication figures.', 'B01; D12')
    add(249, 262, both, 'Figure 3 has nine illustrated steps, not assembly photographs. V7 P114 gives the legend; V7 P162 starts the assembly protocol.', 'D12')
    add(249, 260, both, 'V7 P56 already reports complete well arrays in each cast; V7 P54 reports repeated reuse. V8 P42-P43 retain those results.', 'D13')
    add(249, 264, both, 'V7 P54 already gives more than 50 casts across three molds. Those aggregate data can appear in Figure 3; they cannot populate exact per-mold reuse bars.', 'D14')
    add(249, 268, both, 'The proposed legend shortens V7 P114 and adds the cast total already reported in V7 P54.', 'D15')
    add(272, 275, both, 'This proposes changes to Figure 4. V7 P46 and V7 P116 already identify technical replicates. The later DMSO files supply device dots and larger calibrated images; R53 covers integrating the counts and reconciling the five artifact exclusions with Methods and Protocol S1. R54 covers the calibrated views.', 'D16; D21-D23')
    add(272, 281, both, 'V7 P116 describes Figure 4\'s three panels, retained in V8. The proposed five-panel replacement would add images and change the letters.', 'D16; D24')
    add(272, 283, both)
    add(272, 285, both, 'V7 P116 already describes tracer images at 0 and 72 h; V7 P61 reports their result and limits. V8 keeps both images. Enlarging representative devices is a presentation change.', 'D18')
    add(287, 287, missing, 'D19 identifies the supplied DMSO mosaics and paired soma/axon views. Those pair different times; a continuous same-time soma–channel–axon view remains an optional image choice (R62).', 'D19')
    add(287, 289, missing, 'D20 identifies the supplied enlarged traced/untraced DMSO views. Higher-magnification views need their source images (R62).', 'D20')
    add(291, 291, missing, 'The old Figure 4 has three bars. D21 and F01-F04 identify the supplied DMSO device dots, 72 source rows, five counting-artifact exclusions and sample-SD calculation. The CTβ plot includes 67 devices. R53 must reconcile those exclusions with the contamination/technical-failure rule in Methods and Protocol S1, then update the plot, means/SD and matching text; this is not only a count swap.', 'D21-D22; F01-F04')
    add(291, 293, both, 'V7 P46 and V7 P116 identify technical replicates from one embryo. V8 keeps that description; the DMSO plot now shows device dots (D22).', 'D22')
    add(272, 297, both, 'Current Figure 4 uses A-C; the proposed replacement uses A-E. The legend needs to match the chosen layout.', 'D24')
    add(301, 301, missing, 'D23 identifies the supplied calibrated 500 µm bars, acquisition scale, crop dimensions and rendering code for the DMSO views. R54 covers using those views. The old tracer panel still needs its own scale/bar.', 'D23')
    add(84, 313, both, 'Figure 5 has three application rows in both drafts. The suggested three-column layout and smaller wafer-scale inset should be revisited (R62).', 'D25')
    add(84, 321, both, 'V7 P118 identifies single-device and wafer-scale masks and individual/arrayed inserts, retained in V8. A smaller wafer inset would leave more room for the device and insert array.', 'D26')
    add(84, 327, both, 'V7 P66 and V7 P118 already state the untested status in Results and the legend; V8 P36 and V8 P79 retain it. An explicit in-figure label is absent and should be revisited (R62), so the limit is visible when the figure is read alone.', 'D27')
    add(361, 364, both, 'Both drafts have the same embedded headings. Reducing them could leave more room for images. The time labels, DIV11 labels and axes identify the data and are not redundant titles.', 'C04')
    add(361, 366, missing, 'The paragraph proposes label placement and a 12 pt manuscript font. C05-C06 compares those choices with the current formatting.', 'C05-C06')
    add(361, 368, both, 'V7 Tables S1 and S5 supply pin heights and mold-use records. Plotting them is a possible use of existing data, not a proposed addition here (R62).', 'C08')
    add(361, 370, missing, 'C10 and the width-check overlays show connecting channels and width rulers.', 'C10')
    add(361, 372, both, 'Figure 3 contains illustrations, not equipment photographs. Figure 2 includes the clamping fixture used for array bonding.', 'C09; D12')
    add(106, 375, both, 'Both drafts have five main figures. The suggested sixth figure has not been added.', 'C11')
    add(199, 380, both, '“Revised existing Fig. 1” is a proposed source for the future figure layout. V7 P110 and V8 P71 retain the same legend and image.', 'D01', 'Revised existing Fig. 1')
    add(249, 382, both, '“Revised existing Fig. 3” is a proposed source for the future figure layout. V7 P114 and V8 P75 retain the same legend and image.', 'D12', 'Revised existing Fig. 3')
    add(224, 388, both, 'The next three points repeat Feedback L247, Feedback L287, Feedback L291 and the earlier layout suggestions.', 'D11; D19; D21')
    add(224, 390, both, 'This repeats Feedback L247. V7 P52 and Table S1 already give the 116 µm height spread. A new panel would plot those existing values.', 'D11; B14')
    add(291, 392, missing, 'This repeats Feedback L287 and Feedback L291. D21 and F01-F04 identify the supplied DMSO device dots, counts, exclusions and calculation. Larger traced/untraced views are also supplied. R53 must reconcile the five counting-artifact exclusions with the stated Methods/Protocol S1 rule before integrating the updated plot and summaries.', 'D19; D21; F01')
    add(180, 398, both, 'Legend lengths are 42, 79, 122, 123 and 95 words. Feedback L398 proposes 60–120 words.', 'C07')
    add(400, 400, other)
    add(413, 406, other, 'Supplementary-material review.', 'E01')
    add(415, 409, v8, 'The later audit describes V8: Table S2 links are missing, main-text citations use PMIDs, and the baseline-image explanation is absent. V7 P7, V7 P8 and V7 P44 contain the removed text; V7 uses author–year citations.', 'E13; E25; F08')
    add(413, 413, v8)
    add(413, 426, v8, 'The audit counts a Figure 3 link added at V8 P42. V7 has the same figure and legend, but no direct Figure 3 link in its main text.', 'E01')
    add(413, 430, v8, 'The audit counts a Figure 4B link added at V8 P50. V7 already reports CTβ labeling at V7 P63, but lacks that direct Figure 4B link.', 'E01', 'Figure 4B')
    add(413, 432, both, 'V7 P61 states the two-time-point tracer limit. V7 P46 identifies technical replicates from one embryo. V8 retains both qualifications.', 'E02')
    add(414, 414, missing)
    for line in (442, 443, 467, 471):
        which = 'S1' if line in (442, 467) else 'S2'
        p = 50 if which == 'S1' else 51
        add(414, line, missing, f'V7 P{p} already describes this result and cites its supporting note. V8 retains it. Both drafts still need the direct Figure {which} link.', 'E06' if which == 'S1' else 'E07')
    add(414, 450, missing, 'V7 P155 identifies Figure S1 beside Note S1, retained in V8. Adding “Fig. S1” inside the note provides another link.', 'E04')
    add(414, 451, missing, 'V7 P161 identifies Figure S2 beside Note S2, retained in V8. Adding “Fig. S2” inside the note provides another link.', 'E05')
    add(454, 475, missing, 'V7 P161 and the unchanged Figure S2 show the failed condition. Neither draft includes a matched image of intact SU-8 after the base layer.', 'E08')
    add(454, 465, missing, 'V7 P50 already reports the filter result; V8 P38 retains it. The proposed sentence adds the direct Figure S1 citation missing from both drafts.', 'E06')
    add(454, 477, missing, 'V7 P155 calls Figure S1 a qualitative comparison; V8 retains that wording. Neither gives ridge heights or a reduction percentage. Measuring those would add data to a comparison already labeled qualitative.', 'E09')
    for line in (415, 445, 488, 492):
        if line == 445:
            add(415, line, v7, 'V7 P7 and V7 P8 already cite Table S2; V8 removes both links. The table is dense in both drafts (R57). V8 introduces the mixed citation styles (R52).', 'E13; E15; F08')
        else:
            add(415, line, v7, groups[415][3], 'E13')
    add(415, 480, v7, 'This repeats the Table S2 proposals at Feedback L445: the missing citation is a V8 change, dense columns affect both drafts, and the mixed citation styles start in V8.', 'E13; E15; F08')
    add(505, 444, both, 'V7 P121 and Table S1 already supply all 96 pin heights. V8 retains the same table.', 'E10')
    add(494, 494, both, 'Table S2 is unchanged. The checked V8 render splits “photolithography” across lines; wider columns or shorter entries would fix it.', 'E15')
    add(494, 500, both, 'V7 P129 describes Table S2 as a comparison of added operations and equipment. V8 P90 retains that description.', 'E17')
    add(505, 505, both)
    add(505, 513, both, 'E12 identifies supplementary/pin_z_variability_raw_mm.csv; all 96 values match V7 Table S1 (V7 P121).', 'E12')
    add(445, 446, both)
    add(445, 507, both, 'Tables S2/S3 are unchanged. The checked render splits long words in S2. S3 distinguishes the tested device from generated-only layouts.', 'E15; E18-E19')
    for line in (447, 449, 509):
        add(446, line, both, 'V7 P22 points to resin settings in Table S4; V7 P26 points to frame settings in Table S6. Both detailed tables are unchanged in V8.', 'E20')
    add(43, 528, both, 'Table S5 already says usable casts were classified by inspection, not by measuring dimensions. Its text is identical in V7 and V8.', 'E22')
    for line in (452, 453, 535, 537):
        add(446, line, both)
    add(446, 541, both, 'V7 P332 and V8 P293 repeat the open-channel result at the end of the fabrication protocol. E24 proposes an inspection step for that location.', 'E24')
    add(543, 543, v7)
    add(291, 547, missing)
    add(291, 551, missing, 'V7 P64 reports 69 devices after three contamination/technical-failure exclusions. R53 gives the supplied DMSO table with five named counting-artifact exclusions and 67 included CTβ devices. R53 must reconcile the exclusion rule and reasons in Methods and Protocol S1, then update Results, means/SD and the legend; high or low counts alone remain insufficient grounds.', 'F01-F02')
    add(291, 553, missing, 'The per-device counts were not included in V7; the later DMSO files supply them. R53 covers integrating that dataset after reconciling its five artifact flags with the stated exclusion rule.', 'F01')
    add(555, 560, both, 'V7 P79 already names the code, masks, resin inserts and frame models in the repository, and promises a versioned archive. V8 P64 keeps those commitments. The actual archive version/link is still missing.', 'F05')
    add(555, 562, both, 'V7 P80 names the frame G-code and Plate 1 microscope XML; V7 P150 gives the G-code filename. V8 retains those descriptions. The final package needs the corresponding files.', 'F06')
    add(555, 564, missing, 'V7 P79 and V8 P64 promise an archive but give no study release or permanent archive link.', 'F07')
    for line in (436, 498, 569):
        add(323, line, v8, 'V7 uses author–year references throughout and includes a bibliography. V8 adds main-text PMIDs but leaves the figure/SI citations unchanged. The mixed PMID/author–year style is introduced in V8.', 'D28; F08')
    add(498, 571, v7, 'V7 P84 starts a 24-entry bibliography; V8 removes it. F09 gives the required numbered citation format.', 'F09')
    add(573, 576, missing)
    add(580, 581, v8)
    add(580, 583, v8, 'V7 has no conflicts statement. V8 adds it after Data availability. The journal’s order is conflicts, data availability, then acknowledgements.', 'F11')
    add(511, 511, both, 'E26 identifies the separate supplement DOCX/PDF: its 212 nonempty paragraphs and ten table contents match V7. E12 identifies the height CSV; R57 covers S2/S3 column layout.', 'E12; E26')
    add(511, 588, both, 'V7 contains both protocols, characterization/design material and printing tables. V8 keeps them. E27 maps those items to the proposed group names.', 'E27')
    add(511, 598, both, 'V7 P79-P81 name files and promise a deposit. E12 identifies the existing height CSV; F01 identifies the DMSO count CSV. F07 identifies the remaining permanent study archive link.', 'F12')
    add(600, 601, both, 'Both drafts contain all five main figures, both supporting figures and both protocols.', 'E28')
    add(414, 605, missing, 'This repeats Feedback L414, Feedback L442 and Feedback L443. Both drafts explain the results and cite the notes, but direct Figure S1/S2 links are missing.', 'E03; E06-E07', 'Supplementary Figures S1–S2')
    add(415, 605, v7, 'This repeats Feedback L415 and Feedback L488. V7 P7 and V7 P8 already cite Table S2; V8 removes both links.', 'E13', 'Table S2.')
    add(445, 606, both, 'This repeats Feedback L505 and Feedback L507. Tables S1-S3 are unchanged from V7. The checked render shows split words in S2, not split numbers in S1; S3 already marks tested versus generated-only layouts.', 'E11; E15; E18-E19')
    add(291, 607, missing, 'This repeats Feedback L551. R53 identifies the supplied 72-row DMSO table and five counting-artifact exclusions, leaving 67 CTβ devices. R53 must reconcile those IDs/reasons with the Methods and Protocol S1 exclusion rule before updating the plot, summaries and matching text.', 'F01-F02', 'underlying CTβ cell-count dataset')
    add(43, 607, missing, 'This repeats Feedback L522. V7 P54 and V8 P43 give the combined cast total and elapsed use, not exact per-mold counts or dates.', 'E21', 'more detailed mold-production records')
    add(323, 608, v8, 'This repeats Feedback L436, Feedback L498 and Feedback L569. V8 introduces the mixed PMID/author–year style; V7 has author–year citations and a bibliography.', 'F08-F09', 'Standardize the references')
    add(543, 608, v7, 'This repeats Feedback L543. V7 P44 already says the images were collected before axotomy; V8 P30 removes that sentence. Both protocols still identify the pre-axotomy dataset.', 'E25', 'clarify the baseline neuronal imaging experiment.')
    add(511, 609, both, 'This repeats Feedback L511 and Feedback L588. The separate supplement already exists with V7’s text and tables (R58).', 'E26-E27', 'separate, well-organized Supplementary Information document')
    add(555, 609, missing, 'This repeats Feedback L560 and Feedback L564. V7 P79 and V8 P64 promise the archive but do not identify a completed deposit.', 'F05-F07', 'archived package of the fabrication files.')
    add(133, 612, missing, 'This repeats Feedback L136 and Feedback L149. V7 P53 identifies unmeasured cast dimensions. The later width check is included in this review.', 'B07; B12; F14')
    return sorted(result, key=lambda note: note[0])


def categories_at_sources(comments):
    categories = {}
    for comment in comments:
        label = ''.join(comment[0].itertext()).removesuffix('.')
        if label not in COMMENT_PALETTES:
            continue
        link = comment[-1].find(w('hyperlink'))
        if link is None or not link.get(w('anchor'), '').startswith('src_L'):
            raise ValueError('Categorized comment has no primary source link')
        categories.setdefault(link.get(w('anchor')), set()).add(label)
    return categories


def label_source_passages(document, comments):
    targets = {node.get(w('anchor')) for tree in (document, comments)
               for node in tree.iter(w('hyperlink'))}
    categories = categories_at_sources(comments)
    count = 0
    for para in document.iter(w('p')):
        for bookmark in list(para.findall(w('bookmarkStart'))):
            name = bookmark.get(w('name'), '')
            match = re.fullmatch(r'src_L(\d+)', name)
            if not match or int(match[1]) > 616 or name not in targets:
                continue
            in_table = any(node.tag == w('tc') for node in para.iterancestors())
            label = f'L{int(match[1])}' if in_table else f'Feedback L{int(match[1])}'
            if any(node.text == label for node in para.iter(w('t'))):
                continue
            # Keep the label outside the comment range and the source wording.
            run = E.Element(w('r'))
            props = sub(run, 'rPr')
            sub(props, 'b')
            sub(props, 'i', val=0)
            sub(props, 'sz', val=18)
            kinds = categories.get(name, set())
            color = COMMENT_PALETTES[next(iter(kinds))][0] if len(kinds) == 1 else '222222'
            sub(props, 'color', val=color)
            sub(run, 't').text = label
            sub(run, 'br')
            para.insert(para.index(bookmark) + 1, run)
            count += 1
    return count


def label_destinations():
    source = (args.source_document or OUTPUT).resolve()
    if (OUTPUT.parent / ('.~lock.' + OUTPUT.name + '#')).exists():
        raise ValueError('Output is open; preserve unsaved work')
    with ZipFile(source) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    document = E.fromstring(parts['word/document.xml'])
    comments = E.fromstring(parts['word/comments.xml'])
    # Saved reviews already have labels; preserve them and their annotations.
    count = 0
    targets = {node.get(w('anchor')) for node in document.iter(w('hyperlink'))}
    targets.update(node.get(w('anchor')) for node in comments.iter(w('hyperlink')))
    targets.add('review_contents')
    incoming_colors = {}
    for tree in (document, comments):
        for link in tree.iter(w('hyperlink')):
            anchor = link.get(w('anchor'))
            for color in link.iter(w('color')):
                incoming_colors.setdefault(anchor, set()).add(color.get(w('val')))
    starts = {node.get(w('name')): node for node in document.iter(w('bookmarkStart'))}
    ends = {node.get(w('id')): node for node in document.iter(w('bookmarkEnd'))}
    for anchor in sorted(target for target in targets if target):
        start = starts[anchor]
        end = ends[start.get(w('id'))]
        parent = start.getparent()
        if parent.tag == w('p'):
            heading = parent
        elif parent.tag == w('body'):
            heading = start.getnext()
            while heading is not None and heading.tag in (w('bookmarkStart'), w('bookmarkEnd')):
                heading = heading.getnext()
            if heading is None or heading.tag != w('p'):
                raise ValueError('Link target has no destination line: ' + anchor)
        else:
            raise ValueError('Unexpected link target container: ' + anchor)
        if anchor.startswith('change_'):
            cell = next(heading.iterancestors(w('tc')), None)
            if cell is None:
                raise ValueError('Table-row target is outside its row: ' + anchor)
            row = cell.getparent()
            heading = row.findall(w('tc'))[1].find(w('p'))
        destination = heading
        if anchor.startswith('cmp_'):
            following = heading.getnext()
            while following is not None and following.tag in (w('bookmarkStart'), w('bookmarkEnd')):
                following = following.getnext()
            if following is None or following.tag != w('p'):
                raise ValueError('Manuscript target has no quoted passage: ' + anchor)
            destination = following
        if not anchor.startswith('src_L'):
            start.getparent().remove(start)
            end.getparent().remove(end)
            first = next((i for i, node in enumerate(heading) if node.tag != w('pPr')), len(heading))
            heading.insert(first, start)
            destination.append(end)
        colors = incoming_colors.get(anchor, set())
        colored = colors - {'222222'}
        color = next(iter(colored)) if len(colored) == 1 else '222222'
        if anchor.startswith(('src_L', 'cmp_', 'evidence_', 'change_', 'summary_change_')):
            props = heading.find(w('pPr'))
            if props is None:
                props = E.Element(w('pPr'))
                heading.insert(0, props)
            borders = props.find(w('pBdr'))
            if borders is None:
                borders = sub(props, 'pBdr')
            left = borders.find(w('left'))
            if left is None:
                left = sub(borders, 'left')
            for key, value in {'val': 'single', 'sz': '20', 'space': '6', 'color': color}.items():
                left.set(w(key), value)
            fill = next((fill for foreground, fill in COMMENT_PALETTES.values() if foreground == color), 'F3F4F5')
            for run in heading.findall(w('r')):
                if not run.findall(w('t')):
                    continue
                # Mark the destination label without shading the whole source paragraph.
                style = heading.find('./' + w('pPr') + '/' + w('pStyle'))
                if anchor.startswith('src_L') and run.find(w('br')) is None:
                    continue
                if not anchor.startswith('src_L') and (style is None or not style.get(w('val'), '').startswith('Heading')):
                    continue
                props = run.find(w('rPr'))
                if props is None:
                    props = E.Element(w('rPr'))
                    run.insert(0, props)
                shade = props.find(w('shd'))
                if shade is None:
                    shade = sub(props, 'shd')
                shade.set(w('val'), 'clear')
                shade.set(w('fill'), fill)
            count += 1
    shade_comment_sources(document, comments)
    parts['word/document.xml'] = xml(document)
    temporary = OUTPUT.with_suffix('.new.docx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    temporary.replace(OUTPUT)
    print('Marked', count, 'destination lines; bookmarks span destination text in', OUTPUT.name)


def embed_evidence(parts, notes):
    document = E.fromstring(parts['word/document.xml'])
    body = document.find(w('body'))
    existing = list(body)
    old_start = next((i for i, node in enumerate(existing)
                      if node.xpath('descendant-or-self::w:bookmarkStart[@w:name="detailed_evidence"]', namespaces={'w': W})), None)
    if old_start is not None:
        owned = [node for node in existing[old_start:] if node.tag != w('sectPr')]
        if any(node.xpath('.//w:commentRangeStart', namespaces={'w': W}) for node in owned):
            raise ValueError('Evidence has annotations; preserve them before rebuilding it')
        for node in owned:
            body.remove(node)
    section = body.find(w('sectPr'))
    if section is not None:
        body.remove(section)
    next_id = max(int(node.get(w('id'))) for node in body.iter(w('bookmarkStart'))) + 1
    names = {node.get(w('name')) for node in body.iter(w('bookmarkStart'))}
    compared = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_comparison.json').read_text())['documents']
    missing = {}
    for row in REVIEW_ROWS:
        for name in ('v7', 'v8'):
            for p in row[name]:
                anchor = reference_anchor(name, p)
                if anchor not in names:
                    missing[anchor] = (name, p)
    for link in body.iter(w('hyperlink')):
        anchor = link.get(w('anchor'), '')
        match = re.fullmatch(r'cmp_(v[78])_P(\d+)', anchor)
        if match is not None and anchor not in names:
            missing[anchor] = (match[1], int(match[2]))
    for answer in [note[3] for note in notes] + [REPORT.read_text()]:
        for match in re.finditer(r'\b(v[78])\s+P(\d+)\b', answer, re.I):
            name, p = match[1].lower(), int(match[2])
            anchor = f'cmp_{name}_P{p}'
            if anchor not in names:
                missing[anchor] = (name, p)
    for anchor in names | set(missing):
        source = re.fullmatch(r'cmp_(v[78])_P(\d+)', anchor)
        if source is not None:
            match = matching_passage(compared, source[1], int(source[2]))
            if match is not None:
                counterpart = reference_anchor(*match)
                if counterpart not in names:
                    missing[counterpart] = match
    if missing:
        paragraph(body, 'Source passages linked from comments', 'Heading1')
    for anchor, (name, p) in missing.items():
        para = paragraph(body, f'{name.upper()} P{p}', 'Heading2')
        sub(para, 'bookmarkStart', id=next_id, name=anchor)
        sub(para, 'bookmarkEnd', id=next_id)
        next_id += 1
        paragraph(body, compared[name]['paragraphs'][p - 1], 'SourceQuote')
        names.add(anchor)

    # Retained appendix passages are full primary quotations, not editable prose.
    for start in body.iter(w('bookmarkStart')):
        match = re.fullmatch(r'cmp_(v[78])_P(\d+)', start.get(w('name'), ''))
        if match is None:
            continue
        heading = start.getparent() if start.getparent().tag == w('p') else start.getnext()
        while heading is not None and heading.tag in (w('bookmarkStart'), w('bookmarkEnd')):
            heading = heading.getnext()
        quote = heading.getnext() if heading is not None else None
        while quote is not None and quote.tag in (w('bookmarkStart'), w('bookmarkEnd')):
            quote = quote.getnext()
        if quote is None or quote.tag != w('p'):
            raise ValueError('Manuscript target has no quotation: ' + match[0])
        if quote.xpath('.//w:commentRangeStart|.//w:commentRangeEnd|.//w:commentReference', namespaces={'w': W}) or any(not node.get(w('name'), '').startswith('nav_') for node in quote.iter(w('bookmarkStart'))):
            raise ValueError('Preserve annotations on manuscript quotation: ' + match[0])
        props = quote.find(w('pPr'))
        if props is None:
            props = E.Element(w('pPr'))
            quote.insert(0, props)
        style = props.find(w('pStyle'))
        if style is None:
            style = sub(props, 'pStyle')
        style.set(w('val'), 'SourceQuote')
        for child in list(quote):
            if child.tag not in (w('pPr'), w('bookmarkStart'), w('bookmarkEnd')):
                quote.remove(child)
        run = text_run(E.Element('holder'), compared[match[1]]['paragraphs'][int(match[2]) - 1])
        end = quote.find(w('bookmarkEnd'))
        quote.insert(quote.index(end) if end is not None else len(quote), run)

    report = REPORT.read_text()
    source = report[report.index('### 1. Methods versus Results'):]
    ast = json.loads(subprocess.check_output(['pandoc', '-f', 'gfm', '-t', 'json'], input=source.encode()))
    entries, publications = [], []
    in_publications = False
    for block in ast['blocks']:
        if block['t'] == 'Header':
            words = [item['c'] for item in block['c'][2] if item['t'] == 'Str']
            in_publications = words[:2] == ['Published', 'Lab']
        if block['t'] != 'Table':
            continue
        for table_body in block['c'][4]:
            for row in table_body[3]:
                cells = [cell[4] for cell in row[1]]
                first = cells[0]
                key = first[0]['c'][0]['c'] if len(first) == 1 and first[0]['t'] in ('Plain', 'Para') and len(first[0]['c']) == 1 and first[0]['c'][0]['t'] == 'Str' else None
                if key and re.fullmatch(r'[A-F]\d{2}', key):
                    if len(cells) != 5:
                        raise ValueError('Unexpected evidence row: ' + key)
                    entries.append((key, cells[1:]))
                elif in_publications:
                    publications.append(cells)
    if len(entries) != 119 or len({key for key, _ in entries}) != 119:
        raise ValueError('The complete 119-entry evidence table was not found')

    blocks = []
    label_texts = set()
    header = lambda level, anchor, label: {'t': 'Header', 'c': [level, [anchor, [], []], [{'t': 'Str', 'c': label}]]}
    para = lambda text: {'t': 'Para', 'c': [{'t': 'Str', 'c': text}]}
    blocks.append(header(1, 'detailed_evidence', 'Additional sources and images'))
    width_root = ROOT / 'build/channel_width_20261013'
    with (width_root / 'measurements.csv').open(newline='') as stream:
        widths = list(csv.DictReader(stream))
    if len(widths) != 9:
        raise ValueError('Expected nine original width measurements')
    width_text = [
        '## Later brightfield width check {#channel_measurements}', '',
        'Widths were measured from existing brightfield images during this review.', '',
        'Nine rulers span 9–11 original pixels, or 10.7–13.1 µm, at 1.18675253 µm/pixel from Index.xml. Endpoints mark the centers of opposing dark wall bands. Blur affects edge placement.', '',
        '| Ruler | Plate / device | Endpoints (x, y), pixels | Pixels | µm |',
        '| --- | --- | --- | --- | --- |',
    ]
    for row in widths:
        assert abs(float(row['width_um']) - float(row['width_px']) * float(row['pixel_size_um'])) < 1e-9
        endpoints = f"({float(row['x0_px']):g}, {float(row['y0_px']):g}) to ({float(row['x1_px']):g}, {float(row['y1_px']):g})"
        width_text.append(f"| {row['measurement_id']} | {row['plate']} / {row['device']} | {endpoints} | {float(row['width_px']):g} | {float(row['width_um']):.1f} |")
    width_text += ['', 'All rulers use field 1, channel 1 of r02c02f01p01-ch1sk1fk1fl1.tiff at original resolution. Moving each endpoint by one pixel changes the span by up to 2.37 µm.', '']
    for plate in ('P1', 'P2', 'P3'):
        row = next(row for row in widths if row['plate'] == plate)
        image_path = width_root / row['overlay']
        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        width_text += [f"### {plate}: {Path(row['source']).parents[1].name}", '',
                       f'![{plate} raw-field rulers]({image_path}){{width=6.2in}}', '']
    width_ast = json.loads(subprocess.check_output(['pandoc', '-f', 'markdown', '-t', 'json'], input='\n'.join(width_text).encode()))
    blocks.extend(width_ast['blocks'])
    # Render only the cited region of the original PDF; leave its images unchanged.
    crop_specs = [
        ('C03', 'page11.png', 'Figure 1 legend title (V8 p. 11)', (112, 1025, 895, 1110), 6.2, (), 1005),
        ('C04', 'page11.png', 'Figure 1 heading (V8 p. 11)', (160, 118, 850, 145), 6.2, (), 1005),
        ('C04', 'page13.png', 'Figure 3 heading (V8 p. 13)', (252, 132, 735, 154), 4.8, (), 1005),
        ('D01', 'page11.png', 'Figure 1A: shared parameters and outputs (V8 p. 11)', (168, 155, 498, 307), 3.8, ('C05',), 1005),
        ('D03', 'page11.png', 'Figure 1B: connected two-well design (V8 p. 11)', (168, 327, 494, 473), 3.8, (), 1005),
        ('D07', 'page12.png', 'Figure 2B: pin and opening (V8 p. 12)', (435, 180, 765, 412), 3.8, ('C05',), 1005),
        ('D09', 'page12.png', 'Figure 2D: backing and clamps (V8 p. 12)', (435, 415, 848, 645), 4.5, ('D11',), 1005),
        ('C09', 'page12.png', 'Figure 2C: clamping fixture (V8 p. 12)', (202, 415, 434, 645), 3.0, (), 1005),
        ('D10', 'page12.png', 'Figure 2A: components before bonding (V8 p. 12)', (202, 180, 434, 410), 3.0, (), 1005),
        ('D10', 'page12.png', 'Figure 2E: bonded inserts, close-up (V8 p. 12)', (202, 650, 435, 880), 3.0, (), 1005),
        ('D12', 'page13.png', 'Figure 3: first three illustrated steps (V8 p. 13)', (265, 178, 725, 286), 5.5, ('C05', 'C09'), 1005),
        ('D18', 'figure4_page14.png', 'Figure 4A: tracer time points (V8 p. 14)', (318, 150, 917, 462), 5.5, ('C04', 'C05'), 1237),
        ('D23', 'figure4_page14.png', 'Figure 4B: original microscopy panels (V8 p. 14)', (316, 480, 917, 709), 5.5, ('C10', 'D16', 'D24'), 1237),
        ('D21', 'figure4_page14.png', 'Figure 4C: original count bars (V8 p. 14)', (334, 725, 904, 1057), 5.0, (), 1237),
        ('D25', 'page15.png', 'Figure 5: three existing application rows (V8 p. 15)', (198, 130, 475, 627), 3.0, (), 1005),
        ('D26', 'page15.png', 'Figure 5: output views in the first row (V8 p. 15)', (198, 130, 805, 282), 6.2, (), 1005),
        ('E04', 'page25.png', 'Note S1 beside Figure S1 (V8 p. 25)', (112, 552, 896, 1075), 6.2, (), 1005),
        ('E08', 'page26.png', 'Figure S2: failed-condition images and legend (V8 p. 26)', (113, 405, 896, 734), 6.2, (), 1005),
        ('E11', 'table_s1_s2_page16.png', 'Table S1A: column headings and row A (V8 p. 16)', (140, 148, 1099, 279), 6.2, (), 1237),
        ('E11', 'table_s1_s2_page16.png', 'Table S1A: row H (V8 p. 16)', (140, 580, 1099, 615), 6.2, (), 1237),
        ('E11', 'table_s1_s2_page16.png', 'Table S1B: row A deviations (V8 p. 16)', (140, 694, 1099, 766), 6.2, (), 1237),
        ('E11', 'table_s1_s2_page16.png', 'Table S1B: row H deviations (V8 p. 16)', (140, 1066, 1099, 1100), 6.2, (), 1237),
        ('E15', 'page17.png', 'Table S2: headings and first row (V8 p. 17)', (112, 126, 893, 320), 6.2, ('F12',), 1005),
        ('E19', 'page19.png', 'Table S3: separation of fabrication layers (V8 p. 19)', (112, 699, 888, 841), 6.2, (), 1005),
    ]
    crop_dir = REPORT.parent.parent / 'build/alyson_feedback_review_20261013/source_crops'
    crop_dir.mkdir(exist_ok=True)
    pdf = crop_dir.parent / 'mfd_draft_v8_alyson_feedback.pdf'
    crops_by_entry, crop_links = {}, {}
    for index, (owner, filename, label, bounds, width, users, page_width) in enumerate(crop_specs, 1):
        page = int(re.search(r'(?:page)?(\d+)\.png$', filename)[1])
        x0, y0, x1, y1 = bounds
        stem = crop_dir / f'{owner.lower()}_{index:02d}'
        subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-singlefile',
                        '-scale-to-x', str(page_width), '-scale-to-y', '-1',
                        '-x', str(x0), '-y', str(y0), '-W', str(x1 - x0), '-H', str(y1 - y0),
                        '-png', str(pdf), str(stem)], check=True, stdout=subprocess.DEVNULL)
        crop = (f'figure_crop_{owner}_{index:02d}', label, stem.with_suffix('.png'), width)
        crops_by_entry.setdefault(owner, []).append(crop)
        for entry in (owner, *users):
            crop_links.setdefault((entry, filename), crop[0])
    current_entry = None
    def normalize(node, publication_url=None):
        if isinstance(node, list):
            return [normalize(item, publication_url) for item in node]
        if not isinstance(node, dict):
            return node
        if node.get('t') == 'RawInline' and node.get('c') in (['html', '<br>'], ['html', '<br/>']):
            return {'t': 'LineBreak'}
        if node.get('t') == 'Link':
            href = node['c'][2][0]
            if not re.match(r'https?://', href) and 'articles/' in href:
                if publication_url is None:
                    raise ValueError('Publication link has no public source: ' + href)
                node = deepcopy(node)
                node['c'][2][0] = publication_url
                label = 'Public article (DOI)' if publication_url.startswith('https://doi.org/') else 'Public full text'
                node['c'][1] = [{'t': 'Str', 'c': label}]
            elif href.lower().endswith('.png'):
                path = (REPORT.parent / href).resolve()
                if not path.is_file():
                    raise FileNotFoundError(path)
                node = deepcopy(node)
                node['c'][2][0] = '#' + crop_links[(current_entry, path.name)]
            elif not urlsplit(href).scheme and not href.startswith('#'):
                path = (REPORT.parent / href).resolve()
                if not path.is_file():
                    raise FileNotFoundError(path)
                # Relevant file data are embedded in this source group, not linked locally.
                return {'t': 'Span', 'c': [['', [], []], normalize(node['c'][1], publication_url)]}
        return {key: normalize(value, publication_url) for key, value in node.items()}
    entries_by_key = dict(entries)
    source_rows = set()
    for row in REVIEW_ROWS:
        crops = [crop for key in row['checks'] for crop in crops_by_entry.get(key, [])]
        if not row['source_checks'] and not crops:
            continue
        source_rows.add(row['id'])
        blocks.append(header(2, 'sources_' + row['id'], row['id'] + '. ' + row['title']))
        blocks.append({'t': 'Para', 'c': [{'t': 'Link', 'c': [['', [], []], [{'t': 'Str', 'c': 'Table row ' + row['id']}], ['#change_' + row['id'], '']]}]})
        for key in row['source_checks']:
            current_entry = key
            content = normalize(deepcopy(entries_by_key[key][1]))
            blocks.extend(content)
        if row['id'] in ('R53', 'R54'):
            panel = 'B' if row['id'] == 'R53' else 'G'
            caption = ('Recent supplementary-biology CTβ count plot' if panel == 'B'
                       else 'Recent supplementary-biology calibrated CTβ views')
            path = ROOT / 'supplementary_bio/figure_output_dmso_only_20260916/panels' / f'panel_{panel}.png'
            if not path.is_file():
                raise FileNotFoundError(path)
            blocks.append(header(3, 'bio_panel_' + panel, caption))
            label_texts.add(caption)
            blocks.append(para('From the DMSO-only figure package; these panels are not in V7 or V8.'))
            blocks.append({'t': 'Para', 'c': [{'t': 'Image', 'c': [['', [], [['width', '6.2in']]], [{'t': 'Str', 'c': caption}], [str(path), '']]}]})
        if row['id'] == 'R33':
            comparison = ('Related hybrid-fabrication paper: [Ristola et al. (2019), Methods 2.2 and Results 3.1]'
                          '(https://trepo.tuni.fi/bitstream/handle/10024/215242/Ristola_2019_J._Micromech._Microeng._29_065009.pdf?sequence=1). '
                          'They inspected devices from the fifth fabrication batch and estimated about 15 mold uses before significant degradation. '
                          'They report reuse and wear observations, not a cast-by-cast durability curve. '
                          'V7 already reports its own cast total and elapsed use; no new durability study is proposed here.')
            comparison_ast = json.loads(subprocess.check_output(['pandoc', '-f', 'markdown', '-t', 'json'], input=comparison.encode()))
            blocks.extend(comparison_ast['blocks'])
        for anchor, caption, path, width in crops:
            blocks.append(header(3, anchor, caption))
            label_texts.add(caption)
            blocks.append({'t': 'Para', 'c': [{'t': 'Image', 'c': [['', [], [['width', f'{width}in']]], [{'t': 'Str', 'c': caption}], [str(path), '']]}]})
        if row['id'] == 'R58':
            with (ROOT / 'supplementary/pin_z_variability_raw_mm.csv').open(newline='') as stream:
                heights = [values for values in csv.reader(stream) if values]
            if not heights or heights[0] != ['Row', *map(str, range(1, 13))] or [values[0] for values in heights[1:]] != list('ABCDEFGH') or any(len(values) != 13 for values in heights):
                raise ValueError('Pin-height CSV must preserve rows A-H and columns 1-12')
            height_text = ['Pin heights (mm), in the original 8 x 12 array order.', '',
                           '| ' + ' | '.join(heights[0]) + ' |',
                           '| ' + ' | '.join(['---'] * 13) + ' |']
            for values in heights[1:]:
                height_text.append('| ' + values[0] + ' | ' + ' | '.join(f'{float(value):.3f}' for value in values[1:]) + ' |')
            height_ast = json.loads(subprocess.check_output(['pandoc', '-f', 'markdown', '-t', 'json'], input='\n'.join(height_text).encode()))
            blocks.extend(height_ast['blocks'])
    blocks.append(header(1, 'published_comparisons', 'Published Lab on a Chip comparisons'))
    blocks.append(para('The papers group fabrication, device use and testing in comparable ways. Lin has five Results groups, Compera three and V7 four.'))
    blocks.append(para('Page locations identify the versions checked for this review. Public links open the article DOI or full text.'))
    corpus = json.loads((REPORT.parent / 'methods_comparison_2026-09-08/verified_corpus.json').read_text())
    for index, cells in enumerate(publications, 1):
        doi_links = [inline['c'][2][0] for block in cells[0] for inline in block['c']
                     if inline['t'] == 'Link' and inline['c'][2][0].startswith('https://doi.org/')]
        if len(doi_links) != 1:
            raise ValueError('Published paper must identify one DOI: ' + str(index))
        doi = doi_links[0].removeprefix('https://doi.org/').lower()
        records = [record for record in corpus if record['doi'].lower() == doi]
        if len(records) != 1 or not records[0]['url'].startswith('https://'):
            raise ValueError('Published paper has no verified public URL: ' + doi)
        blocks.append(header(2, f'published_paper_{index}', f'Paper {index}'))
        article_url = records[0]['url']
        pmc_ids = [part for part in urlsplit(article_url).path.split('/')
                   if re.fullmatch(r'PMC\d+', part)]
        if pmc_ids:
            article_url = 'https://pmc.ncbi.nlm.nih.gov/articles/' + pmc_ids[0] + '/'
        for label, content in zip(('Paper', 'Published headings and location', 'Matching draft passage', 'What matches', 'What differs'), cells):
            label_texts.add(label)
            blocks.append({'t': 'Para', 'c': [{'t': 'Strong', 'c': [{'t': 'Str', 'c': label}]}]})
            blocks.extend(normalize(deepcopy(content), article_url))
    for index, title, citation, relevance in KENNEDY_PAPERS:
        blocks.append(header(2, f'published_paper_{index}', f'Paper {index}. {title}'))
        paper_ast = json.loads(subprocess.check_output(
            ['pandoc', '-f', 'markdown', '-t', 'json'],
            input=(citation + '\n\n' + relevance).encode()))
        blocks.extend(paper_ast['blocks'])
    ast['blocks'] = blocks
    reference = (args.source_document or OUTPUT).resolve()
    converted = subprocess.check_output(['pandoc', '-f', 'json', '-t', 'docx', '--reference-doc=' + str(reference)], input=json.dumps(ast).encode(), cwd=REPORT.parent)
    with ZipFile(BytesIO(converted)) as archive:
        appendix_parts = {name: archive.read(name) for name in archive.namelist()}
    appendix = E.fromstring(appendix_parts['word/document.xml'])
    for table in appendix.iter(w('tbl')):
        rows = table.findall(w('tr'))
        if not rows:
            continue
        labels = [''.join(cell.xpath('.//w:t/text()', namespaces={'w': W}))
                  for cell in rows[0].findall(w('tc'))]
        if labels == ['Row'] + [str(number) for number in range(1, 13)]:
            for row in rows[:-1]:
                for para in row.iter(w('p')):
                    props = para.find(w('pPr'))
                    if props is None:
                        props = E.Element(w('pPr'))
                        para.insert(0, props)
                    if props.find(w('keepNext')) is None:
                        sub(props, 'keepNext')
    crop_captions = {spec[2] for spec in crop_specs}
    for heading in appendix.iter(w('p')):
        if ''.join(heading.xpath('.//w:t/text()', namespaces={'w': W})) not in crop_captions:
            continue
        previous = heading.getprevious()
        while previous is not None and previous.tag in (w('bookmarkStart'), w('bookmarkEnd')):
            previous = previous.getprevious()
        if previous is not None and previous.tag == w('p') and not previous.xpath('.//w:drawing', namespaces={'w': W}):
            props = previous.find(w('pPr'))
            if props is None:
                props = E.Element(w('pPr'))
                previous.insert(0, props)
            if props.find(w('keepNext')) is None:
                sub(props, 'keepNext')
    for para in appendix.iter(w('p')):
        if ''.join(para.xpath('.//w:t/text()', namespaces={'w': W})) in label_texts:
            props = para.find(w('pPr'))
            if props is None:
                props = E.Element(w('pPr'))
                para.insert(0, props)
            if props.find(w('keepNext')) is None:
                sub(props, 'keepNext')
    children = [node for node in appendix.find(w('body')) if node.tag != w('sectPr')]
    if appendix.xpath('//w:footnoteReference|//w:endnoteReference|//w:numPr', namespaces={'w': W}):
        raise ValueError('Evidence introduced footnotes or numbering that need explicit merging')
    relationships = E.fromstring(parts['word/_rels/document.xml.rels'])
    next_relation = max(int(node.get('Id')[3:]) for node in relationships if re.fullmatch(r'rId\d+', node.get('Id', ''))) + 1
    relation_map = {}
    content_types = E.fromstring(parts['[Content_Types].xml'])
    for node in E.fromstring(appendix_parts['word/_rels/document.xml.rels']):
        kind = node.get('Type').rsplit('/', 1)[-1]
        if kind not in ('hyperlink', 'image'):
            continue
        old_id = node.get('Id')
        if kind == 'image':
            image_bytes = appendix_parts['word/' + node.get('Target')]
            existing_image = next((existing for existing in relationships
                                   if existing.get('Type') == node.get('Type')
                                   and parts.get('word/' + existing.get('Target', '')) == image_bytes), None)
            if existing_image is not None:
                relation_map[old_id] = existing_image.get('Id')
                continue
        node = deepcopy(node)
        node.set('Id', f'rId{next_relation}')
        next_relation += 1
        if kind == 'image':
            source_path = 'word/' + node.get('Target')
            image_bytes = appendix_parts[source_path]
            suffix = Path(source_path).suffix
            target = f'word/media/evidence_{node.get("Id")}{suffix}'
            parts[target] = image_bytes
            node.set('Target', target.removeprefix('word/'))
            extension = suffix.lstrip('.')
            if not any(n.get('Extension') == extension for n in content_types):
                E.SubElement(content_types, '{' + CT + '}Default', Extension=extension, ContentType='image/png')
        relation_map[old_id] = node.get('Id')
        relationships.append(node)
    bookmark_ids = {}
    for child in children:
        for node in child.iter():
            for attribute in (R + '}id', R + '}embed', R + '}link'):
                attribute = '{' + attribute
                if node.get(attribute) in relation_map:
                    node.set(attribute, relation_map[node.get(attribute)])
            if node.tag == w('bookmarkStart'):
                name = node.get(w('name'))
                if name in names:
                    raise ValueError('Duplicate evidence bookmark: ' + name)
                names.add(name)
                bookmark_ids[node.get(w('id'))] = str(next_id)
                next_id += 1
            if node.tag in (w('bookmarkStart'), w('bookmarkEnd')):
                node.set(w('id'), bookmark_ids[node.get(w('id'))])
            if node.tag == w('pStyle') and node.get(w('val')) == 'BlockText':
                node.set(w('val'), 'SourceQuote')
            if node.tag == w('tbl') and len(node.findall(w('tr'))) == 9 and len(node.find(w('tr')).findall(w('tc'))) == 13:
                for run in node.iter(w('r')):
                    props = run.find(w('rPr'))
                    if props is None:
                        props = E.Element(w('rPr'))
                        run.insert(0, props)
                    size = props.find(w('sz'))
                    if size is None:
                        size = sub(props, 'sz')
                    size.set(w('val'), '17')
        body.append(child)
    for node in body.iter(w('t')):
        if node.text in ('The pasted discussion follows. The comments are our review notes, not Alyson’s edits. Full evidence and the proposed decisions are in ALYSON_FEEDBACK_CHECK_20261013.md.',
                         'The pasted discussion follows. The comments are our review notes, not Alyson’s edits. Their evidence links jump to the detailed entries later in this document.',
                         'The pasted discussion follows. The comments are our review notes, not Alyson’s edits. Their source links jump to the detailed entries later in this document.'):
            node.text = 'The pasted discussion follows. The comments link to table rows and quoted passages.'
    if section is not None:
        body.append(section)
    parts['word/document.xml'] = xml(document)
    parts['word/_rels/document.xml.rels'] = xml(relationships)
    parts['[Content_Types].xml'] = xml(content_types)
    table = next(table for table in body.findall(w('tbl'))
                 if len(table.findall(w('tr'))) == len(REVIEW_ROWS) + 1
                 and ''.join(table.findall(w('tr'))[1].find(w('tc')).itertext()) == 'R01')
    for tr, row in zip(table.findall(w('tr'))[1:], REVIEW_ROWS):
        cell = tr.findall(w('tc'))[-1]
        for para in list(cell.findall(w('p'))):
            if para.xpath('.//w:hyperlink[starts-with(@w:anchor, "sources_") or @w:anchor="channel_measurements"]', namespaces={'w': W}) and ''.join(para.itertext()) == 'Sources':
                if para.xpath('.//w:commentRangeStart', namespaces={'w': W}):
                    raise ValueError('Preserve annotations on the table source link')
                cell.remove(para)
        if row['id'] in source_rows or row['id'] == 'R59':
            source_link = paragraph(cell, '')
            anchor = reference_anchor('measurement', None) if row['id'] == 'R59' else 'sources_' + row['id']
            internal_link(source_link, 'Sources', anchor, color='222222')
    print('Kept additional sources for', len(source_rows), 'table rows,', len(publications), 'paper comparisons and', len(crop_specs), 'crops; removed the 119 repeated check write-ups.')
    return document


def format_existing(lines):
    with ZipFile(OUTPUT) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    document = E.fromstring(parts['word/document.xml'])
    body = document.find(w('body'))
    old = list(body)
    source_index = next(i for i, node in enumerate(old)
                        if ''.join(node.itertext()) == 'Source transcript')
    anchors = {}
    for node in old[source_index + 1:]:
        for item in node.iter(w('p')):
            label = re.match(r'L(\d+)\s', ''.join(item.itertext()))
            if label is None:
                label = next((re.fullmatch(r'src_L(\d+)', c.get(w('name'), ''))
                              for c in item.iter(w('bookmarkStart'))), None)
            if label and int(label[1]) <= len(lines):
                anchors[int(label[1])] = [int(c.get(w('id')))
                                         for c in item.iter(w('commentRangeStart'))]
    comment_ids = {int(c.get(w('id'))) for c in E.fromstring(parts['word/comments.xml'])}
    if comment_ids != {i for ids in anchors.values() for i in ids}:
        raise ValueError('Source anchors changed; preserve document for manual review')
    section = deepcopy(body.find(w('sectPr')))
    for node in old[source_index + 1:]:
        body.remove(node)
    for item in body.iter(w('t')):
        if item.text == 'The transcript is copied from alyson_feedback.md. Its pasted-table spacing is preserved. L numbers identify lines in that file.':
            item.text = 'Transcript wording is preserved; pasted tables and lists have been restored. Comments cite source lines in alyson_feedback.md.'

    # Pasted tabs are corrupt separators. Column boundaries are recovered from
    # the original headers/phrases, with a text-equivalence check for every row.
    tables = {
        18: ([4000, 5360], [
            ['Materials and Methods', 'Corresponding Results'],
            ['OpenMFD design and fabrication-file generation', 'Parametric design'],
            ['Hybrid mold fabrication', 'Development and optimization'],
            ['PDMS casting and plate assembly', 'Repeated device fabrication'],
            ['Mold and device characterization', 'Device integrity'],
            ['Fluorescent tracer assay', 'Directional fluid transport'],
            ['Primary cortical neuron culture and CTβ retrograde axon tracing', 'Neuronal culture'],
            ['Imaging and cell counting', 'Incorporated into'],
            ['Statistical analysis', 'Quantitative outcomes'],
        ]),
        125: ([2800, 4100, 2460], [
            ['Panel', 'Measurement', 'Data available'],
            ['A. Spatial variation in insert height', 'Heatmap showing', 'All 96'],
            ['B. Insert-height distribution', 'Histogram showing', 'Mean 5.551'],
            ['C. Mold fabrication outcomes', 'Number of molds', '3 routinely'],
        ]),
        317: ([2400, 4100, 2860], [
            ['Application', 'Device geometry', 'Corresponding resin-insert array'],
            ['Myelination', 'Two cell populations', 'Matched insert'],
            ['Axon guidance', 'Orthogonal compartment', 'Matched insert'],
            ['Three-compartment culture', 'Three interconnected', 'Matched insert'],
        ]),
        341: ([800, 5700, 2860], [
            ['Panel', 'Content', 'Availability'],
            ['A', 'Heatmap', 'Available'],
            ['B', 'Distribution', 'Available'],
            ['C', 'Mold fabrication', 'Partially available'],
            ['D', 'Measured microchannel', 'Additional measurements'],
            ['E', 'Comparison of microchannel', 'Additional measurements'],
        ]),
        379: ([1250, 5450, 2660], [
            ['Final figure', 'Principal message', 'Source'],
            ['Figure 1', 'Parametric design', 'Revised existing'],
            ['Figure 2', 'Hybrid fabrication', 'Existing Fig. 2'],
            ['Figure 3', 'Reusable molds', 'Revised existing'],
            ['Figure 4', 'Devices support', 'Expanded existing'],
            ['Figure 5', 'The design framework', 'Simplified existing'],
        ]),
        423: ([1000, 3460, 2200, 2700], [
            ['Figure', 'Content', 'Cited in main text?', 'Assessment'],
            ['Figure 1', 'OpenMFD design', 'Yes — Methods', 'Appropriate'],
            ['Figure 2', 'Insert alignment', 'Yes — Methods', 'Appropriate'],
            ['Figure 3', 'Repeated PDMS', 'Yes — Results', 'Appropriate'],
            ['Figure 4', 'Directional tracer', 'Yes — Results', 'Appropriate'],
            ['Figure 5', 'Alternative microfluidic', 'Yes — Results', 'Appropriate'],
        ]),
        441: ([3200, 1800, 4360], [
            ['Supplementary item', 'Cited in main manuscript?', 'Assessment and recommendation'],
            ['Figure S1 — Effect of LP360 filtering on SUEX', 'No direct citation', 'Retain.'],
            ['Figure S2 — SU-8 delamination', 'No direct citation', 'Retain.'],
            ['Table S1 — Resin-insert height measurements', 'Yes', 'Essential.'],
            ['Table S2 — Comparison of fabrication approaches', 'No', 'Useful but'],
            ['Table S3 — Design parameters and validation checks', 'Yes', 'Very valuable.'],
            ['Table S4 — Resin-printing parameters', 'Yes', 'Essential for'],
            ['Table S5 — Mold fabrication and casting outcomes', 'Yes', 'Important but'],
            ['Table S6 — HIPS frame-printing settings', 'Yes', 'Appropriate.'],
            ['Note S1 — LP360 exposure optimization', 'Yes', 'Appropriate,'],
            ['Note S2 — SU-8 adhesion and thermal processing', 'Yes', 'Appropriate,'],
            ['Protocol S1 — Device assembly and neuronal culture', 'Yes', 'Essential.'],
            ['Protocol S2 — Hybrid mold fabrication', 'Yes', 'Essential.'],
        ]),
        592: ([3400, 5960], [
            ['Component', 'Contents'],
            ['Supplementary Methods', 'Protocol S1:'],
            ['Supplementary Characterization and Design', 'Figures S1–S2'],
            ['Supplementary Fabrication Parameters', 'Tables S4 and S6'],
        ]),
    }
    major = {106, 118, 163, 169, 173, 406}
    headings = {13, 29, 57, 86, 95, 180, 198, 329, 361, 374,
                420, 438, 479, 502, 517, 530, 545, 587, 600}
    subheadings = {30, 43, 50, 60, 64, 68, 72, 76, 80, 133, 142,
                   199, 224, 249, 272, 303, 338, 429, 454,
                   546, 555, 566, 573, 580}
    bullets = set(range(33, 37)) | set(range(191, 194)) | set(range(237, 241))
    bullets |= set(range(308, 311)) | set(range(413, 418)) | set(range(605, 610))

    def add_text(parent, text, number, header=False, table=False):
        item = sub(parent, 'p')
        props = sub(item, 'pPr')
        style = 'Normal'
        if number in major or text.startswith('Prompt:'):
            style = 'Heading1'
        elif number in headings:
            style = 'Heading2'
        elif number in subheadings or text in ('Suggested improvements', 'Proposed title and legend', 'Suggested title and legend', 'My recommendation'):
            style = 'Heading3'
        sub(props, 'pStyle', val=style)
        sub(props, 'jc', val='left')
        sub(props, 'spacing', before=140 if style != 'Normal' else 0,
            after=60 if table else 120, line=264, lineRule='auto')
        if style != 'Normal' or header:
            sub(props, 'keepNext')
        if number in bullets and not table:
            num = sub(props, 'numPr')
            sub(num, 'ilvl', val=0)
            sub(num, 'numId', val=90)
        sub(props, 'widowControl')
        bookmark = 1000 + number
        sub(item, 'bookmarkStart', id=bookmark, name=f'src_L{number:03d}')
        for index in anchors.get(number, []):
            sub(item, 'commentRangeStart', id=index)
        prefix = None
        if header:
            prefix = text
        elif text.startswith(('Fig. ', 'Figure X.')):
            match = re.match(r'(Fig\. \d+\. .*?\.|Figure X\. .*?\.)(?: |$)', text)
            prefix = match[1] if match else text
        elif ':' in text and len(text.split(':', 1)[0]) < 75:
            prefix = text.split(':', 1)[0] + ':'
        if prefix:
            run = text_run(item, prefix)
            run_props = E.Element(w('rPr'))
            sub(run_props, 'b')
            run.insert(0, run_props)
            text_run(item, text[len(prefix):])
        else:
            text_run(item, text)
        for index in reversed(anchors.get(number, [])):
            sub(item, 'commentRangeEnd', id=index)
            run = sub(item, 'r')
            sub(sub(run, 'rPr'), 'rStyle', val='CommentReference')
            sub(run, 'commentReference', id=index)
        sub(item, 'bookmarkEnd', id=bookmark)
        return item

    number = 1
    while number <= len(lines):
        text = lines[number - 1].replace('\t', '').strip()
        if not text or text == '\ue117':
            if anchors.get(number):
                raise ValueError('Cannot discard an anchored source line')
            number += 1
            continue
        if number not in tables:
            add_text(body, text, number)
            number += 1
            continue
        widths, row_markers = tables[number]
        table = sub(body, 'tbl')
        props = sub(table, 'tblPr')
        sub(props, 'tblW', w=sum(widths), type='dxa')
        sub(props, 'tblLayout', type='fixed')
        borders = sub(props, 'tblBorders')
        for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            sub(borders, edge, val='single', sz=4, color='D4D4D4')
        margins = sub(props, 'tblCellMar')
        for edge in ('top', 'bottom', 'left', 'right'):
            sub(margins, edge, w=90, type='dxa')
        grid = sub(table, 'tblGrid')
        for width in widths:
            sub(grid, 'gridCol', w=width)
        for row_index, markers in enumerate(row_markers):
            text = lines[number - 1].replace('\t', '').strip()
            positions = [0]
            for marker in markers[1:]:
                positions.append(text.index(marker, positions[-1] + 1))
            positions.append(len(text))
            cells = [text[a:b].strip() for a, b in zip(positions, positions[1:])]
            if re.sub(r'\s', '', ''.join(cells)) != re.sub(r'\s', '', text):
                raise ValueError('Table text changed at line ' + str(number))
            row = sub(table, 'tr')
            row_props = sub(row, 'trPr')
            sub(row_props, 'cantSplit')
            if row_index == 0:
                sub(row_props, 'tblHeader')
            for column, (cell_text, width) in enumerate(zip(cells, widths)):
                cell = sub(row, 'tc')
                cell_props = sub(cell, 'tcPr')
                sub(cell_props, 'tcW', w=width, type='dxa')
                sub(cell_props, 'vAlign', val='top')
                if row_index == 0:
                    sub(cell_props, 'shd', fill='F0F0F0')
                # Only the first cell owns that source line's comment anchors.
                add_text(cell, cell_text, number if column == 0 else 10000 + number * 10 + column,
                         header=row_index == 0, table=True)
            number += 1
        paragraph(body, '')

    body.append(section)
    parts['word/document.xml'] = xml(document)
    styles = E.fromstring(parts['word/styles.xml'])
    sizes = {'Normal': 22, 'Title': 32, 'Heading1': 28, 'Heading2': 25, 'Heading3': 23, 'CommentText': 20}
    for name, size in sizes.items():
        style = next((s for s in styles.findall(w('style')) if s.get(w('styleId')) == name), None)
        if style is None:
            style = sub(styles, 'style', type='paragraph', styleId=name)
            sub(style, 'name', val=name)
            sub(style, 'basedOn', val='Normal')
        props = style.find(w('rPr'))
        if props is None:
            props = sub(style, 'rPr')
        for tag in ('rFonts', 'sz', 'szCs', 'color', 'i', 'iCs', 'b', 'bCs'):
            for node in props.findall(w(tag)):
                props.remove(node)
        sub(props, 'rFonts', ascii='Arial', hAnsi='Arial')
        sub(props, 'sz', val=size)
        sub(props, 'szCs', val=size)
        sub(props, 'color', val='000000')
        if name in ('Title', 'Heading1', 'Heading2', 'Heading3'):
            sub(props, 'b')
    parts['word/styles.xml'] = xml(styles)
    numbering = E.fromstring(parts['word/numbering.xml'])
    for node in list(numbering):
        if node.get(w('abstractNumId')) == '90' or node.get(w('numId')) == '90':
            numbering.remove(node)
    abstract = sub(numbering, 'abstractNum', abstractNumId=90)
    level = sub(abstract, 'lvl', ilvl=0)
    sub(level, 'start', val=1)
    sub(level, 'numFmt', val='bullet')
    sub(level, 'lvlText', val='•')
    sub(sub(level, 'pPr'), 'ind', left=300, hanging=180)
    sub(sub(numbering, 'num', numId=90), 'abstractNumId', val=90)
    parts['word/numbering.xml'] = xml(numbering)
    backup = OUTPUT.parent.parent / 'build/alyson_feedback_review_20261013/alyson_feedback_before_formatting.docx'
    if not backup.exists():
        backup.write_bytes(OUTPUT.read_bytes())
    temporary = OUTPUT.with_suffix('.format.docx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with ZipFile(temporary) as archive:
        assert archive.testzip() is None
        assert archive.read('word/comments.xml') == parts['word/comments.xml']
    temporary.replace(OUTPUT)
    print('Restored', len(tables), 'tables, headings and lists; preserved', len(comment_ids), 'comments.')


def lead_with_findings():
    if args.source_document is None:
        raise ValueError('--source-document must identify the saved review to preserve')
    source = args.source_document.resolve()
    if (OUTPUT.parent / ('.~lock.' + OUTPUT.name + '#')).exists():
        raise ValueError('Output is open; preserve unsaved work')
    opening = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_opening.json').read_text())
    original_bytes = source.read_bytes()
    with ZipFile(BytesIO(original_bytes)) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    document = E.fromstring(parts['word/document.xml'])
    body = document.find(w('body'))
    original = list(body)
    def text_of(node):
        return ''.join(node.xpath('.//w:t/text()', namespaces={'w': W}))

    if text_of(original[0]) in ('First: work removed and requested again',
                                'Start with which draft the comments describe',
                                'How I put this comparison together'):
        boundary = next(i for i, node in enumerate(original)
                        if text_of(node) in ('The rest of the V7 to V8 changes', 'Changes and remaining work'))
        old_opening = original[:boundary]
        if any(node.xpath('.//w:commentRangeStart', namespaces={'w': W}) for node in old_opening):
            raise ValueError('Old opening has annotations; preserve them before replacing it')
        if any(bookmark.get(w('name')) not in ('comment_color_key', 'review_contents', 'review_contents_end', 'remaining_support_pages')
               and not bookmark.get(w('name'), '').startswith('nav_')
               and not bookmark.get(w('name'), '').startswith('finding_')
               and not bookmark.get(w('name'), '').startswith('summary_change_')
               for node in old_opening for bookmark in node.iter(w('bookmarkStart'))):
            raise ValueError('Old opening has user bookmarks; preserve them')
        original = original[boundary:]
    email_start = next((i for i, node in enumerate(original)
                        if text_of(node) in ('What the emails say', 'What the email says')), None)
    if email_start is not None:
        email_end = next(i for i in range(email_start + 1, len(original))
                         if text_of(original[i]) == 'What the files show')
        if any(node.xpath('.//w:commentRangeStart | .//w:bookmarkStart', namespaces={'w': W})
               for node in original[email_start:email_end]):
            raise ValueError('Email block has annotations or bookmarks; preserve them before removing it')
        original = original[:email_start] + original[email_end:]
    for heading in ('What the files show', 'What was not changed'):
        start = next((i for i, node in enumerate(original) if text_of(node) == heading), None)
        if start is None:
            continue
        end = next(i for i in range(start + 1, len(original))
                   if original[i].xpath('./w:pPr/w:pStyle[starts-with(@w:val, "Heading")]',
                                        namespaces={'w': W}))
        if any(node.xpath('.//w:commentRangeStart | .//w:bookmarkStart', namespaces={'w': W})
               for node in original[start:end]):
            raise ValueError('Repeated summary has annotations; preserve them before removing it')
        original = original[:start] + original[end:]
    for node in list(body):
        body.remove(node)
    existing_names = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    existing_names |= {node.get(w('name')) for child in original for node in child.iter(w('bookmarkStart'))}
    existing_names |= {f'published_paper_{index}' for index, *_ in KENNEDY_PAPERS}
    additional_quotes = {}
    compared = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_comparison.json').read_text())['documents']
    decisions = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_decisions.json').read_text())
    rows_by_id = {row['id']: row for row in decisions}
    for item in opening:
        for name, p in item.get('refs', []):
            anchor = reference_anchor(name, p)
            if anchor not in existing_names:
                if name == 'measurement':
                    existing_names.add(anchor)
                    continue
                if name in ('change', 'source'):
                    if not any(row['id'] == p for row in json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_decisions.json').read_text())):
                        raise ValueError('Unknown change row: ' + p)
                    existing_names.add(anchor)
                    continue
                if name not in compared:
                    raise ValueError('Missing feedback source link: ' + anchor)
                additional_quotes[anchor] = (name, p, compared[name]['paragraphs'][p - 1])
                existing_names.add(anchor)
    for index, item in enumerate(opening):
        para = paragraph(body, item['text'], item.get('style'))
        if '{remaining_pages}' in item['text']:
            prefix, suffix = item['text'].split('{remaining_pages}')
            para.remove(para.find(w('r')))
            text_run(para, prefix)
            sub(para, 'bookmarkStart', id=50000 + index, name='remaining_support_pages')
            text_run(para, '00')
            sub(para, 'bookmarkEnd', id=50000 + index)
            text_run(para, suffix)
        if item.get('underline'):
            for run in list(para.findall(w('r'))):
                para.remove(run)
            cursor = 0
            for label in item['underline']:
                position = item['text'].index(label, cursor)
                text_run(para, item['text'][cursor:position])
                run = text_run(para, label)
                props = E.Element(w('rPr'))
                run.insert(0, props)
                sub(props, 'u', val='single')
                cursor = position + len(label)
            text_run(para, item['text'][cursor:])
        if item.get('finding'):
            marker = item['finding']
            bookmark_id = 50000 + index
            anchor = (f'finding_feedback_L{marker["feedback"]}_{index}' if 'feedback' in marker
                      else f'finding_wording_{index}')
            sub(para, 'bookmarkStart', id=bookmark_id, name=anchor)
            sub(para, 'bookmarkEnd', id=bookmark_id)
        props = para.find(w('pPr'))
        sub(props, 'jc', val='left')
        spacing = props.find(w('spacing'))
        spacing.set(w('after'), '110')
        spacing.set(w('line'), '250')
        if item.get('style') or (index + 1 < len(opening) and opening[index + 1].get('quote')):
            sub(props, 'keepNext')
        if item.get('quote'):
            sub(props, 'ind', left=180)
            if item.get('refs'):
                sub(props, 'keepNext')
        if item.get('refs'):
            refs = para if item.get('inline_refs') else sub(body, 'p')
            if refs is not para:
                source_props = sub(refs, 'pPr')
                sub(source_props, 'spacing', before=0, after=80)
                sub(source_props, 'keepNext')
            if item.get('inline_refs'):
                text_run(refs, '  ')
            for name, p in item['refs']:
                if not item.get('quote') and not item.get('style') and reference_label(name, p) in item['text']:
                    continue
                anchor = reference_anchor(name, p)
                if anchor not in existing_names:
                    raise ValueError('Missing source link: ' + anchor)
                link = sub(refs, 'hyperlink', anchor=anchor)
                run = sub(link, 'r')
                run_props = sub(run, 'rPr')
                sub(run_props, 'u', val='single')
                sub(run_props, 'sz', val=18)
                text = sub(run, 't')
                text.set(XML + 'space', 'preserve')
                text.text = reference_label(name, p)
                text_run(refs, '    ')
        if item.get('related_feedback'):
            feedback = item['related_feedback']
            if feedback:
                related = paragraph(body, 'Related feedback: ')
                for index, line in enumerate(feedback):
                    anchor = reference_anchor('feedback', line)
                    if anchor not in existing_names:
                        raise ValueError('Summary feedback is missing: ' + anchor)
                    if index:
                        text_run(related, '    ')
                    internal_link(related, reference_label('feedback', line), anchor, color='222222')
                sub(related.find(w('pPr')), 'keepNext')
                for run in related.iter(w('r')):
                    run_props = run.find(w('rPr'))
                    if run_props is None:
                        run_props = E.Element(w('rPr'))
                        run.insert(0, run_props)
                    sub(run_props, 'sz', val=18)
    for child in original:
        if text_of(child).startswith(('P numbers below identify body paragraphs',
                                      'P numbers identify body paragraphs')):
            if child.xpath('.//w:commentRangeStart | .//w:bookmarkStart', namespaces={'w': W}):
                raise ValueError('Paragraph-count explanation has annotations; preserve them')
            continue
        for item in child.iter(w('t')):
            if item.text == ': a matched intact-SU-8 image or raised-edge measurements would add evidence, not repair absent observations.':
                item.text = ': a matched intact-SU-8 image or raised-edge measurements would add data; the observations are already reported.'
            if item.text in ('V7 to V8: proposed decisions', 'The rest of the V7 to V8 changes'):
                item.text = 'Changes and remaining work'
            if item.text == 'Exact V7 and V8 wording':
                item.text = 'Cited V7 and V8 passages'
        body.append(child)
    decisions = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_decisions.json').read_text())
    extend_change_table(document, decisions)
    decision_tables = []
    for table in body.findall(w('tbl')):
        rows = table.findall(w('tr'))
        if len(rows) == len(decisions) + 1 and [text_of(row.find(w('tc'))) for row in rows[1:]] == [row['id'] for row in decisions]:
            decision_tables.append(table)
    if len(decision_tables) != 1:
        raise ValueError('The owned comparison table could not be identified')
    table = decision_tables[0]
    if table.xpath('.//w:commentRangeStart', namespaces={'w': W}):
        raise ValueError('Comparison table has annotations; preserve them before updating its wording')
    rows = table.findall(w('tr'))
    updates = [(rows[0].findall(w('tc'))[1], 'Change or work'),
               (rows[0].findall(w('tc'))[2], 'My suggestion'),
               (rows[0].findall(w('tc'))[3], 'What the sources show')]
    for node, decision in zip(rows[1:], decisions):
        cells = node.findall(w('tc'))
        prefix = {'draft': '', 'remaining': 'Remaining: ', 'supplied': 'Supplied: ', 'optional': 'Optional: '}[decision['kind']]
        updates.extend([(cells[1], prefix + decision['title']), (cells[2], decision['decision']), (cells[3], decision['reason'])])
    for cell, value in updates:
        texts = cell.find(w('p')).xpath('.//w:t', namespaces={'w': W})
        current = ''.join(node.text or '' for node in texts)
        if re.sub(r'\s+', ' ', current).strip() == re.sub(r'\s+', ' ', value).strip():
            continue
        para = cell.find(w('p'))
        if para.xpath('.//w:commentRangeStart|.//w:commentRangeEnd|.//w:commentReference', namespaces={'w': W}) or any(not start.get(w('name'), '').startswith('change_R') for start in para.iter(w('bookmarkStart'))):
            raise ValueError('Preserve annotations in the changed comparison cell')
        for child in list(para):
            if child.tag not in (w('pPr'), w('bookmarkStart'), w('bookmarkEnd')):
                para.remove(child)
        run = text_run(E.Element('holder'), value)
        end = para.find(w('bookmarkEnd'))
        para.insert(para.index(end) if end is not None else len(para), run)
    for node in body.findall(w('p')):
        if text_of(node) == 'This table lists the working preferences for the combined draft.':
            if node.xpath('.//w:commentRangeStart|.//w:bookmarkStart', namespaces={'w': W}):
                raise ValueError('Preserve annotations on the table introduction')
            body.remove(node)
            continue
        if text_of(node).startswith('My working preference:'):
            if node.xpath('.//w:commentRangeStart|.//w:bookmarkStart', namespaces={'w': W}):
                raise ValueError('Preserve annotations on the repeated decision')
            body.remove(node)
            continue
        if text_of(node) == 'Each passage is printed once. The table links to these passages. Original scientific terms are retained inside the quotes; the decision explanations use plain language.':
            if node.xpath('.//w:commentRangeStart|.//w:bookmarkStart', namespaces={'w': W}):
                raise ValueError('Preserve annotations on the passage introduction')
            body.remove(node)
            continue
        replacement = {
            'Decisions to review': 'My suggestions',
            'My working preferences': 'My suggestions',
            'The preferences in this table are mine, not instructions to anyone. No manuscript changes have been applied.':
                'My suggestions for the combined draft.',
            'This is not a list of 52 problems with V7. It is 52 choices about the rewrite. Most reversions restore existing text; they do not require new writing or experiments.':
                'R01-R52 compare the rewrite. R53 onward list remaining work, supplied files and optional additions.',
            'The numerical tables, supplementary text, figure legends and image contents were not revised. A proposed figure redesign is not a completed edit. Remaining tasks include direct Figure S1/S2 links, correct scale bars, the actual counting settings and source table, ethics details and the promised files.':
                'V7 and V8 retain the same tables, supplement, legends and images. The DMSO counts and calibrated views now exist. Remaining work includes integrating them, direct Figure S1/S2 links, tracer scale bars, counting settings, ethics details and the study-file deposit.',
            'These are proposed decisions for Tristan to review. No manuscript changes have been made.':
                'My suggestions for the combined draft.',
        }.get(text_of(node))
        if text_of(node) == 'The table lists 52 choices about the rewrite.':
            replacement = 'R01-R52 compare the rewrite. R53 onward list remaining work, supplied files and optional additions.'
        if text_of(node) == 'V7 and V8 retain the same tables, supplement, legends and images. Remaining work: Figure S1/S2 links, scale bars, counting settings and source counts, ethics details, and the study-file deposit.':
            replacement = 'V7 and V8 retain the same tables, supplement, legends and images. The DMSO counts and calibrated views now exist. Remaining work includes integrating them, direct Figure S1/S2 links, tracer scale bars, counting settings, ethics details and the study-file deposit.'
        if replacement is not None:
            texts = node.xpath('.//w:t', namespaces={'w': W})
            if len(texts) != 1:
                raise ValueError('Comparison introduction has unexpected formatting')
            texts[0].text = replacement
    table_note = 'In this table, link colors show where the exact quoted wording appears: blue in V7 only, green in both, amber in V8 only.'
    for node in list(body.findall(w('p'))):
        if text_of(node) == table_note:
            body.remove(node)
    for row in decisions:
        for name in ('v7', 'v8'):
            for p in row[name]:
                anchor = reference_anchor(name, p)
                if anchor not in existing_names:
                    additional_quotes[anchor] = (name, p, compared[name]['paragraphs'][p - 1])
                    existing_names.add(anchor)
    if additional_quotes:
        section = body.find(w('sectPr'))
        if section is not None:
            body.remove(section)
        paragraph(body, 'Additional source passages', 'Heading1')
        next_id = max(int(node.get(w('id'))) for node in body.iter(w('bookmarkStart'))) + 1
        for anchor, (name, p, text) in additional_quotes.items():
            para = paragraph(body, f'{name.upper()} P{p}', 'Heading2')
            sub(para, 'bookmarkStart', id=next_id, name=anchor)
            sub(para, 'bookmarkEnd', id=next_id)
            paragraph(body, text)
            next_id += 1
        if section is not None:
            body.append(section)
    styles = E.fromstring(parts['word/styles.xml'])
    quote_style = next((node for node in styles.findall(w('style'))
                        if node.get(w('styleId')) == 'SourceQuote'), None)
    if quote_style is None:
        quote_style = sub(styles, 'style', type='paragraph', styleId='SourceQuote')
        sub(quote_style, 'name', val='Source Quote')
        sub(quote_style, 'basedOn', val='Normal')
        sub(quote_style, 'next', val='Normal')
        props = sub(quote_style, 'pPr')
        sub(props, 'ind', left=300, right=120)
        sub(props, 'shd', val='clear', fill='F3F4F5')
        sub(sub(props, 'pBdr'), 'left', val='single', sz=12, space=8, color='999999')
        sub(props, 'spacing', before=90, after=110, line=250, lineRule='auto')
        sub(sub(quote_style, 'rPr'), 'i')
    for para in body.iter(w('p')):
        props = para.find(w('pPr'))
        if props is None:
            continue
        indent = props.find(w('ind'))
        if indent is not None and indent.get(w('left')) == '180':
            style = props.find(w('pStyle'))
            if style is None:
                style = E.Element(w('pStyle'))
                props.insert(0, style)
            style.set(w('val'), 'SourceQuote')
            props.remove(indent)
    parts['word/styles.xml'] = xml(styles)
    link_change_rows(document, decisions)
    parts['word/document.xml'] = xml(document)
    core = E.fromstring(parts['docProps/core.xml'])
    title = core.find('{http://purl.org/dc/elements/1.1/}title')
    if title is not None:
        title.text = 'V7 to V8: how I put this comparison together'
    parts['docProps/core.xml'] = xml(core)
    temporary = OUTPUT.with_suffix('.new.docx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    with ZipFile(temporary) as archive:
        assert archive.testzip() is None
    assert source.read_bytes() == original_bytes
    temporary.replace(OUTPUT)
    print('Created', OUTPUT.name, 'with the version evidence first; saved review and comments preserved.')


def prepend_decisions():
    here = ROOT / 'build/alyson_feedback_review_20261013'
    decisions = json.loads((here / 'v7_v8_decisions.json').read_text())
    documents = json.loads((here / 'v7_v8_comparison.json').read_text())['documents']
    if OUTPUT == ANNOTATED:
        raise ValueError('Use --output for a separate copy; the original is open in Word/LibreOffice')
    if (OUTPUT.parent / ('.~lock.' + OUTPUT.name + '#')).exists():
        raise ValueError('Output is open; do not overwrite unsaved work')
    with ZipFile(ANNOTATED) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    document = E.fromstring(parts['word/document.xml'])
    body = document.find(w('body'))
    children = list(body)
    source = next(i for i, node in enumerate(children) if ''.join(node.itertext()) == 'Source transcript')
    if any(node.find('.//' + w('commentRangeStart')) is not None for node in children[:source]):
        raise ValueError('Cover has comments; preserve them for manual review')
    retained = children[source:]
    for node in list(body):
        body.remove(node)

    def para(parent, text, style=None, bold=False, quote=False, compact=False):
        item = paragraph(parent, text, style)
        props = item.find(w('pPr'))
        sub(props, 'jc', val='left')
        spacing = props.find(w('spacing'))
        spacing.set(w('after'), '70' if compact else '120')
        spacing.set(w('line'), '250')
        if style:
            sub(props, 'keepNext')
        if quote:
            sub(props, 'ind', left=180)
        if bold or compact:
            run = item.find(w('r'))
            run_props = E.Element(w('rPr'))
            if bold:
                sub(run_props, 'b')
            if compact:
                sub(run_props, 'sz', val=20)
            run.insert(0, run_props)
        return item

    def link(parent, label, anchor):
        item = sub(parent, 'hyperlink', anchor=anchor)
        run = sub(item, 'r')
        props = sub(run, 'rPr')
        sub(props, 'u', val='single')
        sub(props, 'sz', val=18)
        text = sub(run, 't')
        text.set(XML + 'space', 'preserve')
        text.text = label

    para(body, 'V7 to V8: proposed decisions', 'Heading1')
    para(body, 'V7 is the manuscript Tristan sent. V8 is the returned rewrite. Every changed, added or removed main-text paragraph is covered below.')
    para(body, 'The table lists 52 choices about the rewrite.')
    para(body, 'My suggestions', 'Heading2')
    table = sub(body, 'tbl')
    props = sub(table, 'tblPr')
    widths = [800, 1800, 1850, 4910]
    sub(props, 'tblW', w=sum(widths), type='dxa')
    sub(props, 'tblLayout', type='fixed')
    borders = sub(props, 'tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        sub(borders, edge, val='single', sz=4, color='D4D4D4')
    margins = sub(props, 'tblCellMar')
    for edge in ('left', 'right', 'top', 'bottom'):
        sub(margins, edge, w=90, type='dxa')
    grid = sub(table, 'tblGrid')
    for width in widths:
        sub(grid, 'gridCol', w=width)
    rows = [['ID', 'What changed', 'My suggestion', 'What the drafts show']] + [
        [row['id'], row['title'], row['decision'], row['reason']] for row in decisions]
    for row_number, values in enumerate(rows):
        row = sub(table, 'tr')
        row_props = sub(row, 'trPr')
        sub(row_props, 'cantSplit')
        if row_number == 0:
            sub(row_props, 'tblHeader')
        for column, (value, width) in enumerate(zip(values, widths)):
            cell = sub(row, 'tc')
            cell_props = sub(cell, 'tcPr')
            sub(cell_props, 'tcW', w=width, type='dxa')
            sub(cell_props, 'vAlign', val='top')
            if row_number == 0:
                sub(cell_props, 'shd', fill='F0F0F0')
            para(cell, value, bold=row_number == 0 or column == 2, compact=True)
            if row_number and column == 3:
                decision = decisions[row_number - 1]
                refs = sub(cell, 'p')
                for name in ('v7', 'v8'):
                    for p in decision[name]:
                        link(refs, f'{name.upper()} P{p}  ', f'cmp_{name}_P{p}')
    para(body, '')
    para(body, 'Cited V7 and V8 passages', 'Heading1')
    para(body, 'Each passage is printed once. The table links to these passages. Original scientific terms are retained inside the quotes; the decision explanations use plain language.')
    bookmark_id = 60000
    for name in ('v7', 'v8'):
        para(body, name.upper(), 'Heading2')
        numbers = sorted({p for row in decisions for p in row[name]})
        for p in numbers:
            label = para(body, f'{name.upper()} P{p}', 'Heading3')
            sub(label, 'bookmarkStart', id=bookmark_id, name=f'cmp_{name}_P{p}')
            sub(label, 'bookmarkEnd', id=bookmark_id)
            bookmark_id += 1
            para(body, documents[name]['paragraphs'][p - 1], quote=True)
    para(body, 'Feedback suggestions and review comments', 'Heading1')
    para(body, 'The pasted discussion follows. The comments are our review notes, not Alyson’s edits. Full evidence and the proposed decisions are in ALYSON_FEEDBACK_CHECK_20261013.md.')
    for node in retained:
        body.append(node)
    parts['word/document.xml'] = xml(document)
    if 'docProps/core.xml' in parts:
        core = E.fromstring(parts['docProps/core.xml'])
        title = core.find('{http://purl.org/dc/elements/1.1/}title')
        if title is not None:
            title.text = 'V7 to V8: proposed decisions'
        parts['docProps/core.xml'] = xml(core)
    temporary = OUTPUT.with_suffix('.new.docx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    with ZipFile(temporary) as archive:
        assert archive.testzip() is None
    temporary.replace(OUTPUT)
    print('Created', OUTPUT.name, 'with', len(decisions), 'decisions first; original Word copy untouched.')


source_bytes = SOURCE.read_bytes()
lines = source_bytes.decode('utf-8').splitlines()
if args.cache_page_numbers:
    cache_page_numbers()
    sys.exit(0)
if args.label_destinations:
    label_destinations()
    sys.exit(0)
if args.lead_with_findings:
    lead_with_findings()
    sys.exit(0)
if args.prepend_decisions:
    prepend_decisions()
    sys.exit(0)
if args.format_existing:
    format_existing(lines)
    assert SOURCE.read_bytes() == source_bytes
    sys.exit(0)
report = REPORT.read_text()
short = report.split('## Short answers to the saved transcript\n', 1)[1]
short = short.split('## What remains\n', 1)[0]
notes = []
# The owned short-answer table supplies every exported comment.
for line in short.splitlines():
    if not line.startswith('| L'):
        continue
    fields = [cell.strip() for cell in line.split('|')[1:-1]]
    if len(fields) != 4:
        raise ValueError('Unexpected short-answer row: ' + line)
    refs, status, answer, details = fields
    anchor = min(map(int, re.findall(r'\d+', refs)))
    while not lines[anchor - 1]:
        anchor += 1
    notes.append((anchor, refs, status, answer, details))
if not notes:
    raise ValueError('No short answers found')
if args.granular_comments:
    notes = granular_notes(notes)

if args.refresh_comments:
    if (OUTPUT.parent / ('.~lock.' + OUTPUT.name + '#')).exists():
        raise ValueError('Output is open; preserve unsaved work')
    with ZipFile((args.source_document or OUTPUT).resolve()) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    comments = E.fromstring(parts['word/comments.xml'])
    existing = comments.findall(w('comment'))
    if (not args.granular_comments and len(existing) != len(notes)) or any(c.get(w('author')) != 'Review notes' for c in existing):
        raise ValueError('Comment set changed; preserve it for manual review')
    document = embed_evidence(parts, notes)
    anchors = {node.get(w('name')) for node in document.iter(w('bookmarkStart'))}
    if args.granular_comments:
        old_ids = {c.get(w('id')) for c in existing}
        for tag in ('commentRangeStart', 'commentRangeEnd', 'commentReference'):
            for node in list(document.iter(w(tag))):
                if node.get(w('id')) not in old_ids:
                    raise ValueError('Unowned comment marker; preserve it')
                parent = node.getparent()
                parent.remove(node)
                if tag == 'commentReference' and not parent.findall(w('t')):
                    parent.getparent().remove(parent)
        for child in list(comments):
            comments.remove(child)
        now = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
        existing = []
        for index in range(len(notes)):
            existing.append(E.SubElement(comments, w('comment'), {
                w('id'): str(index), w('author'): 'Review notes', w('initials'): 'RN', w('date'): now}))
        body = document.find(w('body'))
        intro = next(node for node in body if ''.join(node.itertext()) == 'Source transcript')
        if not document.xpath('//w:bookmarkStart[@w:name="comment_color_key"]', namespaces={'w': W}):
            key = paragraph(E.Element('holder'), 'Comment colors: ')
            sub(key, 'bookmarkStart', id=max(int(n.get(w('id'))) for n in document.iter(w('bookmarkStart'))) + 1,
                name='comment_color_key')
            sub(key, 'bookmarkEnd', id=key.find(w('bookmarkStart')).get(w('id')))
            for label, (color, fill) in COMMENT_PALETTES.items():
                if label == 'Not a paper claim':
                    continue
                run = text_run(key, label + '  ')
                props = sub(run, 'rPr')
                run.insert(0, props)
                sub(props, 'b')
                sub(props, 'color', val=color)
                sub(props, 'shd', fill=fill, val='clear')
            guide = next((node for node in body if ''.join(node.itertext()) == 'Reading guide'), None)
            first_comparison = next((node for node in body if ''.join(node.itertext()) == '1. Points already covered in V7'), None)
            key_position = body.index(first_comparison) if guide is not None and first_comparison is not None else 1
            body.insert(key_position, key)
            explanation = paragraph(E.Element('holder'),
                'Manuscript links compare the linked passages: blue means V7 only, green means the same passage in both drafts, and orange means V8 only. '
                'Comment labels and highlights describe whether the point is covered, even when its wording changed. '
                'Gray marks a point absent from both drafts; our note says when later files supply it. Black links are navigation, later sources or mixed points; links are never gray.')
            body.insert(key_position + 1, explanation)
        for index, note in enumerate(notes):
            source_line, _, status, _, _, needle = note
            source_anchor = f'src_L{source_line:03d}'
            bookmark = document.xpath(f'//w:bookmarkStart[@w:name="{source_anchor}"]', namespaces={'w': W})
            if len(bookmark) != 1:
                raise ValueError('Missing granular source: ' + source_anchor)
            first = bookmark[0].getparent()
            row = next((n for n in first.iterancestors() if n.tag == w('tr')), None)
            candidates = list(row.iter(w('p'))) if row is not None else [first]
            if needle is not None:
                candidates = [p for p in candidates if needle in ''.join(p.itertext())]
                if len(candidates) != 1:
                    raise ValueError('Source wording not found: ' + str(source_line) + ' ' + needle)
            start_p, end_p = candidates[0], candidates[-1]
            if needle is not None:
                matches = [r for r in start_p.findall(w('r')) if needle in ''.join(r.itertext())]
                if len(matches) != 1:
                    raise ValueError('Source span crosses runs: ' + needle)
                run = matches[0]
                text = ''.join(run.itertext())
                before, after = text.split(needle, 1)
                position = start_p.index(run)
                replacement = []
                for part in (before, needle, after):
                    clone = deepcopy(run)
                    for child in list(clone):
                        if child.tag != w('rPr'):
                            clone.remove(child)
                    sub(clone, 't').text = part
                    clone[-1].set(XML + 'space', 'preserve')
                    replacement.append(clone)
                start_p.remove(run)
                for offset, node in enumerate(replacement):
                    start_p.insert(position + offset, node)
                start_node = end_node = replacement[1]
            else:
                def content_nodes(p):
                    return [node for node in p if node.findall('.//' + w('t'))
                            and not (node.find(w('br')) is not None
                                     and re.fullmatch(r'(?:Feedback )?L\d+', ''.join(node.itertext())))]
                start_node = content_nodes(start_p)[0]
                end_node = content_nodes(end_p)[-1]
            start_p.insert(start_p.index(start_node), E.Element(w('commentRangeStart'), {w('id'): str(index)}))
            end_p.insert(end_p.index(end_node) + 1, E.Element(w('commentRangeEnd'), {w('id'): str(index)}))
            reference = E.Element(w('r'))
            sub(sub(reference, 'rPr'), 'rStyle', val='CommentReference')
            sub(reference, 'commentReference', id=index)
            end_p.insert(end_p.index(end_node) + 2, reference)
            parts['word/document.xml'] = xml(document)
    for index, note in enumerate(notes):
        source_line, refs, status, answer, details = note[:5]
        answer = table_handles(answer)
        comment = next(c for c in existing if c.get(w('id')) == str(index))
        source_anchor = f'src_L{source_line:03d}'
        source_nodes = document.xpath(f'//w:commentRangeStart[@w:id="{index}"]/ancestor::w:p[1]', namespaces={'w': W})
        if len(source_nodes) != 1 or (not args.granular_comments and source_anchor not in {node.get(w('name')) for node in source_nodes[0].iter(w('bookmarkStart'))}):
            raise ValueError('Comment source changed: ' + str(index))
        for child in list(comment):
            comment.remove(child)
        paragraph(comment, status + '.')
        for block in re.split(r'<br\s*/?>', answer):
            para = sub(comment, 'p')
            cursor = 0
            for match in re.finditer(r'\b(v[78])\s+P(\d+)\b|\bFeedback L(\d+)\b', block, re.I):
                text_run(para, block[cursor:match.start()])
                target = (f'src_L{int(match[3]):03d}' if match[3]
                          else f'cmp_{match[1].lower()}_P{int(match[2])}')
                if target not in anchors:
                    raise ValueError('Missing comment source passage: ' + target)
                internal_link(para, match[0], target)
                cursor = match.end()
            text_run(para, block[cursor:])
        related = []
        for source_range in refs.split(';'):
            numbers = list(map(int, re.findall(r'\d+', source_range)))
            first = numbers[0]
            last = numbers[-1]
            first = next((n for n in range(first, last + 1)
                          if f'src_L{n:03d}' in anchors), None)
            if first is None:
                raise ValueError('No linked source paragraph in ' + source_range)
            if first == source_line:
                continue
            label = f'L{first}' + (f'-{last}' if first != last else '')
            related.append((label, f'src_L{first:03d}'))
        if related:
            para = paragraph(comment, 'Related passages: ')
            for n, (label, target) in enumerate(related):
                if target not in anchors:
                    raise ValueError('Missing related transcript passage: ' + target)
                if n:
                    text_run(para, ' · ')
                internal_link(para, 'Feedback ' + label, target)
        para = paragraph(comment, 'Links: ')
        internal_link(para, f'Feedback L{source_line}', source_anchor)
        if details == 'Published-paper table':
            text_run(para, ' · ')
            internal_link(para, 'Published papers', 'published_comparisons')
        else:
            evidence_ids = []
            for group in details.split(';'):
                match = re.fullmatch(r'\s*([A-F])(\d{2})(?:-([A-F])?(\d{2}))?\s*', group)
                if match is None:
                    raise ValueError('Unrecognized evidence handles: ' + details)
                last = int(match[4]) if match[4] else int(match[2])
                if match[3] and match[3] != match[1]:
                    raise ValueError('Evidence range crosses sections: ' + group)
                evidence_ids.extend(f'{match[1]}{number:02d}' for number in range(int(match[2]), last + 1))
            for row in dict.fromkeys(CHECK_ROWS[key] for key in evidence_ids):
                target = 'change_' + row
                if target not in anchors:
                    raise ValueError('Missing evidence target: ' + key)
                text_run(para, ' · ')
                internal_link(para, row, target, color='222222')
    if args.granular_comments:
        source_categories = categories_at_sources(comments)
        for comment in comments:
            status = ''.join(comment[0].itertext())
            label = next(label for label in COMMENT_PALETTES if status.startswith(label))
            color, fill = COMMENT_PALETTES[label]
            for run in comment.iter(w('r')):
                props = run.find(w('rPr'))
                if props is None:
                    props = E.Element(w('rPr'))
                    run.insert(0, props)
                existing_color = props.find(w('color'))
                if existing_color is None:
                    existing_color = sub(props, 'color')
                existing_color.set(w('val'), color)
                if color == COMMENT_PALETTES['Not supplied in V7 or V8'][0] and run.getparent().tag == w('hyperlink'):
                    existing_color.set(w('val'), '222222')
                if run.getparent() is comment[0]:
                    sub(props, 'b')
                    sub(props, 'shd', fill=fill, val='clear')
        for p in document.iter(w('p')):
            bookmark = p.find(w('bookmarkStart'))
            if bookmark is None:
                continue
            kinds = source_categories.get(bookmark.get(w('name')), set())
            color = COMMENT_PALETTES[next(iter(kinds))][0] if len(kinds) == 1 else '222222'
            for run in p.findall(w('r')):
                if run.find(w('br')) is not None and re.fullmatch(r'(?:Feedback )?L\d+', ''.join(run.itertext())):
                    run.find(w('rPr')).find(w('color')).set(w('val'), color)
        label_source_passages(document, comments)
    compared = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_comparison.json').read_text())['documents']
    decisions = json.loads((ROOT / 'build/alyson_feedback_review_20261013/v7_v8_decisions.json').read_text())
    link_change_rows(document, decisions)
    add_change_feedback(document, decisions)
    link_checks_to_rows(document, comments)
    link_handles_in_prose(document, comments, compared)
    pair_shared_passage_links(document, comments, compared)
    color_source_links(document, comments, compared, source_categories if args.granular_comments else {})
    if args.granular_comments:
        shade_comment_sources(document, comments)
    for para in document.find(w('body')).findall(w('p')):
        if ''.join(para.xpath('.//w:t/text()', namespaces={'w': W})).startswith('Manuscript links compare the linked passages:'):
            for child in list(para):
                if child.tag != w('pPr'):
                    para.remove(child)
            text_run(para, 'Link colors compare the passage wording: blue V7 only, green identical in both, orange V8 only. Comment colors show whether the point was covered. Gray notes mean absent from both drafts; the note says when later files supply it. Black links are navigation, later sources or mixed points.')
    space_handles(document)
    space_handles(comments)
    parts['word/comments.xml'] = xml(comments)
    for item in document.iter(w('t')):
        if item.text == 'New measurements: finished channel sizes and individual mold histories. These are not existing data.':
            item.text = 'Optional measurements: finished-device width from calibrated images; mold histories if available. No requirement for a new height experiment is established by the feedback.'
    parts['word/document.xml'] = xml(document)
    order_reference_sections(parts)
    add_contents(parts)
    add_intro_links(parts)
    add_section_footer(parts)
    add_review_header(parts)
    temporary = OUTPUT.with_suffix('.refresh.docx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with ZipFile(temporary) as archive:
        assert archive.testzip() is None
    temporary.replace(OUTPUT)
    print('Refreshed', len(notes), 'anchored review comments; working manuscript untouched.')
    sys.exit(0)

for path in (OUTPUT, WORKING):
    if path.exists():
        raise FileExistsError(path)

reference = subprocess.check_output(['pandoc', '--print-default-data-file', 'reference.docx'])
with ZipFile(BytesIO(reference)) as archive:
    parts = {name: archive.read(name) for name in archive.namelist()}
document = E.Element(w('document'))
body = sub(document, 'body')
paragraph(body, 'Alyson feedback: transcript and review notes', 'Title')
paragraph(body, 'The transcript is copied from alyson_feedback.md. Its pasted-table spacing is preserved. L numbers identify lines in that file.')
paragraph(body, 'Comments are our draft review notes, not Alyson\'s edits. Repeated recommendations share one answer.')
paragraph(body, 'Sources refer to mfd_draft_v8_alyson_feedback.docx. P numbers identify its body paragraphs. Search the quoted wording in that document.')
paragraph(body, 'The opening comparison distinguishes the sent V7 from returned V8.')
paragraph(body, 'mfd_draft_v9_working.docx preserves the v8 text and images, with Track Changes enabled for future edits.')
paragraph(body, 'What remains', 'Heading1')
for text in (
    'Text fixes: direct supporting-figure/table links; baseline-image context; conflicts before data availability.',
    'Presentation: Table S2 word breaks; correct Figure 4 scale bars; final bibliography and reference format.',
    'Missing facts: exact counts, excluded IDs, counting settings/error bars; ethics details; deposited study files.',
    'Optional measurements: finished-device width from calibrated images; mold histories if available. No requirement for a new height experiment is established by the feedback.',
    'Optional: height panel, clearer labels, shorter Figure 3 legend and other styling.',
):
    paragraph(body, text)
paragraph(body, 'Full quotations and calculations: ALYSON_FEEDBACK_CHECK_20261013.md in this review folder.')
page = sub(body, 'p')
sub(sub(page, 'r'), 'br', type='page')
paragraph(body, 'Source transcript', 'Heading1')
by_line = {}
for index, note in enumerate(notes):
    by_line.setdefault(note[0], []).append(index)
comments = E.Element(w('comments'))
now = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
headings = {1, 13, 29, 57, 86, 95, 118, 133, 142, 180, 198, 199, 224, 249, 272, 303, 329, 361, 374, 404, 420, 438, 454, 479, 502, 517, 530, 545, 546, 555, 566, 573, 580, 587, 600}
for number, text in enumerate(lines, 1):
    if not text:
        continue
    item = sub(body, 'p')
    props = sub(item, 'pPr')
    if number in headings:
        sub(props, 'pStyle', val='Heading2')
    sub(props, 'spacing', after=80, line=240, lineRule='auto')
    text_run(item, f'L{number:03d}  ', small=True)
    for index in by_line.get(number, []):
        sub(item, 'commentRangeStart', id=index)
    text_run(item, text)
    for index in reversed(by_line.get(number, [])):
        sub(item, 'commentRangeEnd', id=index)
        run = sub(item, 'r')
        sub(sub(run, 'rPr'), 'rStyle', val='CommentReference')
        sub(run, 'commentReference', id=index)
        _, refs, status, answer, details = notes[index]
        comment = E.SubElement(comments, w('comment'), {w('id'): str(index), w('author'): 'Review notes', w('initials'): 'RN', w('date'): now})
        paragraph(comment, status + '. Transcript ' + refs + '.')
        paragraph(comment, answer)
        paragraph(comment, 'Detailed sources: ' + details + ' in ALYSON_FEEDBACK_CHECK_20261013.md.')
section = sub(body, 'sectPr')
sub(section, 'pgSz', w=12240, h=15840)
sub(section, 'pgMar', top=1440, bottom=1440, left=1440, right=1440, header=720, footer=720)
parts['word/document.xml'] = xml(document)
parts['word/comments.xml'] = xml(comments)
relationships = E.fromstring(parts['word/_rels/document.xml.rels'])
if not any(item.get('Type') == R + '/comments' for item in relationships):
    ids = {item.get('Id') for item in relationships}
    index = 1
    while 'rId' + str(index) in ids:
        index += 1
    E.SubElement(relationships, '{' + PKG + '}Relationship', {'Id': 'rId' + str(index), 'Type': R + '/comments', 'Target': 'comments.xml'})
parts['word/_rels/document.xml.rels'] = xml(relationships)
types = E.fromstring(parts['[Content_Types].xml'])
if not any(item.get('PartName') == '/word/comments.xml' for item in types):
    E.SubElement(types, '{' + CT + '}Override', {'PartName': '/word/comments.xml', 'ContentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml'})
parts['[Content_Types].xml'] = xml(types)
styles = E.fromstring(parts['word/styles.xml'])
for style in styles.findall(w('style')):
    if style.get(w('styleId')) in ('Normal', 'Title', 'Heading1', 'Heading2', 'CommentText'):
        props = style.find(w('rPr'))
        if props is None:
            props = sub(style, 'rPr')
        for tag in ('rFonts', 'sz', 'szCs', 'color'):
            for item in props.findall(w(tag)):
                props.remove(item)
        sub(props, 'rFonts', ascii='Times New Roman', hAnsi='Times New Roman')
        size = 32 if style.get(w('styleId')) == 'Title' else 24
        sub(props, 'sz', val=size)
        sub(props, 'szCs', val=size)
        sub(props, 'color', val='000000')
parts['word/styles.xml'] = xml(styles)
with ZipFile(OUTPUT, 'w', ZIP_DEFLATED) as archive:
    for name, data in parts.items():
        archive.writestr(name, data)
with ZipFile(BASELINE) as archive:
    base_parts = {name: archive.read(name) for name in archive.namelist()}
settings = E.fromstring(base_parts['word/settings.xml'])
track = settings.find(w('trackRevisions'))
if track is None:
    track = sub(settings, 'trackRevisions')
track.set(w('val'), 'true')
base_parts['word/settings.xml'] = xml(settings)
with ZipFile(WORKING, 'w', ZIP_DEFLATED) as archive:
    for name, data in base_parts.items():
        archive.writestr(name, data)
assert SOURCE.read_bytes() == source_bytes
print('Created annotated feedback with', len(notes), 'comments.')
print('Created v9 working copy: text/images unchanged; Track Changes enabled.')
