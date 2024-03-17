# `slicepy`

is a Streamlined Lists of Important Code Edits - A tool to manage TODO comments
in codebases.

If you are like me, you have a lot of TODO comments in your code. They prevent
you from forgetting about important tasks while remaining "in the zone". But
they are still often forgotten about, and they can be hard to manage. `slicepy`
is a tool to help manage these comments.

It parses the codebase and extracts all the TODO comments with some context,
calls the openai API to summarize the comments, and then presents them in a
streamlined markdown todo list. Nothing fancy but very handy.

## Installation

This project is pre-alpha and not yet available on pypi. To install, clone the
repo and run `pip install .` in the root directory.

````bash git clone https://github.com/weygoldt/slicepy.git && cd slicepy && pip
install . ```

## Usage

To use `slicepy`, simply run `slice -f <file_extension> <path_to_codebase>`.
This will generate a `todo.md` file in the root of the codebase with all the
todo comments it found.

An example usage would be:

```bash
slice -f py .
```

This would generate a `todo.md` file in the root of the codebase with all the
todo comments in the python files.
````
