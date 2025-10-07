# Parallels + Proxmox Homelab Workflows

Integration patterns for using Parallels Desktop alongside your Proxmox homelab.

## Philosophy: Local Dev + Remote Prod

```
┌─────────────────────────────────────────────┐
│           Your MacBook (Parallels)          │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │  Windows VM  │      │   Linux Dev VM  │ │
│  │  (Excel)     │      │   (Testing)     │ │
│  └──────────────┘      └─────────────────┘ │
│         │                      │            │
│         │  Fast, Offline,      │            │
│         │  Tight Integration   │            │
└─────────┼──────────────────────┼────────────┘
          │                      │
          │   Network/Deploy     │
          ↓                      ↓
┌─────────────────────────────────────────────┐
│         Proxmox Homelab (Remote)            │
│                                             │
│  ┌────────────┐  ┌─────────────┐  ┌──────┐│
│  │ Metabase   │  │  Databases  │  │Docker││
│  │ (Analytics)│  │  (PostgreSQL)│  │ Apps ││
│  └────────────┘  └─────────────┘  └──────┘│
│                                             │
│  Always-on, More Resources, Shared          │
└─────────────────────────────────────────────┘
```

**Key Insight:** Use Parallels for development/analysis (local, fast), Proxmox for production services (always-on, shared).

---

## Workflow 1: Excel Analytics Pipeline

**Use Case:** Daily data analysis with Excel connecting to Proxmox-hosted databases.

### Architecture
```
Metabase (Proxmox)
    ↓ SQL Query
PostgreSQL (Proxmox)
    ↓ ODBC Connection
Excel (Parallels Windows)
    ↓ Process/Format
Reports (macOS, version controlled)
```

### Implementation

**Morning Startup:**
```bash
#!/bin/bash
# ~/bin/morning-analytics.sh

# Start Excel VM
prlctl start "Windows Analytics"
echo "Waiting for Windows to boot..."
sleep 30

# Verify database connectivity
prlctl exec "Windows Analytics" ping -n 1 192.168.1.100

# Open pre-configured Excel workbook
prlctl exec "Windows Analytics" \
  cmd.exe /c "start excel \"C:\Analytics\Daily_Report.xlsx\""

echo "✓ Analytics environment ready"
```

**Excel Side (Windows VM):**
1. Power Query pulls data from PostgreSQL via ODBC
2. Excel formulas calculate metrics
3. Pivot tables create summaries
4. Save to shared folder: `\\psf\Home\Analytics\Daily_Report_$(date).xlsx`

**Automation Side (macOS):**
```bash
# Watch for new reports, commit to Git
fswatch ~/Analytics/*.xlsx | while read file; do
  cd ~/Analytics
  git add "$file"
  git commit -m "Auto: $(basename $file) - $(date)"
  git push
done
```

### Benefits
- **Offline Capable:** Work on plane, train, coffee shop
- **Fast:** Local VM, no network latency
- **Integrated:** Shared folders between macOS and Windows
- **Version Controlled:** Reports automatically backed up to Git

---

## Workflow 2: Dev → Test → Prod Pipeline

**Use Case:** Develop scripts locally, test in Parallels, deploy to Proxmox.

### Pipeline
```
1. Code in macOS (VS Code)
2. Test in Parallels Linux VM
3. If pass → Deploy to Proxmox VM
4. If fail → Iterate locally
```

### Implementation

```bash
#!/bin/bash
# ~/bin/deploy-pipeline.sh <script_name>

SCRIPT=$1
LOCAL_TEST_VM="Ubuntu Dev"
PROXMOX_VM="prod-app-01"
PROXMOX_HOST="192.168.1.50"

echo "1. Testing in local Parallels VM..."
prlctl exec "$LOCAL_TEST_VM" /bin/bash -c "cd /psf/Home/projects && ./$SCRIPT"

if [ $? -eq 0 ]; then
    echo "✓ Local test passed"

    echo "2. Deploying to Proxmox..."
    scp "$SCRIPT" root@$PROXMOX_HOST:/tmp/
    ssh root@$PROXMOX_HOST "qm exec $PROXMOX_VM -- bash /tmp/$SCRIPT"

    echo "✓ Deployed to production"
else
    echo "✗ Local test failed, aborting deployment"
    exit 1
fi
```

### Benefits
- **Fast Feedback:** Test locally in seconds, not minutes
- **Safe:** Never touch prod until local tests pass
- **Consistent:** Same OS (Ubuntu) locally and in Proxmox
- **Efficient:** Only deploy what's tested

