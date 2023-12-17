import os
import sqlite3
import json

from typing import List, Dict

from pupgui2.datastructures import LutrisGame
from pupgui2.constants import HOME_DIR


LUTRIS_PGA_GAMELIST_QUERY = 'SELECT slug, name, runner, installer_slug, installed_at, directory FROM games'


def get_lutris_game_list(install_loc) -> List[LutrisGame]:
    """
    Returns a list of installed games in Lutris
    Return Type: List[LutrisGame]
    """
    install_dir = os.path.expanduser(install_loc.get('install_dir'))
    lutris_data_dir = os.path.join(install_dir, os.pardir, os.pardir)
    pga_db_file = os.path.join(lutris_data_dir, 'pga.db')
    lgs = []
    try:
        con = sqlite3.connect(pga_db_file)
        cur = con.cursor()
        cur.execute(LUTRIS_PGA_GAMELIST_QUERY)
        res = cur.fetchall()
        for g in res:
            lg = LutrisGame()
            lg.install_loc = install_loc
            lg.slug = g[0]
            lg.name = g[1]
            lg.runner = g[2]
            lg.installer_slug = g[3]
            lg.installed_at = g[4]
            
            # Lutris database file will only store some fields for games installed via an installer and not if it was manually added
            # If a game doesn't have an install dir (e.g. it was manually added to Lutris), try to use the following for the install dir:
            # - Working directory (may not be specified)
            # - Executable: may not be accurate as the exe could be heavily nested, but a good fallback)
            lutris_install_dir = g[5]
            if not lutris_install_dir:
                lg_config = lg.get_game_config()
                working_dir = lg_config.get('game', {}).get('working_dir')
                exe_dir = lg_config.get('game', {}).get('exe')
                lutris_install_dir = working_dir or (os.path.dirname(str(exe_dir)) if exe_dir else None)

            lg.install_dir = os.path.abspath(lutris_install_dir) if lutris_install_dir else ''
            lgs.append(lg)
    except Exception as e:
        print('Error: Could not get lutris game list:', e)
    return lgs


def get_lutris_global_version(name: str) -> str:

    """
    Return the name of the global tool that Lutris uses for a specified runner/runtime name (i.e. wine-ge-8-25 for 'wine', v2.3 for 'dxvk')
    Return Type: str
    """

    # TODO figure out how to get Lutris cache dir
    ## Flatpak Cache: ~/.var/app/net.lutris.Lutris/cache/lutris
    ## Everywhere else: ~/.cache/lutris

    # Hardcoded for now
    versions_json_path = os.path.join(HOME_DIR, '.cache', 'lutris', 'versions.json')
    if not os.path.isfile(versions_json_path):
        return ''

    # 'versions.json' has two object keys we're interested in: 'runtimes', and 'runners'
    # Each object inside of these has the name of the runner/runtime
    # The 'runtimes' are just objects, but 'runners' has a list of objects per runner, i.e. example structure:
    # "runtimes": { "dxvk": { "name": "...", "version": "...", "url": "..." } }  // Note how this isn't wrapped in a list
    # "runners": { "wine": [ { "name": "...", "version": "...", "url": "..." } ] }
    #
    # To get runner version, we need to get the first object in the list of versions for a given runner
    # and get that first object 'version' (if the runner with the specified name exists at all)
    #
    # To get the runtime version, since it doesn't use a list we can just use chained get() calls to get the version
    with open(versions_json_path, 'r') as versions_json_file:
        versions_json = json.load(versions_json_file)

        # Elegantly handle cases where list of tools for a runner is empty
        runner_versions: List[Dict] = versions_json.get('runners', {}).get(name, [])
        runner_version: str = runner_versions[0].get('version', '') if runner_versions else ''

        runtime_version: str = versions_json.get('runtimes', {}).get(name, {}).get('version', '')

        return runner_version or runtime_version or ''
