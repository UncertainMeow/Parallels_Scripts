# Parallels Scripts & Automation Framework

**Production-grade automation for Parallels Desktop on macOS**

Complete Infrastructure as Code solution for managing Windows/Linux VMs, Excel data analytics, and corporate reporting workflows.

## 🎯 What Is This?

A comprehensive automation framework that transforms Parallels Desktop into a powerful platform for:

1. **Corporate Data Analytics** - Excel + SQL + Metabase automation for business reporting
2. **Infrastructure as Code** - Packer + Terraform + Ansible for reproducible VM environments
3. **CI/CD & Testing** - Cross-platform testing and automated deployments
4. **Homelab Integration** - Complement your Proxmox setup with local development VMs

## ✨ Key Features

### 🔧 Production-Ready Tools

- **Python Library** (`excel_automation`) - Complete API for VM and ODBC management
- **CLI Tool** (`excel-auto`) - User-friendly command-line interface
- **Interactive Wizards** - Guided setup for common tasks
- **Data Pipeline** - Automated Metabase → Excel → Reports workflow

### 🏗️ Infrastructure as Code

- **Packer Templates** - Build reproducible Windows golden images
- **Terraform Configs** - Declarative VM lifecycle management
- **Ansible Playbooks** - Automated configuration management
- **Version Controlled** - All infrastructure defined in code

### 📊 Excel + Data Analytics

- **ODBC Automation** - Install drivers and configure DSNs programmatically
- **Metabase Integration** - Pull data from Metabase via API
- **Scheduled Data Pulls** - Automated daily/hourly reports
- **Excel Macro Deployment** - Version-controlled Excel automation

### 🚀 Automation & Scheduling

- **Task Scheduler** - Cron-like scheduling for data pulls
- **Data Pipelines** - Multi-step workflows (ETL + reporting)
- **Error Handling** - Comprehensive logging and retry logic
- **Notifications** - Email/Slack alerts on completion/failure

## 📁 Project Structure

```
Parallels_Scripts/
├── python/                      # Python automation framework
│   └── excel_automation/        # Core library
│       ├── vm_manager.py        # Parallels VM management
│       ├── odbc_config.py       # ODBC automation
│       ├── metabase.py          # Metabase API client
│       ├── scheduler.py         # Task scheduling
│       ├── cli.py               # Command-line interface
│       └── config_loader.py     # Configuration management
│
├── scripts/                     # Standalone scripts
│   ├── vm-manager.sh            # VM lifecycle management
│   ├── excel-setup-wizard.sh   # Interactive Excel setup
│   ├── excel-odbc-setup.sh     # Automated ODBC configuration
│   ├── metabase-export.py      # Metabase data export
│   ├── data-pipeline.py        # Complete data pipeline
│   └── schedule-manager.sh     # Cron job management
│
├── packer/                      # Infrastructure as Code
│   └── windows-excel/           # Windows golden image template
│       ├── windows-excel.pkr.hcl        # Packer template
│       └── scripts/             # Provisioning scripts
│           ├── install-chocolatey.ps1
│           ├── install-postgresql-odbc.ps1
│           ├── install-mysql-odbc.ps1
│           └── configure-windows.ps1
│
├── terraform/                   # VM lifecycle management
│   ├── main.tf                  # VM resources
│   ├── variables.tf             # Configuration variables
│   └── terraform.tfvars.example # Example config
│
├── ansible/                     # Configuration management
│   ├── inventory.yml            # Dynamic inventory
│   ├── playbooks/
│   │   ├── configure-excel-vm.yml    # Complete VM setup
│   │   └── test-connection.yml       # Connectivity test
│   └── group_vars/
│       └── windows_vms.yml      # Windows VM variables
│
├── config/                      # Configuration files
│   └── database-connections.example.yml  # Database config template
│
└── docs/                        # Documentation
    ├── QUICKSTART_EXCEL_SQL.md      # Excel + SQL guide
    ├── WORKFLOWS.md                 # Integration patterns
    ├── AUTOMATION_IDEAS.md          # 10 categories of ideas
    ├── FIRST_TIME_SETUP.md          # Initial setup guide
    └── GET_STARTED.md               # Onboarding
```

