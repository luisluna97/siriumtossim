"""
SIRIUM Version Management
"""

VERSION = "1.0.0.4"
VERSION_DATE = "2025-08-25"
VERSION_NOTES = "Ultra-robust data processing to eliminate float/string comparison errors"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
