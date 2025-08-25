"""
SIRIUM Version Management
"""

VERSION = "1.0.1.0"
VERSION_DATE = "2025-08-25"
VERSION_NOTES = "FEATURE: Time parsing working perfectly! SFO format (1730 → 17:30) correctly converted to SSIM"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
