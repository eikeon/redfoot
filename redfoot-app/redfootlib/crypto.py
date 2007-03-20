import logging

_logger = logging.getLogger(__name__)

from pickle import dumps, loads

try:
    from Crypto.Hash import MD5
    from Crypto.PublicKey import RSA
    import Crypto.Util.randpool as randpool
except ImportError, ie:
    _logger.error("Must have http://cheeseshop.python.org/pypi/pycrypto/2.0.1 installed")
    raise ie
else:
    _randpool = randpool.RandomPool(int(10000))
    _get_bytes = _randpool.get_bytes

    class Crypto(object):
        def __init__(self, keypair):
            self.__encrypt = keypair.encrypt
            self.__decrypt = keypair.decrypt
        def encrypt(self, value):
            return self.__encrypt(value, _get_bytes(1024))[0] # why is this is tuple?
        def decrypt(self, value):
            return self.__decrypt(value)

    def generate_key(passphrase):
        keypair=RSA.generate(1024, _get_bytes)
        file("redfoot.key", "wb").write(dumps(keypair))
        signature = keypair.sign(passphrase, "")
        file("redfoot.signature", "wb").write(dumps(signature))

    def use_key(passphrase):
        # TODO: how to passphrase protect private key... not just verify it.
        keypair = loads(file("redfoot.key", "rb").read())
        signature = loads(file("redfoot.signature", "rb").read())
        if keypair.verify(passphrase, signature):
            crypto = Crypto(keypair)
            del keypair
            _logger.info("passphrase verified")
            return crypto
        else:
            raise Exception("passphrase didn't verify")

