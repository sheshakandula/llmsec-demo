# DEMO ONLY - do not enable in production
"""
Sandboxed file reader for demo - permits only data/tmp_demo, forbids data/secret_demo
"""
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# UPDATED BY CLAUDE: Project root and allowed/forbidden paths
PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # UPDATED BY CLAUDE
ALLOWED_ROOT = os.path.abspath(os.path.join(PROJ_ROOT, "data", "tmp_demo"))  # UPDATED BY CLAUDE
FORBIDDEN_ROOT = os.path.abspath(os.path.join(PROJ_ROOT, "data", "secret_demo"))  # UPDATED BY CLAUDE
ALLOWED_EXTENSIONS = {".txt", ".md", ".log"}  # UPDATED BY CLAUDE


class ReadFileRequest(BaseModel):
    """
    Validated file read request with path traversal protection

    Fields:
        path: Relative path within allowed root (no absolute paths, no ..)
        max_bytes: Maximum bytes to read (default 2048)
    """
    path: str = Field(..., min_length=1, max_length=500, description="Relative file path")  # UPDATED BY CLAUDE
    max_bytes: Optional[int] = Field(default=2048, ge=1, le=1048576, description="Max bytes to read")  # UPDATED BY CLAUDE

    @field_validator('path')  # UPDATED BY CLAUDE
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate path is relative and has no traversal"""
        # UPDATED BY CLAUDE: Reject absolute paths
        if os.path.isabs(v):
            raise ValueError("Absolute paths not allowed")

        # UPDATED BY CLAUDE: Reject paths with traversal after normalization
        normalized = os.path.normpath(v)
        if normalized.startswith("..") or "/.." in normalized or "\\.." in normalized:
            raise ValueError("Path traversal not allowed")

        return v.strip()  # UPDATED BY CLAUDE


class FilesDemoTool:
    """
    🎭 DEMO: Sandboxed file reader with explicit allow/deny roots

    Allows: data/tmp_demo/*
    Forbids: data/secret_demo/*
    Extensions: .txt, .md, .log only
    """

    def read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:  # UPDATED BY CLAUDE
        """
        Read file with path validation and sandboxing

        Args:
            args: Dictionary with 'path' and optional 'max_bytes'

        Returns:
            Result dict with status, path, and content (or error)

        Example:
            >>> FilesDemoTool().read_file({"path": "hello.txt", "max_bytes": 1000})
            {'status': 'ok', 'path': 'hello.txt', 'content': '...'}
        """
        try:
            # UPDATED BY CLAUDE: Validate with Pydantic
            req = ReadFileRequest(**args)

            # UPDATED BY CLAUDE: Resolve target path relative to allowed root
            target_path = os.path.join(ALLOWED_ROOT, req.path)
            target_real = os.path.realpath(target_path)

            logger.info(f"[FilesDemoTool] Request path={req.path}, resolved={target_real}")

            # UPDATED BY CLAUDE: Check if path is under FORBIDDEN_ROOT
            if target_real.startswith(FORBIDDEN_ROOT):
                logger.warning(f"[FilesDemoTool] BLOCKED: forbidden path {target_real}")
                return {
                    "status": "error",
                    "error": "access denied: forbidden path",
                    "path": req.path
                }

            # UPDATED BY CLAUDE: Check if path is under ALLOWED_ROOT
            if not target_real.startswith(ALLOWED_ROOT):
                logger.warning(f"[FilesDemoTool] BLOCKED: outside allowed root {target_real}")
                return {
                    "status": "error",
                    "error": "access denied: outside allowed root",
                    "path": req.path
                }

            # UPDATED BY CLAUDE: Check file extension
            ext = os.path.splitext(target_real)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                logger.warning(f"[FilesDemoTool] BLOCKED: invalid extension {ext}")
                return {
                    "status": "error",
                    "error": f"access denied: extension {ext} not allowed",
                    "path": req.path,
                    "allowed_extensions": list(ALLOWED_EXTENSIONS)
                }

            # UPDATED BY CLAUDE: Check file exists
            if not os.path.exists(target_real):
                return {
                    "status": "error",
                    "error": "file not found",
                    "path": req.path
                }

            # UPDATED BY CLAUDE: Read file with max_bytes limit
            try:
                with open(target_real, 'rb') as f:
                    raw_bytes = f.read(req.max_bytes)

                # UPDATED BY CLAUDE: Decode UTF-8 with error replacement
                content = raw_bytes.decode('utf-8', errors='replace')

                logger.info(f"[FilesDemoTool] SUCCESS: read {len(raw_bytes)} bytes from {req.path}")

                return {
                    "status": "ok",
                    "path": req.path,
                    "content": content,
                    "bytes_read": len(raw_bytes),
                    "truncated": len(raw_bytes) == req.max_bytes
                }

            except Exception as read_error:
                logger.error(f"[FilesDemoTool] Read error: {read_error}")
                return {
                    "status": "error",
                    "error": f"read error: {str(read_error)}",
                    "path": req.path
                }

        except ValueError as e:
            # UPDATED BY CLAUDE: Pydantic validation error
            logger.warning(f"[FilesDemoTool] Validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "args": args
            }

        except Exception as e:
            # UPDATED BY CLAUDE: Unexpected error
            logger.error(f"[FilesDemoTool] Unexpected error: {e}")
            return {
                "status": "error",
                "error": f"Internal error: {str(e)}"
            }
