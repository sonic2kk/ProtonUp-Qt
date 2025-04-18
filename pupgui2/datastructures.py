import os
import vdf
import yaml
import json

from enum import Enum

from pupgui2.constants import PROTON_EAC_RUNTIME_APPID, PROTON_BATTLEYE_RUNTIME_APPID, STEAMLINUXRUNTIME_APPID


class SteamDeckCompatEnum(Enum):
    UNKNOWN = 0
    UNSUPPORTED = 1
    PLAYABLE = 2
    VERIFIED = 3


class AWACYStatus(Enum):
    UNKNOWN = 0
    DENIED = 4
    ASUPPORTED = 5
    PLANNED = 6
    RUNNING = 7
    BROKEN = 8


class RuntimeType(Enum):
    EAC = PROTON_EAC_RUNTIME_APPID  # ProtonEasyAntiCheatRuntime
    BATTLEYE = PROTON_BATTLEYE_RUNTIME_APPID  # ProtonBattlEyeRuntime
    STEAMLINUXRUNTIME = STEAMLINUXRUNTIME_APPID  # Steam Linux Runtime 1.0 (scout)


class CTType(Enum):
    UNKNOWN = 0
    CUSTOM = 10   # user installed ctool (e.g. GE-Proton in compatibilitytools.d)
    STEAM_CT = 20 # Steam installed compatibility tool (e.g. Proton in steamapps)
    STEAM_RT = 21 # Steam Runtime (e.g. BattlEye/EAC Runtime in steamapps)


class MsgBoxType(Enum):
    OK = 0
    OK_CANCEL = 1
    OK_CB = 2
    OK_CANCEL_CB = 3
    OK_CB_CHECKED = 4
    OK_CANCEL_CB_CHECKED = 5


class MsgBoxResult:
    BUTTON_OK = 0
    BUTTON_CANCEL = 1

    msgbox_type : MsgBoxType = None
    button_clicked = None
    is_checked : bool = None


class SteamUser:
    long_id = -1
    account_name = ''
    persona_name = ''
    most_recent = False
    timestamp = -1

    def get_short_id(self) -> int:
        """
        Returns the shortened Steam user id
        """
        return self.long_id & 0xFFFFFFFF


class SteamApp:
    app_id = -1
    libraryfolder_id = -1
    libraryfolder_path = ''
    shortcut_id = ''  # dict key must be string (e.g. '1')
    shortcut_startdir = ''
    shortcut_exe = ''
    shortcut_icon = ''
    shortcut_user = ''
    game_name = ''
    compat_tool = ''
    app_type = ''
    deck_compatibility = {}
    ctool_name = ''  # Steam's internal compatiblity tool name, e.g. 'proton_7'
    ctool_from_oslist = ''
    awacy_status = AWACYStatus.UNKNOWN  # areweanticheatyet.com Status
    protondb_summary = {}  # protondb status summary from JSON file
    anticheat_runtimes = { RuntimeType.EAC: False, RuntimeType.BATTLEYE: False }  # Dict of boolean values for which anti-cheat runtime are in use

    def get_app_id_str(self) -> str:
        return str(self.app_id)

    def get_libraryfolder_id_str(self) -> str:
        return str(self.libraryfolder_id)

    def get_deck_compat_category(self) -> SteamDeckCompatEnum:
        try:
            return SteamDeckCompatEnum(self.deck_compatibility.get('category'))
        except:
            return SteamDeckCompatEnum.UNKNOWN

    def get_deck_recommended_tool(self) -> str:
        try:
            return self.deck_compatibility.get('configuration').get('recommended_runtime', '')
        except:
            return ''


class BasicCompatTool:
    displayname = ''
    version = ''
    no_games = -1
    install_dir = ''
    install_folder = ''
    ct_type = CTType.UNKNOWN
    is_global = False

    def __init__(self, displayname, install_dir, install_folder, ct_type = CTType.UNKNOWN) -> None:
        self.displayname = displayname
        self.install_dir = install_dir
        self.install_folder = install_folder
        self.ct_type = ct_type

    def set_version(self, ver : str) -> None:
        self.version = ver

    def set_global(self, is_global: bool = True):
        self.is_global = is_global

    def get_displayname(self, unused_tr='unused', global_tr='global') -> str:
        """ Returns the display name, e.g. GE-Proton7-17 or luxtorpeda v57 """
        displayname = self.displayname
        if self.version != '':
            displayname += f' {self.version}'

        # Don't mark global tools as unused
        if self.is_global:
            displayname += f' ({global_tr})'
        elif self.no_games == 0:
            displayname += f' ({unused_tr})'

        return displayname

    def get_internal_name(self) -> str:
        """
        Returns the internal name if available, e.g. Proton-stl.
        If unavailable, returns the displayname
        """
        compat_tool_vdf_path = os.path.join(self.install_dir, self.install_folder, 'compatibilitytool.vdf')
        if os.path.exists(compat_tool_vdf_path):
            # TODO: Move this somewhere else and use steamutil.py#vdf_safe_load
            with open(compat_tool_vdf_path, 'r', encoding='utf-8', errors='replace') as f:
                compat_tool_vdf = vdf.loads(f.read())
            if 'compatibilitytools' in  compat_tool_vdf and 'compat_tools' in compat_tool_vdf['compatibilitytools']:
                return list(compat_tool_vdf['compatibilitytools']['compat_tools'].keys())[0]

        return self.displayname

    def get_install_dir(self) -> str:
        """ Returns the install directory, e.g. .../compatibilitytools.d/ """
        return os.path.normpath(self.install_dir)

    def get_install_folder(self) -> str:
        """ Returns the install folder, e.g. GE-Proton7-17 or luxtorpeda """
        return self.install_folder


