import os
import re
import json
import string
import unittest
import gita_encode
import matcher
import in_para_text
import in_para_id
import in_para_bookmark
import in_para_phrase
import in_para_externalref
import in_para_allcontent


def strip_whitespaces(string_with_whitespace):
    return string_with_whitespace.translate(str.maketrans('', '', string.whitespace))


def encoding_of_doc_matches(test_docx_filename, expected_json_patterns):
    docx_as_dict = gita_encode.encode_doc(os.path.join('../test_data', test_docx_filename))
    docx_as_jsonstr_nospace = strip_whitespaces(json.dumps(docx_as_dict))
    matched = True
    for expected_json_regex in expected_json_patterns:
        expected_regex_nospace = strip_whitespaces(expected_json_regex)
        if re.search(expected_regex_nospace, docx_as_jsonstr_nospace) is None:
            print(f'--Regex not matched: {expected_json_regex}')
            matched = False
    return matched


def match_results(content_regex, object_list):
    matched_results = []
    for list_member in object_list:
        matched_results.append(matcher.match(content_regex, list_member))
    return matched_results


def paras_from(docx_filename):
    docx_as_dict = gita_encode.encode_doc(os.path.join('../test_data', docx_filename))
    return in_para_allcontent.paralist(docx_as_dict)


class EncodeTest(unittest.TestCase):
    def assertAllAreOk(self, results):
        self.assertTrue(results and False not in results)

    def assertAtleastOneOk(self, results):
        self.assertTrue(True in results)

    def test_no_array_in_array(self):
        array_in_array_pattern = [r'\[\[']
        self.assertFalse(encoding_of_doc_matches('heading1.docx', array_in_array_pattern))

    def test_doc_is_encoded_as_para(self):
        paragraphs = paras_from('heading1.docx')
        para_ids_ok = match_results(in_para_id.content_regex, paragraphs)
        para_texts_ok = match_results(in_para_allcontent.content_regex, paragraphs)
        self.assertAllAreOk(para_ids_ok)
        self.assertAtleastOneOk(para_texts_ok)

    def test_H1_is_encoded_as_a_para(self):
        paragraphs = paras_from('heading1.docx')
        contents = paragraphs[0]['content']
        contents_comply = match_results(in_para_text.content_regex, contents)
        self.assertAtleastOneOk(contents_comply)

        style = paragraphs[0]['style']
        self.assertEqual(style, 'heading1')

        expected_content = {"type": "text", "content": "Chapter 1"}
        expected_finds = match_results(expected_content, contents)
        self.assertAtleastOneOk(expected_finds)

    def test_default_style_is_normal(self):
        paragraphs = paras_from('anchor.docx')
        style = paragraphs[0]['style']
        self.assertEqual(style, 'normal')

    def test_bookmark_is_encoded_as_anchor(self):
        anchors_match = []
        for para in paras_from('anchor.docx'):
            anchor_contents = in_para_allcontent.pick_contents\
                (in_para_allcontent.contentlist(para), lambda x: x['type'] == "anchor")
            for content in anchor_contents:
                anchors_match.append(matcher.match(in_para_bookmark.content_regex, content))
        self.assertAllAreOk(anchors_match)

    def test_link_is_encoded_as_phrase(self):
        links_match = []
        for para in paras_from('bookmark with link.docx'):
            phrase_contents = in_para_allcontent.pick_contents\
                (in_para_allcontent.contentlist(para), lambda x: x["type"] == "phrase")
            for content in phrase_contents:
                links_match.append(matcher.match(in_para_phrase.content_regex, content))
        self.assertAllAreOk(links_match)

    def test_link_to_html_is_encoded_as_phrase(self):
        links_match = []
        para_with_link = paras_from('link to html.docx')[0]
        phrase_contents = in_para_allcontent.pick_contents\
                (in_para_allcontent.contentlist(para_with_link), lambda x: x["type"] == "phrase")
        for content in phrase_contents:
            links_match.append(matcher.match(in_para_phrase.content_regex, content))
        self.assertAllAreOk(links_match)

    def test_reference_is_encoded_as_external(self):
        extrefs_match = []
        for para in paras_from('externalref.docx'):
            extref_contents = in_para_allcontent.pick_contents\
                (in_para_allcontent.contentlist(para), lambda x: x["type"] == "extref")
            for content in extref_contents:
                extrefs_match.append(matcher.match(in_para_externalref.content_regex, content))
        self.assertAllAreOk(extrefs_match)

    def test_current_chapter_goes_by_heading1(self):
        current_area = {'chapter': 'Chapter 1', 'shloka': '1-5'}
        chapter_name = 'Chapter 2'
        current_area = gita_encode.compute_current_area\
            ('heading1',
             [{"type": "text", "content": chapter_name}],
             current_area)
        self.assertEqual(current_area['chapter'], chapter_name)
        self.assertEqual(current_area['shloka'], '')
        current_area = gita_encode.compute_current_area\
            ('some style',
             [{"type": "text", "content": 'some content'}],
             current_area)
        self.assertEqual(current_area['chapter'], chapter_name)

    def test_current_shloka_goes_by_heading2(self):
        current_area = {'chapter': '', 'shloka': ''}
        shloka_name = '12-4'
        current_area = gita_encode.compute_current_area\
            ('heading2',
             [{"type": "text", "content": shloka_name}],
             current_area)
        self.assertEqual(current_area['shloka'], shloka_name)
        current_area = gita_encode.compute_current_area\
            ('some style',
             [{"type": "text", "content": 'some content'}],
             current_area)
        self.assertEqual(current_area['shloka'], shloka_name)


if __name__ == '__main__':
    unittest.main()
