# CloudComputing_PA4

### K8_Deployment
This folder contains the necessary files for the Kubernetes deployment. It specifies the yaml files for the producer and consumers and the configurations for running them.

Inside of this folder: final_deployment contains the deployment files used to test our workload on our 4 VMs and large-cluster-deployment contains the files used on the larger Chameleon project. These primarily contain spark service and deployment files. 

We also have Dockerfile.spark which contains the dockerfile used to build the spark image located in our home directory. mapreduce.py is also located here and contains the logic for the mapreduce functionality of this assignment.
