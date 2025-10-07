# Quick Start: Excel + SQL Analytics with Parallels

Your specific use case: Excel on Windows for data analysis, connecting to Metabase/SQL databases.

## Goal Architecture

```
┌──────────────────────────────────────────┐
│  Parallels Windows VM                    │
│  ├─ Microsoft Excel                      │
│  ├─ ODBC Drivers (PostgreSQL, MySQL)    │
│  ├─ Power Query / Power BI Desktop      │
│  └─ SQL Clients (optional)              │
└──────────────────────────────────────────┘
          │
          │ ODBC/JDBC
          ↓
┌──────────────────────────────────────────┐
│  Your Homelab (Proxmox)                  │
│  ├─ Metabase (PostgreSQL backend)       │
│  ├─ Data Warehouses                     │
│  └─ Analytics Databases                 │
└──────────────────────────────────────────┘
```

## Phase 1: Manual Setup (Start Here)

### Step 1: Create Windows VM in Parallels
1. Open Parallels Desktop
2. File → New → Install Windows from ISO
3. Allocate resources:
   - **RAM**: 8-16GB (Excel can be memory-hungry with large datasets)
   - **CPU**: 4-8 cores
   - **Disk**: 64GB minimum
4. Name it: "Windows Analytics" or "Excel SQL"

### Step 2: Install Excel
- Install Microsoft Office 365 in Windows VM
- Install SQL clients you prefer:
  - DBeaver (universal)
  - pgAdmin (PostgreSQL)
  - MySQL Workbench

### Step 3: Test Basic Connectivity
```bash
# From macOS, test if VM can reach your homelab
prlctl exec "Windows Analytics" ping <your_metabase_host>
```

### Step 4: Manual ODBC Setup (First Time)
In Windows VM:
1. Open "ODBC Data Sources (64-bit)"
2. Add → PostgreSQL Unicode(x64)
3. Configure:
   - Data Source Name: `Metabase`
   - Server: Your Proxmox host IP
   - Port: 5432
   - Database: metabase
   - User: your_username

### Step 5: Connect Excel to Data
In Excel (Windows VM):
1. **Data** → **Get Data** → **From Database** → **From PostgreSQL Database**
2. Enter server and database
3. Select tables
4. Load to Excel or create Power Query

**Or use ODBC:**
1. **Data** → **Get Data** → **From Other Sources** → **From ODBC**
2. Select your configured DSN
3. Enter password

## Phase 2: Automate with Scripts

Once you've done it manually and understand the process, automate it.

### Automated ODBC Setup
```bash
# Set your database info
export METABASE_HOST="192.168.1.100"  # Your Proxmox host
export METABASE_USER="analytics"
export METABASE_DB="metabase"
export PARALLELS_EXCEL_VM="Windows Analytics"

# Run automated setup
./scripts/excel-odbc-setup.sh all
```

This script will:
- ✓ Check if VM is running
- ✓ Install PostgreSQL ODBC drivers
- ✓ Configure DSN connections
- ✓ Test connectivity
- ✓ Create Excel connection guide

### VM Management
```bash
# List all VMs
./scripts/vm-manager.sh list

# Start your Excel VM
./scripts/vm-manager.sh start "Windows Analytics"

# Create snapshot before major changes
./scripts/vm-manager.sh snapshot "Windows Analytics" "before_office_update"

# View VM stats
./scripts/vm-manager.sh stats "Windows Analytics"
```

## Phase 3: Golden Image with Packer (Advanced)

Once you have a working setup, create a template so you can rebuild quickly.

### Create Packer Template
```bash
cd packer/windows-excel/
# Edit windows-excel.json with your settings
packer build windows-excel.json
```

This creates a "golden image" with:
- Windows pre-configured
- Office/Excel installed
- ODBC drivers pre-installed
- Network settings configured
- Your preferred tools

**Benefits:**
- Rebuild VM from scratch in 10 minutes
- Test new Excel plugins safely (rollback if broken)
- Create multiple VMs for different projects
- Version control your VM configuration

## Phase 4: Integration Patterns

### Pattern 1: Scheduled Data Refresh
```bash
# Run daily at 8am - fetch data, process in Excel, export results
cron: 0 8 * * * /path/to/data-refresh-pipeline.sh
```

Pipeline:
1. Python script pulls data from Metabase API
2. Saves CSV to shared folder
3. PowerShell script in Windows VM opens Excel
4. Excel macro processes data, applies formulas
5. Saves results to shared folder
6. Python script uploads to S3/reports folder

