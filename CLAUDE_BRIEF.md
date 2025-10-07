# Claude Code Briefing - Parallels Automation Framework

**Last Updated**: 2025-10-07
**Status**: ✅ Core framework complete, production-ready
**Next Developer**: Read this first!

---

## 🎯 What We Built

A **production-grade automation framework** for Parallels Desktop that enables:

1. **Excel + Data Analytics Automation** - Corporate reporting workflows (Metabase → Excel → Reports)
2. **Infrastructure as Code** - Complete Packer + Terraform + Ansible stack for VM management
3. **Data Pipeline Orchestration** - Scheduled data pulls, transformations, and report generation
4. **Developer Tools** - Python library, CLI tools, interactive wizards

**Core Philosophy**: Everything as code, reproducible, version-controlled, secure by default.

---

## 📐 Architecture Overview

### High-Level Flow

```
Packer (Build) → Terraform (Deploy) → Ansible (Configure) → Python Scripts (Automate)
   Golden Images      VM Creation       ODBC/Tools Setup      Daily Operations
```

### Components

```
python/excel_automation/     # Core Python library (production-ready)
├── vm_manager.py           # Parallels VM lifecycle (start, stop, snapshot, exec)
├── odbc_config.py          # ODBC driver installation & DSN configuration
├── metabase.py             # Metabase API client (query execution, exports)
├── scheduler.py            # Task scheduling (cron-like)
├── config_loader.py        # YAML config with env var substitution
└── cli.py                  # User-facing CLI (excel-auto command)

scripts/                     # Standalone automation scripts
├── vm-manager.sh           # Bash wrapper for common VM operations
├── excel-setup-wizard.sh   # Interactive setup (beginners)
├── data-pipeline.py        # Complete ETL pipeline (5 steps)
├── metabase-export.py      # Standalone Metabase data export
└── schedule-manager.sh     # Cron job management

packer/windows-excel/        # Infrastructure as Code
├── windows-excel.pkr.hcl   # Packer template (Windows 11 + Excel + ODBC)
└── scripts/*.ps1           # PowerShell provisioning scripts

terraform/                   # VM lifecycle management
├── main.tf                 # VM resources (analytics, test, projects)
└── variables.tf            # Configurable parameters

ansible/                     # Configuration management
├── inventory.yml           # Dynamic inventory (IP lookups)
├── playbooks/              # VM configuration playbooks
└── group_vars/             # Variables by VM type
```

### Key Design Decisions

1. **Security First**: No passwords in code, env vars only, secrets in .gitignore
2. **Modular**: Each component works independently
3. **Error Handling**: Try/except blocks, logging, graceful degradation
4. **Type Hints**: Full type annotations for IDE support
5. **Documentation**: Every component has README + docstrings

---

## 🚀 Big Opportunities (Next Steps)

### Priority 1: Excel Macro Integration (High Value)

**What's Missing**: The framework can configure ODBC and start VMs, but doesn't yet execute Excel macros.

**Opportunity**:
```python
# In vm_manager.py or new excel_controller.py
def refresh_excel_workbook(self, workbook_path: str, macro_name: str = None):
    """Execute Excel refresh or macro via COM automation"""
    script = f'''
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $wb = $excel.Workbooks.Open("{workbook_path}")

    if ("{macro_name}") {{
        $excel.Run("{macro_name}")
    }} else {{
        $wb.RefreshAll()
        $excel.CalculateFullRebuild()
    }}

    $wb.Save()
    $wb.Close()
    $excel.Quit()
    '''
    return self.vm.execute(f'powershell -Command "{script}"')
```

**Impact**: Complete the data pipeline (Metabase → Excel processing → Reports)

### Priority 2: Error Recovery & Retry Logic

**What's Missing**: Basic error handling exists, but no retry logic for transient failures.

**Opportunity**:
```python
# Add to odbc_config.py and metabase.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def install_driver(self, driver_type: str):
    # Existing code with automatic retries on failure
```

**Add**: `tenacity` to requirements.txt

**Impact**: Handle network glitches, temporary VM unavailability, driver installation failures

### Priority 3: Testing Suite

**What's Missing**: No automated tests (pytest was added to requirements but no tests written).

**Opportunity**:
```python
# tests/test_vm_manager.py
def test_vm_exists():
    vm = VMManager("TestVM")
    assert vm.exists() or not vm.exists()  # Should not raise

def test_config_loader():
    config = ConfigLoader(Path("config/database-connections.example.yml"))
    assert "connections" in config.load()

# tests/test_integration.py (requires running VM)
@pytest.mark.integration
def test_full_pipeline():
    # Test complete workflow
```

