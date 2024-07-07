import hashlib
import secrets
from datetime import datetime


class EncryptService:
    def generate_verification_code(self, email):
        datetime_now = datetime.now()
        _year = datetime_now.year
        _month = datetime_now.month
        _day = datetime_now.day
        _hour = datetime_now.hour
        _minute = datetime_now.minute
        _second = datetime_now.second
        _microsec = datetime_now.microsecond

        today = f"{_year}{_month}{_day}{_hour}{_minute}{_second}{_microsec}"
        decrypt_code = str(today) + (email * 4) + secrets.token_hex(16)
        verification_code = self.generate_hash_code(decrypt_code)
        return verification_code

    def generate_hash_code(self, decrypt_code):
        hash_code = hashlib.sha256(bytes(decrypt_code, encoding="utf-8"))
        return hash_code.hexdigest()
