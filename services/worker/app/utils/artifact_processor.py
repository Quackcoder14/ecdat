"""
Artifact processor for extracting and preparing artifacts for scanning
"""

import os
import shutil
import tempfile
import zipfile
import tarfile
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ArtifactProcessor:
    """Process artifacts for scanning - extract archives, prepare directories"""
    
    def __init__(self, artifact_storage_path: str = "/app/artifacts"):
        self.artifact_storage_path = artifact_storage_path
        self.temp_dir = tempfile.mkdtemp(prefix="ecdat_scan_")
    
    def prepare_artifact_for_scan(self, artifact) -> str:
        """
        Prepare an artifact for scanning by extracting if needed
        Returns the path to scan
        """
        if not artifact.file_path:
            raise ValueError("Artifact has no file path")
        
        if not os.path.exists(artifact.file_path):
            raise FileNotFoundError(f"Artifact file not found: {artifact.file_path}")
        
        # If it's a directory already, return it
        if os.path.isdir(artifact.file_path):
            logger.info(f"Artifact is already a directory: {artifact.file_path}")
            return artifact.file_path
        
        # If it's an archive, extract it
        if self._is_archive(artifact.file_path):
            logger.info(f"Extracting archive: {artifact.file_path}")
            extract_path = self._extract_archive(artifact.file_path)
            return extract_path
        
        # If it's a single file, create a directory for it
        logger.info(f"Processing single file: {artifact.file_path}")
        return self._prepare_single_file(artifact.file_path)
    
    def _is_archive(self, file_path: str) -> bool:
        """Check if file is an archive"""
        archive_extensions = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz']
        return any(file_path.endswith(ext) for ext in archive_extensions)
    
    def _extract_archive(self, file_path: str) -> str:
        """Extract archive to temporary directory"""
        extract_dir = os.path.join(self.temp_dir, os.path.basename(file_path))
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            if file_path.endswith('.zip'):
                self._extract_zip(file_path, extract_dir)
            elif file_path.endswith('.tar') or file_path.endswith('.tar.gz') or \
                 file_path.endswith('.tgz') or file_path.endswith('.tar.bz2') or \
                 file_path.endswith('.tbz2') or file_path.endswith('.tar.xz') or \
                 file_path.endswith('.txz'):
                self._extract_tar(file_path, extract_dir)
            else:
                raise ValueError(f"Unsupported archive format: {file_path}")
            
            logger.info(f"Successfully extracted to: {extract_dir}")
            return extract_dir
            
        except Exception as e:
            logger.error(f"Failed to extract archive {file_path}: {e}")
            # Clean up on failure
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            raise
    
    def _extract_zip(self, file_path: str, extract_dir: str):
        """Extract ZIP archive"""
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    
    def _extract_tar(self, file_path: str, extract_dir: str):
        """Extract TAR archive (including compressed variants)"""
        with tarfile.open(file_path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_dir)
    
    def _prepare_single_file(self, file_path: str) -> str:
        """Prepare a single file for scanning by copying to temp directory"""
        file_dir = os.path.join(self.temp_dir, os.path.basename(file_path))
        os.makedirs(file_dir, exist_ok=True)
        
        dest_path = os.path.join(file_dir, os.path.basename(file_path))
        shutil.copy2(file_path, dest_path)
        
        logger.info(f"Copied single file to: {file_dir}")
        return file_dir
    
    def cleanup(self):
        """Clean up temporary directories"""
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory: {e}")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()


def process_artifact_for_scan(artifact, artifact_storage_path: str = "/app/artifacts") -> str:
    """
    Convenience function to process an artifact for scanning
    Returns the path to scan
    """
    processor = ArtifactProcessor(artifact_storage_path)
    try:
        scan_path = processor.prepare_artifact_for_scan(artifact)
        return scan_path
    except Exception as e:
        processor.cleanup()
        raise
