import passlib.hash
from flaskaws import config


lib = passlib.hash.__getattr__(config.HASH_ALGO_CLS)


def encrypt_password(password):
    return lib.encrypt(password, salt_size=config.HASH_SALT_SIZE, rounds=config.HASH_ROUNDS)


def check_password(password, encrypted):
    return lib.verify(password, encrypted)


def identify(password):
    return lib.identify(password)
