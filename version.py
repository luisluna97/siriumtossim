"""
SIRIUM Version Management
"""

VERSION = "1.0.0.2"
VERSION_DATE = "2024-12-25"
VERSION_NOTES = "Fix: String formatting error and enhanced data type protection"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
