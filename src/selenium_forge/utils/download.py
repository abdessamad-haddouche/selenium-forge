"""Download utilities for driver and resource management."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Callable
from urllib.parse import urlparse

import requests
from packaging import version

from selenium_forge.core.constants import DEFAULT_DOWNLOAD_TIMEOUT
from selenium_forge.exceptions import RetryableError, UserError


class Downloader:
    """Handles file downloads with progress tracking and verification."""

    def __init__(
        self,
        timeout: float = DEFAULT_DOWNLOAD_TIMEOUT,
        chunk_size: int = 8192,
    ) -> None:
        """Initialize downloader.

        Args:
            timeout: Download timeout in seconds
            chunk_size: Download chunk size in bytes
        """
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "selenium-forge/0.1.0 (+https://github.com/abdessamad-haddouche/selenium-forge)"
            }
        )

    def download_file(
        self,
        url: str,
        destination: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        verify_ssl: bool = True,
    ) -> Path:
        """Download a file from URL to destination.

        Args:
            url: URL to download from
            destination: Destination file path
            progress_callback: Optional callback for progress updates (downloaded, total)
            verify_ssl: Whether to verify SSL certificates

        Returns:
            Path to downloaded file

        Raises:
            RetryableError: If download fails temporarily
            UserError: If URL is invalid or download fails permanently
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise UserError(
                    f"Invalid download URL: {url}",
                    suggestion="Provide a valid HTTP/HTTPS URL",
                )

            # Create parent directory
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Download to temporary file first
            temp_file = destination.with_suffix(destination.suffix + ".tmp")

            try:
                response = self.session.get(
                    url,
                    stream=True,
                    timeout=self.timeout,
                    verify=verify_ssl,
                )
                response.raise_for_status()

                # Get total file size
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(temp_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback:
                                progress_callback(downloaded, total_size)

                # Move temp file to final destination
                shutil.move(str(temp_file), str(destination))

                return destination

            except requests.Timeout:
                raise RetryableError(
                    f"Download timeout after {self.timeout}s: {url}",
                ).add_context("url", url)

            except requests.RequestException as e:
                # Check if error is retryable
                if isinstance(e, (requests.ConnectionError, requests.Timeout)):
                    raise RetryableError(
                        f"Connection error while downloading: {e}",
                        cause=e,
                    ).add_context("url", url)
                else:
                    raise UserError(
                        f"Failed to download file: {e}",
                        cause=e,
                    ).add_context("url", url)

            finally:
                # Clean up temp file if it exists
                if temp_file.exists():
                    temp_file.unlink()

        except Exception as e:
            if isinstance(e, (RetryableError, UserError)):
                raise
            raise UserError(
                f"Unexpected error during download: {e}",
                cause=e,
            ).add_context("url", url)

    def download_to_memory(
        self,
        url: str,
        verify_ssl: bool = True,
    ) -> bytes:
        """Download file content to memory.

        Args:
            url: URL to download from
            verify_ssl: Whether to verify SSL certificates

        Returns:
            Downloaded file content as bytes

        Raises:
            RetryableError: If download fails temporarily
            UserError: If download fails
        """
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                verify=verify_ssl,
            )
            response.raise_for_status()
            return response.content

        except requests.Timeout:
            raise RetryableError(
                f"Download timeout after {self.timeout}s: {url}",
            ).add_context("url", url)

        except requests.RequestException as e:
            if isinstance(e, (requests.ConnectionError, requests.Timeout)):
                raise RetryableError(
                    f"Connection error while downloading: {e}",
                    cause=e,
                ).add_context("url", url)
            else:
                raise UserError(
                    f"Failed to download file: {e}",
                    cause=e,
                ).add_context("url", url)

    def get_url_content_type(self, url: str) -> Optional[str]:
        """Get content type of URL without downloading.

        Args:
            url: URL to check

        Returns:
            Content type string, or None if unavailable
        """
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.headers.get("content-type")
        except Exception:
            return None

    def get_url_size(self, url: str) -> Optional[int]:
        """Get size of file at URL without downloading.

        Args:
            url: URL to check

        Returns:
            File size in bytes, or None if unavailable
        """
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            content_length = response.headers.get("content-length")
            return int(content_length) if content_length else None
        except Exception:
            return None

    def verify_file_hash(
        self,
        file_path: Path,
        expected_hash: str,
        algorithm: str = "sha256",
    ) -> bool:
        """Verify file integrity using hash.

        Args:
            file_path: Path to file to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm (md5, sha1, sha256, etc.)

        Returns:
            True if hash matches, False otherwise
        """
        if not file_path.exists():
            return False

        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest().lower() == expected_hash.lower()

        except Exception:
            return False

    def extract_archive(
        self,
        archive_path: Path,
        destination: Path,
    ) -> Path:
        """Extract archive file to destination.

        Supports: .zip, .tar, .tar.gz, .tgz, .tar.bz2

        Args:
            archive_path: Path to archive file
            destination: Destination directory

        Returns:
            Path to extraction directory

        Raises:
            UserError: If extraction fails
        """
        if not archive_path.exists():
            raise UserError(
                f"Archive file not found: {archive_path}",
            )

        destination.mkdir(parents=True, exist_ok=True)

        try:
            shutil.unpack_archive(str(archive_path), str(destination))
            return destination

        except Exception as e:
            raise UserError(
                f"Failed to extract archive: {e}",
                cause=e,
            ).add_context("archive", str(archive_path))

    def close(self) -> None:
        """Close the downloader session."""
        self.session.close()

    def __enter__(self) -> Downloader:
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit."""
        self.close()
