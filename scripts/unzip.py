from sh import gunzip
import os

def unzip(gz_path: str) -> None:
    gunzip(gz_path, "--keep", "--force") # Overwrites the unzipped file if it already exists (--force)
    assert os.path.exists(gz_path[:-3]) == True
        
    