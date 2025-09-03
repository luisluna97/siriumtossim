"""
CIRIUM Version Management
"""

VERSION = "1.1.4"
VERSION_DATE = "2025-08-03"
VERSION_NOTES = "📦 CARGO LOGIC: Seats = 0 → Cargo (F), Seats > 0 → Passenger (J). Perfect flight type detection!"

def get_version_info():
    """Return version information"""
    return {
        "version": VERSION,
        "date": VERSION_DATE,
        "notes": VERSION_NOTES
    }
