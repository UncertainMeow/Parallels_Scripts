# Packer Template: Windows + Excel + SQL Clients

Create a golden image Windows VM with Excel and database tools pre-installed.

## Prerequisites

1. **Install Packer**
   ```bash
   brew install packer
   ```

2. **Install Parallels Packer Plugin**
   ```bash
   packer plugins install github.com/Parallels/parallels
   ```

3. **Get Windows ISO**
   - Download Windows 11 ISO from Microsoft
   - Place in: `~/Downloads/Win11.iso`

4. **Get Office Installer** (optional for full automation)
   - Download Office installer or use Office 365 web installer

## What This Template Creates

A Windows VM with:
- ✓ Windows 11 Pro
- ✓ Latest Windows updates
- ✓ Microsoft Office (Excel, Word, PowerPoint)
- ✓ PostgreSQL ODBC driver
- ✓ MySQL ODBC driver
- ✓ SQL Server ODBC driver
- ✓ DBeaver (universal SQL client)
- ✓ Python 3.x (for automation scripts)
- ✓ PowerShell configured
- ✓ Network optimized for Parallels
- ✓ Shared folders enabled
- ✓ Your custom ODBC DSNs

## Files

```
packer/windows-excel/
├── README.md                 (this file)
├── windows-excel.pkr.hcl     (Packer template - HCL format)
├── scripts/
│   ├── install-office.ps1    (Office installation)
│   ├── install-odbc.ps1      (ODBC drivers)
│   ├── install-tools.ps1     (DBeaver, Python, etc)
│   └── configure-dsns.ps1    (Pre-configure database connections)
├── files/
│   └── odbc-config.json      (Your database connection details)
└── autounattend.xml          (Windows unattended install)
```

## Usage

### 1. Configure Variables
Edit `variables.auto.pkrvars.hcl`:
```hcl
# Your settings
metabase_host = "192.168.1.100"
metabase_user = "analytics"
metabase_db = "metabase"

vm_name = "Windows-Analytics-Golden"
vm_memory = "8192"
vm_cpus = "4"
```

### 2. Build Golden Image
```bash
cd packer/windows-excel/
packer build .
```

This takes ~30-45 minutes:
- Install Windows (10 min)
- Install updates (10 min)
- Install Office (10 min)
- Install ODBC/tools (5 min)
- Configure settings (5 min)

### 3. Use the Golden Image
```bash
# Clone from golden image
prlctl clone "Windows-Analytics-Golden" --name "Windows-Analytics-Prod"
prlctl start "Windows-Analytics-Prod"
```

Now you have a fresh VM with everything pre-configured!

## Template Structure (Simplified)

```hcl
# windows-excel.pkr.hcl (simplified example)

source "parallels-iso" "windows" {
  iso_url          = "~/Downloads/Win11.iso"
  iso_checksum     = "sha256:..."

  vm_name          = "Windows-Analytics-Golden"
  guest_os_type    = "win-11"

  memory           = 8192
  cpus             = 4
  disk_size        = 65536

  parallels_tools_mode = "attach"

  boot_command = [
    # Automated Windows installation
  ]

  communicator = "winrm"
  winrm_username = "vagrant"
  winrm_password = "vagrant"
}

build {
  sources = ["source.parallels-iso.windows"]

  # Install Office
  provisioner "powershell" {
    script = "scripts/install-office.ps1"
  }

  # Install ODBC drivers
  provisioner "powershell" {
    script = "scripts/install-odbc.ps1"
  }

  # Configure DSNs
  provisioner "powershell" {
    script = "scripts/configure-dsns.ps1"
  }

  # Install additional tools
  provisioner "powershell" {
    script = "scripts/install-tools.ps1"
  }

  # Cleanup
  provisioner "powershell" {
    inline = [
      "Clear-RecycleBin -Force",
      "Remove-Item C:\\Windows\\Temp\\* -Recurse -Force"
    ]
  }
}
```

## Customization

### Add Your Own Software
Edit `scripts/install-tools.ps1`:
```powershell
# Install via Chocolatey
choco install -y vscode
choco install -y git
choco install -y your-favorite-tool
```

### Pre-configure Excel Settings
Create `scripts/configure-excel.ps1`:
```powershell
# Set Excel defaults
$excelPath = "HKCU:\Software\Microsoft\Office\16.0\Excel"
New-Item -Path $excelPath -Force
Set-ItemProperty -Path "$excelPath\Options" -Name "DisableAutoRecover" -Value 0
```

### Add Custom ODBC DSNs
Edit `files/odbc-config.json`:
```json
{
  "dsns": [
    {
      "name": "Metabase",
      "driver": "PostgreSQL Unicode(x64)",
      "server": "192.168.1.100",
      "port": "5432",
      "database": "metabase"
    },
    {
      "name": "Analytics_MySQL",
      "driver": "MySQL ODBC 8.0 Driver",
      "server": "192.168.1.101",
      "port": "3306",
      "database": "analytics"
    }
  ]
}
```

## Benefits of Golden Images

1. **Reproducibility**: Rebuild identical VMs anytime
2. **Version Control**: Git tracks your VM configuration
3. **Fast Deployment**: Clone in seconds vs. hours of manual setup
4. **Testing**: Test changes in cloned VM before production
5. **Disaster Recovery**: Rebuild from code if VM corrupted
6. **Scaling**: Need 5 VMs? Clone 5 times
7. **Documentation**: Packer template IS your documentation

## Integration with Terraform

After Packer builds the image, use Terraform to manage instances:

```hcl
# terraform/main.tf
resource "parallels_vm" "analytics" {
  name = "Windows-Analytics-Prod"
  base_image = "Windows-Analytics-Golden"

  memory = 8192
  cpus   = 4

  network {
    type = "shared"
  }
}
```

```bash
terraform apply  # Creates VM from golden image
terraform destroy  # Removes VM (golden image preserved)
```

## Maintenance

### Update Golden Image Monthly
```bash
# Start golden image
prlctl start "Windows-Analytics-Golden"

# Update Windows and Office (manual or scripted)
# Test everything

# Shutdown and create new snapshot
prlctl snapshot "Windows-Analytics-Golden" --name "2024-10-$(date +%d)"

# Or rebuild from Packer with latest updates
packer build -force .
```

### Version Your Images
```bash
# Tag images with dates
prlctl rename "Windows-Analytics-Golden" "Windows-Analytics-Golden-2024-10"

# Keep last 3 months of golden images
```

## Next Steps

1. Start with manual VM setup to understand the process
2. Document every installation step
3. Convert manual steps to Packer provisioner scripts
4. Build your first golden image
5. Test cloning from golden image
6. Iterate and improve

## Resources

- [Packer Parallels Builder Docs](https://www.packer.io/plugins/builders/parallels/iso)
- [Windows Unattended Installation](https://docs.microsoft.com/en-us/windows-hardware/manufacture/desktop/automate-windows-setup)
- [PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands)

---

**Note:** This is a starting template. You'll need to customize for your specific Office license, database credentials, etc. Start simple and add complexity as needed.
