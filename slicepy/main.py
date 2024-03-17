"""Main module for the project."""

import argparse
from rich.markdown import Markdown
from rich.console import Console
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

# Define custom progress bar
progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)

todo_file_header = """
# Refactoring tasks 📋

Get yourself a cup of coffee and happy refactoring! 🚀

"""

filetype_comments = {
    "tex": "%",
    "py": "#",
    "sh": "#",
    "c": "//",
    "cpp": "//",
    "java": "//",
    "js": "//",
    "ts": "//",
    "html": "<!--",
    "css": "/*",
    "scss": "/*",
    "sass": "/*",
    "php": "//",
    "rb": "#",
    "cs": "//",
    "go": "//",
    "rs": "//",
    "swift": "//",
    "kt": "//",
    "clj": ";;",
    "cljc": ";;",
    "cljs": ";;",
    "edn": ";;",
    "yaml": "#",
    "json": "//",
    "xml": "<!--",
    "md": "<!--",
    "rst": "..",
    "toml": "#",
    "ini": "#",
    "cfg": "#",
    "conf": "#",
}

output_markdown_file = "todo.md"
todo_keywords = ["TODO", "Todo", "todo", "ToDo"]
client = OpenAI()
console = Console()

# TODO: This is just a test to see if the API works

sysprompt = """
You are an assistant, skilled in explaining complex programming concepts. Your
task is to write a helpful and human readable item for a TODO list from
comments in a codebase. You will get the comment itself, a context of 40 lines
around the comment, the line number and the file path. You will also get the
file type. You should write a helpful and human readable item for a TODO list
from the comment. Keep it short and simple but provide enough context for the
reader to understand and act upon. Try to keep it in a single sentence. Always
start with a verb. For example, "Refactor this function to use a loop instead
of recursion." or "Add a check for the edge case where the list is empty."
Always remove the "TODO" prefix from the comment. Do not include the line
number or file path in the response. Just return a single sentence without
markdown formatting or punctuation. If the comment contains an Author tag, you
should Include the author's name in the response with the syntax "by @author"
If there is no author tag,
you should not include the author or the "by" keyword in the response. Also
do not add something like "unknown author" if there is no author tag.
"""


class Comment(BaseModel):
    comment: str
    context: str
    line_number: int
    file_path: Path
    file_type: str


def decipher_comment(comment: str) -> str:
    prompt = f"""
    The comment is:
    {comment.comment}
    The context is:
    {comment.context}
    The line number is:
    {comment.line_number}
    The file path is:
    {comment.file_path}
    The file type is:
    {comment.file_type}
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": sysprompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message


def make_keywords(filetype: str) -> list:
    comment_prefix = filetype_comments[filetype]
    return [f"{comment_prefix} {tag}" for tag in todo_keywords] + [
        f"{comment_prefix}{tag}" for tag in todo_keywords
    ]


def find_todos(
    root_dir: Path, filetype: str = "tex", todo_keywords: list = None
) -> dict:
    todos = {}
    n_todos = 0
    # TODO: Add support for other files
    console.print(f"Looking for TODO tasks in {filetype} files 👀")
    for file_path in root_dir.rglob(f"*.{filetype}"):
        with file_path.open("r", encoding="utf-8") as file:
            lines = file.readlines()
            todo_comments = []
            for line_number, line in enumerate(lines, start=1):
                # remove leading and trailing whitespace
                line = line.strip()
                if any(
                    keyword in line for keyword in todo_keywords
                ) and line.startswith(filetype_comments[filetype]):
                    # take previous 10 lines and next 10 lines
                    context = lines[line_number - 20 : line_number + 20]
                    # context to multiline string
                    context = "".join(context)
                    comment = line.strip()
                    path = file_path.relative_to(root_dir)
                    file_type = filetype

                    com = Comment(
                        comment=comment,
                        context=context,
                        line_number=line_number,
                        file_path=path,
                        file_type=file_type,
                    )
                    todo_comments.append(com)
                    n_todos += 1

            if todo_comments:
                # Use relative path from the project directory for better readability
                relative_path = file_path.relative_to(root_dir)
                todos[str(relative_path)] = todo_comments
    console.print(f"Found {n_todos} TODO tasks in {len(todos)} files 🎉")
    return todos


def write_markdown(todos, output_file, todo_keywords=todo_keywords):
    # open file and open progress bar
    console.print(f"Writing TODO tasks to {output_file} 📝")
    with progress_bar as p, open(
        output_file, "w", encoding="utf-8"
    ) as md_file:
        md_file.write(todo_file_header)
        for file, comments in p.track(todos.items()):
            md_file.write(f"## {file}\n")
            for comment in comments:
                aicomment = decipher_comment(comment).content
                # remove full stop at the end of the comment
                if aicomment.endswith("."):
                    aicomment = aicomment.strip(".")
                path_line = f"({comment.file_path}:{comment.line_number})"
                md_file.write(f"- [ ] {aicomment} {path_line}\n")
            md_file.write("\n")


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract TODO tasks from a project to a markdown file"
    )
    parser.add_argument(
        "project_directory",
        type=Path,
        help="The root directory of the project",
    )
    parser.add_argument(
        "--filetype",
        "-f",
        type=str,
        default="tex",
        help="The file type to look for TODO tasks",
    )
    return parser.parse_args()


def main():
    """Main entry point of the program."""
    args = argparser()
    project_directory = args.project_directory
    filetype = args.filetype
    keywords = make_keywords(filetype)
    todos = find_todos(project_directory, filetype, keywords)
    write_markdown(todos, output_markdown_file, keywords)
    console.print(
        f"TODO tasks have been extracted to {output_markdown_file} 📝"
    )

    # TODO: Add support for opening the markdown file in the terminal

    # with Path.open(output_markdown_file, "r", encoding="utf-8") as file:
    #     markdown = file.read()
    #     md = Markdown(markdown)
    #     console.print(md)


if __name__ == "__main__":
    main()
