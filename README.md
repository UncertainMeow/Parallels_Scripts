# Parallels Scripts & Automation

Parallels Desktop automation toolkit for macOS, complementing existing Proxmox homelab infrastructure.

## Why Parallels + Proxmox?

- **Parallels**: Local dev VMs on MacBook (fast, offline-capable, tight macOS integration)
- **Proxmox**: Production homelab services (always-on, more resources, remote access)
- **Together**: Develop locally in Parallels, deploy to Proxmox, test cross-platform

## Architecture

```
┌─────────────────────────────────────┐
│   MacBook (Parallels Desktop)      │
│   ├─ Windows VM (Excel + SQL)      │
│   ├─ Ubuntu Dev VM                 │
│   └─ Test/Staging VMs              │
└─────────────────────────────────────┘
         │
         │ Deploy/Test
         ↓
┌─────────────────────────────────────┐
│   Proxmox Homelab                   │
│   ├─ Production Services            │
│   ├─ Docker Hosts                   │
│   └─ Infrastructure VMs             │
└─────────────────────────────────────┘
```

## Repository Structure

```
parallels_scripts/
├── packer/              # Golden image templates
│   ├── windows-excel/
│   ├── ubuntu-dev/
│   └── macos-test/
├── terraform/           # VM lifecycle management
│   ├── dev-environment/
│   └── test-matrix/
├── ansible/             # Post-provisioning
│   ├── excel-setup/
│   ├── sql-clients/
│   └── dev-tools/
├── scripts/             # Utility scripts
│   ├── vm-manager.sh
│   ├── snapshot-rotate.sh
│   └── excel-odbc-setup.sh
├── python/              # Advanced automation
│   ├── vm_api/
│   └── excel_bridge/
└── docs/                # Documentation
    ├── AUTOMATION_IDEAS.md
    └── WORKFLOWS.md
```

## Quick Start

### 1. Check Parallels CLI
```bash
# List all VMs
prlctl list -a

# Get VM info
prlctl list -i <vm_name>

# Start/Stop VM
prlctl start <vm_name>
prlctl stop <vm_name>

# Snapshot management
prlctl snapshot <vm_name> --name "before_changes"
prlctl snapshot-list <vm_name>
```

### 2. Create Your First Automation
```bash
# Clone this repo
cd ~/code/Parallels_Scripts

# Run example VM manager
./scripts/vm-manager.sh list
```

## Integration Patterns

### Pattern 1: Parallels → Proxmox Pipeline
1. Develop in Parallels Windows VM (Excel + SQL scripts)
2. Test against local database replica
3. Push to Git
4. Ansible deploys to Proxmox production VM

### Pattern 2: Unified VM Management
- Single script that manages both Parallels (local) and Proxmox (remote) VMs
- Similar to your `pve-utils` but for hybrid infrastructure

### Pattern 3: Excel as Analysis Frontend
- Parallels Windows VM runs Excel
- Connects to Proxmox-hosted databases
- Python scripts orchestrate data pipeline

## Use Cases

### Primary: Excel + SQL Analytics
- Windows VM with Excel, Power Query, SQL clients
- Pre-configured ODBC connections to Metabase/PostgreSQL
- Automated data refresh scripts
- Version-controlled Excel macros

### Development: Cross-Platform Testing
- Test scripts on macOS host, Windows VM, Linux VM
- Match to Proxmox production environments
- Disposable test VMs

### Homelab: Complementary Services
- Run lightweight Windows services not suitable for Proxmox
- Testing ground before deploying to Proxmox
- Offline-capable development environment

## Tooling Stack

- **prlctl/prlsrvctl**: Direct Parallels CLI control
- **Packer**: Golden image creation (like your Ubuntu templates)
- **Ansible**: Configuration management (integrate with your ansible_base)
- **Python**: Advanced orchestration
- **Bash**: Quick utilities (like your existing scripts)

## Parallels Editions

- **Standard**: Basic virtualization
- **Pro**: Includes prlctl CLI (required for automation)
- **Business**: Enterprise management features

*You need Pro or Business for CLI automation.*

## Connection to Your Existing Work

This repo follows patterns from your other projects:
- **Similar to pve-utils**: But for Parallels VMs
- **Uses Ansible**: Can extend your ansible_base playbooks
- **Shell + Python**: Your preferred stack
- **Systematic approach**: Configuration as code, like your dotfiles

## Next Steps

See [AUTOMATION_IDEAS.md](AUTOMATION_IDEAS.md) for comprehensive category breakdown and examples.

---

**Quick Links:**
- [Parallels CLI Docs](https://docs.parallels.com/parallels-desktop-developers-guide/command-line-interface-utility)
- [Packer Parallels Builder](https://www.packer.io/plugins/builders/parallels)
- [Terraform Parallels Provider](https://registry.terraform.io/providers/Parallels/parallels/latest)
