import unittest
import consolidate
import in_para_text
import in_para_phrase


class ConsolidationTests(unittest.TestCase):
    def test_adjacent_texts_are_consolidated(self):
        consecutive_texts = [in_para_text.good_example_object,
                             in_para_text.good_example_object,
                             in_para_text.good_example_object]
        expected_consolidated_text = in_para_text.good_example_object["content"] + ' ' +\
                                     in_para_text.good_example_object["content"] + ' ' + \
                                     in_para_text.good_example_object["content"]
        merged_batch, search_index = consolidate.consolidate_adjacent(consecutive_texts, 0)
        self.assertEqual(merged_batch, {"type": "text", "content": expected_consolidated_text})
        self.assertEqual(search_index, 3)

    def test_consecutive_textparas_are_concatenated(self):
        consecutive_texts = [in_para_text.good_example_object,
                             in_para_text.good_example_object,
                             in_para_phrase.good_example_object,
                             in_para_text.good_example_object]
        expected_first_consolidation =\
            {"type": "text",
             "content": in_para_text.good_example_object["content"] + ' ' +
                        in_para_text.good_example_object["content"]}
        self.assertEqual(consolidate.consolidate_contentlist(consecutive_texts),
                         [expected_first_consolidation,
                          in_para_phrase.good_example_object,
                          in_para_text.good_example_object])


if __name__ == '__main__':
    unittest.main()
