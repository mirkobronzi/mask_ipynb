"""
Quick script to generate the to_complete and the solution version for a ipynb.
It expected the source file to have tags to mark the code that should be masked in the
to_complete version.

----------------
E.g., to mask a block of code

code_before
# __START_BLOCK_ANSWER__
lot of stuff
and more stuff
# __END_BLOCK_ANSWER__
code_after

becomes:
code_before
... # To complete.
code_after
----------------
E.g., to mask just after an equal symbol:

code_before
# __NEXT_LINE_ANSWER__
x, y = my_function(a, b, c)
code_after

becomes:
code_before
x, y = ... # To complete.
code_after
----------------
"""
import copy
import json

__author__ = "Mirko Bronzi - mirko.bronzi@mila.quebec"

import argparse
import re

RE_START_BLOCK = re.compile('.*__START_BLOCK_ANSWER__.*')
RE_END_BLOCK = re.compile('.*__END_BLOCK_ANSWER__.*')
RE_START_OUT_CODE_BLOCK = re.compile('.*__START_OUT_OF_CODE_ANSWER__.*')
RE_END_OUT_OF_CODE_BLOCK = re.compile('.*__END_OUT_OF_CODE_ANSWER__.*')
RE_NEXT_LINE = re.compile('.*__NEXT_LINE_ANSWER__.*')
BEFORE_EQUAL = re.compile('^.* = ')
SPACES_AT_LINE_START = re.compile(' *')
REPLACEMENT_TEXT = '... # To complete.'


def parse_code_source(source):
    in_answer_block = False
    next_line_answer = False
    blocks = 0
    result_solution = []
    result_to_complete = []
    for code_line in source:
        if RE_START_BLOCK.match(code_line):
            in_answer_block = True
            spaces_reg = SPACES_AT_LINE_START.findall(code_line)
            if len(spaces_reg) > 0:
                spaces = spaces_reg[0]
            else:
                spaces = ""
            result_to_complete.append(spaces + REPLACEMENT_TEXT)
        elif RE_END_BLOCK.match(code_line):
            in_answer_block = False
            blocks += 1
        elif RE_NEXT_LINE.match(code_line):
            next_line_answer = True
        elif in_answer_block:
            result_solution.append(code_line)
        elif next_line_answer:
            next_line_answer = False

            part_to_keep = BEFORE_EQUAL.findall(code_line)
            if len(part_to_keep) != 1:
                raise ValueError(
                    'expecting a one line answer format (i.e., .. = ...\n'
                    'instead I found the next line:\n{}'.format(code_line))
            result_to_complete.append(part_to_keep[0] + REPLACEMENT_TEXT + '\n')
            result_solution.append(code_line)
        else:
            result_solution.append(code_line)
            result_to_complete.append(code_line)
    if in_answer_block:
        raise ValueError('completed source code without closing a masking block')
    return result_solution, result_to_complete, blocks


def parse_markdown_source(source):
    in_answer_block = False
    blocks = 0
    result_solution = []
    result_to_complete = []
    for code_line in source:
        if RE_START_OUT_CODE_BLOCK.match(code_line):
            in_answer_block = True
            result_to_complete.append(REPLACEMENT_TEXT)
        elif RE_END_OUT_OF_CODE_BLOCK.match(code_line):
            in_answer_block = False
            blocks += 1
        elif in_answer_block:
            result_solution.append(code_line)
        else:
            result_solution.append(code_line)
            result_to_complete.append(code_line)
    if in_answer_block:
        raise ValueError('completed source code without closing a masking block')
    return result_solution, result_to_complete, blocks


def parse_cells(cells):
    solution_cells = []
    to_complete_cells = []
    tot_code_blocks = 0
    tot_markdown_blocks = 0
    for cell in cells:
        if isinstance(cell, dict) and cell['cell_type'] == 'code' and 'source' in cell:
            solution, to_complete, code_blocks = parse_code_source(cell['source'])
            tot_code_blocks += code_blocks
            cell_to_complete = copy.deepcopy(cell)
            cell['source'] = solution
            cell_to_complete['source'] = to_complete
        elif isinstance(cell, dict) and cell['cell_type'] == 'markdown' and 'source' in cell:
            solution, to_complete, markdown_blocks = parse_markdown_source(cell['source'])
            tot_markdown_blocks += markdown_blocks
            cell_to_complete = copy.deepcopy(cell)
            cell['source'] = solution
            cell_to_complete['source'] = to_complete
        else:
            raise ValueError('found a cell that I do not know how to parse:\n\n{}'.format(cell))
        solution_cells.append(cell)
        to_complete_cells.append(cell_to_complete)
    print('substituted {} code blocks and {} mardown blocks.'.format(
        tot_code_blocks, tot_markdown_blocks))
    return solution_cells, to_complete_cells


def mask_ipynb(in_stream, to_complete_stream, solution_stream):
    parsed_json = json.loads(in_stream.read())

    solution_cells, to_complete_cells = parse_cells(parsed_json['cells'])
    parsed_json['cells'] = solution_cells
    json.dump(parsed_json, solution_stream, ensure_ascii=False, indent=2)
    parsed_json['cells'] = to_complete_cells
    json.dump(parsed_json, to_complete_stream, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--input_file', help='path to input ipynb (source)',
                        required=True)
    parser.add_argument('--to_complete_file', help='path to output ipynb (to complete)',
                        required=True)
    parser.add_argument('--solution_file', help='path to output ipynb (solution)',
                        required=True)
    parser.add_argument('--debug', help='more verbose', action='store_true')
    args = parser.parse_args()

    print('masking file {} - writing output (to complete) into {} - writing'
          ' output (solution) into {}'.format(
        args.input_file, args.to_complete_file, args.solution_file))

    with open(args.input_file, 'r', encoding='utf8') as in_stream:
        with open(args.to_complete_file, 'w', encoding='utf8') as to_complete_stream:
            with open(args.solution_file, 'w', encoding='utf8') as solution_stream:
                mask_ipynb(in_stream, to_complete_stream, solution_stream)


if __name__ == '__main__':
    main()
