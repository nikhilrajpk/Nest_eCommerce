import pyotp
from datetime import datetime, timedelta

def send_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=180)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=3)
    request.session['otp_valid_date'] = str(valid_date)
    print('OTP : ',otp)
    return otp