#!/usr/bin/env python3
"""
data-pipeline.py - Complete data pipeline automation

Orchestrates: Metabase → Excel → Reports workflow

Pipeline Steps:
1. Pull data from Metabase
2. Process/transform data
3. Update Excel workbooks
4. Save reports to shared folder
5. Notify on completion

Usage:
    # Run full pipeline
    ./data-pipeline.py run

    # Dry run (test without executing)
    ./data-pipeline.py run --dry-run

    # Run specific step
    ./data-pipeline.py step metabase-pull

    # Schedule pipeline
    ./data-pipeline.py schedule --cron "every day at 08:00"
"""

import sys
import os
from pathlib import Path
import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from excel_automation import (
    MetabaseClient,
    MetabaseAutomation,
    VMManager,
    ConfigLoader,
    setup_logger,
)

logger = setup_logger("data_pipeline")


class DataPipeline:
    """Automated data pipeline orchestrator"""

    def __init__(self, config_path: Path):
        """
        Initialize pipeline.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config_loader = ConfigLoader(self.config_path)
        self.config = self.config_loader.load()

        # Set up components
        self.metabase_client = None
        self.vm_manager = None

        # Pipeline state
        self.state = {
            "started": None,
            "completed": None,
            "steps_completed": [],
            "errors": [],
        }

    def step_metabase_pull(self, dry_run: bool = False) -> Dict:
        """
        Step 1: Pull data from Metabase.

        Args:
            dry_run: If True, don't actually execute

        Returns:
            Step result dictionary
        """
        logger.info("=" * 80)
        logger.info("STEP 1: Metabase Data Pull")
        logger.info("=" * 80)

        if dry_run:
            logger.info("[DRY RUN] Would pull data from Metabase")
            return {"status": "skipped", "dry_run": True}

        # Get Metabase config
        metabase_config = self.config.get('metabase', {})

        if not metabase_config:
            logger.warning("No Metabase configuration found, skipping")
            return {"status": "skipped", "reason": "not_configured"}

        # Initialize client
        self.metabase_client = MetabaseClient(
            base_url=metabase_config['base_url'],
            api_key=metabase_config.get('api_key'),
            username=metabase_config.get('username'),
            password=metabase_config.get('password'),
        )

        # Get export settings
        export_config = metabase_config.get('export', {})
        output_dir = Path(export_config.get('output_dir', 'data/metabase_exports'))

        automation = MetabaseAutomation(self.metabase_client, output_dir)

        # Pull data based on schedules
        exported_files = []
        schedules = metabase_config.get('schedules', {})

        for schedule_name, schedule_info in schedules.items():
            question_ids = schedule_info.get('question_ids', [])
            format = schedule_info.get('format', 'csv')

            if not question_ids:
                logger.warning(f"Schedule '{schedule_name}' has no question IDs")
                continue

            logger.info(f"Exporting schedule: {schedule_name}")

            files = automation.scheduled_export(
                question_ids=question_ids,
                format=format,
                prefix=schedule_name,
            )

            exported_files.extend(files)

        logger.info(f"✓ Exported {len(exported_files)} files")

        return {
            "status": "success",
            "files_exported": len(exported_files),
            "files": [str(f) for f in exported_files],
        }

    def step_process_data(self, dry_run: bool = False) -> Dict:
        """
        Step 2: Process and transform data.

        Args:
            dry_run: If True, don't actually execute

        Returns:
            Step result dictionary
        """
        logger.info("=" * 80)
        logger.info("STEP 2: Data Processing")
        logger.info("=" * 80)

        if dry_run:
            logger.info("[DRY RUN] Would process data")
            return {"status": "skipped", "dry_run": True}

        # TODO: Add custom data processing logic here
        #
        # Example:
        # - Clean data
        # - Apply transformations
        # - Merge datasets
        # - Calculate metrics

        logger.info("No custom processing configured (placeholder)")

        return {"status": "success", "processed": 0}

    def step_update_excel(self, dry_run: bool = False) -> Dict:
        """
        Step 3: Update Excel workbooks.

        Args:
            dry_run: If True, don't actually execute

        Returns:
            Step result dictionary
        """
        logger.info("=" * 80)
        logger.info("STEP 3: Excel Update")
        logger.info("=" * 80)

        if dry_run:
            logger.info("[DRY RUN] Would update Excel workbooks")
            return {"status": "skipped", "dry_run": True}

        vm_config = self.config.get('vm', {})
        vm_name = vm_config.get('name')

        if not vm_name:
            logger.warning("No VM configured, skipping Excel update")
            return {"status": "skipped", "reason": "no_vm"}

        # Start VM if not running
        self.vm_manager = VMManager(vm_name)

        if not self.vm_manager.is_running():
            logger.info(f"Starting VM: {vm_name}")
            self.vm_manager.start(
                wait=True, wait_seconds=vm_config.get('startup_wait_seconds', 45)
            )

        # TODO: Execute Excel refresh macros
        #
        # Example:
        # vm_manager.execute(
        #     'powershell -Command "excel refresh macro here"'
        # )

        logger.info("Excel refresh not implemented yet (placeholder)")

        return {"status": "success", "workbooks_updated": 0}

    def step_save_reports(self, dry_run: bool = False) -> Dict:
        """
        Step 4: Save reports to shared folder.

        Args:
            dry_run: If True, don't actually execute

        Returns:
            Step result dictionary
        """
        logger.info("=" * 80)
        logger.info("STEP 4: Save Reports")
        logger.info("=" * 80)

        if dry_run:
            logger.info("[DRY RUN] Would save reports")
            return {"status": "skipped", "dry_run": True}

        # TODO: Copy/save reports
        #
        # Example:
        # - Copy Excel files from VM shared folder
        # - Save to network drive
        # - Upload to cloud storage
        # - Archive old versions

        logger.info("Report saving not implemented yet (placeholder)")

        return {"status": "success", "reports_saved": 0}

    def step_notify(self, dry_run: bool = False) -> Dict:
        """
        Step 5: Send notifications.

        Args:
            dry_run: If True, don't actually execute

        Returns:
            Step result dictionary
        """
        logger.info("=" * 80)
        logger.info("STEP 5: Notifications")
        logger.info("=" * 80)

        if dry_run:
            logger.info("[DRY RUN] Would send notifications")
            return {"status": "skipped", "dry_run": True}

        notification_config = self.config.get('automation', {}).get('notifications', {})

        if not notification_config.get('enabled'):
            logger.info("Notifications not enabled")
            return {"status": "skipped", "reason": "disabled"}

        # TODO: Send notifications
        #
        # Example:
        # - Email reports
        # - Slack notifications
        # - Teams messages

        logger.info("Notifications not implemented yet (placeholder)")

        return {"status": "success", "notifications_sent": 0}

    def run_full_pipeline(self, dry_run: bool = False) -> Dict:
        """
        Run the complete pipeline.

        Args:
            dry_run: If True, don't actually execute

        Returns:
            Pipeline results dictionary
        """
        logger.info("╔════════════════════════════════════════════════╗")
        logger.info("║   Starting Data Pipeline                       ║")
        logger.info("╚════════════════════════════════════════════════╝")

        if dry_run:
            logger.info("[DRY RUN MODE - No changes will be made]")

        self.state['started'] = datetime.now().isoformat()

        steps = [
            ("metabase_pull", self.step_metabase_pull),
            ("process_data", self.step_process_data),
            ("update_excel", self.step_update_excel),
            ("save_reports", self.step_save_reports),
            ("notify", self.step_notify),
        ]

        results = {}

        for step_name, step_func in steps:
            try:
                result = step_func(dry_run=dry_run)
                results[step_name] = result

                if result['status'] == 'success':
                    self.state['steps_completed'].append(step_name)
                    logger.info(f"✓ Step completed: {step_name}")
                else:
                    logger.info(f"⊘ Step skipped: {step_name} ({result.get('reason', 'N/A')})")

            except Exception as e:
                logger.error(f"✗ Step failed: {step_name}: {e}", exc_info=True)
                self.state['errors'].append(f"{step_name}: {str(e)}")
                results[step_name] = {"status": "failed", "error": str(e)}

                # Decide whether to continue or stop
                # For now, continue with other steps
                continue

        self.state['completed'] = datetime.now().isoformat()

        # Summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("Pipeline Summary")
        logger.info("=" * 80)
        logger.info(f"Started: {self.state['started']}")
        logger.info(f"Completed: {self.state['completed']}")
        logger.info(f"Steps completed: {len(self.state['steps_completed'])}/{len(steps)}")

        if self.state['errors']:
            logger.error(f"Errors: {len(self.state['errors'])}")
            for error in self.state['errors']:
                logger.error(f"  - {error}")
        else:
            logger.info("✓ No errors")

        return {
            "state": self.state,
            "results": results,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Data pipeline automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("config/database-connections.yml"),
        help="Configuration file",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run full pipeline")
    run_parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")

    # Step command
    step_parser = subparsers.add_parser("step", help="Run specific step")
    step_parser.add_argument(
        "step_name",
        choices=[
            "metabase-pull",
            "process-data",
            "update-excel",
            "save-reports",
            "notify",
        ],
        help="Step to run",
    )
    step_parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        pipeline = DataPipeline(args.config)

        if args.command == "run":
            results = pipeline.run_full_pipeline(dry_run=args.dry_run)

            if results['state']['errors']:
                sys.exit(1)

        elif args.command == "step":
            step_map = {
                "metabase-pull": pipeline.step_metabase_pull,
                "process-data": pipeline.step_process_data,
                "update-excel": pipeline.step_update_excel,
                "save-reports": pipeline.step_save_reports,
                "notify": pipeline.step_notify,
            }

            step_func = step_map[args.step_name]
            result = step_func(dry_run=args.dry_run)

            if result['status'] != 'success':
                sys.exit(1)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
