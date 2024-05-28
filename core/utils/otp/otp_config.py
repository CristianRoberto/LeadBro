import pyotp
import os
from dotenv import load_dotenv
load_dotenv()


class OTP_ACCESS :

    def __init__(self) -> None:
        self.totp = pyotp.totp.TOTP(os.getenv("OTP_TOKEN"))

    def __generate_code(self):
        self.totp.now() # => '492039'
    
    def verificate_code (self, code):
        return self.totp.verify(code)
    
