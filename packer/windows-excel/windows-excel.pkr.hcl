#
# Packer template for Windows 11 + Excel + ODBC Drivers
# Creates a golden image for corporate data analytics
#

packer {
  required_version = ">= 1.9.0"

  required_plugins {
    parallels = {
      version = ">= 1.1.0"
      source  = "github.com/Parallels/parallels"
    }
  }
}

# Variables
variable "iso_url" {
  type    = string
  default = "~/Downloads/Win11_English_x64v1.iso"
  description = "Path to Windows 11 ISO"
}

variable "iso_checksum" {
  type    = string
  default = "file:~/Downloads/Win11_English_x64v1.iso.sha256"
  description = "ISO checksum (sha256:value or file:path)"
}

variable "vm_name" {
  type    = string
  default = "Windows-Analytics-Golden"
  description = "VM name"
}

variable "vm_memory" {
  type    = number
  default = 8192
  description = "Memory in MB"
}

variable "vm_cpus" {
  type    = number
  default = 4
  description = "Number of CPUs"
}

variable "vm_disk_size" {
  type    = number
  default = 65536
  description = "Disk size in MB"
}

variable "winrm_username" {
  type    = string
  default = "vagrant"
  description = "Windows username for provisioning"
}

variable "winrm_password" {
  type      = string
  default   = "vagrant"
  sensitive = true
  description = "Windows password for provisioning"
}

# Source configuration
source "parallels-iso" "windows11" {
  # ISO configuration
  iso_url      = var.iso_url
  iso_checksum = var.iso_checksum

  # VM configuration
  vm_name         = var.vm_name
  guest_os_type   = "win-11"
  memory          = var.vm_memory
  cpus            = var.vm_cpus
  disk_size       = var.vm_disk_size
  disk_type       = "expand"

  # Parallels configuration
  parallels_tools_flavor = "win"
  parallels_tools_mode   = "attach"

  # Unattended installation
  floppy_files = [
    "autounattend.xml",
    "scripts/disable-winrm.ps1",
    "scripts/enable-winrm.ps1",
  ]

  # Boot configuration
  boot_wait = "3s"
  boot_command = [
    "<enter>"
  ]

  # WinRM configuration
  communicator     = "winrm"
  winrm_username   = var.winrm_username
  winrm_password   = var.winrm_password
  winrm_timeout    = "8h"
  winrm_use_ssl    = false
  winrm_insecure   = true

  # Shutdown
  shutdown_command = "shutdown /s /t 10 /f /d p:4:1 /c \"Packer Shutdown\""
  shutdown_timeout = "15m"

  # Output
  output_directory = "output-${var.vm_name}"
}

# Build
build {
  sources = ["source.parallels-iso.windows11"]

  # Wait for Windows installation
  provisioner "powershell" {
    inline = [
      "Write-Host 'Waiting for Windows to be ready...'",
      "Start-Sleep -Seconds 30"
    ]
  }

  # Install Chocolatey (package manager)
  provisioner "powershell" {
    script = "scripts/install-chocolatey.ps1"
  }

  # Windows updates
  provisioner "powershell" {
    script           = "scripts/install-windows-updates.ps1"
    elevated_user    = var.winrm_username
    elevated_password = var.winrm_password
  }

  # Install ODBC drivers
  provisioner "powershell" {
    scripts = [
      "scripts/install-postgresql-odbc.ps1",
      "scripts/install-mysql-odbc.ps1",
      "scripts/install-sqlserver-odbc.ps1",
    ]
  }

  # Install development tools (optional)
  provisioner "powershell" {
    script = "scripts/install-dev-tools.ps1"
  }

  # Configure Windows
  provisioner "powershell" {
    scripts = [
      "scripts/configure-windows.ps1",
      "scripts/configure-power-settings.ps1",
    ]
  }

  # Install Office/Excel
  # NOTE: This requires an Office installer or license
  # Uncomment if you have Office setup file
  # provisioner "powershell" {
  #   script = "scripts/install-office.ps1"
  # }

  # Cleanup
  provisioner "powershell" {
    scripts = [
      "scripts/cleanup-temp.ps1",
      "scripts/cleanup-windows.ps1",
    ]
  }

  # Defragment and compact
  provisioner "powershell" {
    inline = [
      "Optimize-Volume -DriveLetter C -Defrag -Verbose",
      "Write-Host 'Disk optimized'"
    ]
  }

  # Final message
  provisioner "powershell" {
    inline = [
      "Write-Host '╔════════════════════════════════════════════════╗'",
      "Write-Host '║   Golden Image Build Complete!                 ║'",
      "Write-Host '╚════════════════════════════════════════════════╝'",
      "Write-Host ''",
      "Write-Host 'Installed components:'",
      "Write-Host '  - Windows 11'",
      "Write-Host '  - Parallels Tools'",
      "Write-Host '  - PostgreSQL ODBC Driver'",
      "Write-Host '  - MySQL ODBC Driver'",
      "Write-Host '  - SQL Server ODBC Driver'",
      "Write-Host '  - Chocolatey package manager'",
      "Write-Host '  - Development tools'",
      "Write-Host ''",
      "Write-Host 'Next steps:'",
      "Write-Host '  1. Install Office/Excel manually or via script'",
      "Write-Host '  2. Configure ODBC DSNs'",
      "Write-Host '  3. Clone this VM for your projects'",
      "Write-Host ''"
    ]
  }

  # Post-processors
  post-processor "manifest" {
    output     = "manifest.json"
    strip_path = true
  }
}
