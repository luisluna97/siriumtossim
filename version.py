"""
CIRIUM Version Management
"""

VERSION = "1.2.0"
VERSION_DATE = "2025-08-03"
VERSION_NOTES = "🎯 MULTIPLE SELECT: Choose specific airlines (e.g., EK + AI) for custom SSIM files! Single, Multiple, or All modes."

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
