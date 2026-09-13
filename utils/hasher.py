import hashlib as hl

def hash(string):
    return l.sha256(string.encode()).hexdigest()