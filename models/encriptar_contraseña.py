from hashlib import sha256
import hashlib

def hash_password(password):
    password = hashlib.sha256(password.encode('utf-8'))
    return password.hexdigest()



