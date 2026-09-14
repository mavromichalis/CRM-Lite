import hashlib as hl

def hash(string):
    return hl.sha256(string.encode()).hexdigest()