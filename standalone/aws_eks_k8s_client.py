#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT

from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.client.api import apps_v1_api


from sts_token import get_token
from kube_config import create_kube_config_file_for_eks, get_configuration
from aws_auth_config import construct_configmap_object,apply_configmap
#import os,sys
#sys.path.append(os.path.join(os.path.dirname(__file__)))

__author__ = "ssengott@"
#main file with functions to access...

def get_k8s_api_client(session, region, account_id, cluster_name):
    token = get_token(session,region, cluster_name)
    #print("\n\ntoken:   "+token)
    #print("\n\n   ")
    create_kube_config_file_for_eks(session,region,account_id,cluster_name)

    configuration = get_configuration(account_id)
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.api_key['authorization'] = token

    api_client = client.ApiClient(configuration)

    return api_client

def apply_aws_auth_config_map(session,region,account_id, cluster_name,cfg_map_user_name, cfg_map_role_name, cluster_role_name):

    api_client = get_k8s_api_client(session,region,account_id, cluster_name)
    v1 = client.CoreV1Api(api_client)

    print("accessing k8s api through client:   " )
    # Get all the pods
    #res = v1.list_namespaced_pod("default")
    #print("pods ="+str(res))

    #list existing config maps in kube-system namespace
    #config_map_read = v1.list_namespaced_config_map(namespace="kube-system")
    #print("\n\nget config map:" + str(config_map_read))

    configmapObj = construct_configmap_object(account_id,cfg_map_user_name, cfg_map_role_name, cluster_role_name)
    #print("\n***************")
    print("\n aws auth configMap:" + str(configmapObj))
    apply_configmap(v1, configmapObj)
    print("\nConfig map created...")

#ds_id = "aws-node-termination-handler"
#def get_daemon_set_term_handler(session,region,account_id,ds_id="aws-test"):
def get_daemonset_term_handler(session,region,account_id, cluster_name, ds_id="aws-node-termination-handler") -> dict:
    api_client = get_k8s_api_client(session,region,account_id, cluster_name)
    api_apps = apps_v1_api.AppsV1Api(api_client)

    result_dict = {'term_handler_available':'NO', 'node_selector_spot':'NO'}

    print("get daemonset - accessing k8s api through client:   " )
    #print("type=" + str(type(api_apps.read_namespaced_daemon_set("aws-node", 'kube-system'))))
    #ds_id = "aws-node"
    try:
        resp = api_apps.read_namespaced_daemon_set(ds_id, 'kube-system')
        result_dict['term_handler_available']='YES'

        # get node selector. assign points if it is lifecycle=Ec2Spot
        node_selector = resp.spec.template.spec.node_selector
        print("Node selector:" + str(node_selector))
        if node_selector == "lifecycle=Ec2Spot":
            result_dict['node_selector_spot'] = 'YES'
    except ApiException as ex:
        print("ApiException:"+ str(ex.reason))
        print("ApiException:" + str(ex))
        #assign negative points if node termination handler has not be deployed.
    except Exception as excp:
        result_dict['term_handler_available'] = 'EXCEPTION'
        print("Exception:" + str(excp))
    return result_dict


def check_pods(session,region,account_id, cluster_name, pod_name_prefix="batch-app") -> dict:
    api_client = get_k8s_api_client(session,region,account_id, cluster_name)
    v1 = client.CoreV1Api(api_client)

    result_dict = {'found_pod':'NO'}

    print("get_pods - accessing k8s api through client:   " )
    try:
        print("Listing pods with their IPs:")
        ret = v1.list_namespaced_pod(namespace='default')
        for pod in ret.items:
            if  pod.metadata.name.startswith(pod_name_prefix):
                result_dict['found_pod'] = 'YES'
                print("found pod: %s\t%s\t%s" % (pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name))
                break

    except ApiException as ex:
        print("ApiException:"+ str(ex.reason))
        print("ApiException:" + str(ex))
        #assign negative points if node termination handler has not be deployed.
    except Exception as excp:
        result_dict['found_pod'] = 'EXCEPTION'
        print("Exception:" + str(excp))
    return result_dict

