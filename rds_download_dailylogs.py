# AWS Version 4 signing example for RDS DownloadComplete Log file
import sys, os, base64, datetime, hashlib, hmac, urllib
import requests # pip install requests

from boto3 import session


args = sys.argv
region = args[1]
instance_name = args[2]
logfile = args[3]

# use to get the hours 00-23 and download the entire day of logs.
hours = ["%.2d" % i for i in range(24)]

method = 'GET'
service = 'rds'

# Get session credentials

# local creds
# session = session.Session()
# cred = session.get_credentials()
# access_key = 'xxxxx'
# secret_key = 'xxxxxxx'
# # # access_key = os.environ.get('AWS_ACCESS_KEY_ID')
# # # secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
# session_token = cred.token

#EC2 Session
session = session.Session()
cred = session.get_credentials()
access_key = cred.access_key
secret_key = cred.secret_key
session_token = cred.token

def get_log_file_via_rest(filename, instance_name):
    # Key derivation functions. Taken from https://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(key, dateStamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'aws4_request')
        return kSigning



    if access_key is None or secret_key is None:
        print ("Credentials are not available.")
        sys.exit()

    # Create a date for headers and the credential string
    host = 'rds.' + region + '.amazonaws.com'
    rds_endpoint = 'https://' + host
    uri = '/v13/downloadCompleteLogFile/' + instance_name + '/' + filename
    endpoint = rds_endpoint + uri

    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ') # Format date as YYYYMMDD'T'HHMMSS'Z'
    datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    # Overview:
    # Create a canonical request - https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
    # Sign the request.
    # Attach headers.
    # Send request

    # Create canonical URI--the part of the URI from domain to query
    canonical_uri = uri

    # Create the canonical headers
    canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'
    # signed_headers is the list of headers that are being included as part of the signing process.
    signed_headers = 'host;x-amz-date'

    # Using recommended hashing algorithm SHA-256
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'

    # Canonical query string. All parameters are sent in http header instead in this example so leave this empty.
    canonical_querystring = ''

    # Create payload hash. For GET requests, the payload is an empty string ("").
    payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()

    # Create create canonical request
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

    # String to sign
    string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()


    # Create the signing key
    signing_key = getSignatureKey(secret_key, datestamp, region, service)

    # Sign the string_to_sign using the signing_key
    signature = hmac.new(signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256).hexdigest()

    # Add signed info to the header
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature='+ signature
    headers = {'Accept-Encoding':'gzip', 'x-amz-date':amzdate, 'x-amz-security-token':session_token, 'Authorization':authorization_header}

    # Send the request
    r = requests.get(endpoint, headers=headers, stream=True)

    print ("Logs Downloaded!")
    print ("Response Code: " + str(r.status_code))
    print ("Content-Encoding: " + r.headers['content-encoding'])

    # oname = str(filename)
    oname = args[4]
    # oname = (str(filename) + "-log")
    print (oname)
    # oname = input('Enter output file name (fullpath): ')
    # if os.path.exists(oname):
    #     append_write = 'a'
    # else:
    #     append_write = 'w'
    with open(oname, 'a') as f:
        for part in r.iter_content(chunk_size=8192, decode_unicode=True):
            f.write(str(part).replace(r'\n', '\n'))

    print ("Log file saved to " + oname)




# def get_log_file_via_rest(filename, db_instance_identifier):
for hour in hours:
    # print(logfile)
    filename = (logfile + f'-{hour}')
    print(filename)
    get_log_file_via_rest(filename, instance_name)