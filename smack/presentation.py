
from pathlib import Path
from markdown_it.tree import SyntaxTreeNode
from markdown_it.token import Token

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader # type: ignore

from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.console import ConsoleRenderable

from .rich import ConsoleMarkdown
from .mdit import md

last_stepinfo = md.parse("!!! end\n\tContinue to next section...")

class Step(object):
    renderable: ConsoleRenderable
    info_node: SyntaxTreeNode
    body_node: SyntaxTreeNode
    section: "Section"

    def __init__(self, section: "Section", info: SyntaxTreeNode, body: SyntaxTreeNode) -> None:
        self.info_node = info
        self.body_node = body
        self.section = section

        root_layout = Layout()
        root_layout.split_column(self.get_body(), self.get_info_layout())
        self.renderable = Layout(Padding(root_layout, (1, 0, 0, 0)))

    def get_body(self):
        content = ConsoleMarkdown(self.body_node.to_tokens(), justify=self.section.justify)
        return Layout(Panel(content, title=self.section.title), name="body")
                
    def get_info_layout(self):
        try:
            title = self.info_node.content
        except IndexError:
            title = ""
        try:
            content = ConsoleMarkdown(self.info_node.children[1].to_tokens())
        except IndexError:
            content = ""
        return Layout(
            Panel(
                content, 
                title=title,
                height=3
            ),
            name="step_info", 
            size=3
        )

class Section(object):
    justify: str | None = "center"
    title: str | None = None
    front_matter: dict | None = None
    tokens: list[Token]
    steps: list[Step]

    def __init__(self, file: Path) -> None:
        self.tokens = md.parse(file.read_text())
        self.node = SyntaxTreeNode(self.tokens)
        self.parse_front_matter()
        self.parse_steps()

    def parse_steps(self):
        self.steps = []
        body_tokens = []
        diff_tokens = []
        for element in self.node.children:
            if element.type == "admonition":
                self.steps.append(Step(self, element, SyntaxTreeNode(body_tokens)))
                diff_tokens = []
            else:
                diff_tokens += element.to_tokens()
                body_tokens += element.to_tokens()

        self.steps.append(Step(self, SyntaxTreeNode(last_stepinfo).children[0], SyntaxTreeNode(body_tokens)))


    def parse_front_matter(self):
        self.front_matter = {}

        for element in self.node.children:
            if element.type == "front_matter":
                self.front_matter = yaml.load(element.content, Loader=Loader)
                self.node.children.remove(element)

        self.title = self.front_matter.get("title", self.title)
        self.justify = self.front_matter.get("justify", self.justify)

class Presentation(object):
    dir_path: Path
    files: list[Path]
    sections: list[Section]

    def __init__(self, dir_path: Path | str ) -> None:
        if isinstance(dir_path, str):  
            dir_path = Path(dir_path)

        self.dir_path = dir_path

        self.files = sorted(list(self.dir_path.glob("*.md")), key=lambda x: x.stem)
        self.sections = []

        for file in self.files:
            self.sections.append(Section(file))


    def yield_steps(self):
        for section in self.sections:
            for step in section.steps:
                yield step
