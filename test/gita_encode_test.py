import os
import unittest
import gita_encode


def encoding_of_doc_complies(test_docx_filename, expected_dict):
    encoded_doc = gita_encode.encode_doc(os.path.join('../test_data', test_docx_filename))
    return encoded_doc == expected_dict


class EncodeTest(unittest.TestCase):
    def test_H1_is_encoded_as_dict(self):
        expected_h1_dict = {
            'paragraphs': [
                {
                    'id': '*',
                    'style': 'heading1',
                    'content': [
                        {
                            'type': 'text',
                            'english': 'Chapter 1'
                        }
                    ]
                }
            ]
        }
        self.assertTrue(encoding_of_doc_complies('heading1.docx', expected_h1_dict))

    def test_bookmark_is_encoded_as_anchor(self):
        expected_anchor_dict = {
            'paragraphs': [
                {
                    'id': '*',
                    'style': 'normal',
                    'content': [
                        {
                            'type': 'anchor',
                            'name': 'one_bookmark'
                        },
                        {
                            'type': 'text',
                            'english': 'Here is a bookmark'
                        }
                    ]
                }
            ]
        }
        self.assertTrue(encoding_of_doc_complies('anchor.docx', expected_anchor_dict))

    def test_link_is_encoded_as_phrase(self):
        expected_phrase_dict = {
            'paragraphs': [
                {
                    'id': '*',
                    'style': 'normal',
                    'content': [
                        {
                            'type': 'anchor',
                            'name': 'karmayOga_a_defn'
                        },
                        {
                            'type': 'text',
                            'english': 'karmayOga is to work without attachment'
                        }]
                },
                {
                    'id': '*',
                    'style': 'normal',
                    'content': [
                        {
                            'type': 'text',
                            'english': 'To realize the Self, they'
                        },
                        {
                            'type': 'text',
                            'english': ' '
                        },
                        {
                            'type': 'phrase',
                            'english': 'work without attachment',
                            'destination': 'karmayOga_a_defn'
                        },
                        {
                            'type': 'text',
                            'english': '.'
                        }
                    ]
                }
            ]
        }
        self.assertTrue(encoding_of_doc_complies('bookmark with link.docx', expected_phrase_dict))

    def test_reference_is_encoded_as_external(self):
        expected_externalref_dict = {
            'paragraphs': [
                {
                    'id': '*',
                    'style': 'normal',
                    'content': [
                        {
                            'type': 'text',
                            'english': 'As per'
                        },
                        {
                            'type': 'externalref',
                            'translit': 'pAncharAtra'
                        }
                    ]
                }
            ]
        }
        self.assertTrue(encoding_of_doc_complies('externalref.docx', expected_externalref_dict))


if __name__ == '__main__':
    unittest.main()
