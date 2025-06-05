
import hashlib
import logging
import os
import urllib.parse
from pathlib import Path
from typing import BinaryIO, Optional

from dbgpt.core.interface.file import FileMetadata, StorageBackend

logger = logging.getLogger(__name__)


class NasFileStorage(StorageBackend):
    """NAS file storage backend that links existing files instead of uploading."""
    
    storage_type: str = "nas"
    
    def __init__(
        self,
        nas_base_path: str,
        allow_symlinks: bool = True,
        read_only: bool = True,
        auto_create_directories: bool = False,
        save_chunk_size: int = 1024 * 1024,
        public_url_base: Optional[str] = None,
    ):
        """Initialize NAS file storage.
        
        Args:
            nas_base_path: NAS挂载的基础路径
            allow_symlinks: 是否允许符号链接
            read_only: 是否为只读模式
            auto_create_directories: 是否自动创建目录
            save_chunk_size: 读取块大小
            public_url_base: 公共访问URL基础路径
        """
        self.nas_base_path = Path(nas_base_path).resolve()
        self.allow_symlinks = allow_symlinks
        self.read_only = read_only
        self.auto_create_directories = auto_create_directories
        self._save_chunk_size = save_chunk_size
        self.public_url_base = public_url_base
        
        # 验证NAS路径是否可访问
        if not self.nas_base_path.exists() or not self.nas_base_path.is_dir():
            raise ValueError(f"NAS base path not accessible: {nas_base_path}")
        
        logger.info(f"Initialized NAS storage with base path: {self.nas_base_path}")
    
    @property
    def save_chunk_size(self) -> int:
        return self._save_chunk_size
    
    def save(
        self,
        bucket: str,
        file_id: str,
        file_data: BinaryIO,
        public_url: bool = False,
        public_url_expire: Optional[int] = None,
    ) -> str:
        """保存文件到NAS存储。
        
        对于NAS场景，支持两种模式：
        1. 关联现有文件：如果file_data.name指向NAS内的现有文件
        2. 创建新文件：将file_data内容写入到NAS指定位置
        """
        # 构建目标路径
        bucket_path = self.nas_base_path / bucket
        target_file_path = bucket_path / file_id
        
        # 检查是否为关联现有文件的模式
        original_path = getattr(file_data, 'name', None)
        if original_path and Path(original_path).exists():
            # 关联现有文件模式
            original_path = Path(original_path).resolve()
            
            # 验证文件是否在NAS路径内
            try:
                original_path.relative_to(self.nas_base_path)
            except ValueError:
                raise ValueError(
                    f"File must be within NAS base path: {self.nas_base_path}"
                )
            
            # 验证文件存在性和可读性
            if not original_path.exists():
                raise FileNotFoundError(f"NAS file not found: {original_path}")
            if not os.access(original_path, os.R_OK):
                raise PermissionError(f"NAS file not readable: {original_path}")
            
            # 检查符号链接权限
            if original_path.is_symlink() and not self.allow_symlinks:
                raise ValueError("Symbolic links are not allowed")
            
            logger.info(f"Linking existing NAS file: {original_path}")
            return f"nas://{bucket}/{file_id}?path={urllib.parse.quote(str(original_path))}"
        
        else:
            # 创建新文件模式
            if self.read_only:
                raise ValueError("Cannot create new files in read-only mode")
            
            # 确保目录存在
            if self.auto_create_directories:
                bucket_path.mkdir(parents=True, exist_ok=True)
            elif not bucket_path.exists():
                raise FileNotFoundError(f"Bucket directory not found: {bucket_path}")
            
            # 写入文件
            try:
                with open(target_file_path, 'wb') as f:
                    while True:
                        chunk = file_data.read(self._save_chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                
                logger.info(f"Created new NAS file: {target_file_path}")
                return f"nas://{bucket}/{file_id}?path={urllib.parse.quote(str(target_file_path))}"
            
            except Exception as e:
                logger.error(f"Failed to save file to NAS: {e}")
                raise
    
    def load(self, fm: FileMetadata) -> BinaryIO:
        """从NAS路径直接加载文件。"""
        file_path = self._parse_storage_path(fm.storage_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"NAS file not found: {file_path}")
        
        # 检查符号链接权限
        if file_path.is_symlink() and not self.allow_symlinks:
            raise ValueError("Symbolic links are not allowed")
        
        try:
            return open(file_path, "rb")
        except Exception as e:
            logger.error(f"Failed to load NAS file {file_path}: {e}")
            raise
    
    def delete(self, fm: FileMetadata) -> bool:
        """删除NAS文件。"""
        file_path = self._parse_storage_path(fm.storage_path)
        
        if self.read_only:
            # 只读模式下不删除原始文件，只移除关联关系
            logger.info(
                f"NAS file association removed (read-only mode), "
                f"original file preserved: {file_path}"
            )
            return True
        
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted NAS file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete NAS file {file_path}: {e}")
            return False
    
    def get_public_url(self, fm: FileMetadata, expire: Optional[int] = None) -> Optional[str]:
        """生成NAS文件的公共访问URL。"""
        if not self.public_url_base:
            return None
        
        file_path = self._parse_storage_path(fm.storage_path)
        
        # 计算相对于NAS基础路径的相对路径
        try:
            relative_path = file_path.relative_to(self.nas_base_path)
            # 构造公共URL
            public_url = f"{self.public_url_base.rstrip('/')}/{relative_path.as_posix()}"
            return public_url
        except ValueError:
            logger.warning(f"File {file_path} is not within NAS base path")
            return None
    
    def _parse_storage_path(self, storage_path: str) -> Path:
        """解析存储路径，提取实际文件路径。"""
        if storage_path.startswith("nas://"):
            # 解析NAS URI: nas://bucket/file_id?path=encoded_path
            from urllib.parse import parse_qs, urlparse
            
            parsed_url = urlparse(storage_path)
            params = parse_qs(parsed_url.query)
            
            encoded_path = params.get("path", [None])[0]
            if encoded_path:
                actual_path = urllib.parse.unquote(encoded_path)
                return Path(actual_path)
            
            # 如果没有path参数，尝试从bucket和file_id构造路径
            path_parts = parsed_url.path.strip("/").split("/", 1)
            if len(path_parts) == 2:
                bucket, file_id = path_parts
                return self.nas_base_path / bucket / file_id
        
        # 兼容旧格式：直接的文件路径
        return Path(storage_path)