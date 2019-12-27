import re


def get_type_and_text(para):
    para_type = ''
    content = ''
    if 'type' in para:
        para_type = para['type']
    if 'content' in para:
        content = para['content']
    return para_type, content


def consolidate_adjacent(contentlist, search_index):
    para_type, content = get_type_and_text(contentlist[search_index])
    if para_type != 'text':
        return contentlist[search_index], search_index + 1
    starting_type = para_type
    consolidated_text = content.strip()
    search_index += 1
    while search_index < len(contentlist):
        para_type, content = get_type_and_text(contentlist[search_index])
        if para_type == starting_type:
            consolidated_text += ' ' + content.strip()
            search_index += 1
        else:
            break
    return {'type': 'text', 'content': consolidated_text}, search_index


def consolidate_contentlist(contentlist):
    consolidated_contentlist = []
    search_index = 0
    while search_index < len(contentlist):
        merged_batch, search_index = consolidate_adjacent(contentlist, search_index)
        consolidated_contentlist.append(merged_batch)
    return consolidated_contentlist


def extract_inline_from_text(text):
    externalref_regex = r'(\[[\w\s]+],[\s]*[\w\-]+)'
    components = re.split(externalref_regex, text)
    extracts = []
    for text_component in components:
        if text_component.startswith('['):
            extracts.append({'type': 'externalref', 'translit': text_component})
        else:
            extracts.append({'type': 'text', 'content': text_component})
    return extracts
