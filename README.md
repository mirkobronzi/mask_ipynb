# Info

**WARNING**: if using Colab, use "Download as ipynb". Do **not** download from gdrive directly.

This script can be used to prepare ipynb files to be used for tutorials.
I.e., the idea is that a tutorial has 2 versions: the one with the solution,
and the one with the questions.

Both these files can be automatically generated with this script starting from
a scource ipynb file. This is convenient cause you will have to maintain only
a single version of your ipynb.

The idea is to write the source ipynb file as you would write the version
with the solution. The difference is that, when you want to mask some code,
you can do that by using some tags to wrap this code.
At the moment, there are only two options:
* masked a block of code.
* mask the code at the right of an equal symbol.

Note these tags (see examples below) only work in a code cell in ipynb. 

----

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

----

It is also possible to mask the code at the right of an equal symbol, e.g.,

    code_before
    # __NEXT_LINE_ANSWER__
    x, y = my_function(a, b, c)
    code_after

becomes:

    code_before
    x, y = ... # To complete.
    code_after

----

Or to mask something in a markdown cell:

    my test here...
    __START_OUT_OF_CODE_ANSWER__
    this part will be masked.
    __END_OUT_OF_CODE_ANSWER__

becomes:

    my test here...
    