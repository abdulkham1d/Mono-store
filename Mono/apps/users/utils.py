import base64
import hashlib
import hmac
import json
import random
import string

from django.conf import settings


def base64url_encode(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def base64url_decode(data):
    padding = '=' * (4 - len(data) % 4)
    padded = data + padding
    return base64.urlsafe_b64decode(padded.encode('utf-8'))


def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def generate_code():
    return ''.join(random.choices(string.digits, k=6))


def create_jwt_token(payload):
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    header_json = json.dumps(header, separators=(',', ':'))
    payload_json = json.dumps(payload, separators=(',', ':'))

    header_base64 = base64url_encode(header_json)
    payload_base64 = base64url_encode(payload_json)

    message = f"{header_base64}.{payload_base64}".encode('utf-8')
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        message,
        hashlib.sha256
    ).digest()

    signature_base64 = base64url_encode(signature)

    jwt_token = f"{header_base64}.{payload_base64}.{signature_base64}"

    return jwt_token


def verify_jwt_token(token):
    try:

        header_base64, payload_base64, signature_base64 = token.split('.')

        message = f"{header_base64}.{payload_base64}".encode('utf-8')

        expected_signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()

        actual_signature = base64url_decode(signature_base64)

        if not hmac.compare_digest(expected_signature, actual_signature):
            return None

        payload_json = base64url_decode(payload_base64).decode('utf-8')
        payload = json.loads(payload_json)

        return payload

    except Exception as e:
        print(f"JWT verification error: {e}")
        return None
