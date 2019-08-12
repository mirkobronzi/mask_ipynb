import argparse
import re

RE_START_BLOCK = re.compile('.*".*# *__START_BLOCK_ANSWER__.*".*')
RE_END_BLOCK = re.compile('.*".*# *__END_BLOCK_ANSWER__.*".*')
RE_NEXT_LINE = re.compile('.*".*# *__NEXT_LINE_ANSWER__.*".*')
BEFORE_EQUAL = re.compile('^.* = ')
NEW_LINE_IN_LINE_ENDING = re.compile('.*",\n$')
SPACES_AT_LINE_START = re.compile('" *')
REPLACEMENT_TEXT = '... # To complete.'


def mask_ipynb(in_stream, to_complete_stream, solution_stream):
    in_answer_block = False
    next_line_answer = False
    blocks = 0
    one_line = 0
    for line in in_stream:
        if RE_START_BLOCK.match(line):
            if in_answer_block:
                raise ValueError('start answer block once already inside an'
                                 ' answer block')
            in_answer_block = True
            spaces = SPACES_AT_LINE_START.findall(line)
            to_complete_stream.write('    ' + spaces[0] + REPLACEMENT_TEXT + '\\n",\n')
        elif RE_END_BLOCK.match(line):
            if not in_answer_block:
                raise ValueError('end answer block when not inside an'
                                 ' answer block')
            in_answer_block = False
            blocks += 1
        elif RE_NEXT_LINE.match(line):
            next_line_answer = True
        elif next_line_answer:
            part_to_keep = BEFORE_EQUAL.findall(line)
            if len(part_to_keep) != 1:
                raise ValueError(
                    'expecting a one line answer format (i.e., .. = ...\n'
                    'instead I found the next line:\n{}'.format(line))
            if NEW_LINE_IN_LINE_ENDING.match(line):
                ending = '\\n",'
            else:
                ending = '"'
            to_complete_stream.write(part_to_keep[0] + REPLACEMENT_TEXT + ending + '\n')
            solution_stream.write(line)
            one_line += 1
            next_line_answer = False
        elif in_answer_block:  # just skip this line for the to_complete
            solution_stream.write(line)
        else:
            to_complete_stream.write(line)
            solution_stream.write(line)
    if in_answer_block:
        raise ValueError('completed without closing the answer block')
    print('substituted {} blocks - and {} lines'.format(blocks, one_line))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', help='path to input ipynb (source)',
                        required=True)
    parser.add_argument('--to_complete_file', help='path to output ipynb (to complete)',
                        required=True)
    parser.add_argument('--solution_file', help='path to output ipynb (solution)',
                        required=True)
    args = parser.parse_args()

    print('masking file {} - writing output (to complete) into {} - writing'
          'output (solution) into {}'.format(
        args.input_file, args.to_complete_file, args.solution_file))

    with open(args.input_file, 'r', encoding='utf8') as in_stream:
        with open(args.to_complete_file, 'w', encoding='utf8') as to_complete_stream:
            with open(args.solution_file, 'w', encoding='utf8') as solution_stream:
                mask_ipynb(in_stream, to_complete_stream, solution_stream)



if __name__ == '__main__':
    main()
