"""
Railway-friendly import script for historical data.

Downloads Excel file from URL and imports it to the Railway database.
This avoids the need to upload large files to Railway's ephemeral filesystem.

Usage:
  python -m backend.import_from_url <url_to_excel_file>
  
Example:
  python -m backend.import_from_url https://example.com/historical_draws.xlsx
"""

import sys
import tempfile
from pathlib import Path
import urllib.request

from backend.import_historical import import_historical_data


def download_file(url: str, destination: str):
    """Download file from URL to destination path."""
    print(f"Downloading file from URL...")
    print(f"  URL: {url}")
    print(f"  Destination: {destination}")
    
    try:
        urllib.request.urlretrieve(url, destination)
        file_size = Path(destination).stat().st_size
        print(f"  ✓ Downloaded {file_size:,} bytes")
        return True
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m backend.import_from_url <url_to_excel_file>")
        print("\nExample:")
        print("  python -m backend.import_from_url https://example.com/data.xlsx")
        print("\nThe Excel file should have:")
        print("  - Sheet name: 'Draws'")
        print("  - Column name: 'letter'")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Download file
        if not download_file(url, tmp_path):
            sys.exit(1)
        
        # Import from downloaded file
        import_historical_data(tmp_path)
        
    finally:
        # Clean up temporary file
        try:
            Path(tmp_path).unlink()
        except:
            pass
