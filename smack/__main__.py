import typer
from pathlib import Path
from .presentation import Presentation
from .host import Host

app = typer.Typer()


@app.command()
def show(path: Path = typer.Argument(
        ..., help="The presentation to show."
    ),):
    pres = Presentation(path)
    host = Host()

    with host.present(pres) as controller:
        controller.run()

@app.command()
def inspect(path: Path = typer.Argument(
        ..., help="The file to inspect."
    ),):
    pres = Presentation(path)
    pass

if __name__ == "__main__":

    app()