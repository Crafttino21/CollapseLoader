from rich.markup import escape

from .API import api
from .Cheat import Cheat
from .Data import data

cheats = []

for cheat in api.get('clients').json():
    if cheat["show_in_loader"]:
        cheats.append(
            Cheat(
                escape(cheat["name"]) + (" [red bold][-][/]" if not cheat["working"] else ""),
                data.get_url(cheat["filename"]),
                cheat["main_class"],
                cheat["version"][:-2],
                cheat["category"],
                cheat["internal"],
            )
        )