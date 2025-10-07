#!/usr/bin/env bash
#
# schedule-manager.sh - Manage scheduled data pipeline jobs
#
# Makes it easy to set up cron jobs for automated data pulls
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

show_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════╗"
    echo "║   Schedule Manager - Automated Data Pulls     ║"
    echo "╚════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# List current cron jobs
list_schedules() {
    echo -e "\n${BOLD}Current Scheduled Jobs:${NC}\n"

    # Get current crontab
    if crontab -l 2>/dev/null | grep -q "data-pipeline\|metabase-export"; then
        crontab -l | grep "data-pipeline\|metabase-export" | while read -r line; do
            echo -e "  ${GREEN}✓${NC} $line"
        done
    else
        echo -e "  ${YELLOW}No scheduled jobs found${NC}"
    fi

    echo ""
}

# Add schedule
add_schedule() {
    local schedule_type="$1"

    echo -e "\n${BOLD}Add New Schedule${NC}\n"

    # Choose schedule type
    if [[ -z "$schedule_type" ]]; then
        echo "Schedule types:"
        echo "  1) Full data pipeline"
        echo "  2) Metabase export only"
        read -p "Choose (1-2): " -n 1 -r
        echo ""

        case $REPLY in
            1) schedule_type="pipeline" ;;
            2) schedule_type="metabase" ;;
            *) echo "Invalid choice"; exit 1 ;;
        esac
    fi

    # Choose frequency
    echo ""
    echo "Frequency:"
    echo "  1) Every hour"
    echo "  2) Daily at specific time"
    echo "  3) Weekdays at specific time"
    echo "  4) Custom cron expression"
    read -p "Choose (1-4): " -n 1 -r
    echo ""

    local cron_expr=""

    case $REPLY in
        1)
            # Every hour
            cron_expr="0 * * * *"
            ;;
        2)
            # Daily at specific time
            read -p "Time (HH:MM, e.g., 08:00): " time_str
            hour=$(echo "$time_str" | cut -d: -f1)
            minute=$(echo "$time_str" | cut -d: -f2)
            cron_expr="$minute $hour * * *"
            ;;
        3)
            # Weekdays at specific time
            read -p "Time (HH:MM, e.g., 08:00): " time_str
            hour=$(echo "$time_str" | cut -d: -f1)
            minute=$(echo "$time_str" | cut -d: -f2)
            cron_expr="$minute $hour * * 1-5"
            ;;
        4)
            # Custom
            read -p "Cron expression (e.g., '0 */6 * * *'): " cron_expr
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac

    # Build command
    local command=""

    if [[ "$schedule_type" == "pipeline" ]]; then
        command="cd $REPO_DIR && $SCRIPT_DIR/data-pipeline.py run >> logs/pipeline.log 2>&1"
    elif [[ "$schedule_type" == "metabase" ]]; then
        read -p "Dashboard ID (or question IDs separated by space): " ids
        command="cd $REPO_DIR && $SCRIPT_DIR/metabase-export.py dashboard $ids >> logs/metabase-export.log 2>&1"
    fi

    # Show preview
    echo ""
    echo -e "${BOLD}Preview:${NC}"
    echo -e "  ${CYAN}$cron_expr $command${NC}"
    echo ""
    read -p "Add this schedule? (Y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Cancelled"
        exit 0
    fi

    # Add to crontab
    (crontab -l 2>/dev/null; echo "$cron_expr $command") | crontab -

    echo -e "${GREEN}✓ Schedule added${NC}"
}

