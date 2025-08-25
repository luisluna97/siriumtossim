"""
SIRIUM Version Management
"""

VERSION = "1.0.0.3"
VERSION_DATE = "2025-08-25"
VERSION_NOTES = "Fix: Syntax error and correct date (we're in 2025!)"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