---

## Workflow 3: Golden Image Factory

**Use Case:** Create standardized VMs for different projects/clients.

### Process
```
Packer Template (Git)
    ↓ Build
Golden Image (Parallels)
    ↓ Clone
Dev VM 1, Dev VM 2, Test VM, Demo VM...
    ↓ Export (optional)
OVA/Template → Import to Proxmox
```

### Monthly Build Cycle

**Day 1: Update Golden Image**
```bash
#!/bin/bash
# packer/build-all-golden-images.sh

# Build Windows + Excel golden image
cd packer/windows-excel/
packer build .

# Build Ubuntu dev golden image
cd ../ubuntu-dev/
packer build .

# Build specialized images
cd ../windows-sqlserver/
packer build .

echo "✓ All golden images built"
echo "✓ Ready to clone for October 2024"
```

**Day 2-30: Use Golden Images**
```bash
# Need a new VM? Clone from golden
prlctl clone "Windows-Analytics-Golden" --name "Project-Alpha-Excel"
prlctl clone "Ubuntu-Dev-Golden" --name "Project-Beta-Test"

# Customize per project
ansible-playbook -i parallels-inventory.yml project-alpha-setup.yml
```

**Benefits:**
- **Consistency:** Every VM identical baseline
- **Speed:** Clone in seconds vs. hours of setup
- **Updates:** Apply once to golden, clone for all projects
- **Compliance:** Standardized security patches

---

## Workflow 4: Snapshot-Driven Development

**Use Case:** Fearlessly experiment, instantly rollback mistakes.

### Pattern
```
Clean State Snapshot
    ↓
Make Risky Changes
    ↓
Test Thoroughly
    ↓
If Good → Snapshot Success State
If Bad  → Revert to Clean State
```

### Implementation

**Wrapper Script for Risky Operations:**
```bash
#!/bin/bash
# scripts/safe-exec.sh <vm_name> <command>

VM=$1
shift
COMMAND=$@

SNAPSHOT_NAME="before_$(echo $COMMAND | tr ' ' '_')_$(date +%s)"

echo "Creating safety snapshot: $SNAPSHOT_NAME"
prlctl snapshot "$VM" --name "$SNAPSHOT_NAME"

echo "Executing: $COMMAND"
prlctl exec "$VM" $COMMAND

read -p "Did it work? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Great! Keeping changes."
else
    echo "Reverting to snapshot..."
    SNAP_ID=$(prlctl snapshot-list "$VM" | grep "$SNAPSHOT_NAME" | grep -oP '\{\K[^}]+')
    prlctl snapshot-switch "$VM" --id "$SNAP_ID"
    echo "✓ Reverted"
fi
```

**Excel Macro Development:**
```bash
# Before editing macros
./scripts/vm-manager.sh snapshot "Windows Analytics" "before_macro_changes"

# Edit macros in Excel, test thoroughly

# If broken:
./scripts/vm-manager.sh snapshots "Windows Analytics"  # List
./scripts/vm-manager.sh restore "Windows Analytics" <snapshot_id>
```

**Benefits:**
- **Fearless Experimentation:** Can't permanently break anything
- **Fast Recovery:** Revert in seconds, not hours
- **Multiple Versions:** Keep snapshots of different configs
- **Before Updates:** Always snapshot before Windows/Office updates

---

## Workflow 5: Multi-OS Testing Matrix

**Use Case:** Test code across Windows, Linux, macOS.

### Matrix
```
┌─────────────┬──────────┬──────────┬──────────┐
│             │ macOS    │ Windows  │  Linux   │
├─────────────┼──────────┼──────────┼──────────┤
│ Python 3.9  │  Host    │  VM #1   │  VM #2   │
│ Python 3.10 │  Host    │  VM #3   │  VM #4   │
│ Python 3.11 │  Host    │  VM #5   │  VM #6   │
└─────────────┴──────────┴──────────┴──────────┘
```

### Parallel Execution
```bash
#!/bin/bash
# scripts/test-matrix.sh

# Run tests in parallel across all VMs
parallel -j 3 ::: \
  "./scripts/run-test.sh 'Windows Py39' python3.9" \
  "./scripts/run-test.sh 'Windows Py310' python3.10" \
  "./scripts/run-test.sh 'Ubuntu Py39' python3.9" \
  "./scripts/run-test.sh 'Ubuntu Py310' python3.10"

# Collect results
./scripts/aggregate-test-results.sh
```