class LutrisGame:
    slug = ''
    name = ''
    runner = ''
    installer_slug = ''
    installed_at = 0
    install_dir = ''

    install_loc = None

    def get_game_config(self) -> dict:
        
        """
        Get a Lutris game config .yml file from either the config directory or the data directory.
        i.e., ~/.config/lutris/games or ~/.local/share/lutris/games

        Return Type: dict
        """

        # Lutris will prefer the config directory if it exists, but will use the data directory if config does not exist.
        # On newer Lutris installations, only the data directory is used, as the config directory is deprecated.
        # However, Lutris does not migrate these installations, so we need to check for both and prefer config if it exists.
        #
        # https://github.com/lutris/lutris/blob/6b968e858955c0638bf93b3a72fec5ae650f0932/lutris/settings.py#L20-L25
        lutris_game_config_dir = os.path.join(os.path.expanduser(self.install_loc.get('config_dir')), 'games')
        if not lutris_game_config_dir:
            return {}
    
        if not os.path.isdir(lutris_game_config_dir):
            # Lutris 'install_dir' will be '/path/to/lutris/runners/wine', go two directories up to get the root Lutris install folder
            lutris_game_config_data_dir = os.path.abspath(
                os.path.join(
                    os.path.expanduser(self.install_loc.get('install_dir')),
                    '..', '..',
                    'games'
                )
            )

            if not os.path.isdir(lutris_game_config_data_dir):
                return {}

            lutris_game_config_dir = lutris_game_config_data_dir

        # search a *.yml game configuration file that contains either the install_slug+installed_at or, if not found, the game slug
        fn = ''
        for game_cfg_file in os.listdir(lutris_game_config_dir):
            if str(self.installer_slug) in game_cfg_file and str(self.installed_at) in game_cfg_file:
                fn = game_cfg_file
                break
        else:
            for game_cfg_file in os.listdir(lutris_game_config_dir):
                if self.slug in game_cfg_file:
                    fn = game_cfg_file
                    break

        lutris_game_cfg = os.path.join(lutris_game_config_dir, fn)
        if not os.path.isfile(lutris_game_cfg):
            return {}
        with open(lutris_game_cfg, 'r') as f:
            return yaml.safe_load(f)


# Information for games is stored in a per-storefront 'library.json' - This has most of the information we need
# Information for installed Epic games is stored at '<heroic_dir>/legendary/installed.json' and has a separate JSON format but the same data we need
# Information about game config (sideload, GOG, Epic) is stored in a 'GamesConfig/<app_name>.json' file, which is universal - This has Wine information
class HeroicGame:
    runner: str  # can be 'GOG', 'sideload' - Epic is hardcoded to 'legendary'
    app_name: str  # internal name encoded in some way, e.g. 'sPZQ5kmzYj5KnZKdxE2bR1'
    title: str  # Real name for game
    developer: str  # May be blank for side-loaded games
    heroic_path: str  # e.g. '~/.config/heroic', '~/.var/app/com.heroicgameslauncher.hgl/config/heroic'
    install_path: str  # Path to game folder, e.g. '/home/Gaben/Games/Half-Life 3'
    store_url: str  # May be blank for side-loaded games
    art_cover: str  # Optional?
    art_square: str  # Optional?
    is_installed: bool  # Not always set properly by Heroic for GOG?
    wine_info: dict[str, str]  # can store bin, name, and type - Has to be fetched from GamesConfig/app_name.json
    platform: str  # Game platform, stored differently for sideload, GOG and legendary
    executable: str  # Path to game executable, always stored at 'start.sh' for native Linux GOG games 
    is_dlc: bool  # Stored for GOG and legendary, defaults to False for sideloaded

    def get_game_config(self):
        game_config = os.path.join(self.heroic_path, 'GamesConfig', f'{self.app_name}.json')
        if not os.path.isfile(game_config):
            return {}
        
        with open(game_config, 'r') as gcf:
            return json.load(gcf).get(self.app_name, {})


class Launcher(Enum):
    UNKNOWN = 0
    STEAM = 1
    LUTRIS = 2
    BOTTLES = 3
    HEROIC = 4
    WINEZGUI = 5


class HardwarePlatform(Enum):
    """ Hardware platform. Used by util.py#detect_platform() """
    DESKTOP = 0
    STEAM_DECK = 1