## 🚀 Quick Start

### Option 1: Interactive Wizard (Easiest)

```bash
# Clone repository
git clone https://github.com/UncertainMeow/Parallels_Scripts.git
cd Parallels_Scripts

# Run interactive setup
./scripts/excel-setup-wizard.sh
```

The wizard will:
- ✓ Check prerequisites
- ✓ Create configuration file
- ✓ Install Python dependencies
- ✓ Configure ODBC drivers
- ✓ Set up Excel VM

### Option 2: Python CLI

```bash
# Install Python library
cd python
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Use CLI
excel-auto vm list                        # List VMs
excel-auto vm start "Windows 11"          # Start VM
excel-auto odbc install-drivers "Windows 11" --driver all
excel-auto odbc configure "Windows 11" --connection metabase_prod
```

### Option 3: Infrastructure as Code

```bash
# 1. Build golden image with Packer
cd packer/windows-excel
packer build -var-file=variables.pkrvars.hcl .

# 2. Create VMs with Terraform
cd ../../terraform
terraform init
terraform apply

# 3. Configure with Ansible
cd ../ansible
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml
```

## 📖 Documentation

### Core Guides

- **[GET_STARTED.md](GET_STARTED.md)** - Start here! Comprehensive onboarding
- **[FIRST_TIME_SETUP.md](FIRST_TIME_SETUP.md)** - GitHub setup and auto-commit
- **[QUICKSTART_EXCEL_SQL.md](docs/QUICKSTART_EXCEL_SQL.md)** - Excel + data analytics
- **[WORKFLOWS.md](docs/WORKFLOWS.md)** - 9 integration patterns

### Component Documentation

- **[python/README.md](python/README.md)** - Python library API reference
- **[packer/windows-excel/README.md](packer/windows-excel/README.md)** - Golden images
- **[terraform/README.md](terraform/README.md)** - VM lifecycle management
- **[ansible/README.md](ansible/README.md)** - Configuration management

### Inspiration

- **[AUTOMATION_IDEAS.md](AUTOMATION_IDEAS.md)** - 10 categories, 50+ ideas

## 🎬 Common Workflows

### Daily Data Analytics Workflow

```bash
# Morning: Start Excel VM and pull data
./scripts/data-pipeline.py run

# This:
# 1. Pulls data from Metabase
# 2. Processes/transforms data
# 3. Updates Excel workbooks
# 4. Saves reports to shared folder
# 5. Sends notifications
```

### Monthly VM Maintenance

```bash
# Build new golden image with latest patches
cd packer/windows-excel
packer build .

# Update production VMs
cd ../../terraform
terraform apply

# Reconfigure if needed
cd ../ansible
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml
```

### Ad-Hoc Data Export

```bash
# Export Metabase dashboard to Excel
./scripts/metabase-export.py dashboard 42 --format excel

# Export specific questions
./scripts/metabase-export.py questions 123 456 789
```

## 🔑 Key Components

### 1. Python Automation Library

```python
from excel_automation import VMManager, ODBCConfigurator, MetabaseClient

# Manage VMs
vm = VMManager("Windows Analytics")
vm.start()
vm.snapshot("before_changes")

# Configure ODBC
odbc = ODBCConfigurator(vm)
odbc.install_driver("postgresql")
odbc.configure_dsn(
    dsn_name="Metabase",
    driver="PostgreSQL Unicode(x64)",
    server="db.company.com",
    database="metabase"
)

# Pull data from Metabase
client = MetabaseClient(base_url="https://metabase.company.com", api_key="...")
df = client.run_question(question_id=123)
df.to_excel("report.xlsx")
```

### 2. Infrastructure as Code Stack

**Packer** (Build golden images):
```bash
packer build packer/windows-excel/
# → Creates: Windows-Analytics-Golden
```

**Terraform** (Deploy VMs):
```bash
terraform apply
# → Creates: Windows-Analytics-Prod (from golden image)
```

