# Ansible Configuration Management for Parallels VMs

Automate configuration of Parallels VMs using Ansible playbooks.

## Prerequisites

1. **Install Ansible**
   ```bash
   # macOS
   brew install ansible

   # Or via Python
   pip3 install ansible
   ```

2. **Install Windows Collections** (for Windows VMs)
   ```bash
   ansible-galaxy collection install community.windows
   ansible-galaxy collection install ansible.windows
   ```

3. **Configure WinRM** (Windows VMs)

   Windows VMs need WinRM enabled for Ansible. This is automatically configured by Packer templates, or run:

   ```powershell
   # In Windows VM
   winrm quickconfig
   winrm set winrm/config/service/auth '@{Basic="true"}'
   winrm set winrm/config/service '@{AllowUnencrypted="true"}'
   ```

## Quick Start

### 1. Test Connectivity

```bash
cd ansible

# Test connection to all VMs
ansible all -i inventory.yml -m ping

# Test specific VM
ansible windows_analytics -i inventory.yml -m win_ping
```

### 2. Run Configuration Playbook

```bash
# Configure Excel VM
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml

# Run specific tags only
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml --tags odbc

# Dry run (check mode)
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml --check
```

### 3. Verify Configuration

```bash
# Run test playbook
ansible-playbook -i inventory.yml playbooks/test-connection.yml
```

## Inventory Configuration

### Dynamic Inventory

The inventory uses dynamic lookups to get VM IP addresses:

```yaml
windows_analytics:
  ansible_host: "{{ lookup('pipe', 'prlctl list \"Windows-Analytics\" -o ip --no-header | tr -d \" \"') }}"
```

This automatically fetches the current IP from Parallels.

### Static Inventory

For stable IPs, you can hardcode:

```yaml
windows_analytics:
  ansible_host: 192.168.1.100
```

### Multiple VMs

Add more VMs to inventory:

```yaml
windows_vms:
  hosts:
    windows_analytics:
      ansible_host: 192.168.1.100
    windows_test:
      ansible_host: 192.168.1.101
    project_alpha:
      ansible_host: 192.168.1.102
```

## Playbooks

### configure-excel-vm.yml

Complete VM configuration:
- Install ODBC drivers
- Configure ODBC DSNs
- Create directories
- Install development tools
- Configure Windows settings

```bash
# Full configuration
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml

# Only ODBC setup
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml --tags odbc

# Only tools installation
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml --tags tools
```

### test-connection.yml

Test connectivity and gather system info:

```bash
ansible-playbook -i inventory.yml playbooks/test-connection.yml
```

## Variables

### Group Variables

Edit `group_vars/windows_vms.yml`:

```yaml
database_connections:
  metabase:
    host: db.company.com
    port: 5432
    database: metabase
    username: analytics

dev_tools:
  - git
  - python
  - your-custom-tool
```

### Environment Variables

Use environment variables for sensitive data:

```bash
export METABASE_HOST=db.company.com
export METABASE_USER=analytics
export METABASE_PASSWORD=secret

ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml
```

### Vault for Secrets

```bash
# Create encrypted vault
ansible-vault create group_vars/secrets.yml

# Add sensitive variables
# database_password: secret123

# Run with vault
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml --ask-vault-pass
```

## Common Tasks

### Install Software

```yaml
- name: Install software via Chocolatey
  win_chocolatey:
    name: firefox
    state: present
```

### Configure ODBC DSN

```yaml
- name: Configure ODBC DSN
  community.windows.win_odbc_dsn:
    name: MyDatabase
    driver: PostgreSQL Unicode(x64)
    dsn_type: system
    attribute_dict:
      Server: db.example.com
      Port: 5432
      Database: mydb
```

### Execute PowerShell

```yaml
- name: Run PowerShell script
  win_shell: |
    Write-Host "Hello from Ansible!"
    Get-Service | Where-Object {$_.Status -eq 'Running'}
```

### Copy Files

```yaml
- name: Copy Excel template
  win_copy:
    src: files/Template.xlsx
    dest: C:\Analytics\Template.xlsx
```

## Integration with Other Tools

### With Terraform

```bash
# 1. Create VMs with Terraform
terraform apply

# 2. Get VM IPs (automatic via dynamic inventory)
# 3. Configure with Ansible
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml
```

### With Packer

```bash
# 1. Build golden image with Packer
packer build packer/windows-excel/

# 2. Create VMs from golden image
terraform apply

# 3. Post-configuration with Ansible
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml
```

## Example Workflows

### Workflow 1: New VM Setup

```bash
# 1. Create VM with Terraform
cd terraform
terraform apply

# 2. Wait for VM to boot
sleep 60

# 3. Test connectivity
cd ../ansible
ansible windows_analytics -i inventory.yml -m win_ping

# 4. Configure VM
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml

# 5. Verify
ansible-playbook -i inventory.yml playbooks/test-connection.yml
```

### Workflow 2: Update All VMs

```bash
# Update ODBC configuration on all Windows VMs
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml --tags odbc

# Update development tools
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml --tags tools
```

### Workflow 3: Disaster Recovery

```bash
# 1. Recreate VM from Terraform
terraform destroy -target=parallels_vm.excel_analytics
terraform apply

# 2. Reconfigure with Ansible
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml

# Everything back to normal!
```

## Troubleshooting

### Connection Issues

```bash
# Check if VM is running
prlctl list -a

# Check IP address
prlctl list "Windows-Analytics" -o ip

# Test WinRM manually
Test-WSMan -ComputerName <IP>  # From Windows
```

### Authentication Issues

```yaml
# Try different WinRM transport
ansible_winrm_transport: ntlm  # or kerberos, credssp
```

### Verbose Output

```bash
# Increase verbosity
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml -vvv
```

## Best Practices

1. **Use Tags**: Tag tasks for selective execution
2. **Idempotency**: Playbooks should be safe to run multiple times
3. **Variables**: Use variables for configurable values
4. **Vault**: Encrypt sensitive data
5. **Version Control**: Commit playbooks to Git
6. **Testing**: Use `--check` mode before applying
7. **Documentation**: Comment complex tasks

## Advanced: Custom Roles

Create reusable roles:

```bash
# Create role structure
ansible-galaxy init roles/excel_analytics

# Use in playbook
- hosts: windows_vms
  roles:
    - excel_analytics
```

## Resources

- [Ansible Windows Guide](https://docs.ansible.com/ansible/latest/os_guide/windows.html)
- [Community Windows Collection](https://docs.ansible.com/ansible/latest/collections/community/windows/index.html)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
