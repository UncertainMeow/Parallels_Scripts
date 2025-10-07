#!/usr/bin/env bash
#
# vm-manager.sh - Parallels VM management utility
# Similar to pve-utils but for local Parallels Desktop VMs
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if prlctl is available
check_parallels() {
    if ! command -v prlctl &> /dev/null; then
        echo -e "${RED}Error: prlctl not found. Make sure Parallels Desktop Pro/Business is installed.${NC}"
        exit 1
    fi
}

# Print colored message
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# List all VMs with status
list_vms() {
    log_info "Listing all Parallels VMs..."
    echo
    prlctl list -a -o name,status,os,ip,uptime --no-header | while IFS= read -r line; do
        if echo "$line" | grep -q "running"; then
            echo -e "${GREEN}●${NC} $line"
        elif echo "$line" | grep -q "stopped"; then
            echo -e "${RED}○${NC} $line"
        else
            echo -e "${YELLOW}◐${NC} $line"
        fi
    done
    echo
}

# Get detailed info about a VM
info_vm() {
    local vm_name="$1"
    log_info "Getting info for VM: $vm_name"
    prlctl list "$vm_name" -i
}

# Start a VM
start_vm() {
    local vm_name="$1"
    log_info "Starting VM: $vm_name"
    prlctl start "$vm_name"
    log_success "VM $vm_name started"
}

# Stop a VM
stop_vm() {
    local vm_name="$1"
    log_info "Stopping VM: $vm_name"
    prlctl stop "$vm_name"
    log_success "VM $vm_name stopped"
}

# Create snapshot
snapshot_vm() {
    local vm_name="$1"
    local snapshot_name="${2:-auto_$(date +%Y%m%d_%H%M%S)}"
    log_info "Creating snapshot '$snapshot_name' for VM: $vm_name"
    prlctl snapshot "$vm_name" --name "$snapshot_name" --description "Created by vm-manager.sh"
    log_success "Snapshot created: $snapshot_name"
}

# List snapshots
list_snapshots() {
    local vm_name="$1"
    log_info "Snapshots for VM: $vm_name"
    prlctl snapshot-list "$vm_name"
}

# Restore snapshot
restore_snapshot() {
    local vm_name="$1"
    local snapshot_id="$2"
    log_warning "Restoring snapshot $snapshot_id for VM: $vm_name"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        prlctl snapshot-switch "$vm_name" --id "$snapshot_id"
        log_success "Snapshot restored"
    else
        log_info "Cancelled"
    fi
}

# Execute command in VM
exec_vm() {
    local vm_name="$1"
    shift
    local command="$*"
    log_info "Executing in VM $vm_name: $command"
    prlctl exec "$vm_name" $command
}

# Get VM stats
stats_vm() {
    local vm_name="$1"
    log_info "Resource usage for VM: $vm_name"
    prlctl statistics "$vm_name"
}

# Clone VM
clone_vm() {
    local source_vm="$1"
    local new_vm="$2"
    log_info "Cloning $source_vm to $new_vm"
    prlctl clone "$source_vm" --name "$new_vm"
    log_success "VM cloned: $new_vm"
}

# Rotate snapshots (keep last N)
rotate_snapshots() {
    local vm_name="$1"
    local keep="${2:-7}"
    log_info "Rotating snapshots for $vm_name (keeping last $keep)"

    # Get snapshot count
    local count=$(prlctl snapshot-list "$vm_name" 2>/dev/null | grep -c "^{" || true)

    if [ "$count" -gt "$keep" ]; then
        local to_delete=$((count - keep))
        log_info "Found $count snapshots, will delete oldest $to_delete"

        # Get oldest snapshot IDs (this is simplified, may need adjustment)
        prlctl snapshot-list "$vm_name" | grep "^{" | head -n "$to_delete" | while read -r line; do
            local snap_id=$(echo "$line" | grep -oP '\{\K[^}]+')
            log_info "Deleting snapshot: $snap_id"
            prlctl snapshot-delete "$vm_name" --id "$snap_id"
        done
        log_success "Snapshot rotation complete"
    else
        log_info "Only $count snapshots, no rotation needed"
    fi
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
    list                        List all VMs with status
    info <vm_name>             Show detailed VM information
    start <vm_name>            Start a VM
    stop <vm_name>             Stop a VM
    snapshot <vm_name> [name]  Create a snapshot
    snapshots <vm_name>        List snapshots
    restore <vm_name> <snap_id> Restore a snapshot
    exec <vm_name> <command>   Execute command in VM
    stats <vm_name>            Show VM resource statistics
    clone <source> <new_name>  Clone a VM
    rotate <vm_name> [keep]    Rotate snapshots (default: keep 7)

Examples:
    $0 list
    $0 start "Windows 11"
    $0 snapshot "Windows 11" "before_updates"
    $0 exec "Ubuntu Dev" "df -h"
    $0 rotate "Windows 11" 5

EOF
}

# Main
main() {
    check_parallels

    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi

    local command="$1"
    shift

    case "$command" in
        list)
            list_vms
            ;;
        info)
            [ $# -eq 0 ] && { log_error "VM name required"; exit 1; }
            info_vm "$1"
            ;;
        start)
            [ $# -eq 0 ] && { log_error "VM name required"; exit 1; }
            start_vm "$1"
            ;;
        stop)
            [ $# -eq 0 ] && { log_error "VM name required"; exit 1; }
            stop_vm "$1"
            ;;
        snapshot)
            [ $# -eq 0 ] && { log_error "VM name required"; exit 1; }
            snapshot_vm "$@"
            ;;
        snapshots)
            [ $# -eq 0 ] && { log_error "VM name required"; exit 1; }
            list_snapshots "$1"
            ;;
        restore)
            [ $# -lt 2 ] && { log_error "VM name and snapshot ID required"; exit 1; }
            restore_snapshot "$1" "$2"
            ;;
        exec)
            [ $# -lt 2 ] && { log_error "VM name and command required"; exit 1; }
            exec_vm "$@"
            ;;
        stats)
            [ $# -eq 0 ] && { log_error "VM name required"; exit 1; }
            stats_vm "$1"
            ;;
        clone)
            [ $# -lt 2 ] && { log_error "Source VM and new name required"; exit 1; }
            clone_vm "$1" "$2"
            ;;
        rotate)
            [ $# -eq 0 ] && { log_error "VM name required"; exit 1; }
            rotate_snapshots "$@"
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
