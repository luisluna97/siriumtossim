"""
SIRIUM Version Management
"""

VERSION = "1.0.0.5"
VERSION_DATE = "2025-08-25"
VERSION_NOTES = "FINAL FIX: Eliminate sorted() error with mixed float/string in airline columns"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
