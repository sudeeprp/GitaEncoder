import in_para_externalref


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
    consolidated_text = content
    search_index += 1
    while search_index < len(contentlist):
        para_type, content = get_type_and_text(contentlist[search_index])
        if para_type == starting_type:
            consolidated_text += content
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


def extract_inline_from_texts(contentlist, style):
    if style != 'normal':
        return contentlist

    extracted_contentlist = []
    for content in contentlist:
        if content["type"] == "text":
            extracted_contentlist += in_para_externalref.expand_extref_in_text_content(content)
        else:
            extracted_contentlist.append(content)
    return extracted_contentlist
