# pupgui2 compatibility tools module
# Proton-GE
# Copyright (C) 2021 DavidoTek, partially based on AUNaseef's protonup

import os

from PySide6.QtCore import QCoreApplication

from pupgui2.util import extract_tar
from pupgui2.resources.ctmods.ctmod import Ctmod


CT_NAME = 'GE-Proton'
CT_LAUNCHERS = ['steam', 'heroicproton', 'bottles']
CT_DESCRIPTION = {'en': QCoreApplication.instance().translate('ctmod_00protonge', '''Steam compatibility tool for running Windows games with improvements over Valve's default Proton.<br/><br/><b>Use this when you don't know what to choose.</b>''')}


class CtInstaller(Ctmod):

    CT_URL = 'https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases'
    CT_INFO_URL = 'https://github.com/GloriousEggroll/proton-ge-custom/releases/tag/'

    def get_tool(self, version, install_dir, temp_dir):
        """
        Download and install the compatibility tool
        Return Type: bool
        """
        data = self.__fetch_github_data(version)

        if not data or 'download' not in data:
            return False

        protondir = os.path.join(install_dir, data['version'])
        if not os.path.exists(protondir):
            protondir = os.path.join(install_dir, 'Proton-' + data['version'])
        checksum_dir = f'{protondir}/sha512sum'
        source_checksum = self.rs.get(data['checksum']).text if 'checksum' in data else None
        local_checksum = open(checksum_dir).read() if os.path.exists(checksum_dir) else None

        if os.path.exists(protondir):
            if local_checksum and source_checksum:
                if local_checksum in source_checksum:
                    return False
            else:
                return False

        proton_tar = os.path.join(temp_dir, data['download'].split('/')[-1])
        if not self._download(url=data['download'], destination=proton_tar):
            return False

        download_checksum = self._sha512sum(proton_tar)
        if source_checksum and (download_checksum not in source_checksum):
            return False

        if not extract_tar(proton_tar, install_dir, mode='gz'):
            return False

        if os.path.exists(checksum_dir):
            open(checksum_dir, 'w').write(download_checksum)

        self._set_download_progress_percent(100)

        return True

    def __fetch_github_data(self, tag):
        """
        Fetch GitHub release information
        Return Type: dict
        Content(s):
            'version', 'date', 'download', 'size', 'checksum'
        """
        url = self.CT_URL + (f'/tags/{tag}' if tag else '/latest')
        data = self.rs.get(url).json()
        if 'tag_name' not in data:
            return None

        values = {'version': data['tag_name'], 'date': data['published_at'].split('T')[0]}
        for asset in data['assets']:
            if asset['name'].endswith('sha512sum'):
                values['checksum'] = asset['browser_download_url']
            elif asset['name'].endswith('tar.gz'):
                values['download'] = asset['browser_download_url']
                values['size'] = asset['size']
        return values
