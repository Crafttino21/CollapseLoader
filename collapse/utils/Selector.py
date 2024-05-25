import os

from rich.console import Console

from .Cheat import Cheat
from .Cheats import cheats
from .Logger import logger
from .RPC import rpc

console = Console()

selector_offset = len(cheats) + 10

class Function:
    def __init__(self, line: str, color: str = 'dark_cyan'):
        global selector_offset
        selector_offset += 1

        self.line = f'\n[{color}]{selector_offset}. {line}[/]'

class Selector:
    """Selector, used to select clients, and tools, the main part of the CLI loader"""

    def __init__(self) -> None:
        """class init that creates a text variable"""

        logger.debug('Initialized Selector')
        
        self.text = self.make_text()
        self.offset = len(cheats)

        if self.offset == 0:
            logger.warn('No clients available')
            self.text += '\n\nNo clients available, make sure you have internet\n'

        logger.debug('Created selector text')

    def make_text(self) -> str:
        text = '\n[bold]CLIENTS & TOOLS[/]\n'


        text += '\n'.join([f'{i + 1}. {cheat}' for i, cheat in enumerate(cheats)])

        text += '\n'
        text += ''.join([Function('Select username').line,
                                Function('Enter RAM').line,
                                Function('Discord RPC ' + ('[green][+][/]' if not rpc.disabled else '[red][-][/]')).line,
                                Function('Ghost mode (PANIC)').line,
                                Function('Remove data folder').line,
                                Function('Exit', 'dark_red').line])
        
        return text
    
    def update_text(self) -> None:
        """refreshes self.text property"""
        self.text = self.make_text()

    def show(self) -> None:
        """print self.text to screen"""
        console.print(self.text, highlight=False)

    def select(self) -> str:
        """requires user selection"""
        return console.input('Select >> ')
    
    def pause(self) -> None:
        """pauses to allow the user to read the text"""
        input('Press enter >> ')

    def ask(self, question: str) -> bool:
        """asks the user for an action"""
        while True:
            i = console.input(f'{question} >> ')
            if i in ['y', 'yes', 'да', 'н']:
                return True
            elif i in ['n', 'no', 'нет']:
                return False
    
    def get_cheat_by_index(self, index: int) -> Cheat:
        """gets the cheat through its index"""
        return cheats[index - 1]
            
    def select_username(self) -> str:
        """asks for the user's nickname"""
        return input('Enter nickname >> ')

    def select_ram(self) -> int:
        """asks how much RAM to use"""
        while True:
            try:
                return int(input('Enter ram in gigabytes >> '))
            except ValueError:
                logger.error('Enter gigabytes (2, 4, 8)')

    def clear(self) -> None:
        os.system('cls')

selector = Selector()