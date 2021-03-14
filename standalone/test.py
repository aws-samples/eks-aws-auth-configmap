import boto3
import os
from aws_eks_k8s_client import get_daemonset_term_handler,apply_aws_auth_config_map,check_pods

ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
SESSION_TOKEN = os.environ['AWS_SESSION_TOKEN']
REGION = os.environ['AWS_DEFAULT_REGION']
#this sample uses AWS temporary credentials. if you are using permanent credentials, modify and remove session token variable
#modify this to use acces keys/secrets from vault/secret manager when integrating into build pipeline or application code.

#update this cluster name and roles to your specific ones
CLUSTER_NAME = 'DemoEKS'

#configure user/role for whom eks cluster permission has to be given. remember to have necessary EKS IAM permission for user configured already
CFG_MAP_USER_NAME = 'sukumar-test'
CFG_MAP_ROLE_NAME = ''
#EC2 instance role name
CLUSTER_ROLE_NAME = 'DemoEKS-NodeInstanceRole'

#function that returns aws session
def get_aws_session():
    aws_session = boto3.Session(
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        aws_session_token=SESSION_TOKEN,
        region_name=REGION
    )
    sts_client = aws_session.client('sts')
    print("in get_aws_session ... caller identity:::" + str(sts_client.get_caller_identity()))
    return aws_session

#test functions

#export/use IAM role/user who created EKS cluster(Cluster admin) and call apply_aws_auth_config_map()
#apply aws-auth ConfigMap
def test_apply_auth_config():
    session = get_aws_session()
    sts_client = session.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]

    apply_aws_auth_config_map(session,REGION,account_id,CLUSTER_NAME,CFG_MAP_USER_NAME, CFG_MAP_ROLE_NAME, CLUSTER_ROLE_NAME)
    print("applied- config")

#export/use IAM role/user for whom permission has been provided in apply_aws_auth_config_map(). (Cluster users)
#verify if daemonset is found in eks/k8s
def test_get_daemonset():
    session = get_aws_session()
    sts_client = session.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    result_dict = get_daemonset_term_handler(session,REGION,account_id,CLUSTER_NAME)
    print(result_dict)

#list pods
def test_get_pods():
    session = get_aws_session()
    sts_client = session.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    res = check_pods(session,REGION,account_id,CLUSTER_NAME)
    print("--pod listed---" + str(res))

#test_apply_auth_config()
#test_get_daemonset()
test_get_pods()
