from unittest import TestCase

from mask_ipynb_answers import parse_code_source


class MaskIpynbAnswersTest(TestCase):

    def test_parse_code_source__next_line(self):
        one_line_input = ["line\n", "__NEXT_LINE_ANSWER__\n", "res = my_res\n"]
        expected_to_complete = ['line\n', 'res = ... # To complete.\n']
        expected_solution = ['line\n', 'res = my_res\n']

        solution, to_complete, _ = parse_code_source(one_line_input)
        self.assertEqual(expected_to_complete, to_complete)
        self.assertEqual(expected_solution, solution)

    def test_parse_code_source__two_next_line(self):
        one_line_input = ["__NEXT_LINE_ANSWER__\n", "res1 = my_res1\n",
                          "__NEXT_LINE_ANSWER__\n", "res2 = my_res2\n"]
        expected_to_complete = ['res1 = ... # To complete.\n', 'res2 = ... # To complete.\n']
        expected_solution = ["res1 = my_res1\n", "res2 = my_res2\n"]

        solution, to_complete, _ = parse_code_source(one_line_input)
        self.assertEqual(expected_to_complete, to_complete)
        self.assertEqual(expected_solution, solution)
