# pupgui2 compatibility tools module
# DXVK for Lutris (nightly version): https://github.com/doitsujin/dxvk/
# Copyright (C) 2022 DavidoTek, partially based on AUNaseef's protonup

from typing import override
from PySide6.QtCore import QCoreApplication

from pupgui2.util import ghapi_rlcheck

from pupgui2.resources.ctmods.ctmod_z0dxvk import CtInstaller as DXVKInstaller


CT_NAME = 'DXVK (nightly)'
CT_LAUNCHERS = ['lutris', 'advmode']
CT_DESCRIPTION = {'en': QCoreApplication.instance().translate('ctmod_z2dxvknightly', '''Nightly version of DXVK (master branch), a Vulkan based implementation of Direct3D 8, 9, 10 and 11 for Linux/Wine.<br/><br/><b>Warning: Nightly version is unstable, use with caution!</b>''')}


class CtInstaller(DXVKInstaller):

    BUFFER_SIZE = 65536
    CT_URL = 'https://api.github.com/repos/doitsujin/dxvk/actions/artifacts'
    CT_INFO_URL = 'https://github.com/doitsujin/dxvk/commit/'

    def __init__(self, main_window = None):

        super().__init__(main_window)

        self.release_format = 'zip'

    def __get_artifact_from_commit(self, commit: str) -> str | None:
        """
        Get artifact from commit
        Return Type: str
        """
        for artifact in self.rs.get(f'{self.CT_URL}?per_page=100').json()["artifacts"]:
            if artifact['workflow_run']['head_sha'][:len(commit)] == commit:
                artifact['workflow_run']['head_sha'] = commit
                return artifact
        return None

    def __fetch_data(self, tag):
        """
        Fetch GitHub release information
        Return Type: dict
        Content(s):
            'version', 'date', 'download', 'size', 'checksum'
        """
        # Tag in this case is the commit hash.
        data = self.__get_artifact_from_commit(tag)
        if not data:
            return
        values = {'version': data['workflow_run']['head_sha'][:7], 'date': data['updated_at'].split('T')[0]}
        values['download'] = f'https://nightly.link/doitsujin/dxvk/actions/runs/{data["workflow_run"]["id"]}/{data["name"]}.zip'

        values['size'] = data['size_in_bytes']
        return values

    def fetch_releases(self, count: int = 100, page: int = 1) -> list:
        """
        List available releases
        Return Type: str[]
        """
        tags = []
        for artifact in ghapi_rlcheck(self.rs.get(f'{self.CT_URL}?per_page={count}&page={page}').json()).get("artifacts", {}):
            workflow = artifact['workflow_run']
            if workflow["head_branch"] != "master" or artifact["expired"]:
                continue
            tags.append(workflow['head_sha'][:7])
        return tags
