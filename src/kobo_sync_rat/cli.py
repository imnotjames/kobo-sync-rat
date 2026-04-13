from typer import Typer

from .commands import serve

app = Typer()

app.add_typer(serve)

if __name__ == "__main__":
    app()
