import hashlib  
from pathlib import Path  
  
def dhash_text(text: str, encoding: str = "utf-8") -> str:  
    data = text.encode(encoding)  
    return hashlib.sha256(hashlib.sha256(data).digest()).hexdigest()  
  
def dhash_file(path: str | Path) -> str:  
    data = Path(path).read_bytes()  
    return hashlib.sha256(hashlib.sha256(data).digest()).hexdigest()  
