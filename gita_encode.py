import xml.etree.ElementTree as et
import re
import zipfile
import xml_navigator as xmlnav


WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA_NAMESPACE = WORD_NAMESPACE + 'p'
STYLE_NAMESPACE = WORD_NAMESPACE + 'pStyle'
TEXT_NAMESPACE = WORD_NAMESPACE + 't'
BOOKMARK_NAMESPACE = WORD_NAMESPACE + 'bookmarkStart'
HYPERLINK_NAMESPACE = WORD_NAMESPACE + 'hyperlink'
VALUE_KEY = WORD_NAMESPACE + 'val'
BOOKMARKNAME_KEY = WORD_NAMESPACE + 'name'
LINK_KEY = WORD_NAMESPACE + 'anchor'

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
        bookmark_encoding = {'type': 'anchor', 'name': bookmark_name}
    else:
        bookmark_encoding = None
    return bookmark_encoding


def extract_hyperlink(element):
    return {'type': 'phrase', 'english': find_text(element), 'destination': find_link(element)}


def extract_inline_from_text(text):
    externalref_regex = r'(\[[\w\s]+],[\s]*[\w\-]+)'
    components = re.split(externalref_regex, text)
    extracts = []
    for text_component in components:
        if text_component.startswith('['):
            extracts.append({'type': 'externalref', 'translit': text_component})
        else:
            extracts.append({'type': 'text', 'english': text_component})
    return extracts


def extract_text(element):
    text = find_text(element)
    if text is not None:
        text_encoding = {'type': 'text', 'english': text}
    else:
        text_encoding = None
    return text_encoding


def find_link(element):
    if LINK_KEY in element.attrib:
        link_encoding = element.attrib[LINK_KEY]
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


def extract_content(para_element):
    content = []
    def add_if_not_none(x):
        if x is not None:
            content.append(x)
    for child_of_para in xmlnav.children(para_element):
        add_if_not_none(content_per_type(child_of_para))
    return content


def encode_doc(docx_path):
    paragraphs = []
    xml_root = get_xml_root(docx_path)
    for para_element in xmlnav.every(xml_root, PARA_NAMESPACE):
        para_encoding = {'id': '*',
                         'content': extract_content(para_element),
                         'style': extract_style(para_element)}
        paragraphs.append(para_encoding)
    return {'paragraphs': paragraphs}
