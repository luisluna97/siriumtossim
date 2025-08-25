"""
SIRIUM Version Management
"""

VERSION = "1.0.0.1"
VERSION_DATE = "2024-12-25"
VERSION_NOTES = "Fix: Data filtering for SFO files with trailing invalid rows"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
