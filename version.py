"""
CIRIUM Version Management
"""

VERSION = "1.1.3"
VERSION_DATE = "2025-08-03"
VERSION_NOTES = "✈️ EQUIPMENT: Now uses real aircraft types from Equip column (388, 359, 77X, etc.) instead of default 320"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
