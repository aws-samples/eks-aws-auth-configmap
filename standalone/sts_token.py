#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT

from botocore.signers import RequestSigner
import base64


#create region specific STS url
STS_END_POINT_PREFIX = 'sts.'
STS_END_POINT_SUFFIX = '.amazonaws.com'
#STS_END_POINT = 'sts.amazonaws.com'
#STS_END_POINT = 'sts.us-west-2.amazonaws.com'

AUTH_SERVICE = "sts"
AUTH_COMMAND = "GetCallerIdentity"
AUTH_API_VERSION = "2011-06-15"
AUTH_SIGNING_VERSION = "v4"
STS_ACTION = 'Action=' + AUTH_COMMAND + '&Version=' + AUTH_API_VERSION
#STS_ACTION = 'Action=GetCallerIdentity&Version=2011-06-15'

# Presigned url timeout in seconds
URL_TIMEOUT = 60

TOKEN_PREFIX = 'k8s-aws-v1.'
CLUSTER_NAME_HEADER = 'x-k8s-aws-id'


def get_token(session, region, cluster_name):
    sts_client = session.client(AUTH_SERVICE, region_name=region)
    # print("caller identity --->" + str (sts_client.get_caller_identity()))
    service_id = sts_client.meta.service_model.service_id

    signer = RequestSigner(
        service_id,
        session.region_name,
        AUTH_SERVICE,
        AUTH_SIGNING_VERSION,
        session.get_credentials(),
        session.events
    )
    sts_end_point = STS_END_POINT_PREFIX + region + STS_END_POINT_SUFFIX
    print("sts end point=" + sts_end_point)
    # print("\n\n Signer= "+str(signer))
    params = {
        'method': 'GET',
        'url': 'https://' + sts_end_point + '/?' + STS_ACTION,
        'body': {},
        'headers': {
            CLUSTER_NAME_HEADER: cluster_name
        },
        'context': {}
    }
    # print("\n\n params= " + str(params))

    signed_url = signer.generate_presigned_url(
        params,
        region_name=session.region_name,
        expires_in=URL_TIMEOUT,
        operation_name=''
    )
    #print("signed url:  " + signed_url)

    k8s_token = TOKEN_PREFIX + base64.urlsafe_b64encode(
        signed_url.encode('utf-8')).decode('utf-8').rstrip('=')

    #print("k8s_token:  " + k8s_token)

    return k8s_token

