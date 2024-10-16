# CloudComputing_PA2

### Scaffolding
The Scaffolding Folder contains the files necessary for the Ansible plays to set up and provision the VMs. It contains the master playbook which can be ran to create the VMs, install the necessary packages, and set the firewall rules. It contains all child playbooks and the structures necessary to provision the Vms.

### Logic
The Logic folder contains the enhanced producer logic in order to log response times. It contains details about adding an additional thread that behaves as a consumer to collect end-to-end response times that will help us determine impacts on latency as the number of producers is varied. These results are saved to files for plotting graphs to analyze latency depending on varied workloads.