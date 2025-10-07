#
# Terraform configuration for Parallels Desktop VMs
# Manages VM lifecycle declaratively
#

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    parallels = {
      source  = "Parallels/parallels"
      version = "~> 1.0"
    }
  }
}

# Provider configuration
provider "parallels" {
  # No configuration needed - uses local Parallels Desktop
}

# Excel Analytics VM
resource "parallels_vm" "excel_analytics" {
  name        = var.vm_name
  description = "Excel + Data Analytics VM for corporate reporting"

  # Use golden image if available, otherwise create from scratch
  base_image = var.base_image_name

  # Resources
  cpus   = var.vm_cpus
  memory = var.vm_memory

  # Networking
  network_adapter {
    type = var.network_type  # shared, bridged, host-only
  }

  # Shared folders
  dynamic "shared_folder" {
    for_each = var.shared_folders
    content {
      name = shared_folder.value.name
      path = shared_folder.value.path
    }
  }

  # Start on boot
  start_on_boot = var.start_on_boot

  # Lifecycle
  lifecycle {
    ignore_changes = [
      # Ignore these to prevent recreation on minor changes
      description,
    ]
  }
}

# Optional: Dev/Test VM (clone of production)
resource "parallels_vm" "excel_test" {
  count = var.create_test_vm ? 1 : 0

  name        = "${var.vm_name}-Test"
  description = "Test environment for ${var.vm_name}"

  # Clone from production VM
  base_image = parallels_vm.excel_analytics.name

  # Lower resources for test
  cpus   = var.vm_cpus / 2
  memory = var.vm_memory / 2

  network_adapter {
    type = var.network_type
  }

  start_on_boot = false
}

# Optional: Multiple project VMs
resource "parallels_vm" "project_vms" {
  for_each = var.project_vms

  name        = each.value.name
  description = each.value.description

  # Clone from golden image
  base_image = var.base_image_name

  cpus   = each.value.cpus
  memory = each.value.memory

  network_adapter {
    type = var.network_type
  }

  shared_folder {
    name = "project_data"
    path = each.value.data_path
  }

  start_on_boot = each.value.start_on_boot
}

# Outputs
output "analytics_vm_name" {
  description = "Name of the analytics VM"
  value       = parallels_vm.excel_analytics.name
}

output "analytics_vm_status" {
  description = "Status of the analytics VM"
  value       = parallels_vm.excel_analytics.status
}

output "analytics_vm_ip" {
  description = "IP address of the analytics VM"
  value       = parallels_vm.excel_analytics.ip_address
}

output "test_vm_name" {
  description = "Name of the test VM (if created)"
  value       = var.create_test_vm ? parallels_vm.excel_test[0].name : null
}

output "project_vm_names" {
  description = "Names of project VMs"
  value       = { for k, v in parallels_vm.project_vms : k => v.name }
}
