"""
CIRUIM Version Management
"""

VERSION = "1.0.1.1"
VERSION_DATE = "2025-08-25"
VERSION_NOTES = "REBRAND: SIRIUM → CIRUIM! 😂 (Time parsing still working perfectly)"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
