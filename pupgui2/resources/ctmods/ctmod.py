# pupgui2 compatibility tools module - Base Compatibility tool 
# Copyright (C) 2023 DavidoTek, partially based on AUNaseef's protonup

import os
import requests
import hashlib

from PySide6.QtCore import QObject, Signal, Property

from pupgui2.util import ghapi_rlcheck
from pupgui2.constants import PROTONUPQT_GITHUB_URL


class Ctmod(QObject):

    BUFFER_SIZE = 65536

    # Hack because constant doesn't end with '/'
    CT_URL = f'{PROTONUPQT_GITHUB_URL}/'
    CT_INFO_URL = f'{PROTONUPQT_GITHUB_URL}/'

    p_download_progress_percent = 0
    download_progress_percent = Signal(int)

    def __init__(self, main_window = None):
        super().__init__()

        self.p_download_canceled = False
        self.rs = main_window.rs or requests.Session()

    # Qt Signal methods
    def get_download_canceled(self):
        return self.p_download_canceled
    def set_download_canceled(self, val):
        self.p_download_canceled = val
    download_canceled = Property(bool, get_download_canceled, set_download_canceled)
    
    # Public methods
    def is_system_compatible(self):
        """
        Are the system requirements met?
        Return Type: bool
        """
        return True

    def get_info_url(self, version):
        """
        Get link with info about version (eg. GitHub release page)
        Return Type: str
        """
        return self.CT_INFO_URL + version
    
    def fetch_releases(self, count=100):
        """
        List available releases
        Return Type: str[]
        """
        return [release['tag_name'] for release in ghapi_rlcheck(self.rs.get(f'{self.CT_URL}?per_page={str(count)}').json()) if 'tag_name' in release]


    # Private methods
    def _set_download_progress_percent(self, value : int):
        if self.p_download_progress_percent == value:
            return
        self.p_download_progress_percent = value
        self.download_progress_percent.emit(value)

    def _download(self, url, destination):
        """
        Download files from url to destination
        Return Type: bool
        """
        try:
            file = self.rs.get(url, stream=True)
        except OSError:
            return False

        self._set_download_progress_percent(1) # 1 download started
        f_size = int(file.headers.get('content-length'))
        c_count = int(f_size / self.BUFFER_SIZE)
        c_current = 1
        destination = os.path.expanduser(destination)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'wb') as dest:
            for chunk in file.iter_content(chunk_size=self.BUFFER_SIZE):
                if self.download_canceled:
                    self.download_canceled = False
                    self._set_download_progress_percent(-2) # -2 download canceled
                    return False
                if chunk:
                    dest.write(chunk)
                    dest.flush()
                self._set_download_progress_percent(int(min(c_current / c_count * 98.0, 98.0))) # 1-98, 100 after extract
                c_current += 1
        self._set_download_progress_percent(99) # 99 download complete
        return True

    def _sha512sum(self, filename):
        """
        Get SHA512 checksum of a file
        Return Type: str
        """
        sha512sum = hashlib.sha512()
        with open(filename, 'rb') as file:
            while True:
                data = file.read(self.BUFFER_SIZE)
                if not data:
                    break
                sha512sum.update(data)
        return sha512sum.hexdigest()
