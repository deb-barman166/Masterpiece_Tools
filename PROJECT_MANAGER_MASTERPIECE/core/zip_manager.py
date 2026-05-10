"""
╔══════════════════════════════════════════════════════════════╗
║         PROJECT_MANAGER_MASTERPIECE - ZIP MANAGER           ║
║         Archive Creation, Extraction & Management           ║
╚══════════════════════════════════════════════════════════════╝
"""

import zipfile
import shutil
import os
from pathlib import Path
from datetime import datetime
from core.security import SecurityGuard


class ZipManager:
    """
    Full ZIP archive manager.
    Handles upload, extraction, compression, and download prep.
    """

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "projects"
        self.temp_dir = self.base_dir.parent / "temp"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.security = SecurityGuard(str(self.base_dir))

    # ══════════════════════════════════════════
    # EXTRACT ZIP
    # ══════════════════════════════════════════

    def extract_zip(self, zip_path: str, extract_to: str = None, project_name: str = None) -> dict:
        """
        Extract a ZIP file into the projects directory.
        
        Args:
            zip_path: Path to the ZIP file (uploaded temp path)
            extract_to: Target directory (defaults to projects/<name>)
            project_name: Override project name
        """
        try:
            zip_path = Path(zip_path)
            if not zip_path.exists():
                return self._err(f"ZIP file not found: {zip_path}")

            # Security: validate ZIP contents
            is_safe, reason = self.security.validate_zip_content(str(zip_path))
            if not is_safe:
                return self._err(reason)

            # Determine project name
            if not project_name:
                project_name = zip_path.stem

            # Determine extraction directory
            if extract_to:
                target_dir = Path(extract_to)
            else:
                target_dir = self.base_dir / project_name

            # Handle duplicate names
            original_target = target_dir
            counter = 1
            while target_dir.exists():
                target_dir = original_target.parent / f"{original_target.name}_{counter}"
                counter += 1

            target_dir.mkdir(parents=True, exist_ok=True)

            # Extract with progress tracking
            with zipfile.ZipFile(zip_path, 'r') as zf:
                members = zf.namelist()
                total = len(members)
                extracted = []

                for i, member in enumerate(members):
                    zf.extract(member, target_dir)
                    extracted.append(member)

            # Count stats
            file_count = sum(1 for _ in target_dir.rglob("*") if _.is_file())
            dir_count = sum(1 for _ in target_dir.rglob("*") if _.is_dir())

            return self._ok(
                f"✅ Extracted {total} items → {target_dir.name}",
                {
                    "project_name": target_dir.name,
                    "path": str(target_dir),
                    "files": file_count,
                    "directories": dir_count,
                    "total_items": total
                }
            )

        except zipfile.BadZipFile:
            return self._err("❌ Invalid or corrupted ZIP file")
        except Exception as e:
            return self._err(f"Extraction failed: {e}")

    # ══════════════════════════════════════════
    # CREATE ZIP
    # ══════════════════════════════════════════

    def create_zip(self, source_path: str, output_name: str = None) -> dict:
        """
        Compress a directory or file into a ZIP archive.
        Returns path to the created ZIP.
        """
        try:
            source = Path(source_path)
            if not source.exists():
                return self._err(f"Source not found: {source_path}")

            # Determine output path
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"{source.name}_{timestamp}.zip"

            if not output_name.endswith(".zip"):
                output_name += ".zip"

            zip_output = self.temp_dir / output_name

            # Create ZIP
            with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zf:
                if source.is_dir():
                    file_count = 0
                    for file_path in source.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source.parent)
                            zf.write(file_path, arcname)
                            file_count += 1
                else:
                    zf.write(source, source.name)
                    file_count = 1

            zip_size = zip_output.stat().st_size

            return self._ok(
                f"📦 Created ZIP: {output_name}",
                {
                    "zip_path": str(zip_output),
                    "zip_name": output_name,
                    "size": self._human_size(zip_size),
                    "files_zipped": file_count
                }
            )

        except Exception as e:
            return self._err(f"ZIP creation failed: {e}")

    # ══════════════════════════════════════════
    # UPLOAD ZIP (handle temp file)
    # ══════════════════════════════════════════

    def handle_upload(self, uploaded_file_path: str, project_name: str = None) -> dict:
        """
        Process an uploaded ZIP file.
        Copies to temp directory, validates, then extracts.
        """
        try:
            src = Path(uploaded_file_path)
            if not src.exists():
                return self._err("Uploaded file not found")

            # Copy to temp
            temp_zip = self.temp_dir / src.name
            shutil.copy2(src, temp_zip)

            # Extract
            result = self.extract_zip(str(temp_zip), project_name=project_name)

            # Cleanup temp zip
            temp_zip.unlink(missing_ok=True)

            return result

        except Exception as e:
            return self._err(f"Upload handling failed: {e}")

    # ══════════════════════════════════════════
    # LIST ZIP CONTENTS
    # ══════════════════════════════════════════

    def list_zip_contents(self, zip_path: str) -> dict:
        """Preview ZIP contents without extracting."""
        try:
            zip_path = Path(zip_path)
            if not zip_path.exists():
                return self._err("ZIP file not found")

            with zipfile.ZipFile(zip_path, 'r') as zf:
                contents = []
                for info in zf.infolist():
                    contents.append({
                        "name": info.filename,
                        "size": self._human_size(info.file_size),
                        "compressed": self._human_size(info.compress_size),
                        "ratio": f"{(1 - info.compress_size/max(info.file_size,1))*100:.0f}%",
                        "type": "directory" if info.filename.endswith("/") else "file"
                    })

            return self._ok(
                f"ZIP contains {len(contents)} items",
                {"contents": contents, "total": len(contents)}
            )

        except zipfile.BadZipFile:
            return self._err("Invalid ZIP file")
        except Exception as e:
            return self._err(f"List failed: {e}")

    # ══════════════════════════════════════════
    # DOWNLOAD PREPARATION
    # ══════════════════════════════════════════

    def prepare_download(self, project_path: str) -> dict:
        """Zip a project and prepare it for download."""
        return self.create_zip(project_path)

    # ══════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════

    @staticmethod
    def _human_size(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def _ok(message: str, data: dict = None) -> dict:
        return {"success": True, "message": message, "data": data or {}}

    @staticmethod
    def _err(message: str) -> dict:
        return {"success": False, "message": message, "data": {}}
