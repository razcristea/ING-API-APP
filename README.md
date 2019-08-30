# ING-API-APP 
<p align="center">
  <img src="https://img.shields.io/badge/tutorial-API-orange?style=plastic"/> <img src="https://img.shields.io/badge/made%20with-Python-blue?style=plastic&logo=python&logoColor=white"/></p>


## About
#### ING Bank - Developer Portal - consume API using Python
This is a python implementation of the ING instructions for consuming their API. Consuming Showcase API is the first step into understanding the OAuth flow so you can afterwards build a custom solution based on consuming other APIs released by ING.

## Requirements

First of all, you should follow steps from 1 to 4 from https://developer.ing.com/openbanking/get-started and subscribe to Showcase API.

After those first 4 steps, you should have certificate and key pairs for both TLS and HTTPS request signing, and the client id. Mind the path and the id, as you will need to replace `tls_cert`, `tls_key`, `sign_key` and `client_id` defined inside the class model.

From step 5, things are beginning to get interesting, as we are gonna use Python instead of curl as described in the tutorial. 

I recommend creating a virtual environment using `virtualenv venv` because you will need to install some new modules as described in `requirements.txt`

## From curl to python

Inside `__init.py__` we are going to define a class of `requests.Session()` object and start by naming some variables that will contain the path to our certificate and keys, as well as our client_id from the application overview. - the application you created on ING developer portal. As for URL, I opted for using the production one - `https://api.ing.com` but you are free to use the sandbox.

The curl instruction to generate date using is the following: 
```
reqDate=`LC_TIME=en_US.UTF-8 date -u "+%a, %d %b %Y %H:%M:%S GMT"` 
```
as the date has to look like this: `2019-08-28 11:22:42 GMT`
I am going to define a variable named also `reqDate` inside the `consume_api()` function, so it matches the requested format:
```
reqDate = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
```
Our class main functions are going to be `get_access_token()` and `showcase()`. Both of them hold own HTTP method stored in `httpMethod` variable, own endpoint, and both of them are returning the result of calling the class function (mind the way it is called: `__class__.consume_api()`) that handles both of the requests.

## get_access_token()

Calling this function is the equivalent of this curl command:
```
curl -X POST --cert yourTLSCertPath/tls.cert --key yourTLSKeyPath/tls.key 
-H Date: $reqDate 
-H Digest: SHA-256=2ajR8Q+lBNm0eQW9DWWX8dZDZLB8+h0Rgmu0UCDdFrw= 
-H Authorization: Signature keyId=$clientId,algorithm="rsa-sha256",headers="(request-target) date digest x-ing-reqid",signature=$signature 
-H Content-Type: application/x-www-form-urlencoded 
-d grant_type=client_credentials&scope=greetings%3Aview https://api.ing.com/oauth2/token
```

This function is making a POST request to `http://api.ing.com/oauth2/token`, with the following body (data): `grant_type=client_credentials&scope=greetings%3Aview` and carrying those headers:
```
headers = {
                    "Date": reqDate,
                    "Digest": f"SHA-256={digest}",
                    "X-ING-ReqID": reqId,
                    "Authorization": f'Signature keyId="{__class__.client_id}",algorithm="rsa-sha256",headers="(request-target) date digest x-ing-reqid",signature="{__class__.calculate_signature(httpMethod.lower(), endpoint, reqDate, digest, reqId)}"',
                    "Content-Type": "application/x-www-form-urlencoded"
           }
```
where the date is generated as stated above, the digest is the result of hashing the body by calling `calculate_digest()` function.
`reqId` variable is taking a random UUID generated using uuid4 and converted into string: `reqId = str(uuid.uuid4())`
Authorization header contains the signature generated using `calculate_signature()`. What this function does is taking the string containing the HTTP method, the endpoint, date, digest and `reqId`: 
```
(request-target): {httpMethod} {endpoint}\ndate: {reqDate}\ndigest: SHA-256={digest}\nx-ing-reqid: {reqId}
```
each on its own line (!) and gets signed - with the X.509 HTTPS signing key uploaded to ING portal - using `sign()` function.

The request also contains also the certificate and the key passed as a tuple to variable `cert`.

*Note that both class variables and functions defined inside the class that are called inside other functions are called using __class__ method!*


## showcase()

Last but not least, the `showcase()` function gets called, and this function does is described in ING developer portal with this curl request: 
```
curl -i -X GET --cert yourTLSCertPath/tls.cert --key yourTLSKeyPath/tls.key 
-H Date: $reqDate 
-H Digest: SHA-256=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU= 
-H Authorization: Bearer $theAccessTokenFromThePreviousRequest 
-H Signature: keyId=$clientId,algorithm="rsa-sha256",headers="(request-target) date digest",signature=$signature 
-H Accept: application/json 
https://api.ing.com/greetings/single
```
When calling the showcase function, first we make shure that we have the access token from `get_access_token()`, and we make a GET request to `/greetings/single` endpoint, while carrying almost the same headers, except now the __Authorization__ header has the access token and we have a  __Signature__ header that holds the signature:
```
headers = {
                    "Date": reqDate,
                    "Digest": f"SHA-256={digest}",
                    "X-ING-ReqID": reqId,
                    "Authorization": f"Bearer {access_token}",
                    "Signature": f'keyId="{__class__.client_id}",algorithm="rsa-sha256",headers="(request-target) date digest x-ing-reqid",signature="{__class__.calculate_signature(httpMethod.lower(), endpoint, reqDate, digest, reqId)}"',
                    "Accept": "application/json"
          }

```

The result of calling this function should be (if everything went ok) `<Response [200]>` and according to the documentation it is a JSON object that returns this output when called using `INGapp.showcase()` :
```
{'message': 'Welcome to ING!', 'id': '53f9ef86-8b37-4d10-b3e9-c44f171bbc3c', 'messageTimestamp': '2019-08-28 11:22:42 GMT'}
```
You can retrieve only the content of 'message' by using `INGapp.showcase()['message']`
and this is going to output only *Welcome to ING!*




