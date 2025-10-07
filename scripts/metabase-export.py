#!/usr/bin/env python3
"""
metabase-export.py - Export data from Metabase questions/dashboards

Standalone script for corporate data pulls from Metabase.
Can be run manually or scheduled via cron.

Usage:
    # Export single question to CSV
    ./metabase-export.py question 123 --output data/report.csv

    # Export multiple questions
    ./metabase-export.py questions 123 456 789 --format excel

    # Export entire dashboard
    ./metabase-export.py dashboard 42 --format csv

    # Schedule via cron (8 AM weekdays)
    0 8 * * 1-5 /path/to/metabase-export.py dashboard 42

Environment Variables:
    METABASE_URL       - Metabase base URL
    METABASE_API_KEY   - API key (recommended)
    METABASE_USERNAME  - Username (if not using API key)
    METABASE_PASSWORD  - Password (if not using API key)
"""

import sys
import os
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from excel_automation import MetabaseClient, MetabaseAutomation, setup_logger

logger = setup_logger("metabase_export")


def get_client_from_env() -> MetabaseClient:
    """Create Metabase client from environment variables"""
    base_url = os.getenv("METABASE_URL")
    if not base_url:
        raise ValueError("METABASE_URL environment variable not set")

    api_key = os.getenv("METABASE_API_KEY")
    username = os.getenv("METABASE_USERNAME")
    password = os.getenv("METABASE_PASSWORD")

    if not api_key and not (username and password):
        raise ValueError(
            "Either METABASE_API_KEY or (METABASE_USERNAME + METABASE_PASSWORD) required"
        )

    return MetabaseClient(
        base_url=base_url,
        api_key=api_key,
        username=username,
        password=password,
    )


def export_question(args):
    """Export single question"""
    client = get_client_from_env()

    output_path = Path(args.output) if args.output else Path(f"question_{args.question_id}.{args.format}")

    if args.format == "csv":
        client.export_question_to_csv(args.question_id, output_path)
    elif args.format == "excel":
        client.export_question_to_excel(args.question_id, output_path)
    else:
        raise ValueError(f"Unsupported format: {args.format}")

    print(f"✓ Exported to: {output_path}")


def export_questions(args):
    """Export multiple questions"""
    client = get_client_from_env()

    output_dir = Path(args.output_dir) if args.output_dir else Path("data/exports")
    automation = MetabaseAutomation(client, output_dir)

    files = automation.scheduled_export(
        question_ids=args.question_ids,
        format=args.format,
        prefix=args.prefix,
    )

    print(f"✓ Exported {len(files)} files to: {output_dir}")
    for f in files:
        print(f"  - {f.name}")


def export_dashboard(args):
    """Export entire dashboard"""
    client = get_client_from_env()

    output_dir = Path(args.output_dir) if args.output_dir else Path("data/dashboards")
    automation = MetabaseAutomation(client, output_dir)

    files = automation.export_dashboard(
        dashboard_id=args.dashboard_id,
        format=args.format,
        include_timestamp=args.timestamp,
    )

    print(f"✓ Exported {len(files)} files")
    for f in files:
        print(f"  - {f}")


def list_recent(args):
    """List recent questions"""
    client = get_client_from_env()

    questions = client.list_recent_questions(limit=args.limit)

    print(f"\nRecent Questions ({len(questions)}):")
    print("-" * 80)

    for item in questions:
        obj = item.get('model_object', {})
        print(f"ID: {obj.get('id')}")
        print(f"Name: {obj.get('name')}")
        print(f"Type: {item.get('model')}")
        print(f"Last viewed: {item.get('timestamp')}")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Export data from Metabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Question command
    question_parser = subparsers.add_parser("question", help="Export single question")
    question_parser.add_argument("question_id", type=int, help="Question/card ID")
    question_parser.add_argument(
        "--output", "-o", help="Output file path (default: question_ID.FORMAT)"
    )
    question_parser.add_argument(
        "--format",
        "-f",
        choices=["csv", "excel"],
        default="csv",
        help="Export format",
    )

    # Questions command (multiple)
    questions_parser = subparsers.add_parser(
        "questions", help="Export multiple questions"
    )
    questions_parser.add_argument(
        "question_ids", type=int, nargs="+", help="Question/card IDs"
    )
    questions_parser.add_argument(
        "--output-dir", "-o", help="Output directory (default: data/exports)"
    )
    questions_parser.add_argument(
        "--format", "-f", choices=["csv", "excel"], default="csv"
    )
    questions_parser.add_argument(
        "--prefix", "-p", default="scheduled", help="Prefix for export directory"
    )

    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Export entire dashboard")
    dashboard_parser.add_argument("dashboard_id", type=int, help="Dashboard ID")
    dashboard_parser.add_argument(
        "--output-dir", "-o", help="Output directory (default: data/dashboards)"
    )
    dashboard_parser.add_argument(
        "--format", "-f", choices=["csv", "excel"], default="csv"
    )
    dashboard_parser.add_argument(
        "--timestamp/--no-timestamp",
        default=True,
        help="Include timestamp in filenames",
    )

    # List recent command
    recent_parser = subparsers.add_parser("recent", help="List recent questions")
    recent_parser.add_argument(
        "--limit", "-l", type=int, default=20, help="Number of questions to list"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "question":
            export_question(args)
        elif args.command == "questions":
            export_questions(args)
        elif args.command == "dashboard":
            export_dashboard(args)
        elif args.command == "recent":
            list_recent(args)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
