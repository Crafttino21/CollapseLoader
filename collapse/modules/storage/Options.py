import random

from rich import print

from ..render.CLI import console, selector
from ..utils.Language import lang
from ..utils.Logger import logger
from ..utils.Module import Module
from .Settings import settings

option_list = []

class Option(Module):
    """The Option class represents a configurable option."""
    def __init__(self, name: str, description: str = '', option_type = str, default_value = object, callback = None, highlight: bool = False) -> None:
        super().__init__(False)
        self.name = name
        self.description = description
        self.option_type = option_type
        self.value = settings.get(name)
        self.default_value = default_value
        self.callback = callback
        self.highlight = highlight

        if description:
            option_list.append(self)

    @property
    def line(self) -> str:
        """Returns a formatted string representing the option"""
        self.value = settings.get(self.name)
        if self.option_type == bool:
            self.value = f'[green]{lang.t("options.enabled")}[/]' if self.value == 'True' else f'[red]{lang.t("options.disabled")}[/]'
        return f"{self.name.title().replace('_', ' ')}[/] / [light_salmon3]{self.description}[/] * {self.value}"

    def create(self, value=None, header: str = 'Options') -> None:
        """Creates a new option in the settings"""
        if not settings.get(self.name, header):
            settings.set(self.name, value if value is not None else self.default_value, header)
            
            self.debug(lang.t('options.created').format(self.name, value if value is not None else self.default_value, header))

    def save(self, value: object) -> None:
        """Saves option to settings file"""
        settings.set(self.name, value)
        self.info(lang.t('options.saved').format(self.name, value))
        if self.callback:
            if callable(self.callback):
                self.callback()

    def input(self) -> None:
        """Handles user input for the option"""
        if self.option_type == str:
            console.print(f'\n{lang.t('options.input.note')}')
            new_value = console.input(lang.t('options.input.prompt').format(self.name, self.value))
            
            if new_value != '':
                self.save(new_value if new_value.upper() != 'RESET' else self.default_value)
                
        elif self.option_type == bool:
            current_value = settings.get(self.name)
            self.save(not current_value.lower() == 'true')

    def reset(self) -> None:
        """Reset option with default value"""
        self.save(self.default_value)
        self.debug(lang.t('options.reset').format(self.name, self.default_value))

    @staticmethod
    def get_option_by_index(index: int) -> 'Option':
        """Gets the option by its index"""
        return option_list[index - 1]

    def __str__(self):
        """Returns option name as title"""
        return self.name.title().replace('_', ' ')

# Define options
Option('nickname', lang.t('options.settings.nickname'), default_value=f'Collapse{random.randint(1000, 9999)}', highlight=True)
Option('custom_title', lang.t('options.settings.custom_title'), default_value='None').create('None')
Option('hide_logo', lang.t('options.settings.hide_logo'), bool, False).create()
Option('hide_messages', lang.t('options.settings.hide_messages'), bool, False).create()
Option('disable_caching', lang.t('options.settings.disable_caching'), bool, False).create()
Option('use_short_logo', lang.t('options.settings.use_short_logo'), bool, False).create()
Option('hide_links', lang.t('options.settings.hide_links'), bool, False).create()
Option('disable_animation', lang.t('options.settings.disable_animation'), bool, False).create()
Option('show_client_version', lang.t('options.settings.show_client_version'), bool, False).create()
Option('discord_rich_presence', lang.t('options.settings.discord_rich_presence'), bool, True).create()
Option('language', lang.t('options.settings.language'), default_value='en').create('en')
Option('language', lang.t('options.settings.language'), default_value='de').create('de')

class Menu:
    """Options menu"""

    def __init__(self) -> None:
        self.offset = len(option_list)

    def show(self) -> None:
        """Displays the options menu"""
        selector.set_title(title_type='settings')

        while True:
            print('\n')
            option_lines = [f'[{"green" if not option.highlight else "green3"}]{i + 1}. {option.line}' for i, option in enumerate(option_list)]
            option_lines.append(f'[dark_red]{self.offset + 1}. {lang.t("menu.return")}[/]')
            option_lines.append(f'[bright_red]{self.offset + 2}. {lang.t("options.reset-all")}[/]')
            console.print('\n'.join(option_lines), highlight=False)

            try:
                choice = int(console.input(f'{lang.t('options.choose')}: '))

                if choice <= len(option_list):
                    Option.get_option_by_index(choice).input()
                elif choice == self.offset + 1:
                    break
                elif choice == self.offset + 2:  # reset all options
                    if selector.ask(lang.t('options.ask-reset')):
                        for option in option_list:
                            option.reset()
                else:
                    logger.error(lang.t('options.invalid-choice'))
            except ValueError:
                logger.error(lang.t('options.invalid-choice'))
                continue

        selector.reset_title()

options_menu = Menu()