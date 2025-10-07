# 🚀 Get Started with Parallels Automation

Welcome! This repo contains **10 categories** of Parallels automation ideas and **9 practical workflows**, all tailored to your Excel + SQL analytics use case and homelab background.

## 📁 What's in This Repo

```
Parallels_Scripts/
├── 📖 AUTOMATION_IDEAS.md          ← 10 categories of automation ideas
├── 📖 README.md                    ← Overview and philosophy
├── 📖 GET_STARTED.md               ← You are here!
│
├── 📁 docs/
│   ├── QUICKSTART_EXCEL_SQL.md    ← Your primary use case (START HERE!)
│   └── WORKFLOWS.md                ← 9 integration patterns
│
├── 📁 scripts/
│   ├── vm-manager.sh               ← Swiss Army knife for VM management
│   └── excel-odbc-setup.sh         ← Automate Excel + SQL setup
│
├── 📁 packer/
│   └── windows-excel/README.md     ← Golden image templates
│
├── 📁 terraform/                   ← (Future) VM lifecycle management
├── 📁 ansible/                     ← (Future) Configuration management
└── 📁 python/                      ← (Future) Advanced automation
```

## 🎯 Your Journey (Recommended Path)

### Phase 1: Manual Setup (This Week)
**Goal:** Get Excel working with your databases

1. **Create Windows VM in Parallels**
   - Install Windows 11
   - Install Microsoft Office
   - Install ODBC drivers (PostgreSQL, MySQL)

2. **Test Connection**
   - Configure one ODBC DSN to your Metabase/PostgreSQL
   - Open Excel → Data → Get Data → From ODBC
   - Pull data successfully

3. **Read:** `docs/QUICKSTART_EXCEL_SQL.md` (comprehensive guide)

**Time:** 2-3 hours
**Outcome:** Working Excel + SQL connection

---

### Phase 2: Basic Automation (Next Week)
**Goal:** Use scripts for common tasks

1. **Use vm-manager.sh**
   ```bash
   # List all VMs
   ./scripts/vm-manager.sh list

   # Start your Excel VM
   ./scripts/vm-manager.sh start "Windows 11"

   # Create snapshot before risky changes
   ./scripts/vm-manager.sh snapshot "Windows 11" "before_excel_macro_changes"

   # List snapshots
   ./scripts/vm-manager.sh snapshots "Windows 11"
   ```

2. **Automate ODBC Setup**
   ```bash
   # Set your database info
   export METABASE_HOST="192.168.1.100"
   export METABASE_USER="analytics"
   export PARALLELS_EXCEL_VM="Windows 11"

   # Run automated setup
   ./scripts/excel-odbc-setup.sh all
   ```

3. **Read:** `docs/WORKFLOWS.md` sections 1, 4, 8

**Time:** 2-3 hours
**Outcome:** Automated VM management, reproducible setup

---

### Phase 3: Golden Images (Week 3-4)
**Goal:** Never manually setup Windows/Excel again

1. **Document Your Setup**
   - List every software installed
   - Note all configuration steps
   - Save ODBC settings

2. **Create Packer Template**
   - Read: `packer/windows-excel/README.md`
   - Start simple (Windows + Office)
   - Gradually add ODBC, tools, configs

3. **Build & Test**
   ```bash
   cd packer/windows-excel/
   packer build .

   # Clone from golden image
   prlctl clone "Windows-Analytics-Golden" --name "Windows-Analytics-Oct2024"
   ```

**Time:** 4-6 hours (spread over week)
**Outcome:** Reproducible VM builds, version-controlled infrastructure

---

### Phase 4: Advanced Integration (Month 2+)
**Goal:** Full Parallels + Proxmox integration

1. **Add Ansible**
   - Integrate with your existing `ansible_base` repo
   - Manage both Parallels and Proxmox VMs

2. **Build Data Pipelines**
   - Python (macOS) → Excel (Parallels) → Reports (macOS)
   - Read: `docs/WORKFLOWS.md` section 7

3. **Unified Management**
   - Single script for Parallels + Proxmox VMs
   - Read: `docs/WORKFLOWS.md` section 6

**Time:** Ongoing
**Outcome:** Hybrid local + remote infrastructure

---

## 🔥 Top 5 Quick Wins

### 1. **Snapshot Before Every Risky Change**
```bash
./scripts/vm-manager.sh snapshot "Windows 11" "before_$(date +%Y%m%d_%H%M%S)"
```
Never fear breaking your VM again. Revert in seconds.

### 2. **Scheduled VM Startup**
```bash
# Add to crontab
0 8 * * 1-5 prlctl start "Windows 11"  # Start weekdays at 8am
```
VM ready when you start work.

