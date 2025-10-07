#
# Terraform variables for Parallels VMs
#

variable "vm_name" {
  description = "Name of the primary analytics VM"
  type        = string
  default     = "Windows-Analytics"
}

variable "base_image_name" {
  description = "Name of the golden image to clone from"
  type        = string
  default     = "Windows-Analytics-Golden"
}

variable "vm_cpus" {
  description = "Number of CPUs for the VM"
  type        = number
  default     = 4

  validation {
    condition     = var.vm_cpus >= 2 && var.vm_cpus <= 32
    error_message = "CPUs must be between 2 and 32"
  }
}

variable "vm_memory" {
  description = "Memory in MB for the VM"
  type        = number
  default     = 8192

  validation {
    condition     = var.vm_memory >= 2048
    error_message = "Memory must be at least 2048 MB (2 GB)"
  }
}

variable "network_type" {
  description = "Network adapter type"
  type        = string
  default     = "shared"

  validation {
    condition     = contains(["shared", "bridged", "host-only"], var.network_type)
    error_message = "Network type must be shared, bridged, or host-only"
  }
}

variable "shared_folders" {
  description = "Shared folders configuration"
  type = list(object({
    name = string
    path = string
  }))
  default = [
    {
      name = "analytics_data"
      path = "~/Analytics/Data"
    },
    {
      name = "analytics_reports"
      path = "~/Analytics/Reports"
    }
  ]
}

variable "start_on_boot" {
  description = "Start VM automatically on host boot"
  type        = bool
  default     = false
}

variable "create_test_vm" {
  description = "Create a test VM (clone of production)"
  type        = bool
  default     = false
}

variable "project_vms" {
  description = "Additional project-specific VMs to create"
  type = map(object({
    name          = string
    description   = string
    cpus          = number
    memory        = number
    data_path     = string
    start_on_boot = bool
  }))
  default = {}

  # Example:
  # project_vms = {
  #   project_alpha = {
  #     name          = "Analytics-ProjectAlpha"
  #     description   = "Excel analytics for Project Alpha"
  #     cpus          = 4
  #     memory        = 8192
  #     data_path     = "~/Projects/Alpha/Data"
  #     start_on_boot = false
  #   }
  # }
}
