import xml.etree.ElementTree as et
import zipfile
import xml_navigator as xmlnav
import consolidate
import in_para_allcontent


WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
RELATION_NAMESPACE = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
PARA_NAMESPACE = WORD_NAMESPACE + 'p'
STYLE_NAMESPACE = WORD_NAMESPACE + 'pStyle'
TEXT_NAMESPACE = WORD_NAMESPACE + 't'
BOOKMARK_NAMESPACE = WORD_NAMESPACE + 'bookmarkStart'
HYPERLINK_NAMESPACE = WORD_NAMESPACE + 'hyperlink'
VALUE_KEY = WORD_NAMESPACE + 'val'
BOOKMARKNAME_KEY = WORD_NAMESPACE + 'name'
LINK_KEY = WORD_NAMESPACE + 'anchor'
URL_LINK_KEY = RELATION_NAMESPACE + 'id'

PARAGRAPH_KEY = 'paragraphs'


def get_xml_root(docx_path):
    with zipfile.ZipFile(docx_path) as document:
        xml_content = document.read('word/document.xml')
    xml_root = et.fromstring(xml_content)
    return xml_root


def extract_style(element):
    DEFAULT_STYLE = 'normal'
    style = DEFAULT_STYLE
    style_elm = xmlnav.find_first(element, STYLE_NAMESPACE)
    if style_elm is not None and VALUE_KEY in style_elm.attrib:
        style = style_elm.attrib[VALUE_KEY].lower()
    if style == 'HTMLPreformatted'.lower():
        style = DEFAULT_STYLE
    return style


def extract_bookmark(element):
    bookmark_name = element.attrib[BOOKMARKNAME_KEY]
    if bookmark_name != '_GoBack':
        bookmark_encoding = {'type': 'anchor', 'name': bookmark_name, 'content': ''}
    else:
        bookmark_encoding = None
    return bookmark_encoding


def extract_hyperlink(element):
    return {'type': 'phrase', 'destination': find_link(element), 'content': find_text(element)}


def extract_text(element):
    text = find_text(element)
    if text is not None:
        text_encoding = {'type': 'text', 'content': text}
    else:
        text_encoding = None
    return text_encoding


def find_link(element):
    if LINK_KEY in element.attrib:
        link_encoding = element.attrib[LINK_KEY]
    elif URL_LINK_KEY in element.attrib:
        link_encoding = element.attrib[URL_LINK_KEY]
    else:
        link_encoding = None
    return link_encoding


def find_text(element):
    collected_text = ""
    for node in xmlnav.every(element, TEXT_NAMESPACE):
        collected_text += node.text
    if collected_text == "":
        collected_text = None
    return collected_text


def content_per_type(element):
    extractor_map = {
        BOOKMARK_NAMESPACE: extract_bookmark,
        HYPERLINK_NAMESPACE: extract_hyperlink
    }
    if element.tag in extractor_map:
        content = extractor_map[element.tag](element)
    else:
        content = extract_text(element)
    return content


def extract_content(para_element, style):
    contentlist = []
    def add_if_not_none(x):
        if x is not None:
            contentlist.append(x)
    for child_of_para in xmlnav.children(para_element):
        add_if_not_none(content_per_type(child_of_para))
    contentlist = consolidate.consolidate_contentlist(contentlist)
    contentlist = consolidate.extract_inline_from_texts(contentlist, style)
    return contentlist


def compute_current_area(style, contentlist, current_area):
    text_contentlist = in_para_allcontent.pick_contents(contentlist, lambda x: x['type'] == 'text')
    if text_contentlist:
        content_text = text_contentlist[0]["content"]
        if style == 'heading1':
            current_area['chapter'] = content_text
            current_area['shloka'] = ''
        if style == 'heading2':
            current_area['shloka'] = content_text
    return current_area


def encode_doc(docx_path):
    paragraphs = []
    current_area = {'chapter': '', 'shloka': ''}
    xml_root = get_xml_root(docx_path)
    for para_element in xmlnav.every(xml_root, PARA_NAMESPACE):
        style = extract_style(para_element)
        contentlist = extract_content(para_element, style)
        current_area = compute_current_area(style, contentlist, current_area)
        para_encoding = {'id': '*',
                         'chapter': current_area['chapter'],
                         'shloka': current_area['shloka'],
                         'content': contentlist,
                         'style': style}
        paragraphs.append(para_encoding)
    return {'paragraphs': paragraphs}
