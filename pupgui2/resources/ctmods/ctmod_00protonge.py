# pupgui2 compatibility tools module
# Proton-GE
# Copyright (C) 2021 DavidoTek, partially based on AUNaseef's protonup

import os
import requests
import hashlib

from PySide6.QtCore import QObject, QCoreApplication, Signal, Property

from pupgui2.datastructures import Launcher
from pupgui2.util import fetch_project_release_data, fetch_project_releases, get_launcher_from_installdir, ghapi_rlcheck, extract_tar
from pupgui2.util import build_headers_with_authorization


CT_NAME = 'GE-Proton'
CT_LAUNCHERS = ['steam', 'heroicproton', 'bottles']
CT_DESCRIPTION = {'en': QCoreApplication.instance().translate('ctmod_00protonge', '''Steam compatibility tool for running Windows games with improvements over Valve's default Proton.<br/><br/><b>Use this when you don't know what to choose.</b>''')}


class CtInstaller(QObject):

    BUFFER_SIZE = 65536
    CT_URL = 'https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases'
    CT_INFO_URL = 'https://github.com/GloriousEggroll/proton-ge-custom/releases/tag/'

    p_download_progress_percent = 0
    download_progress_percent = Signal(int)

    def __init__(self, main_window = None):
        super(CtInstaller, self).__init__()
        self.p_download_canceled = False

        self.release_format = f'tar.gz'

        self.rs = requests.Session()
        rs_headers = build_headers_with_authorization({}, main_window.web_access_tokens, 'github')
        self.rs.headers.update(rs_headers)

    def get_download_canceled(self):
        return self.p_download_canceled

    def set_download_canceled(self, val):
        self.p_download_canceled = val

    download_canceled = Property(bool, get_download_canceled, set_download_canceled)

    def __set_download_progress_percent(self, value : int):
        if self.p_download_progress_percent == value:
            return
        self.p_download_progress_percent = value
        self.download_progress_percent.emit(value)

    def __download(self, url: str, destination: str) -> bool:
        """
        Download files from url to destination
        Return Type: bool
        """
        try:
            file = self.rs.get(url, stream=True)
        except OSError:
            return False

        self.__set_download_progress_percent(1) # 1 download started
        f_size = int(file.headers.get('content-length'))
        c_count = int(f_size / self.BUFFER_SIZE)
        c_current = 1
        destination = os.path.expanduser(destination)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'wb') as dest:
            for chunk in file.iter_content(chunk_size=self.BUFFER_SIZE):
                if self.download_canceled:
                    self.download_canceled = False
                    self.__set_download_progress_percent(-2) # -2 download canceled
                    return False
                if chunk:
                    dest.write(chunk)
                    dest.flush()
                self.__set_download_progress_percent(int(min(c_current / c_count * 98.0, 98.0))) # 1-98, 100 after extract
                c_current += 1
        self.__set_download_progress_percent(99) # 99 download complete
        return True

    def __sha512sum(self, filename):
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

    def __fetch_github_data(self, tag: str) -> dict[str, str]:
        """
        Fetch GitHub release information
        Return Type: dict
        Content(s):
            'version', 'date', 'download', 'size', 'checksum'
        """

        return fetch_project_release_data(self.CT_URL, self.release_format, self.rs, tag=tag)

    def is_system_compatible(self):
        """
        Are the system requirements met?
        Return Type: bool
        """
        return True

    def fetch_releases(self, count: int = 100, page: int = 1) -> list[str]:
        """
        List available release names

        Return Type: list[str]
        """

        return fetch_project_releases(self.CT_URL, self.rs, count=count, page=page)

    def get_tool(self, version: str, install_dir: str, temp_dir: str) -> bool:
        """
        Download and install the compatibility tool
        Return Type: bool
        """

        data: dict[str, str] = self.__fetch_github_data(version)
        if not data or 'download' not in data:
            return False

        data_download: str = data['download']
        proton_tar = os.path.join(temp_dir, data_download.split('/')[-1])
        if not self.__download(url=data_download, destination=proton_tar):
            return False

        if not self.__extract(data, install_dir, temp_dir, proton_tar):
            return False

        self.__set_download_progress_percent(100)
        return True

    def __extract(self, data: dict[str, str], install_dir: str, temp_dir: str, proton_tar: str) -> bool:
        """
        Extract tool into given directory and rename the extract directory if required
        to match launcher expectations.

        Returns `True` if tool could be extracted sucessfully, `False` otherwise.

        Return Type: bool
        """

        data_version = data['version']
        ge_extract_fullpath, ge_extract_basename = self.__get_extract_paths(install_dir, data_version)

        # NOTE: Checksum stuff should go in separate method
        checksum_dir = f'{ge_extract_fullpath}/sha512sum'
        source_checksum = self.rs.get(data['checksum']).text if 'checksum' in data else None
        local_checksum = open(checksum_dir).read() if os.path.exists(checksum_dir) else None

        # Older GE-Proton releases don't have checksums (i.e. Proton-5.6-GE-2)
        if os.path.exists(ge_extract_fullpath):
            if local_checksum and source_checksum:
                if local_checksum in source_checksum:
                    return False
            else:
                return False

        download_checksum = self.__sha512sum(proton_tar)
        if source_checksum and (download_checksum not in source_checksum):
            return False

        tarmode: str = self.release_format.split('.')[-1]  # i.e. 'gz' from 'tar.gz', and if no match, 'tar' returns 'tar'
        if not extract_tar(proton_tar, install_dir, mode=tarmode):
            return False

        if os.path.exists(checksum_dir):
            open(checksum_dir, 'w').write(download_checksum)

        # Rename directory relevant to Steam (default archive name), Lutris (wine-ge), Heroic (Wine-GE)
        updated_dirname = os.path.join(install_dir, self.get_launcher_extract_dirname(ge_extract_basename, install_dir))
        os.rename(ge_extract_fullpath, updated_dirname)

        return True

    def __get_extract_paths(self, extract_dir: str, tool_version: str) -> tuple[str, str]:
        """
        Get the extract directory path with and without the extract filename

        Return Type: tuple[str, str]
        """

        # Set GE-Proton basename to "data['version']", set Wine-GE to "lutris-{data['version']}-x86_64"
        # Assume Wine-GE if release foramt ends in xz
        #
        # We can't use launcher name because Proton and Wine-GE may be available for the same launcher
        if self.release_format.endswith('xz'):  # Wine-GE
            extract_basename = f'lutris-{tool_version}-x86_64'
            extract_fullpath = os.path.join(extract_dir, extract_basename)
        else:  # GE-Proton
            extract_basename = tool_version

            # If version tag doesn't start with 'GE-' it's probably an older GE-Proton release
            # The old Proton-GE naming scheme versions were only tagged with X.Y-GE-Z
            #
            # Converts 5.6-GE-2 -> Proton-5.6-GE-2, matching archive extract, and leaves GE-Proton alone, where archive name and tag name match
            if not extract_basename.lower().startswith('ge-'):
                extract_basename = f'Proton-{tool_version}'

            extract_fullpath = os.path.join(extract_dir, extract_basename)

        return extract_fullpath, extract_basename

    def get_launcher_extract_dirname(self, original_name: str, install_dir: str) -> str:
        """
        Return base extract directory name updated to match naming scheme expected for given launcher.
        Example: 'lutris-GE-Proton8-17-x86_64' -> 'wine-ge-8-17-x86_64'

        Return Type: str
        """

        launcher_name = ''
        launcher = get_launcher_from_installdir(install_dir)
        if launcher == Launcher.LUTRIS:
            # Lutris expects this name format for self-updating, see #294 -- ex: wine-ge-8-17-x86_64
            launcher_name = original_name.lower().replace('lutris', 'wine').replace('proton', '')
        elif launcher == Launcher.HEROIC:
            # This matches Heroic Wine-GE naming convention -- ex: Wine-GE-Proton8-17
            launcher_name = original_name.replace('lutris', 'Wine').rsplit('-', 1)[0]

        return launcher_name or original_name

    def get_info_url(self, version):
        """
        Get link with info about version (eg. GitHub release page)
        Return Type: str
        """

        return self.CT_INFO_URL + version