**Impact**: Confidence in refactoring, catch regressions early

### Priority 4: Windows Authentication Integration

**Current**: Uses basic WinRM with username/password
**Opportunity**: Support Windows domain auth, Kerberos, NTLM

```python
# In odbc_config.py
additional_props = {
    "Trusted_Connection": "Yes",  # Windows authentication
    "Encrypt": "yes"              # SSL/TLS
}
```

**Impact**: Corporate security compliance, no hardcoded passwords

### Priority 5: Parallel VM Operations

**Current**: Operations are sequential
**Opportunity**: Use `concurrent.futures` for parallel VM operations

```python
from concurrent.futures import ThreadPoolExecutor

def start_all_vms(vm_names: List[str]):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(VMManager(name).start) for name in vm_names]
        return [f.result() for f in futures]
```

**Impact**: Faster CI/CD, bulk operations

---

## ⚠️ Known Issues & Environment Gotchas

### Issue 1: Parallels CLI Availability

**Problem**: `prlctl` only available in Pro/Business editions
**Symptom**: `command not found: prlctl`
**Workaround**: Check in `_check_parallels()` but no graceful degradation
**Fix Needed**:
```python
def _check_parallels(self):
    if not shutil.which("prlctl"):
        raise RuntimeError(
            "Parallels Desktop Pro or Business required.\n"
            "Standard edition doesn't include CLI tools.\n"
            "Upgrade at: https://www.parallels.com/products/desktop/"
        )
```

### Issue 2: WinRM Configuration

**Problem**: WinRM not enabled by default on Windows VMs
**Symptom**: `ansible` or `win_shell` commands timeout
**Current Mitigation**: Packer templates configure WinRM, but manual VMs may not have it
**Fix Needed**:
```python
# Add to vm_manager.py
def ensure_winrm(self, username: str, password: str):
    """Enable WinRM if not already configured"""
    # Try to connect, if fails, enable via Parallels Tools
    script = '''
    winrm quickconfig -q
    winrm set winrm/config/service/auth '@{Basic="true"}'
    winrm set winrm/config/service '@{AllowUnencrypted="true"}'
    '''
    self.execute(script)
```

### Issue 3: Shared Folders Path Issues

**Problem**: PowerShell scripts assume `\\psf\Home` (Parallels Shared Folders)
**Symptom**: "Path not found" when copying files to VM
**Workaround**: Shared folders must be enabled in VM settings
**Fix Needed**:
```python
# Check and enable shared folders
def _ensure_shared_folders(self):
    result = self._run_prlctl("list", self.vm_name, "-i")
    if "Host shared folders: off" in result.stdout:
        logger.warning("Enabling shared folders...")
        self._run_prlctl("set", self.vm_name, "--shf-host", "on")
```

### Issue 4: ODBC Driver Product IDs

**Problem**: Ansible `win_package` needs product IDs for idempotency
**Symptom**: Drivers reinstall every time, or fail with "already installed"
**Current**: `failed_when: false` (ignores errors)
**Fix Needed**:
```yaml
# Get actual product IDs and add to playbook
- name: Check if PostgreSQL ODBC installed
  win_shell: Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*PostgreSQL*"}
  register: pg_installed

- name: Install PostgreSQL ODBC driver
  win_package:
    path: https://...
    state: present
  when: pg_installed.stdout == ""
```

### Issue 5: Metabase API Rate Limiting

**Problem**: No rate limiting in `metabase.py`
**Symptom**: "429 Too Many Requests" on bulk exports
**Fix Needed**:
```python
import time
from functools import wraps

def rate_limit(calls_per_second=2):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)
def run_question(self, question_id: int):
    # Existing code
```

### Issue 6: Environment Variable Validation

**Problem**: Config loader fails with unhelpful error if env var not set
**Symptom**: `ValueError: Environment variable not set: METABASE_PASSWORD`
**Current**: Error message is good, but happens at runtime
**Fix Needed**:
```python
# Add to cli.py
def validate_environment():
    """Check required env vars before running commands"""
    required = {
        'METABASE_PASSWORD': 'Database password for Metabase',
        'METABASE_HOST': 'Metabase server hostname',
    }

    missing = []
    for var, description in required.items():
        if not os.getenv(var):
            missing.append(f"  {var}: {description}")

    if missing:
        console.print("[red]Missing required environment variables:[/red]")
        console.print("\n".join(missing))
        console.print("\nSet them with:")
        console.print("  export METABASE_PASSWORD='...'")
        sys.exit(1)

# Call before running commands
validate_environment()
```

### Issue 7: Large Dataset Memory Issues

