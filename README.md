[//]: # (Repo name: eks-aws-auth-configmap)

# Amazon Elastic Kubernetes Service eks-aws-auth-configmap-api
This package provides code(api/programmatic way) for
* Applying aws-auth ConfigMap in Amazon EKS (Programmatic Amazon EKS Cluster permission for IAM User/Role)
* Access Kubernetes Objects like list pods and read daemonset (accessing/updating Kubernetes objects through Kubernetes client api)

Code can be run without installing or depending on aws commnd line interface (cli) and kubectl cli. Code uses AWS SDK for Python (Boto3), AWS Security Token Service API and Kubernetes(k8s) API to achieve this.

##Scenario:
For security reasons, when you create an Amazon EKS cluster, only the IAM entity user or role, such as a federated user that creates the cluster, is granted permissions in the cluster's RBAC configuration in the control plane. User or role that created cluster has to login through kubectl to provide cluster access to additional users/roles.

###Issue:
For automation like build pipeline or infrastructure as code, there is a dependency on kubectl, aws cli to apply aws auth ConfigMap. Also for a scenario where we need to standup large number of EKS clusters for training/learning purpose or for DR automation one has to automate with dependency on kubectl cli.

###Approach to solve the problem/used in this sample:
 Create custom http request/api that generates token/sts signed url for EKS and generating kubeconfig in temporary folder. This way, automation can be done in lambda or any other automation tools/application without need to have CLI dependency or invoking through command line interface.

### Use Cases where this can be used
* Automation for providing Amazon EKS Cluster permission and this can be extended to event based user/role permission addition or removal.
* Access/manage Amazon EKS Cluster & K8s Objects from AWS Lambda without doing workaround for installing Kubectl, aws cli
* Scenario where EKS cluster will be provisioned through api/automation/build pipeline and providing permission to predefined users/roles

[//]: # (Infrastructure as Code Automation & CI/CD)

###Code Flow
Refer standalone/test.py file for available functions & its flow. Read function comments.

###Installation & Run

####Standalone python
Pre requisites:

&nbsp;&nbsp;Python 3.7

&nbsp;&nbsp;pip3

Installation:

&nbsp;&nbsp;cd standalone

&nbsp;&nbsp;pip3 install -r requirements.txt

Configuration:

* Export aws access keys and secret access keys as env variable (for standalone test)
* Update cluster name and user/role variables value in test.py

####Attention! 
For demo purpose, access key and secret access keys are exported as environment variables in this sample. Folow security best practice to read access key and secret access keys from secrets manager or from vault when integrating into build pipeline or application code.

Run:

&nbsp;&nbsp;python3 test.py



####AWS Lambda
Pre requisites:

* Create Lambda function through AWS Console or from command line
* Assign required EKS permission for Lambda execution role  
* Run standalone code(refer previous section) or manually create/edit EKS aws auth ConfigMap to provide permission for the Lambda execution role
* Update cluster name and user/role variables value in Lambda Code (lambda/lambda_function.py)
    
Packaging steps:

* cd lambda/package
* run package.sh to create zip file
* upload Lambda zip file to s3 bucket (optional)
* upload/update Lambda source code from s3 or upload generated zip file
* &nbsp;&nbsp;Note: increase default timeout for Lambda function if needed.
* Test created Lambda function

####Note:

* In this sample code, compatible versions of k8s client api's are used. If you change version, then test it before using it
* This works for both role based login or user based login
* This can be extended to add/remove users based on event.
* Use layers in Lambda if you want to re-use or reduce size of Lambda function/zip file

###References
https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html

###FAQ
* Why this sample has both aws auth config map and k8s api in same package?
    * To access k8s through api, you always need auth config setup. So, both samples are clubbed together to help end to end flow.
* Every time when I run this example, it overwrites aws auth ConfigMap. why?
    * This sample code is to demonstrate how aws auth ConfigMap can be applied programmatically. Please modify code based on your requirement.
* When I run Lambda function, I get 'error: You must be logged in to the server (Unauthorized)'?
    * When you create an Amazon EKS cluster, the IAM entity user or role, such as a federated user that creates the cluster, is automatically granted system:masters permissions in the cluster's RBAC configuration in the control plane. So, for Lambda execution role make sure to provide EKS Cluster permission by either running standalone program or manually editing auth ConfigMap.
    
## License

This library is licensed under the MIT-0 License. See the LICENSE file.
