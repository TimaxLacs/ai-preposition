import hashlib

def get_post_hash(text: str) -> str:
    """Возвращает MD5 хеш текста"""
    return hashlib.md5(text.strip().encode('utf-8')).hexdigest()





