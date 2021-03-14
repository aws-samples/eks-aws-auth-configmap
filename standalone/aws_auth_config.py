#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT

from kubernetes import client
from pprint import pprint
from kubernetes.client.rest import ApiException

# code to provide EKS Cluster permission for IAM role and user

__author__ = "ssengott@"
CFG_MAP_API_VERSION = 'v1'

#This function assumes that you have default setup in cluster (without aws-auth ConfigMap)
#if you have existing configuration, update this function to reflect those
#this function provide access to one role or user or both
def construct_configmap_object(account_id,cfg_map_user_name, cfg_map_role_name, cluster_role_name):
    cfg_metadata = client.V1ObjectMeta( name="aws-auth",namespace="kube-system")

    #{
    #    'mapRoles': '- rolearn: arn:aws:iam::<account_id>:role/DemoEKS-NodeInstanceRole\n  username: system:node:{{EC2PrivateDNSName}}\n  groups:\n    - system:bootstrappers\n    - system:nodes\n\n- rolearn: arn:aws:iam::<account_id>:role/TeamRole\n  username: TeamRole\n  groups:\n  - system:masters\n',
    #    'mapUsers': '- userarn: arn:aws:iam::<account_id>:user/sukumar\n  username: sukumar\n  groups:\n    - system:masters\n'
    #}

    #prepare role arn
    #arn:aws:iam::<account_id>:role/EKS-NodeInstanceRole
    node_role_arn = 'arn:aws:iam::' + account_id + ':role/' + cluster_role_name
    map_role_txt = '- rolearn: ' + node_role_arn + '\n  username: system:node:{{EC2PrivateDNSName}}\n  groups:\n    - system:bootstrappers\n    - system:nodes\n'

    if cfg_map_role_name != '':
        # arn:aws:iam::<account_id>:role/TeamRole
        iam_role_arn = 'arn:aws:iam::' + account_id + ':role/' + cfg_map_role_name
        map_role_txt = map_role_txt + '- rolearn: ' + iam_role_arn + '\n  username: ' + cfg_map_role_name + '\n  groups:\n  - system:masters\n'

    #prepare user arn
    user_arn = ''
    if cfg_map_user_name != '':
        #arn:aws:iam::<account_id>:user/sukumar-test
        user_arn = 'arn:aws:iam::' + account_id + ':user/' + cfg_map_user_name

    if user_arn != '':
        map_user_txt = '- userarn: ' + user_arn +'\n  username: ' + cfg_map_user_name + '\n  groups:\n    - system:masters\n'
        cfg_data = {
            'mapRoles': map_role_txt,
            'mapUsers': map_user_txt
        }
    else:
        cfg_data= {
            'mapRoles': map_role_txt
        }

    #print("AWS auth-cfg Config data:\n\n")
    #print(cfg_data)
    #Config data**\n\n")

    #TODO. add IAM group, once support is added in EKS. refer enhancement request in container roadmap.

    configmap = client.V1ConfigMap(
        api_version=CFG_MAP_API_VERSION,
        kind="ConfigMap",
        metadata=cfg_metadata,
        data=cfg_data
    )
    return configmap


def apply_configmap(client_api_instance, configmap):
    try:
        api_response = client_api_instance.create_namespaced_config_map(
            namespace="kube-system",
            body=configmap,
            pretty = 'simple_example',
        )
        pprint(api_response)

    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_config_map: %s\n" % e)
        raise
