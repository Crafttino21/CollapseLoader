import os
import random
import zipfile

import requests
from rich.progress import (BarColumn, DownloadColumn, Progress, SpinnerColumn,
                           TextColumn, TransferSpeedColumn)

from .Logger import logger
from .Servers import servers
from ..static import REPO_URL, VERSION


class DataManager:
    """Used to manage loader data"""

    def __init__(self) -> None:
        self.root_dir = 'data/'
        self.server = servers.check_servers()

        if self.server is None:
            logger.critical('No server was found for downloading files (this is a critical function in the loader)')
            quit()

        self.repo = REPO_URL
        self.version = VERSION
        self.session = requests.Session()

        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
            logger.debug('Created root dir')

        logger.debug('Initialized DataManager')


    def get_local(self, path: str) -> str:
        """Get file locally"""
        return os.path.join(self.root_dir, path)

    def get_url(self, path: str) -> str:
        """Gets a link from the web, uses a fallback server if the main one is down"""
        return self.server + path

    def download(self, path: str, destination: str = None, mod: bool = False) -> None:
        logger.debug(f'Downloading {path}')
        filename = os.path.basename(path)
        jar = os.path.splitext(filename)[0] + '.jar'
        path_dir = os.path.join(self.root_dir, os.path.splitext(filename)[0])
        dest = destination if destination else os.path.join(self.root_dir, filename)

        if not filename.endswith('.jar') and not os.path.exists(self.get_local(filename)):
            if os.path.isdir(path_dir):
                logger.debug(f'{path} already downloaded, skip')
                return
            os.makedirs(path_dir, exist_ok=True)
        elif filename.endswith('.jar'):
            if os.path.exists(os.path.join(path_dir, jar)):
                logger.debug(f'{path} file already downloaded, skip')
                return
            if not os.path.isdir(path_dir) and not mod:
                os.makedirs(path_dir, exist_ok=True)

        headers = {}
        
        if os.path.exists(dest):
            headers['Range'] = f'bytes={os.path.getsize(dest)}-'

        try:
            response = self.session.get(self.server + filename, headers=headers, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {path}: {e}")
            return

        with Progress(TextColumn(f'[blue]{path}'), SpinnerColumn(f'dots{random.randint(2, 9)}'), BarColumn(), DownloadColumn(), TransferSpeedColumn()) as progress:
            task = progress.add_task('', total=total_size)
            
            with open(dest, "ab") as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

        try:
            if filename.endswith('.zip'):
                with zipfile.ZipFile(dest, 'r') as zip_file:
                    zip_file.extractall(path_dir)
                os.remove(dest)
            elif filename.endswith('.jar'):
                os.rename(dest, os.path.join(path_dir, filename))
        except (zipfile.BadZipFile, OSError) as e:
            logger.error(f"Error processing {dest}: {e}")
            if os.path.exists(dest):
                os.remove(dest)

data = DataManager()
