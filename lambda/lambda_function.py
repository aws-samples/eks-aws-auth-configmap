#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT

import boto3
import os
from aws_eks_k8s_client import *

REGION = 'us-east-1'
#update this cluster name and roles to your specific ones
CLUSTER_NAME = 'DemoEKS'

#configure user/role for whom eks cluster permission has to be given. remember to have necessary EKS IAM permission for user configured already
CFG_MAP_USER_NAME = 'sukumar-test'
CFG_MAP_ROLE_NAME = 'eks-lambda-execution-role'
#EC2 instance role name
CLUSTER_ROLE_NAME = 'DemoEKS-NodeInstanceRole'

__author__ = "ssengott@"
#lambda to give eks cluster permission for mentioned user/role
def lambda_handler(event, context):

    aws_session = boto3.Session(region_name=REGION)
    sts_client = aws_session.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    print("account id=" + account_id)
    apply_aws_auth_config_map(aws_session, REGION, account_id, CLUSTER_NAME, CFG_MAP_USER_NAME, CFG_MAP_ROLE_NAME,
                              CLUSTER_ROLE_NAME)
    print("aws auth config applied for given role/user.")
