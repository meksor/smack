from contextlib import contextmanager
from rich.markdown import Markdown
from rich.console import Console
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from .presentation import Presentation, Section, Step
import typer

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
        self.host.console.print(state.current_step.renderable)

        