# snaps-boot CI
Readme for information on running _snaps-boot_ CI

## Build Host Requirements
- Python installed

- Ansible has been installed into the Python runtime

- Download and install Terraform from <https://www.terraform.io/downloads.html>

- Download and install Azure command line client

  - az login (for now until we get shared credentials) 

## Setup bare metal host on AWS and execute deployment from the build host
Run the following bash command from this directory:
```bash
export TF_CLI_CONFIG_FILE="{snaps-config dir}/aws/terraform_rc"
terraform init
terraform apply -auto-approve \
-var-file='{snaps-common dir}/ci/snaps-boot-env/boot-env.tfvars' \
-var build_id={some unique readable value}
```

## Cleanup
Always perform cleanup after completion by running the following command from this directory:
```bash
terraform destroy -auto-approve \
-var-file='{snaps-common dir}/ci/snaps-boot-env/boot-env.tfvars' \
-var build_id={some unique readable value}
```