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

```bash
git clone https://github.com/weygoldt/slicepy.git && cd slicepy && pip
install .
```

## Usage

To use `slicepy`, simply run `slice -f <file_extension> <path_to_codebase>`.
This will generate a `todo.md` file in the root of the codebase with all the
todo comments it found.

An example usage would be:

```bash
slice -f py .
```

This would generate a [`todo.md`](todo.md) file in the root of the codebase with all the
todo comments in the python files.

## Setting up the OpenAI API

To use the OpenAI API, you need to set up an account and get an API key. You can
then set the `OPENAI_API_KEY` environment variable to your key. You could either
simply run `export OPENAI_API_KEY=<your_key>` in your terminal or add it to your
`.bashrc` or `.zshrc` file.

## Notes

> > Can I use this without paying for the OpenAI API?

Not yet but soon. I am planning to (1) simply include the comments as they are
without summarizing them and (2) use `ollama` with a local LLM to summarize the
comments.

> > Why not simply go through the codebase and remove the TODO comments as you
> > go?

I use `slicepy` mainly in during refactoring sessions. I will usually have
intense coding sessions where I don't want to be interrupted by refactoring
tasks. If refactoring is due, I will run `slice -f py .` and then open the
`todo.md` file in a separate window. I will then go through the list and start
refactoring the code, removing the todo comments as I go. I can then just run
`slice -f py .` again to see if I missed anything. This works well in
my python data science projects as well as in my latex documents and I imagine
it would work well in other codebases too.

> > Why not simply use grep?

Of course I could simply use `grep` to find all the todo comments in the
codebase and go through them manually. But I find that in many cases, it makes
sense to have a summary of the comments especially if it makes sense to prioritize
certain tasks or if they depend on each other.