# Remove schedule
remove_schedule() {
    echo -e "\n${BOLD}Remove Schedule${NC}\n"

    # List jobs with numbers
    local jobs=()
    while IFS= read -r line; do
        jobs+=("$line")
    done < <(crontab -l 2>/dev/null | grep "data-pipeline\|metabase-export")

    if [[ ${#jobs[@]} -eq 0 ]]; then
        echo "No scheduled jobs found"
        return
    fi

    # Show jobs
    for i in "${!jobs[@]}"; do
        echo "  $((i+1))) ${jobs[$i]}"
    done

    echo ""
    read -p "Job number to remove (or 'all'): " choice

    if [[ "$choice" == "all" ]]; then
        # Remove all data pipeline jobs
        crontab -l 2>/dev/null | grep -v "data-pipeline\|metabase-export" | crontab -
        echo -e "${GREEN}✓ All schedules removed${NC}"
    elif [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -ge 1 ]] && [[ $choice -le ${#jobs[@]} ]]; then
        # Remove specific job
        local job_to_remove="${jobs[$((choice-1))]}"
        crontab -l 2>/dev/null | grep -v -F "$job_to_remove" | crontab -
        echo -e "${GREEN}✓ Schedule removed${NC}"
    else
        echo "Invalid choice"
        exit 1
    fi
}

# Enable/disable schedules
toggle_schedules() {
    local action="$1"

    echo -e "\n${BOLD}${action^} Schedules${NC}\n"

    if [[ "$action" == "disable" ]]; then
        # Comment out jobs
        crontab -l 2>/dev/null | sed 's/^\([^#].*data-pipeline\|.*metabase-export\)/# \1/' | crontab -
        echo -e "${YELLOW}✓ Schedules disabled (commented out)${NC}"
    elif [[ "$action" == "enable" ]]; then
        # Uncomment jobs
        crontab -l 2>/dev/null | sed 's/^# \(.*data-pipeline\|.*metabase-export\)/\1/' | crontab -
        echo -e "${GREEN}✓ Schedules enabled (uncommented)${NC}"
    fi
}

# Show logs
show_logs() {
    local log_type="$1"

    echo -e "\n${BOLD}Logs${NC}\n"

    if [[ "$log_type" == "pipeline" ]]; then
        if [[ -f "$REPO_DIR/logs/pipeline.log" ]]; then
            tail -50 "$REPO_DIR/logs/pipeline.log"
        else
            echo "No pipeline logs found"
        fi
    elif [[ "$log_type" == "metabase" ]]; then
        if [[ -f "$REPO_DIR/logs/metabase-export.log" ]]; then
            tail -50 "$REPO_DIR/logs/metabase-export.log"
        else
            echo "No Metabase export logs found"
        fi
    else
        echo "Available logs:"
        echo "  ./schedule-manager.sh logs pipeline"
        echo "  ./schedule-manager.sh logs metabase"
    fi
}

# Test schedule
test_schedule() {
    echo -e "\n${BOLD}Test Schedule (Dry Run)${NC}\n"

    echo "Running data pipeline in dry-run mode..."
    echo ""

    cd "$REPO_DIR"
    "$SCRIPT_DIR/data-pipeline.py" run --dry-run

    echo ""
    echo -e "${GREEN}✓ Dry run complete${NC}"
}

# Show usage
show_usage() {
    cat << EOF
${BOLD}Schedule Manager - Automated Data Pipeline${NC}

Usage: $0 <command> [options]

Commands:
    list                List all scheduled jobs
    add [type]          Add new schedule (type: pipeline|metabase)
    remove              Remove a schedule
    disable             Disable all schedules (comment out)
    enable              Enable all schedules (uncomment)
    test                Test pipeline in dry-run mode
    logs [type]         Show logs (type: pipeline|metabase)

Examples:
    $0 list
    $0 add pipeline
    $0 remove
    $0 disable
    $0 logs pipeline

Common Schedules:
    Morning reports:    0 8 * * 1-5    (8 AM weekdays)
    Every hour:         0 * * * *
    Every 6 hours:      0 */6 * * *
    Daily at noon:      0 12 * * *

EOF
}

# Main
main() {
    show_banner

    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi

    case "$1" in
        list)
            list_schedules
            ;;
        add)
            add_schedule "${2:-}"
            ;;
        remove)
            remove_schedule
            ;;
        disable)
            toggle_schedules "disable"
            ;;
        enable)
            toggle_schedules "enable"
            ;;
        test)
            test_schedule
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        *)
            echo "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
