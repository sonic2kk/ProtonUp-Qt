# pupgui2 compatibility tools module
# Steam-Play-None https://github.com/Scrumplex/Steam-Play-None
# Copyright (C) 2022 DavidoTek, partially based on AUNaseef's protonup

import os
import requests

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, QCoreApplication, Signal, Property

from pupgui2.util import extract_tar, remove_if_exists
from pupgui2.util import build_headers_with_authorization
from pupgui2.networkutil import download_file


CT_NAME = 'Steam-Play-None'
CT_LAUNCHERS = ['steam', 'advmode']
CT_DESCRIPTION = {'en': QCoreApplication.instance().translate('ctmod_steamplaynone', '''Run Linux games as is, even if Valve recommends Proton for a game.<br/>Created by Scrumplex.<br/><br/>Useful for Steam Deck.<br/><br/>Note: The internal name has been changed from <b>none</b> to <b>Steam-Play-None</b>!''')}


class CtInstaller(QObject):

    CT_URL = 'https://github.com/Scrumplex/Steam-Play-None/archive/refs/heads/main.tar.gz'  # no releases
    CT_INFO_URL = 'https://github.com/Scrumplex/Steam-Play-None'

    p_download_progress_percent = 0
    download_progress_percent = Signal(int)
    message_box_message = Signal((str, str, QMessageBox.Icon))

    def __init__(self, main_window = None):
        super(CtInstaller, self).__init__()
        self.p_download_canceled = False

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
            return download_file(
                url=url,
                destination=os.path.expanduser(destination),
                progress_callback=self.__set_download_progress_percent,
                download_cancelled=self.download_canceled,
            )
        except Exception as e:
            print(f"Failed to download tool {CT_NAME} - Reason: {e}")

            self.message_box_message.emit(
                self.tr("Download Error!"),
                self.tr("Failed to download tool '{CT_NAME}'!\n\nReason: {EXCEPTION}".format(CT_NAME=CT_NAME, EXCEPTION=e)),
                QMessageBox.Icon.Warning
            )

            return False

    def is_system_compatible(self):
        """
        Are the system requirements met?
        Return Type: bool
        """
        return True

    def fetch_releases(self, count=100, page=1):
        """
        List available releases
        Return Type: str[]
        """
        return ['main']

    def get_tool(self, version, install_dir, temp_dir):
        """
        Download and install the compatibility tool
        Return Type: bool
        """
        steam_play_none_tar = os.path.join(temp_dir, 'main.tar.gz')

        # Rename extracted Steam-Play-None-main to Steam-Play-None
        steam_play_none_main = os.path.join(install_dir, 'Steam-Play-None-main')
        steam_play_none_dir = os.path.join(install_dir, 'Steam-Play-None')

        dl_url = self.CT_URL

        remove_if_exists(steam_play_none_main)
        if not self.__download(url=dl_url, destination=steam_play_none_tar):
            return False

        remove_if_exists(steam_play_none_dir)
        if not extract_tar(steam_play_none_tar, install_dir, mode='gz'):
            return False

        os.rename(steam_play_none_main, steam_play_none_dir)

        self.__set_download_progress_percent(100)

        return True

    def get_info_url(self, version):
        """
        Get link with info about version (eg. GitHub release page)
        Return Type: str
        """
        return self.CT_INFO_URL