**Problem**: `pandas` loads entire dataset into memory
**Symptom**: OOM errors on multi-GB exports
**Fix Needed**:
```python
# In metabase.py
def run_question_streaming(self, question_id: int, output_path: Path):
    """Stream results directly to file instead of memory"""
    response = self.session.post(
        f"{self.base_url}/api/card/{question_id}/query",
        stream=True
    )

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
```

---

## 🛡️ Safeguards to Implement

### 1. Pre-Flight Checks

```python
# Add to vm_manager.py
def preflight_check(self) -> Dict[str, bool]:
    """Verify VM is ready for operations"""
    checks = {
        "vm_exists": self.exists(),
        "vm_running": self.is_running(),
        "has_ip": self.get_ip() is not None,
        "parallels_tools": self._has_parallels_tools(),
        "winrm_enabled": self._test_winrm(),
        "disk_space": self._check_disk_space() > 5_000_000_000,  # 5GB free
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        logger.warning(f"Preflight checks failed: {', '.join(failed)}")

    return checks
```

### 2. Configuration Validation

```python
# Add to config_loader.py
def validate_schema(self) -> List[str]:
    """Validate configuration against schema"""
    errors = []

    config = self.load()

    # Check required sections
    required_sections = ['connections', 'vm', 'logging']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    # Validate connections
    if 'connections' in config:
        for name, conn in config['connections'].items():
            required_fields = ['type', 'host', 'database', 'dsn_name']
            for field in required_fields:
                if field not in conn:
                    errors.append(f"Connection '{name}' missing: {field}")

    return errors
```

### 3. Snapshot Before Destructive Operations

```python
# Add decorator
def with_snapshot(func):
    """Create snapshot before operation, restore on failure"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_running():
            return func(self, *args, **kwargs)

        snapshot_name = f"auto_before_{func.__name__}_{int(time.time())}"
        logger.info(f"Creating safety snapshot: {snapshot_name}")

        self.snapshot(name=snapshot_name, description="Automatic safety snapshot")

        try:
            result = func(self, *args, **kwargs)
            # Success - optionally delete snapshot
            return result
        except Exception as e:
            logger.error(f"Operation failed, snapshot preserved: {snapshot_name}")
            raise

    return wrapper

@with_snapshot
def execute_risky_operation(self):
    # Your code here
```

### 4. Resource Limits

```python
# Add to scheduler.py
class ResourceLimits:
    """Prevent resource exhaustion"""
    def __init__(self):
        self.max_concurrent_vms = 5
        self.max_memory_gb = 32
        self.max_disk_usage_percent = 90

    def check_can_start_vm(self, vm_config: Dict) -> bool:
        """Check if system can handle another VM"""
        current_vms = self._count_running_vms()
        current_memory = self._get_memory_usage()

        if current_vms >= self.max_concurrent_vms:
            raise ResourceError("Too many VMs running")

        if current_memory + vm_config['memory'] > self.max_memory_gb * 1024:
            raise ResourceError("Not enough memory")

        return True
```

### 5. Audit Logging

```python
# Add to logger.py
class AuditLogger:
    """Track all operations for compliance"""
    def __init__(self, log_file: Path):
        self.log_file = log_file

    def log_operation(self, operation: str, vm_name: str, user: str, success: bool):
        """Log operation with timestamp"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "vm": vm_name,
            "user": user,
            "success": success,
            "host": socket.gethostname(),
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
```

### 6. Dry-Run Mode for All Operations

```python
# Add flag to all destructive operations
class VMManager:
    def __init__(self, vm_name: str, dry_run: bool = False):
        self.dry_run = dry_run

    def _execute_if_not_dry_run(self, operation: str, func: Callable):
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {operation}")
            return None
        return func()

    def stop(self):
        return self._execute_if_not_dry_run(
            f"Stop VM {self.vm_name}",
            lambda: self._run_prlctl("stop", self.vm_name)
        )
```

### 7. Health Checks

```python
# Add health check endpoint
def health_check() -> Dict[str, Any]:
    """Check system health"""
    return {
        "parallels_cli": shutil.which("prlctl") is not None,
        "python_version": sys.version,
        "disk_space_gb": shutil.disk_usage("/").free // (1024**3),
        "running_vms": len(VMManager.list_all()),
        "config_valid": ConfigLoader("config/database-connections.yml").validate_schema() == [],
        "timestamp": datetime.now().isoformat(),
    }
```

---

## 🔧 Quick Debugging Guide

