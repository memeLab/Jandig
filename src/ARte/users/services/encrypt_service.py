import hashlib, secrets
from datetime import datetime


class EncryptService():
    def generate_verification_code(self, email):
        datetime_now = datetime.now()
        today =  '{}{}{}{}{}{}{}'.format(datetime_now.year, datetime_now.month, datetime_now.day, datetime_now.hour, datetime_now.minute, datetime_now.second, datetime_now.microsecond)
        decrypt_code = str(today) + (email * 4) + secrets.token_hex(16)
        verification_code = self.generate_hash_code(decrypt_code)
        return verification_code

    def generate_hash_code(self, decrypt_code):
        hash_code = hashlib.sha256(bytes(decrypt_code, encoding='utf-8'))
        return hash_code.hexdigest()