
from rich.markdown import Markdown, JustifyMethod, TextType, Style, CodeBlock as DCodeBlock, Heading as DHeading, MarkdownContext, MarkdownElement, TextElement
from rich.layout import Layout
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.console import ConsoleRenderable, Console, ConsoleOptions, RenderResult
from rich.syntax import Syntax
from rich.text import Text
from rich.align import Align
import polars as pl

from io import StringIO

import pyfiglet
import termplotlib as tpl

from markdown_it.token import Token

class CodeBlock(DCodeBlock):
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text)
        lines = code.splitlines()
        if len(lines) > 0:
            max_width = max(len(l) for l in lines)
        else: 
            max_width = 0
        padding = 0
        syntax = Syntax(
            code, self.lexer_name, word_wrap=True, padding=padding, background_color="default", code_width=max_width
        )
        if self.lexer_name in ["text"]:
            yield Align.center(syntax)
        else:
            yield Align.center(Panel(syntax, title=self.lexer_name, width=max_width + 2))

class Heading(DHeading):
    figlet_font: str | None = None

    def __init__(self, tag: str) -> None:
        super().__init__(tag)
        if self.tag == "h1":
            self.figlet_font = "isometric1"
        elif self.tag == "h2":
            self.figlet_font = "standard"

    def on_enter(self, context: MarkdownContext) -> None:
        super().on_enter(context)
        self.code_block = CodeBlock("text", "ansi_dark")
        self.code_block.text = Text(justify="left")

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = self.text
        text.justify = "center"
        if self.figlet_font is not None:
            self.code_block.text = Text(pyfiglet.figlet_format(str(text), font=self.figlet_font))
            yield Padding(Align.center(self.code_block), (1,0,0,0))
        else:
            yield text

class CenterElement(MarkdownElement):
    style_name = "none"
    children: list[ConsoleRenderable]

    def on_enter(self, context: MarkdownContext) -> None:
        self.style = context.enter_style(self.style_name)
        self.children = []

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        self.children = [Align.center(child)]
        return False

    def on_leave(self, context: MarkdownContext) -> None:
        context.leave_style()

    def __rich_console__(
        self, console, options
    ):
        yield Group(*self.children)

class PlotElement(MarkdownElement):
    style_name = "none"
    data: pl.DataFrame

    def on_enter(self, context: MarkdownContext) -> None:
        self.style = context.enter_style(self.style_name)
        self.code_block = CodeBlock("text", "ansi_dark")

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        if isinstance(child, CodeBlock) and child.lexer_name == "csv":
            self.data = pl.read_csv(StringIO(str(child.text)))
        return False

    def on_leave(self, context: MarkdownContext) -> None:
        context.leave_style()

    def get_axes_from_data(self):
        if len(self.data.columns) != 2:
            raise ValueError("Data must have 2 columns.")
        
        [x_col, y_col, *extra] = self.data.columns

        x = self.data.get_column(x_col)
        y = self.data.get_column(y_col)
        
        return (
            x,
            y
        )
    def __rich_console__(
        self, console, options
    ):
        x, y = self.get_axes_from_data()
        xlabel = self.data.columns[0]
        label = self.data.columns[1]
        fig = tpl.figure()
        fig.plot(x, y, label=label, xlabel=xlabel, width=options.max_width - 20, height=options.max_height - 15,  plot_command = "plot '-' w boxes",)
        self.code_block.text = Text(fig.get_string())
        yield self.code_block

class ConsoleMarkdown(Markdown):
    extra_elements = {
        "heading_open": Heading,
        "container_plot_open": PlotElement,
        "container_center_open": CenterElement,
        "code_block": CodeBlock,
        "fence": CodeBlock,
    }

    def __init__(
        self,
        tokens: list[Token],
        code_theme: str = "ansi_dark",
        justify: JustifyMethod | None = None,
        style: str | Style = "none",
        hyperlinks: bool = True,
        inline_code_lexer: str | None = None,
        inline_code_theme: str | None = None,
    ) -> None:
        self.elements.update(self.extra_elements)
        self.markup = ""
        self.parsed = tokens
        self.code_theme = code_theme
        self.justify: JustifyMethod | None = justify
        self.style = style
        self.hyperlinks = hyperlinks
        self.inline_code_lexer = inline_code_lexer
        self.inline_code_theme = inline_code_theme or code_theme
        