### Pattern 2: Excel as Frontend for SQL
- Keep raw data in PostgreSQL (on Proxmox)
- Excel connects via ODBC for queries
- Use Power Query for transformations
- Excel handles visualization and final formatting
- Save Excel files to macOS for backup/version control

### Pattern 3: Multi-Environment Testing
```bash
# Clone VM for testing new Excel macros
./scripts/vm-manager.sh clone "Windows Analytics" "Windows Test"

# Test your changes in Windows Test
# If it works, snapshot and apply to production VM
```

## Common Workflows

### Daily Morning Routine
```bash
#!/bin/bash
# morning-analytics-startup.sh

# Start Excel VM
./scripts/vm-manager.sh start "Windows Analytics"

# Wait for boot
sleep 30

# Refresh data from overnight batch jobs
./scripts/refresh-excel-data.sh

# Open Excel to pre-configured workbook (optional)
prlctl exec "Windows Analytics" \
  cmd.exe /c "start excel.exe \"C:\Analytics\DailyReport.xlsx\""
```

### Before Major Excel Changes
```bash
# Create safety snapshot
./scripts/vm-manager.sh snapshot "Windows Analytics" "before_macro_changes"

# Make your changes in Excel
# Test thoroughly

# If something breaks:
./scripts/vm-manager.sh snapshots "Windows Analytics"  # List snapshots
./scripts/vm-manager.sh restore "Windows Analytics" <snapshot-id>
```

### Weekly Cleanup
```bash
# Rotate old snapshots (keep only last 7)
./scripts/vm-manager.sh rotate "Windows Analytics" 7

# Check VM disk usage
./scripts/vm-manager.sh stats "Windows Analytics"
```

## Excel + SQL Best Practices

### Use Power Query (Not VBA) When Possible
- More maintainable
- Version controllable (M language)
- Better for IT governance
- Faster for large datasets

### Keep Heavy Processing in Database
- Don't pull 10M rows into Excel
- Use SQL to aggregate first
- Excel for final transforms and visualization

### Version Control Your Excel Files
```bash
# Save Excel files to macOS, commit to Git
cp "/Users/kellen/Parallels/Windows Analytics.pvm/Shared Folders/Home/Analytics/*.xlsx" ~/reports/
cd ~/reports && git add . && git commit -m "Daily report $(date +%Y-%m-%d)"
```

### Shared Folders for Data Exchange
In Parallels:
1. VM → Configure → Sharing → Share Mac folders with Windows
2. Share: `~/Analytics` → Appears as `\\psf\Home\Analytics` in Windows

Now you can:
- Drop CSVs from macOS → Auto-available in Windows
- Excel saves to shared folder → Backup scripts on macOS see it immediately

## Troubleshooting

### VM Won't Connect to Homelab Database
```bash
# Check VM networking
prlctl exec "Windows Analytics" ipconfig
prlctl exec "Windows Analytics" ping <homelab_ip>

# Check firewall on Proxmox
# Ensure PostgreSQL accepts connections from Parallels VM IP
```

### Excel Slow with Large Datasets
- Increase VM RAM: `prlctl set "Windows Analytics" --memsize 16384`
- Enable 3D acceleration: `prlctl set "Windows Analytics" --3d-accelerate highest`
- Use Power Query instead of formulas

### ODBC Driver Not Found
```bash
# Reinstall drivers
./scripts/excel-odbc-setup.sh install
```

## Next Steps

1. ✓ Get basic Excel + ODBC working manually
2. ✓ Use vm-manager.sh for daily operations
3. ✓ Automate ODBC setup with excel-odbc-setup.sh
4. Create your first data refresh pipeline
5. Build Packer template for reproducibility
6. Integrate with your existing Ansible playbooks

## Resources

- [Excel ODBC Connection Guide](https://support.microsoft.com/en-us/office/connect-to-an-odbc-data-source-42f5faef-5e0e-4a91-8560-91a0dc5bbf9b)
- [Power Query M Formula Language](https://docs.microsoft.com/en-us/powerquery-m/)
- [PostgreSQL ODBC Driver](https://odbc.postgresql.org/)
- [Parallels CLI Reference](https://docs.parallels.com/parallels-desktop-developers-guide/command-line-interface-utility)

---

**Pro Tip:** Start simple. Get Excel connecting to one database first. Then automate. Then build golden images. Don't try to do everything at once.
