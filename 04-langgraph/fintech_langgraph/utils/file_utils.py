import os
from typing import Optional
from datetime import datetime

def ensure_directory(directory: str) -> None:
    """Ensure a directory exists, create if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename."""
    return os.path.splitext(filename)[1].lower()

def is_valid_text_file(filename: str) -> bool:
    """Check if the file is a valid text file."""
    return get_file_extension(filename) == '.txt'

def generate_timestamp() -> str:
    """Generate a timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S") 