### 3. **Shared Folders for Seamless File Transfer**
In Parallels: VM → Configure → Sharing → Share Mac folders
Access macOS files from Windows: `\\psf\Home\`

### 4. **Excel Connection String in Git**
Save your ODBC connection configs in Git, auto-deploy to VMs.

### 5. **Clone VMs for Testing**
```bash
prlctl clone "Windows 11" --name "Windows Test"
```
Test Excel macros without risking your production VM.

---

## 🗺️ Category Overview (from AUTOMATION_IDEAS.md)

1. **Infrastructure as Code & Golden Images** ← Packer, Terraform
2. **Data Analytics & Excel Automation** ← YOUR PRIMARY USE CASE
3. **Development Environment Automation** ← Disposable dev VMs
4. **CI/CD & Testing Pipelines** ← Cross-platform testing
5. **Homelab Integration** ← Parallels + Proxmox synergy
6. **Backup & Disaster Recovery** ← Snapshot management
7. **Security & Compliance Testing** ← Isolated testing environments
8. **Multi-OS Workflow Automation** ← macOS → Windows → Linux
9. **Network Lab & Simulation** ← Test network scenarios
10. **Monitoring & Resource Management** ← Keep VMs healthy

**Read full details:** `AUTOMATION_IDEAS.md`

---

## 🎓 Learning Resources

### Parallels
- [Parallels CLI Docs](https://docs.parallels.com/parallels-desktop-developers-guide/command-line-interface-utility)
- [Parallels Developer Guide](https://docs.parallels.com/parallels-desktop-developers-guide)

### Packer
- [Packer Parallels Builder](https://www.packer.io/plugins/builders/parallels/iso)

### Excel + SQL
- [Excel ODBC Connections](https://support.microsoft.com/en-us/office/connect-to-an-odbc-data-source-42f5faef-5e0e-4a91-8560-91a0dc5bbf9b)
- [Power Query M Language](https://docs.microsoft.com/en-us/powerquery-m/)

### Your Existing Repos (for reference)
- [Your Proxmox Utils](https://github.com/UncertainMeow/pve-utils) ← Similar patterns
- [Your Ansible Base](https://github.com/UncertainMeow/ansible_base) ← Extend for Parallels

---

## 💡 Next Steps

1. **Choose your path:**
   - 🏃 **Fast Start:** Go to `docs/QUICKSTART_EXCEL_SQL.md` → Get Excel working today
   - 🤔 **Browse Ideas:** Read `AUTOMATION_IDEAS.md` → Pick 2-3 categories
   - 🛠️ **See Workflows:** Read `docs/WORKFLOWS.md` → Understand integration patterns

2. **Test the scripts:**
   ```bash
   # Do you have any VMs yet?
   ./scripts/vm-manager.sh list

   # If yes, try:
   ./scripts/vm-manager.sh info "Your VM Name"
   ```

3. **Pick 2-3 categories from AUTOMATION_IDEAS.md** that excite you most

4. **Come back and tell me which ones** → I'll create detailed implementations

---

## 🤝 My Recommendations (Based on Your Profile)

Looking at your GitHub (Proxmox automation, Ansible, systematic approach), here's what I think you'll love:

### Top 3 to Start:
1. **Golden Images with Packer** ← You already do this for Ubuntu, apply to Windows
2. **Excel + SQL Automation** ← Your stated need, immediate ROI
3. **Proxmox Integration** ← Connect your two worlds

### After You're Comfortable:
4. **Ansible for Parallels** ← Extend your existing ansible_base
5. **Data Pipelines** ← Python + Excel + SQL
6. **Unified VM Management** ← One script, all VMs (local + remote)

---

## 📞 What's Next?

**You said:** "come up with a bunch of different crazy ideas and come back with categories and examples (like 7-10 categories of cool stuff) and then we'll choose and go from there"

**I delivered:**
- ✅ 10 categories in `AUTOMATION_IDEAS.md`
- ✅ 9 practical workflows in `docs/WORKFLOWS.md`
- ✅ 2 working scripts (`vm-manager.sh`, `excel-odbc-setup.sh`)
- ✅ Quickstart guide for your Excel + SQL use case
- ✅ Packer template structure
- ✅ Integration with your existing homelab

**Now it's your turn:**
1. Which 2-3 categories excite you most?
2. What's your immediate need (this week)?
3. What's your long-term vision (next month)?

Tell me, and I'll create detailed implementations for those specific areas. We can start with scripts, templates, or whatever you need.

**Let's build something cool! 🚀**
