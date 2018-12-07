# 5th
5th is a my implementation of the Forth programming language.

As taken from Wikipedia:
>Forth is an imperative stack-based computer programming language

This version of the interpreter/compiler isn't optimised at all because it ~~passes around literal objects instead of memory addresses~~(basic implementation of memory addresses is completed as of version 0.2), and the dictionary and variable "heap" are distinct entities. This should be fixed in the next version which will also be written in python, but the one after that will be in C and 5th.

# Language Specifics
5th, like Forth, is stack-based. That means all values are read/pushed/popped of a stack.

    forth> 40 2 + .
    42

Everything in 5th is a word, which is, if not the same but, very similar to functions in other languages.
`40` is a word that pushes 40 to the stack. `+` is a word that pops the stack for its 2 operands then pushes the sum onto the stack. "." pops and displays the result.

You can make your own words:

    forth> : 1+ 1 + ;
    forth> 41 1+ .
    42

The word `:` starts the definition of a new word. The immediate next word the new words label. All words till the `;` are compiled (not executed) into the definition of the word. `;` stops the definition.

You can also make variables(not in version 0.2):

    forth> var pi
    forth> 3 pi !
    forth> pi @ .
    3

`var` makes a new word. This new word is special because whenever used it pushes the address of whatever it points to. `!` stores a value into an address and `@` pushes the value in an address onto the stack.

It is also possible to reserve contiguous spaces of memory for data (like an array):

    forth> var list 9 cells allot

This sequences of words make an address named list, then allots it 9 extra memory cells. Accessing different parts of the "array" is just like pointer arithmetic in C: just add/subtract to/from the base value.

To run the interpreter, just run the 5th.py file in this repository.
There may be many bugs in this implementation. There is no control flow as well.
