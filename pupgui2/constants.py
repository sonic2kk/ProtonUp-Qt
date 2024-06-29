import os

from xdg.BaseDirectory import xdg_config_home, xdg_cache_home

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette


def PALETTE_DARK() -> QPalette:
    """ returns dark color palette """
    palette_base: QColor = QColor(12, 12, 12)

    palette_dark: QPalette = QPalette()
    palette_dark.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette_dark.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette_dark.setColor(QPalette.ColorRole.Base, palette_base)
    palette_dark.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
    palette_dark.setColor(QPalette.ColorRole.ToolTipBase, palette_base)
    palette_dark.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette_dark.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette_dark.setColor(QPalette.ColorRole.Button, QColor(30, 30, 30))
    palette_dark.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette_dark.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette_dark.setColor(QPalette.ColorRole.Link, QColor(40, 120, 200))
    palette_dark.setColor(QPalette.ColorRole.Highlight, QColor(40, 120, 200))
    palette_dark.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    return palette_dark


# General application information
APP_NAME = 'ProtonUp-Qt'
APP_VERSION = '2.9.2'
APP_ID = 'net.davidotek.pupgui2'
APP_THEMES: tuple[str | None, ...] = ( 'light', 'dark', 'system', None )
APP_ICON_FILE: str = os.path.join(xdg_config_home, 'pupgui/appicon256.png')
APP_GHAPI_URL = 'https://api.github.com/repos/Davidotek/ProtonUp-qt/releases'

DAVIDOTEK_KOFI_URL = 'https://ko-fi.com/davidotek'
PROTONUPQT_GITHUB_URL = 'https://github.com/DavidoTek/ProtonUp-Qt'

ABOUT_TEXT: str = '''\
{APP_NAME} v{APP_VERSION} by DavidoTek: <a href="{PROTONUPQT_GITHUB_URL}">https://github.com/DavidoTek/ProtonUp-Qt</a><br />
Copyright (C) 2021-2024 DavidoTek, licensed under GPLv3
'''.format(APP_NAME=APP_NAME, APP_VERSION=APP_VERSION, PROTONUPQT_GITHUB_URL=PROTONUPQT_GITHUB_URL)

BUILD_INFO = 'built from source'

# Internal paths
CONFIG_FILE: str = os.path.join(xdg_config_home, 'pupgui/config.ini')
TEMP_DIR: str = os.path.join(xdg_cache_home, 'tmp', 'pupguo2.a70200')
HOME_DIR: str = os.path.expanduser('~')

# DBus constants
DBUS_APPLICATION_URI: str = f'application://{APP_ID}.desktop'
DBUS_DOWNLOAD_OBJECT_BASEPATH = '/net/davidotek/pupgui2'

DBUS_INTERFACES_AND_SIGNALS: dict[str, dict[str, str]] = {
    'LauncherEntryUpdate': {
        'interface': 'com.canonical.Unity.LauncherEntry',
        'signal': 'Update',
    }
}

# support different Steam root directories, building paths relative to HOME_DIR (i.e. /home/gaben/.local/share/Steam)
# Use os.path.realpath to expand all _STEAM_ROOT paths
_base_steam_roots: list[str] = [
    os.path.realpath(os.path.join(HOME_DIR, _STEAM_ROOT)) for _STEAM_ROOT in ['.local/share/Steam', '.steam/root', '.steam/steam', '.steam/debian-installation']
]

# Remove duplicate paths while preserving order, as os.path.realpath may expand some symlinks to the real Steam root
_POSSIBLE_STEAM_ROOTS: list[str] = list(dict.fromkeys(_base_steam_roots))

# Steam can be installled in any of the locations at '_POSSIBLE_STEAM_ROOTS' - usually only one, and the others (if they exist) are typically symlinks,
# i.e. '~/.steam/root' is usually a symlink to '~/.local/share/Steam'
# These paths may still not be valid installations however, as they could be leftother paths from an old Steam installation without the data files we need ('config.vdf' and 'libraryfolders.vdf')
# We catch this later on in util#is_valid_launcher_installation though
POSSIBLE_STEAM_INSTALL_LOCATIONS: list[dict[str, str]] = [
        {
            'install_dir': f'{_STEAM_ROOT}/compatibilitytools.d/',
            'display_name': 'Steam',
            'launcher': 'steam',
            'type': 'native',
            'icon': 'steam',
            'vdf_dir': f'{_STEAM_ROOT}/config'
        } for _STEAM_ROOT in _POSSIBLE_STEAM_ROOTS if os.path.exists(_STEAM_ROOT)
]

