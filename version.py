"""
CIRUIM Version Management
"""

VERSION = "1.1.1"
VERSION_DATE = "2025-08-03"
VERSION_NOTES = "🔧 FIXED: All Companies now generates single SSIM file + Filtered invalid airline codes + Professional design"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