**Ansible** (Configure VMs):
```bash
ansible-playbook -i inventory.yml playbooks/configure-excel-vm.yml
# → Configures: ODBC, Excel, tools, settings
```

### 3. Data Pipeline Automation

```bash
# Run complete pipeline
./scripts/data-pipeline.py run

# Dry run (test without changes)
./scripts/data-pipeline.py run --dry-run

# Run specific step
./scripts/data-pipeline.py step metabase-pull

# Schedule with cron
./scripts/schedule-manager.sh add
```

## 🎯 Use Cases

### Corporate Data Analytics (Primary)

- **Problem**: Manually pulling data from Metabase, updating Excel, generating reports
- **Solution**: Automated pipeline that runs daily/hourly
- **Benefit**: Save hours per week, consistent reports, version-controlled

### Infrastructure as Code

- **Problem**: Manually setting up Windows VMs, installing software, configuring ODBC
- **Solution**: Packer + Terraform + Ansible automates everything
- **Benefit**: Reproducible environments, fast deployment, disaster recovery

### Homelab Integration

- **Problem**: Need local development VMs that complement Proxmox homelab
- **Solution**: Parallels for local dev, Proxmox for production
- **Benefit**: Fast local testing, offline capability, tight macOS integration

### CI/CD & Testing

- **Problem**: Need to test across Windows/Linux/macOS
- **Solution**: Automated VM creation and testing
- **Benefit**: Cross-platform confidence, automated testing, disposable environments

## 🛠️ Technology Stack

- **Languages**: Python 3.9+, Bash, PowerShell, HCL
- **IaC**: Packer, Terraform, Ansible
- **Data**: pandas, requests, openpyxl
- **CLI**: Click, Rich (colored output)
- **VM Management**: Parallels Desktop Pro/Business
- **Scheduling**: Python schedule, cron
- **Version Control**: Git, GitHub

## 🔐 Security

- **Environment Variables**: Passwords never stored in files
- **Git Ignore**: Secrets automatically excluded
- **SSH Keys**: 1Password integration
- **Ansible Vault**: Encrypted secrets
- **Read-Only DB Users**: Recommended for analytics

## 📊 Project Stats

- **9 commits** (auto-commit every 30 minutes)
- **3,500+ lines of code**
- **40+ files**
- **7 major components**
- **10 automation categories**
- **9 integration patterns**
- **Production-grade quality**

## 🤝 Contributing

This is a personal project, but feel free to:
- Fork for your own use
- Open issues for bugs
- Submit PRs for improvements
- Share your automation ideas

## 📝 License

MIT License - See LICENSE file

## 🎓 Learning Resources

- [Parallels CLI Docs](https://docs.parallels.com/parallels-desktop-developers-guide/command-line-interface-utility)
- [Packer Parallels Builder](https://www.packer.io/plugins/builders/parallels)
- [Terraform Parallels Provider](https://registry.terraform.io/providers/Parallels/parallels/latest)
- [Ansible Windows Guide](https://docs.ansible.com/ansible/latest/os_guide/windows.html)

## 🚀 What's Next?

Check out [GET_STARTED.md](GET_STARTED.md) for your personalized learning path based on your interests:

- 🎯 **Excel + Data Analytics** → Start with `docs/QUICKSTART_EXCEL_SQL.md`
- 🏗️ **Infrastructure as Code** → Start with Packer templates
- 🔄 **CI/CD & Testing** → Check out test matrix workflows
- 🏠 **Homelab Integration** → See Proxmox integration patterns

## ⭐ Key Highlights

- ✅ **Production-Ready**: Error handling, logging, retry logic
- ✅ **Well-Documented**: Comprehensive guides and examples
- ✅ **Modular**: Use components independently or together
- ✅ **Tested**: Real-world corporate usage
- ✅ **Maintainable**: Clean code, type hints, comments
- ✅ **Extensible**: Easy to add new features
- ✅ **Version Controlled**: Auto-commit tracks all changes

---

**Built with ❤️ for corporate data analysts and homelab enthusiasts**

**Questions?** Check the docs or open an issue on GitHub.

**Ready to automate?** Run `./scripts/excel-setup-wizard.sh` to get started!