# Possible install locations for all other launchers, ensuring Steam paths are at the top of the list
POSSIBLE_INSTALL_LOCATIONS = POSSIBLE_STEAM_INSTALL_LOCATIONS + [
    {'install_dir': '~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d/', 'display_name': 'Steam Flatpak', 'launcher': 'steam', 'type': 'flatpak', 'icon': 'steam', 'vdf_dir': '~/.var/app/com.valvesoftware.Steam/.local/share/Steam/config'},
    {'install_dir': '~/snap/steam/common/.steam/root/compatibilitytools.d/', 'display_name': 'Steam Snap', 'launcher': 'steam', 'type': 'snap', 'icon': 'steam', 'vdf_dir': '~/snap/steam/common/.steam/root/config'},
    {'install_dir': '~/.local/share/lutris/runners/wine/', 'display_name': 'Lutris', 'launcher': 'lutris', 'type': 'native', 'icon': 'lutris', 'config_dir': '~/.config/lutris'},
    {'install_dir': '~/.var/app/net.lutris.Lutris/data/lutris/runners/wine/', 'display_name': 'Lutris Flatpak', 'launcher': 'lutris', 'type': 'flatpak', 'icon': 'lutris', 'config_dir': '~/.var/app/net.lutris.Lutris/config/lutris'},
    {'install_dir': '~/.config/heroic/tools/wine/', 'display_name': 'Heroic Wine', 'launcher': 'heroicwine', 'type': 'native', 'icon': 'heroic'},
    {'install_dir': '~/.config/heroic/tools/proton/', 'display_name': 'Heroic Proton', 'launcher': 'heroicproton', 'type': 'native', 'icon': 'heroic'},
    {'install_dir': '~/.var/app/com.heroicgameslauncher.hgl/config/heroic/tools/wine/', 'display_name': 'Heroic Wine Flatpak', 'launcher': 'heroicwine', 'type': 'flatpak', 'icon': 'heroic'},
    {'install_dir': '~/.var/app/com.heroicgameslauncher.hgl/config/heroic/tools/proton/', 'display_name': 'Heroic Proton Flatpak', 'launcher': 'heroicproton', 'type': 'flatpak', 'icon': 'heroic'},
    {'install_dir': '~/.local/share/bottles/runners/', 'display_name': 'Bottles', 'launcher': 'bottles', 'type': 'native', 'icon': 'com.usebottles.bottles'},
    {'install_dir': '~/.var/app/com.usebottles.bottles/data/bottles/runners/', 'display_name': 'Bottles Flatpak', 'launcher': 'bottles', 'type': 'flatpak', 'icon': 'com.usebottles.bottles'},
    {'install_dir': '~/.local/share/winezgui/Runners/', 'display_name': 'WineZGUI', 'launcher': 'winezgui', 'type': 'native', 'icon': 'io.github.fastrizwaan.WineZGUI'},
    {'install_dir': '~/.var/app/io.github.fastrizwaan.WineZGUI/data/winezgui/Runners/', 'display_name': 'WineZGUI Flatpak', 'launcher': 'winezgui', 'type': 'flatpak', 'icon': 'io.github.fastrizwaan.WineZGUI'}
]

PROTONDB_COLORS: dict[str, str] = {
    'platinum': '#b4c7dc',
    'gold': '#cfb53b',
    'silver': '#a6a6a6',
    'bronze': '#cd7f32',
    'borked': '#ff0000',
    'pending': '#748472'
}

# Third-party API urls and paths
STEAM_API_GETAPPLIST_URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
STEAM_APP_PAGE_URL = 'https://store.steampowered.com/app/'

AWACY_GAME_LIST_URL = 'https://raw.githubusercontent.com/Starz0r/AreWeAntiCheatYet/master/games.json'
AWACY_WEB_URL = 'https://areweanticheatyet.com/?search={GAMENAME}&sortOrder=&sortBy='
LOCAL_AWACY_GAME_LIST: str = os.path.join(TEMP_DIR, 'awacy_games.json')

PROTONDB_API_URL = 'https://www.protondb.com/api/v1/reports/summaries/{game_id}.json'
PROTONDB_APP_PAGE_URL = 'https://protondb.com/app/'

LUTRIS_WEB_URL = 'https://lutris.net/games/'
EPIC_STORE_URL = 'https://store.epicgames.com/p/'

# SteamTinkerLaunch-specific paths
STEAM_BOXTRON_FLATPAK_APPSTREAM = 'appstream://com.valvesoftware.Steam.CompatibilityTool.Boxtron'
STEAM_STL_FLATPAK_APPSTREAM = 'appstream://com.valvesoftware.Steam.Utility.steamtinkerlaunch'

STEAM_STL_INSTALL_PATH: str = os.path.join(HOME_DIR, 'stl')
STEAM_STL_CONFIG_PATH: str = os.path.join(HOME_DIR, '.config', 'steamtinkerlaunch')
STEAM_STL_CACHE_PATH: str = os.path.join(HOME_DIR, '.cache', 'steamtinkerlaunch')
STEAM_STL_DATA_PATH: str = os.path.join(HOME_DIR, '.local', 'share', 'steamtinkerlaunch')
STEAM_STL_SHELL_FILES: list[str] = [ '.bashrc', '.zshrc', '.kshrc' ]
STEAM_STL_FISH_VARIABLES: str = os.path.join(HOME_DIR, '.config/fish/fish_variables')

# GitLab can have any self-hosted instance, so we store a list of known GitLab instances
GITHUB_API = 'https://api.github.com/'
GITLAB_API: list[str] = [
    'https://gitlab.com/api/'
]
GITLAB_API_RATELIMIT_TEXT: list[str] = [
    'Rate limit exceeded; see https://docs.gitlab.com/ee/user/gitlab_com/#gitlabcom-specific-rate-limits for more details',
    'Rate limit exceeded',
    'Retry later'
]

# Known constant Steam/Proton AppIDs
PROTON_NEXT_APPID = 2230260
PROTON_EAC_RUNTIME_APPID = 1826330
PROTON_BATTLEYE_RUNTIME_APPID = 1161040

STEAMLINUXRUNTIME_APPID = 1070560
STEAMLINUXRUNTIME_SOLDIER_APPID = 1391110
STEAMLINUXRUNTIME_SNIPER_APPID = 1628350
