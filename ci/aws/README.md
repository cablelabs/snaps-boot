# snaps-kubernetes CI
Readme for information on running _snaps-boot_ CI

### Build Host Requirements

- Python installed
- Ansible has been installed into the Python runtime
- Download and install your binary for your platform from  https://www.terraform.io/downloads.html

### Setup and execute playbook _ci-main.yml_ on build host

```bash
terraform apply -var-file={snaps-config dir}/aws/snaps-ci.tfvars \
-auto-approve -var 'build_id={some unique value}'
```


### Cleanup
Should the script either fail or configued not to cleanup. Destruction of the
EC2 environment can be performed with the following command from this directory
```bash
terraform destroy -var-file={snaps-config dir}/aws/snaps-ci.tfvars \
-auto-approve -var 'build_id={some unique value}'
````