**Benefits:**
- **Confidence:** Know it works everywhere
- **Fast:** Parallel execution
- **CI/CD:** Integrate with GitHub Actions
- **Edge Cases:** Find OS-specific bugs early

---

## Workflow 6: Proxmox Integration Scripts

**Use Case:** Unified management of Parallels (local) + Proxmox (remote) VMs.

### Unified VM Manager
```bash
#!/bin/bash
# scripts/unified-vm-manager.sh

case $1 in
  list)
    echo "=== Local VMs (Parallels) ==="
    prlctl list -a

    echo "=== Remote VMs (Proxmox) ==="
    ssh root@proxmox "qm list"
    ;;

  start)
    if [[ $2 == local-* ]]; then
      prlctl start "${2#local-}"
    elif [[ $2 == remote-* ]]; then
      ssh root@proxmox "qm start ${2#remote-}"
    fi
    ;;

  stats)
    # Show combined resource usage
    ./scripts/parallels-stats.sh
    ssh root@proxmox "./scripts/pve-stats.sh"
    ;;
esac
```

### Disaster Recovery: Parallels → Proxmox
```bash
#!/bin/bash
# Export Parallels VM to Proxmox format

VM_NAME="Windows Analytics"
EXPORT_DIR="/tmp/vm-export"

# Export from Parallels
prlctl backup "$VM_NAME" --storage "$EXPORT_DIR"

# Convert to Proxmox-compatible format
qemu-img convert \
  "$EXPORT_DIR/${VM_NAME}.hdd" \
  -O qcow2 \
  "$EXPORT_DIR/${VM_NAME}.qcow2"

# Upload to Proxmox
scp "$EXPORT_DIR/${VM_NAME}.qcow2" root@proxmox:/var/lib/vz/images/

# Import to Proxmox
ssh root@proxmox "qm importdisk 100 /var/lib/vz/images/${VM_NAME}.qcow2 local-lvm"
```

**Benefits:**
- **Unified Interface:** One script for all VMs
- **Flexibility:** Move VMs between platforms
- **Backup:** Parallels VMs backed up to Proxmox
- **Resource Optimization:** Run where it makes sense

---

## Workflow 7: Excel + Python Data Pipeline

**Use Case:** Combine Python's power with Excel's flexibility.

### Pipeline
```
Python (macOS)
    ↓ Extract data from APIs/databases
CSV files (Shared Folder)
    ↓ Trigger Excel macro
Excel (Windows VM)
    ↓ Complex formulas, formatting, pivots
Final Reports (Shared Folder)
    ↓ Python archives/emails
Distribution
```

### Implementation

**macOS Side:**
```python
# ~/scripts/data-pipeline.py
import pandas as pd
import subprocess

# Extract data
df = fetch_data_from_metabase()
df.to_csv('~/Parallels/Shared/raw_data.csv')

# Trigger Excel processing
subprocess.run([
    'prlctl', 'exec', 'Windows Analytics',
    'powershell', '-File', 'C:\\Scripts\\process_data.ps1'
])

# Wait for Excel to finish
time.sleep(60)

# Collect results
report = pd.read_excel('~/Parallels/Shared/final_report.xlsx')
email_report(report)
```

**Windows Side (PowerShell):**
```powershell
# C:\Scripts\process_data.ps1
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false

$workbook = $excel.Workbooks.Open("\\psf\Home\raw_data.csv")

# Run macro that does complex Excel stuff
$excel.Run("ProcessDataMacro")

# Save results
$workbook.SaveAs("\\psf\Home\final_report.xlsx")
$excel.Quit()
```

**Benefits:**
- **Best of Both:** Python for data, Excel for business logic
- **Automated:** Runs unattended
- **Reliable:** Each tool does what it's best at
- **Maintainable:** Business users edit Excel, devs edit Python

---

## Workflow 8: Scheduled VM Operations

**Use Case:** Automate routine VM tasks.

### Cron Schedule
```bash
# crontab -e

# Start Excel VM weekday mornings
0 8 * * 1-5 prlctl start "Windows Analytics"

# Snapshot before nightly updates
0 2 * * * ~/Parallels_Scripts/scripts/nightly-snapshot.sh

# Rotate old snapshots weekly
0 3 * * 0 ~/Parallels_Scripts/scripts/snapshot-rotate.sh "Windows Analytics" 7

# Shutdown VMs at night to save resources
0 22 * * * prlctl stop "Windows Analytics" && prlctl stop "Ubuntu Dev"

# Monthly golden image rebuild
0 4 1 * * cd ~/Parallels_Scripts/packer && ./build-all.sh
```