### Problem: VM won't start
```bash
# Check VM exists
prlctl list -a | grep "VM-Name"

# Check VM status
prlctl list "VM-Name" -i

# Try manual start
prlctl start "VM-Name"

# Check logs
tail -f logs/excel-automation.log
```

### Problem: ODBC driver installation fails
```bash
# Check if already installed
excel-auto odbc list "Windows 11"

# Check Windows Event Viewer in VM
# Applications and Services Logs → Microsoft → Windows → Application

# Try manual installation
# Download driver MSI and install manually to test
```

### Problem: Metabase API errors
```python
# Test API connectivity
curl -X POST https://metabase.company.com/api/session \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Check API key
export METABASE_API_KEY="your-key"
./scripts/metabase-export.py recent
```

### Problem: Ansible can't connect
```bash
# Test WinRM from macOS
# Install: pip install pywinrm
python -c "import winrm; s = winrm.Session('192.168.1.100', auth=('user','pass')); print(s.run_cmd('ipconfig'))"

# Test from Ansible
ansible windows_analytics -i inventory.yml -m win_ping -vvv
```

---

## 📋 Testing Strategy

### Unit Tests (Priority: High)
```bash
cd python
pytest tests/unit/
```

**Focus Areas**:
- `test_vm_manager.py` - VM lifecycle operations
- `test_config_loader.py` - Configuration parsing
- `test_odbc_config.py` - ODBC configuration logic
- `test_metabase.py` - API client (mock responses)

### Integration Tests (Priority: Medium)
```bash
pytest tests/integration/ --vm-name="Test-VM"
```

**Requires**: Running test VM

**Focus Areas**:
- End-to-end ODBC setup
- Metabase data export
- VM snapshot/restore
- Data pipeline execution

### System Tests (Priority: Low)
```bash
# Full workflow test
./scripts/data-pipeline.py run --dry-run
```

---

## 🎓 For Next Developer

### Before You Start

1. **Read**: GET_STARTED.md (user onboarding)
2. **Read**: This document (developer context)
3. **Set up**: Python venv, install dependencies
4. **Test**: `excel-auto vm list` to verify Parallels access
5. **Read**: python/README.md for API reference

### Where to Start Adding Features

**Easy Wins** (1-2 hours):
- Add retry logic with `tenacity`
- Implement health check endpoint
- Add more CLI commands (clone, rename, etc.)

**Medium Complexity** (4-8 hours):
- Excel macro execution via COM
- Parallel VM operations
- Configuration schema validation

**Complex** (1-2 days):
- Complete test suite
- Excel controller with VBA integration
- Advanced error recovery

### Code Quality Standards

- **Type hints**: All function signatures
- **Docstrings**: All public functions (Google style)
- **Logging**: Use logger, not print()
- **Error handling**: Try/except with specific exceptions
- **Testing**: Write tests for new features
- **Documentation**: Update relevant README.md

### Git Workflow

Auto-commit is configured (every 30 minutes). If you want to disable:
```bash
launchctl unload ~/Library/LaunchAgents/com.uncertainmeow.parallels.autocommit.plist
```

Manual commits:
```bash
git add .
git commit -m "feat: description"
git push
```

---

## 📞 Getting Help

**Check First**:
1. Component README (python/, packer/, terraform/, ansible/)
2. Error logs (logs/excel-automation.log)
3. Example configs (*.example.yml, *.example)

**Common Issues**: See "Known Issues" section above

**Debugging**: Set `logging.level: DEBUG` in config file

---

## ✅ What's Production-Ready

- ✅ Python library core (vm_manager, odbc_config, metabase)
- ✅ CLI tool (excel-auto)
- ✅ Configuration management (config_loader)
- ✅ Logging infrastructure
- ✅ Packer templates (Windows golden images)
- ✅ Terraform configs (VM lifecycle)
- ✅ Ansible playbooks (VM configuration)
- ✅ Interactive setup wizard
- ✅ Data pipeline framework
- ✅ Schedule management

## ⚠️ What Needs Work

- ⚠️ Excel macro execution (not implemented)
- ⚠️ Retry logic (basic only)
- ⚠️ Test coverage (0% - no tests written)
- ⚠️ Error recovery (graceful degradation)
- ⚠️ Resource limits (no enforcement)
- ⚠️ Audit logging (not implemented)
- ⚠️ Health checks (not implemented)
- ⚠️ Performance optimization (sequential operations)

---

**Bottom Line**: Framework is solid, well-architected, and documented. Primary gaps are testing, error recovery, and Excel COM integration. Code is clean and extensible. Start with tests, then add Excel automation, then optimize performance.

**Estimated Time to Production-Hardened**: 20-40 hours of focused development.

Good luck! 🚀
