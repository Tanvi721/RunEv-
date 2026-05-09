import random

def generate_otp():
    """Generates a 6-digit mockup OTP"""
    return str(random.randint(100000, 999999))

def verify_otp(input_otp, generated_otp):
    return input_otp == generated_otp
