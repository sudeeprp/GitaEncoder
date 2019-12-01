import os
import re
import json
import string
import unittest
import gita_encode


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


class EncodeTest(unittest.TestCase):
    def test_no_array_in_array(self):
        array_in_array_pattern = [r'\[\[']
        self.assertFalse(encoding_of_doc_matches('heading1.docx', array_in_array_pattern))

    def test_doc_is_encoded_as_para(self):
        expected_para_json_patterns = \
            [r'"paragraphs": \[', r'{ "id":"[^"]*"', r'"content": \[', r'"type": "text"',
             r'"english": "[^"]*"']
        self.assertTrue(encoding_of_doc_matches('heading1.docx', expected_para_json_patterns))

    def test_H1_is_encoded_as_a_para(self):
        expected_h1_json_patterns = [r'"english": "Chapter 1"', r'"style":"heading1"']
        self.assertTrue(encoding_of_doc_matches('heading1.docx', expected_h1_json_patterns))

    def test_default_style_is_normal(self):
        expected_normal_pattern = [r'"style": "normal"']
        self.assertTrue(encoding_of_doc_matches('anchor.docx', expected_normal_pattern))

    def test_bookmark_is_encoded_as_anchor(self):
        expected_anchor_patterns = [r'"type": "anchor"', r'"name": "one_bookmark"',
                                    r'"type": "text"', r'"english": "Here is a bookmark"']
        self.assertTrue(encoding_of_doc_matches('anchor.docx', expected_anchor_patterns))

    def test_link_is_encoded_as_phrase(self):
        expected_phrase_patterns = [r'"type": "phrase"', r'"english": "work without attachment"',
                                    r'"destination": "karmayOga_a_defn"']
        self.assertTrue(encoding_of_doc_matches('bookmark with link.docx',
                                                expected_phrase_patterns))

    def test_reference_is_encoded_as_external(self):
        expected_externalref_patterns = [r'"type": "externalref"', r'"translit": "pAncharAtra"',
                                         r'"section": "2-23"']
        self.assertTrue(encoding_of_doc_matches('externalref.docx', expected_externalref_patterns))


if __name__ == '__main__':
    unittest.main()
