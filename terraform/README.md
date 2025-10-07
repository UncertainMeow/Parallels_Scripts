# Terraform for Parallels VM Management

Manage Parallels Desktop VMs declaratively using Infrastructure as Code.

## Prerequisites

1. **Install Terraform**
   ```bash
   brew install terraform
   ```

2. **Install Parallels Terraform Provider**
   The provider will be installed automatically when you run `terraform init`.

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Configure Variables

```bash
# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your settings
nano terraform.tfvars
```

### 3. Plan Changes

```bash
# See what will be created
terraform plan
```

### 4. Apply Configuration

```bash
# Create VMs
terraform apply

# Auto-approve (skip confirmation)
terraform apply -auto-approve
```

### 5. Manage VMs

```bash
# Show current state
terraform show

# List resources
terraform state list

# Get outputs
terraform output

# Destroy VMs
terraform destroy
```

## Configuration Examples

### Basic: Single Analytics VM

```hcl
# terraform.tfvars
vm_name         = "Windows-Analytics"
base_image_name = "Windows-Analytics-Golden"
vm_cpus         = 4
vm_memory       = 8192
```

```bash
terraform apply
```

### With Test Environment

```hcl
vm_name        = "Windows-Analytics-Prod"
create_test_vm = true
```

This creates:
- `Windows-Analytics-Prod` (full resources)
- `Windows-Analytics-Prod-Test` (half resources)

### Multiple Project VMs

```hcl
project_vms = {
  project_alpha = {
    name          = "Analytics-ProjectAlpha"
    description   = "Excel analytics for Project Alpha"
    cpus          = 4
    memory        = 8192
    data_path     = "~/Projects/Alpha/Data"
    start_on_boot = false
  }
  project_beta = {
    name          = "Analytics-ProjectBeta"
    description   = "Excel analytics for Project Beta"
    cpus          = 2
    memory        = 4096
    data_path     = "~/Projects/Beta/Data"
    start_on_boot = false
  }
}
```

## Common Workflows

### Workflow 1: Create Production VM from Golden Image

```bash
# 1. Create golden image with Packer
cd ../packer/windows-excel
packer build .

# 2. Use Terraform to create production VM
cd ../../terraform
terraform apply
```

### Workflow 2: Clone for Testing

```bash
# Enable test VM
echo 'create_test_vm = true' >> terraform.tfvars

terraform apply

# Test your changes in test VM
# If good, update production
```

### Workflow 3: Scale Up/Down

```bash
# Edit resources
nano terraform.tfvars
# Change: vm_memory = 16384  (16 GB)

# Apply changes (will resize VM)
terraform apply
```

### Workflow 4: Manage Multiple Projects

```bash
# Add project in terraform.tfvars
# Then apply
terraform apply

# Remove project
terraform destroy -target=parallels_vm.project_vms[\"project_alpha\"]
```

## Resource Management

### Update VM Resources

Terraform can update some properties without recreating the VM:
- Memory (cpus, memory)
- Network settings
- Shared folders

Changes that require recreation:
- Base image
- VM name

### Start/Stop VMs

Terraform doesn't manage VM power state directly. Use `prlctl`:

```bash
# Get VM name from Terraform
VM_NAME=$(terraform output -raw analytics_vm_name)

# Start VM
prlctl start "$VM_NAME"

# Stop VM
prlctl stop "$VM_NAME"

# Or use our vm-manager script
../scripts/vm-manager.sh start "$VM_NAME"
```

## State Management

### Local State (Default)

State is stored in `terraform.tfstate`. Keep this file safe!

```bash
# Backup state
cp terraform.tfstate terraform.tfstate.backup

# View state
terraform show
```

### Remote State (Recommended for Teams)

Store state in Git (encrypted) or remote backend:

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "parallels-vms/terraform.tfstate"
    region = "us-west-2"
  }
}
```

## Outputs

```bash
# Get all outputs
terraform output

# Get specific output
terraform output analytics_vm_name
terraform output analytics_vm_ip

# Use in scripts
VM_IP=$(terraform output -raw analytics_vm_ip)
echo "VM IP: $VM_IP"
```

## Integration with Other Tools

### With Ansible

```bash
# Get VM IP for Ansible inventory
terraform output -json | jq -r '.analytics_vm_ip.value'

# Or use Terraform inventory plugin
```

### With Packer

```bash
# Build golden image
cd ../packer/windows-excel
packer build .

# Create VMs from image
cd ../../terraform
terraform apply
```

### With Python Automation

```python
import subprocess
import json

# Get Terraform outputs
result = subprocess.run(
    ["terraform", "output", "-json"],
    capture_output=True,
    text=True,
    cwd="terraform"
)

outputs = json.loads(result.stdout)
vm_name = outputs["analytics_vm_name"]["value"]

# Use with Python automation
from excel_automation import VMManager
vm = VMManager(vm_name)
vm.start()
```

## Troubleshooting

### Provider Not Found

```bash
terraform init
terraform providers
```

### VM Already Exists

```bash
# Import existing VM
terraform import parallels_vm.excel_analytics "VM-Name"
```

### State Out of Sync

```bash
# Refresh state
terraform refresh

# Force recreation
terraform taint parallels_vm.excel_analytics
terraform apply
```

## Best Practices

1. **Version Control**: Commit `.tf` files, `.gitignore` state files
2. **Golden Images**: Always use golden images (via Packer)
3. **Test First**: Create test VM before touching production
4. **Snapshot Before Changes**: `prlctl snapshot` before `terraform apply`
5. **Modular**: Use workspaces or separate directories for different environments

## Advanced: Workspaces

Manage multiple environments:

```bash
# Create workspaces
terraform workspace new dev
terraform workspace new prod

# Switch workspace
terraform workspace select prod

# Apply (creates prod-specific resources)
terraform apply

# List workspaces
terraform workspace list
```

## Example: Complete Flow

```bash
# 1. Build golden image (monthly)
cd packer/windows-excel
packer build -var-file=variables.pkrvars.hcl .

# 2. Create production VM
cd ../../terraform
terraform apply

# 3. Get VM details
VM_NAME=$(terraform output -raw analytics_vm_name)
VM_IP=$(terraform output -raw analytics_vm_ip)

echo "VM Created: $VM_NAME"
echo "IP Address: $VM_IP"

# 4. Start VM
prlctl start "$VM_NAME"

# 5. Configure ODBC (using Python CLI)
cd ..
source python/venv/bin/activate
excel-auto odbc configure "$VM_NAME" --connection metabase_prod

# 6. Done!
echo "✓ Infrastructure deployed"
```

## Resources

- [Terraform Parallels Provider](https://registry.terraform.io/providers/Parallels/parallels/latest)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Parallels CLI Reference](https://docs.parallels.com/parallels-desktop-developers-guide/command-line-interface-utility)