### Smart Scheduling Script
```bash
#!/bin/bash
# scripts/smart-scheduler.sh

HOUR=$(date +%H)
DAY=$(date +%u)  # 1=Monday, 7=Sunday

# Only during work hours, work days
if [ $HOUR -ge 8 ] && [ $HOUR -le 18 ] && [ $DAY -le 5 ]; then
    prlctl start "Windows Analytics"
else
    prlctl stop "Windows Analytics"
fi
```

**Benefits:**
- **Resource Efficient:** VMs only run when needed
- **Automated Backups:** Never forget snapshots
- **Cost Savings:** Less RAM/CPU usage when not working
- **Consistency:** Same schedule every week

---

## Workflow 9: Ansible + Parallels Integration

**Use Case:** Manage Parallels VMs with your existing Ansible playbooks.

### Inventory
```yaml
# ansible/parallels-inventory.yml
all:
  children:
    parallels_vms:
      hosts:
        windows_analytics:
          ansible_host: "{{ lookup('pipe', 'prlctl list \"Windows Analytics\" -o ip --no-header') }}"
          ansible_user: "vagrant"
          ansible_connection: "winrm"
        ubuntu_dev:
          ansible_host: "{{ lookup('pipe', 'prlctl list \"Ubuntu Dev\" -o ip --no-header') }}"
          ansible_user: "vagrant"
```

### Playbook
```yaml
# ansible/excel-setup.yml
---
- name: Configure Excel VM
  hosts: windows_analytics
  tasks:
    - name: Install ODBC drivers
      win_package:
        path: "https://ftp.postgresql.org/pub/odbc/releases/REL-13_02_0000/psqlodbc_x64.msi"
        state: present

    - name: Configure ODBC DSN
      win_odbc_dsn:
        name: "Metabase"
        driver: "PostgreSQL Unicode(x64)"
        state: present
        attribute_dict:
          Server: "{{ metabase_host }}"
          Database: "{{ metabase_db }}"
          Port: "5432"

    - name: Copy Excel macros
      win_copy:
        src: "files/macros.xlam"
        dest: "C:\\Users\\vagrant\\AppData\\Roaming\\Microsoft\\AddIns\\"
```

### Run
```bash
ansible-playbook -i ansible/parallels-inventory.yml ansible/excel-setup.yml
```

**Benefits:**
- **Declarative:** Describe desired state, Ansible makes it so
- **Reusable:** Same playbooks for Parallels and Proxmox VMs
- **Version Controlled:** Infrastructure as code
- **Idempotent:** Safe to run multiple times

---

## Choosing the Right Workflow

| Workflow | Best For | Complexity | Payoff |
|----------|----------|------------|--------|
| Excel Analytics | Daily data work | Low | Immediate |
| Dev→Test→Prod | Software development | Medium | High |
| Golden Images | Standardization | High | Very High |
| Snapshots | Experimentation | Low | High |
| Test Matrix | Multi-platform apps | Medium | High |
| Proxmox Integration | Hybrid infrastructure | High | Very High |
| Excel+Python | Data pipelines | Medium | High |
| Scheduled Ops | Automation | Low | Medium |
| Ansible | Configuration mgmt | High | Very High |

---

## Getting Started

1. **Week 1:** Manual Excel + ODBC setup (Workflow 1)
2. **Week 2:** Use vm-manager.sh, add snapshots (Workflow 4)
3. **Week 3:** Automate ODBC setup script
4. **Week 4:** Build first Packer golden image (Workflow 3)
5. **Month 2:** Add Ansible, integrate with Proxmox (Workflow 9)
6. **Month 3:** Full data pipeline automation (Workflow 7)

Start simple, build gradually, automate as you understand the patterns.

---

## Resources

- [Your Proxmox Utils](https://github.com/UncertainMeow/pve-utils)
- [Your Ansible Base](https://github.com/UncertainMeow/ansible_base)
- Parallels CLI Docs
- Packer Parallels Builder
- Ansible Windows Modules

**Remember:** You already know Proxmox automation. This is just applying the same principles to Parallels. Start with what you know, extend to what you want to build.
