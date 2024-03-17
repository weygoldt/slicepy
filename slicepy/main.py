import argparse
from rich.markdown import Markdown
from rich.console import Console
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel

console = Console()

filetype_comments = {
    "tex": "%",
    "py": "#",
    "sh": "#",
}

output_markdown_file = "todo.md"
todo_keywords = ["TODO", "Todo", "todo", "ToDo"]

client = OpenAI()


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
    Please summarize the provided information into a human readable item for a TODO list that
    captures the essence of the comment for people to understand and act upon.
    Importantly, include not only the task but also why it is important.
    As an output, give me just the comment, no markdown formatting is needed.
    Remove the "todo" keyword and the leading space if there is any. Also do not provide the line number or the file path, this will be added later.
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant, skilled in explaining complex programming concepts with creative flair. Your task is to write a helpful and human readable item for a TODO list from comments in a codebase. You will get the comment itself, a context of 40 lines around the comment, the line number and the file path. You will also get the file type. You should write a helpful and human readable item for a TODO list from the comment. Keep it short and simple but provide enough context for the reader to understand and act upon. Always include not only the task but also why it is important. Try to keep it in a single sentence.",
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
    # TODO: Add support for other files
    console.print(f"Looking for TODO tasks in {filetype} files 👀")
    for file_path in root_dir.rglob(f"*.{filetype}"):
        with file_path.open("r", encoding="utf-8") as file:
            lines = file.readlines()
            todo_comments = []
            for line_number, line in enumerate(lines, start=1):
                if any(keyword in line for keyword in todo_keywords):
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

            if todo_comments:
                # Use relative path from the project directory for better readability
                relative_path = file_path.relative_to(root_dir)
                todos[str(relative_path)] = todo_comments
    return todos


def write_markdown(todos, output_file, todo_keywords=todo_keywords):
    with open(output_file, "w", encoding="utf-8") as md_file:
        for file, comments in todos.items():
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
    args = argparser()
    project_directory = args.project_directory
    filetype = args.filetype
    keywords = make_keywords(filetype)

    todos = find_todos(project_directory, filetype, keywords)
    write_markdown(todos, output_markdown_file, keywords)
    console.print(f"TODO tasks have been extracted to {output_markdown_file} 📝")

    with open(output_markdown_file, "r", encoding="utf-8") as file:
        markdown = file.read()
        md = Markdown(markdown)
        console.print(md)


if __name__ == "__main__":
    main()
