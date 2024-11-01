from contextlib import contextmanager
from rich.markdown import Markdown
from rich.console import Console
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from .presentation import Presentation, Section, Step
import typer
from io import StringIO

class Host(object):
    console: Console

    def __init__(self) -> None:
        self.console = Console()

    @contextmanager
    def present(self, pres: Presentation):
        with self.console.screen():
            controller = Controller(self, pres)
            yield controller


class State(object):
    step_index = 0
    current_step: Step
    presentation: Presentation

    def __init__(self, presentation: Presentation) -> None:
        self.presentation = presentation
        self.steps = list(self.presentation.yield_steps())
        self.apply_index()

    def apply_index(self):
        self.current_step = self.steps[self.step_index]

    def next(self):
        self.step_index = min(self.step_index + 1, len(self.steps) - 1)
        self.apply_index()

    def previous(self):
        self.step_index = max(self.step_index - 1, 0)
        self.apply_index()

    def start(self):
        self.step_index = 0
        self.apply_index()

    def end(self):
        self.step_index = len(self.steps) - 1
        self.apply_index()

    def quit(self):
        raise typer.Exit(0)

class Controller(object):
    host: Host
    state: State

    def __init__(self, host: Host, presentation: Presentation) -> None:
        self.host = host
        self.state = State(presentation)

        self.command_map = {
            ("", ">", "n"): self.state.next,
            ("<", "p"): self.state.previous, 
            ("r", ): (lambda: None), 
            ("q", ): self.state.quit, 
        }

    def run(self):
        while True:
            self.show(self.state)
            cmd = self.host.console.input("> ").strip().lower()
            for commands, handler in self.command_map.items():
                if cmd in commands:
                    handler()

    def show(self, state: State):
        console = Console(width=self.host.console.width - 4, color_system="truecolor", force_interactive=True, force_terminal=True)

        with console.capture() as capture:
            console.print(state.current_step.get_body())

        body_lines = capture.get().splitlines()

        desired_height = self.host.console.height - 7
        # get last n lines if too many lines ...
        body_lines = body_lines[-desired_height:]
        body = Panel(Layout(Text.from_ansi("\n".join(body_lines)), name="body"), title=state.current_step.section.title)

        info = Layout(
            Panel(
                state.current_step.get_info(), 
                title=state.current_step.info_title,
                height=3
            ),
            name="info", 
            size=3
        )

        root_layout = Layout()
        root_layout.split_column(body, info)

        self.host.console.print(Layout(Padding(root_layout, (1, 0, 0, 0))))
        #self.host.console.print(body)
