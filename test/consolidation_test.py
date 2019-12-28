import unittest
import consolidate
import in_para_text
import in_para_phrase


class ConsolidationTests(unittest.TestCase):
    def test_adjacent_texts_are_consolidated(self):
        consecutive_texts = [in_para_text.good_example_object,
                             in_para_text.good_example_object,
                             in_para_text.good_example_object]
        expected_consolidated_text = in_para_text.good_example_object["content"] +\
                                     in_para_text.good_example_object["content"] +\
                                     in_para_text.good_example_object["content"]
        merged_batch, search_index = consolidate.consolidate_adjacent(consecutive_texts, 0)
        self.assertEqual(merged_batch, {"type": "text", "content": expected_consolidated_text})
        self.assertEqual(search_index, 3)

    def test_consecutive_textparas_are_concatenated(self):
        consecutive_texts = [{"type": "text", "content": "This"},
                             {"type": "text", "content": " is "},
                             in_para_phrase.good_example_object,
                             {"type": "text", "content": " it."}]
        expected_first_consolidation = {"type": "text", "content": "This is "}
        self.assertEqual(consolidate.consolidate_contentlist(consecutive_texts),
                         [expected_first_consolidation,
                          in_para_phrase.good_example_object,
                          {"type": "text", "content": " it."}])


    def test_extract_inline_from_normal_text(self):
        contentlist = [in_para_text.good_example_object,
                       in_para_phrase.good_example_object,
                       {"type": "text", "content": "Here - [puruShasUkta] is a reference"},
                       in_para_phrase.good_example_object]
        self.assertEqual(consolidate.extract_inline_from_texts(contentlist, 'normal'),
                         [in_para_text.good_example_object,
                          in_para_phrase.good_example_object,
                          {"type": "text", "content": "Here - "},
                          {"type": "extref",
                           "destination": "[puruShasUkta]", "content": "[puruShasUkta]"},
                          {"type": "text", "content": " is a reference"},
                          in_para_phrase.good_example_object])


    def test_shloka_is_not_extracted_as_ref(self):
        contentlist = [{"type": "text", "content": "[arjuna] Arjuna, "}]
        self.assertEqual((consolidate.extract_inline_from_texts(contentlist, 'style not normal')),
                         contentlist)


if __name__ == '__main__':
    unittest.main()
