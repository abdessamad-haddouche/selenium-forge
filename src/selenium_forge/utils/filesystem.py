"""Filesystem utilities for managing driver files and cache."""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path
from typing import List, Optional

from selenium_forge.exceptions import UserError


class FileSystemManager:
    """Manages filesystem operations for selenium-forge."""

    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure directory exists, create if necessary.

        Args:
            path: Directory path

        Returns:
            Path to directory

        Raises:
            UserError: If directory cannot be created
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except Exception as e:
            raise UserError(
                f"Failed to create directory: {path}",
                cause=e,
            )

    @staticmethod
    def make_executable(file_path: Path) -> None:
        """Make file executable.

        Args:
            file_path: Path to file

        Raises:
            UserError: If permissions cannot be set
        """
        if not file_path.exists():
            raise UserError(f"File not found: {file_path}")

        try:
            # Add execute permissions for user, group, and others
            current_permissions = file_path.stat().st_mode
            new_permissions = (
                current_permissions
                | stat.S_IXUSR
                | stat.S_IXGRP
                | stat.S_IXOTH
            )
            file_path.chmod(new_permissions)
        except Exception as e:
            raise UserError(
                f"Failed to make file executable: {file_path}",
                cause=e,
            )

    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            File size in bytes

        Raises:
            UserError: If file cannot be accessed
        """
        if not file_path.exists():
            raise UserError(f"File not found: {file_path}")

        try:
            return file_path.stat().st_size
        except Exception as e:
            raise UserError(
                f"Failed to get file size: {file_path}",
                cause=e,
            )

    @staticmethod
    def get_directory_size(directory: Path) -> int:
        """Get total size of directory in bytes.

        Args:
            directory: Directory path

        Returns:
            Total size in bytes
        """
        total_size = 0
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass

        return total_size

    @staticmethod
    def delete_path(path: Path, ignore_errors: bool = False) -> None:
        """Delete file or directory.

        Args:
            path: Path to delete
            ignore_errors: Whether to ignore errors

        Raises:
            UserError: If deletion fails and ignore_errors is False
        """
        if not path.exists():
            return

        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception as e:
            if not ignore_errors:
                raise UserError(
                    f"Failed to delete: {path}",
                    cause=e,
                )

    @staticmethod
    def clean_directory(
        directory: Path,
        pattern: str = "*",
        exclude: Optional[List[str]] = None,
    ) -> int:
        """Clean files from directory matching pattern.

        Args:
            directory: Directory to clean
            pattern: Glob pattern for files to delete
            exclude: List of patterns to exclude from deletion

        Returns:
            Number of files deleted
        """
        if not directory.exists():
            return 0

        deleted_count = 0
        exclude = exclude or []

        try:
            for item in directory.glob(pattern):
                # Check if item matches any exclude pattern
                should_exclude = any(
                    item.match(exclude_pattern) for exclude_pattern in exclude
                )

                if should_exclude:
                    continue

                try:
                    if item.is_file():
                        item.unlink()
                        deleted_count += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        deleted_count += 1
                except Exception:
                    continue

        except Exception:
            pass

        return deleted_count

    @staticmethod
    def find_files(
        directory: Path,
        pattern: str = "*",
        recursive: bool = True,
    ) -> List[Path]:
        """Find files in directory matching pattern.

        Args:
            directory: Directory to search
            pattern: Glob pattern to match
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        if not directory.exists():
            return []

        try:
            if recursive:
                return list(directory.rglob(pattern))
            else:
                return list(directory.glob(pattern))
        except Exception:
            return []

    @staticmethod
    def copy_file(source: Path, destination: Path) -> Path:
        """Copy file to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            Path to copied file

        Raises:
            UserError: If copy fails
        """
        if not source.exists():
            raise UserError(f"Source file not found: {source}")

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return destination
        except Exception as e:
            raise UserError(
                f"Failed to copy file: {e}",
                cause=e,
            ).add_context("source", str(source)).add_context(
                "destination", str(destination)
            )

    @staticmethod
    def move_file(source: Path, destination: Path) -> Path:
        """Move file to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            Path to moved file

        Raises:
            UserError: If move fails
        """
        if not source.exists():
            raise UserError(f"Source file not found: {source}")

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            return destination
        except Exception as e:
            raise UserError(
                f"Failed to move file: {e}",
                cause=e,
            ).add_context("source", str(source)).add_context(
                "destination", str(destination)
            )

    @staticmethod
    def is_writable(path: Path) -> bool:
        """Check if path is writable.

        Args:
            path: Path to check

        Returns:
            True if writable, False otherwise
        """
        try:
            if path.exists():
                return os.access(path, os.W_OK)
            else:
                # Check parent directory
                return os.access(path.parent, os.W_OK)
        except Exception:
            return False

    @staticmethod
    def get_temp_directory() -> Path:
        """Get temporary directory for selenium-forge.

        Returns:
            Path to temporary directory
        """
        import tempfile

        temp_dir = Path(tempfile.gettempdir()) / "selenium-forge"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    @staticmethod
    def create_temp_file(suffix: str = "", prefix: str = "sf_") -> Path:
        """Create temporary file.

        Args:
            suffix: File suffix
            prefix: File prefix

        Returns:
            Path to temporary file
        """
        import tempfile

        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)
        return Path(path)
