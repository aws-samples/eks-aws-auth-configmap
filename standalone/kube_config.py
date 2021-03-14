#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT

import yaml
import sys
from kubernetes import client, config


KUBE_CFG_FILEPATH = '/tmp/kubeconfig'

def create_kube_config_file_for_eks(session,region,account_id, cluster_name):

    #get eks cluster details for creating kubeconfig content
    eks_api = session.client('eks', region_name=region)
    cluster_info = eks_api.describe_cluster(name=cluster_name)

    print("*** eks cluster info::" + str(cluster_info))

    certificate = cluster_info['cluster']['certificateAuthority']['data']
    endpoint = cluster_info['cluster']['endpoint']

    print("eks cluster endpoint=    " + endpoint)

    #generate kubeconfig
    kube_cfg_content = dict()

    kube_cfg_content['apiVersion'] = 'v1'
    kube_cfg_content['clusters'] = [
        {
            'cluster':
                {
                    'server': endpoint,
                    'certificate-authority-data': certificate
                },
            'name':'kubernetes'

        }]

    kube_cfg_content['contexts'] = [
        {
            'context':
                {
                    'cluster':'kubernetes',
                    'user':'aws'
                },
            'name':'aws'
        }]

    kube_cfg_content['current-context'] = 'aws'
    kube_cfg_content['Kind'] = 'config'
    kube_cfg_content['users'] = [
        {
            'name':'aws',
            'user':{'name': 'lambda'}
        }]
    # {'name': 'lambda'}
    # 'user' value in 'users' content above should be key value {'name': 'lambda'} for k8s client version > 9. for version 9, just have {'user': 'lambda'}
    #print("kube config content:    " + str(kube_cfg_content))

    #Write to kubeconfig file
    try:
        with open(KUBE_CFG_FILEPATH + "_" + account_id, 'w') as outfile:
            yaml.dump(kube_cfg_content, outfile, default_flow_style=False)
            print("completed creating kube config file.")
    except OSError as err:
        print("OS error: {0}".format(err))
        raise err
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    #file_o = open(KUBE_CFG_FILEPATH + "_" + account_id)
    #content = file_o.read()
    #print("*** kube config file from /tmp/kubeconfig_<account_id>::")
    #print(content)
    #file_o.close()

def get_configuration(account_id):
    #k8s client call with api token to update aws-auth configmap
    config.load_kube_config(KUBE_CFG_FILEPATH + "_" + account_id)
    configuration = client.Configuration()
    #print("Client kube config host/server:"+ str(configuration.host))
    return  configuration
