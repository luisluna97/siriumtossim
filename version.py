"""
CIRUIM Version Management
"""

VERSION = "1.1.0"
VERSION_DATE = "2025-01-27"
VERSION_NOTES = "🔧 MAJOR UPDATES: Fixed date operation period in line 3 (Eff Date to Disc Date) + All Companies option + 50-line preview"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
