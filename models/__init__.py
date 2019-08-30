import requests
import datetime
import uuid
import json
import hashlib
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256


class INGapp(requests.Session):
    """docstring for Test."""
    tls_cert = '/Users/razvancristea/sandboxcerts/rING_app_TLS_public.crt'
    tls_key = '/Users/razvancristea/sandboxcerts/rING_app_TLS.key'
    sign_key = '/Users/razvancristea/sandboxcerts/rING_app_signing.key'

    client_id = "004a496f-1551-476c-baae-5a3dbf81f5b9"

    reqPath = "https://api.ing.com"


    def calculate_digest(payload):
        payloadDigest = hashlib.sha256()
        payloadDigest.update(payload.encode())
        digest = b64encode(payloadDigest.digest()).decode()
        return digest

    def calculate_signature(httpMethod, endpoint, reqDate, digest, reqId):
        stringToSign = f"""(request-target): {httpMethod} {endpoint}\ndate: {reqDate}\ndigest: SHA-256={digest}\nx-ing-reqid: {reqId}"""
        signature = __class__.sign(stringToSign)
        return signature

    def sign(stringToSign):
        with open (__class__.sign_key, 'r') as mykey:
            private_key = RSA.importKey(mykey.read())
            signer = PKCS1_v1_5.new(private_key)
            digest = SHA256.new()
            digest.update(stringToSign.encode())
            signingString = signer.sign(digest)
            signingString = b64encode(signingString).decode()
            return signingString


    def consume_api(httpMethod, endpoint, body="", access_token=None):
        reqId = str(uuid.uuid4())
        reqDate = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        cert = (__class__.tls_cert, __class__.tls_key)
        digest = __class__.calculate_digest(body)
        headers = {
                    "Date": reqDate,
                    "Digest": f"SHA-256={digest}",
                    "X-ING-ReqID": reqId,
                    "Authorization": f'Signature keyId="{__class__.client_id}",algorithm="rsa-sha256",headers="(request-target) date digest x-ing-reqid",signature="{__class__.calculate_signature(httpMethod.lower(), endpoint, reqDate, digest, reqId)}"',
                    }

        if access_token:
            headers.update({
                    "Authorization": f"Bearer {access_token}",
                    "Signature": f'keyId="{__class__.client_id}",algorithm="rsa-sha256",headers="(request-target) date digest x-ing-reqid",signature="{__class__.calculate_signature(httpMethod.lower(), endpoint, reqDate, digest, reqId)}"',
                    "Accept": "application/json"})
        else:
            headers.update({
                    "Content-Type": "application/x-www-form-urlencoded"})
        response = requests.request(httpMethod.upper(), __class__.reqPath+endpoint, headers=headers, data=body, cert=cert)
        return response

    def get_access_token():
        httpMethod = "POST"
        endpoint = "/oauth2/token"
        body = "grant_type=client_credentials&scope=greetings%3Aview"
        response = __class__.consume_api(httpMethod, endpoint, body)
        access_token =json.loads(response.content)['access_token']
        return access_token


    def showcase():
        access_token = __class__.get_access_token()
        httpMethod = "get"
        endpoint = "/greetings/single"
        response = __class__.consume_api(httpMethod, endpoint, access_token=access_token)
        #return response
        print(json.loads(response.content))
