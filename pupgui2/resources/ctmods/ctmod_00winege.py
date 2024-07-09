# pupgui2 compatibility tools module
# Wine-GE
# Copyright (C) 2021 DavidoTek, partially based on AUNaseef's protonup

from PySide6.QtCore import QCoreApplication

from pupgui2.resources.ctmods.ctmod_00protonge import CtInstaller as GEProtonInstaller


CT_NAME = 'Wine-GE'
CT_LAUNCHERS = ['lutris', 'heroicwine', 'bottles', 'winezgui']
CT_DESCRIPTION = {'en': QCoreApplication.instance().translate('ctmod_00winege', '''Compatibility tool "Wine" to run Windows games on Linux. Based on Valve Proton Experimental's bleeding-edge Wine, built for Lutris.<br/><br/><b>Use this when you don't know what to choose.</b>''')}


class CtInstaller(GEProtonInstaller):

    BUFFER_SIZE = 65536
    CT_URL = 'https://api.github.com/repos/GloriousEggroll/wine-ge-custom/releases'
    CT_INFO_URL = 'https://github.com/GloriousEggroll/wine-ge-custom/releases/tag/'

    def __init__(self, main_window = None):
        super().__init__(main_window)

        self.release_format = 'tar.xz'

