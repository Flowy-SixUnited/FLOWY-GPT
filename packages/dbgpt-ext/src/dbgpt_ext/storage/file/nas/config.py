'''
Author: zhangyj 563346743@qq.com
Date: 2025-06-05 10:45:16
LastEditors: zhangyj 563346743@qq.com
LastEditTime: 2025-06-05 10:47:32
FilePath: \FLOWY-GPT\packages\dbgpt-ext\src\dbgpt_ext\storage\file\nas\config.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
"""NAS storage configuration."""

from dataclasses import dataclass, field
from typing import Optional

from dbgpt.core.interface.file import StorageBackend, StorageBackendConfig
from dbgpt.util.i18n_utils import _


@dataclass
class NasStorageConfig(StorageBackendConfig):
    """NAS storage configuration."""
    
    __type__ = "nas"
    
    nas_base_path: str = field(
        metadata={
            "help": _(
                "The base path of the NAS mount point. "
                "e.g. /mnt/nas or D:\\nas_mount"
            )
        },
    )
    
    allow_symlinks: Optional[bool] = field(
        default=True,
        metadata={
            "help": _(
                "Whether to allow symbolic links in NAS paths. "
                "Default is True."
            ),
        },
    )
    
    read_only: Optional[bool] = field(
        default=True,
        metadata={
            "help": _(
                "Whether the NAS storage is read-only. "
                "If True, delete operations will not remove actual files. "
                "Default is True."
            ),
        },
    )
    
    auto_create_directories: Optional[bool] = field(
        default=False,
        metadata={
            "help": _(
                "Whether to automatically create directories if they don't exist. "
                "Only works when read_only is False. Default is False."
            ),
        },
    )
    
    save_chunk_size: Optional[int] = field(
        default=1024 * 1024,
        metadata={
            "help": _(
                "The chunk size when reading files. "
                "Default is 1M."
            )
        },
    )
    
    public_url_base: Optional[str] = field(
        default=None,
        metadata={
            "help": _(
                "The base URL for public access to NAS files. "
                "e.g. http://nas.example.com/files/. "
                "If not set, public URLs will not be generated."
            )
        },
    )

    def create_storage(self) -> StorageBackend:
        """Create NAS storage backend."""
        from .nas_storage import NasFileStorage

        return NasFileStorage(
            nas_base_path=self.nas_base_path,
            allow_symlinks=self.allow_symlinks,
            read_only=self.read_only,
            auto_create_directories=self.auto_create_directories,
            save_chunk_size=self.save_chunk_size,
            public_url_base=self.public_url_base,
        )