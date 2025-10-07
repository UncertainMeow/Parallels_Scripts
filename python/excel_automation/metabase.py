"""
Metabase integration for automated data pulls
Supports both Metabase API and direct database access
"""

import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from datetime import datetime
from .logger import setup_logger

logger = setup_logger(__name__)


class MetabaseClient:
    """Client for Metabase API"""

    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Metabase client.

        Args:
            base_url: Metabase base URL (e.g., https://metabase.company.com)
            username: Metabase username (if using password auth)
            password: Metabase password (if using password auth)
            api_key: Metabase API key (preferred method)

        Note:
            Either (username + password) OR api_key must be provided
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session_token = None

        if api_key:
            self.session.headers['X-Metabase-Session'] = api_key
            logger.info("Initialized with API key")
        elif username and password:
            self._login(username, password)
        else:
            raise ValueError("Either api_key or (username + password) required")

    def _login(self, username: str, password: str) -> None:
        """Authenticate with username/password"""
        logger.info(f"Logging in to Metabase as {username}")

        response = self.session.post(
            f"{self.base_url}/api/session",
            json={"username": username, "password": password},
        )

        if response.status_code != 200:
            raise RuntimeError(f"Failed to authenticate: {response.text}")

        data = response.json()
        self.session_token = data['id']
        self.session.headers['X-Metabase-Session'] = self.session_token

        logger.info("✓ Authenticated successfully")

    def get_question(self, question_id: int) -> Dict[str, Any]:
        """
        Get question metadata.

        Args:
            question_id: Metabase question/card ID

        Returns:
            Question metadata dictionary
        """
        logger.debug(f"Fetching question: {question_id}")

        response = self.session.get(f"{self.base_url}/api/card/{question_id}")
        response.raise_for_status()

        return response.json()

    def run_question(
        self, question_id: int, parameters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Run a Metabase question and return results as DataFrame.

        Args:
            question_id: Metabase question/card ID
            parameters: Optional parameters for the question

        Returns:
            pandas DataFrame with query results
        """
        logger.info(f"Running question: {question_id}")

        # Build request
        url = f"{self.base_url}/api/card/{question_id}/query"

        payload = {}
        if parameters:
            payload['parameters'] = parameters

        # Execute query
        response = self.session.post(
            url, json=payload if payload else None, timeout=300
        )

        if response.status_code != 202 and response.status_code != 200:
            raise RuntimeError(f"Query failed: {response.text}")

        data = response.json()

        # Check if results are in the response
        if 'data' in data:
            return self._parse_results(data['data'])

        # If async, need to poll for results (Metabase Cloud)
        if 'id' in data:
            return self._poll_for_results(data['id'])

        raise RuntimeError("Unexpected response format")

    def _parse_results(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse Metabase query results into DataFrame"""
        if 'rows' not in data or 'cols' not in data:
            raise ValueError("Invalid result format")

        rows = data['rows']
        cols = [col['name'] for col in data['cols']]

        logger.info(f"✓ Query returned {len(rows)} rows, {len(cols)} columns")

        return pd.DataFrame(rows, columns=cols)

    def _poll_for_results(self, query_id: str, timeout: int = 300) -> pd.DataFrame:
        """Poll for async query results (Metabase Cloud)"""
        import time

        logger.info(f"Polling for results (query ID: {query_id})")

        start = time.time()
        while time.time() - start < timeout:
            response = self.session.get(
                f"{self.base_url}/api/card/{query_id}/query/execution"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'completed':
                    return self._parse_results(data['data'])

            time.sleep(2)  # Poll every 2 seconds

        raise TimeoutError(f"Query did not complete within {timeout}s")

    def export_question_to_csv(
        self,
        question_id: int,
        output_path: Path,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Export question results to CSV file.

        Args:
            question_id: Metabase question/card ID
            output_path: Path to save CSV file
            parameters: Optional parameters for the question
        """
        logger.info(f"Exporting question {question_id} to CSV")

        df = self.run_question(question_id, parameters)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, index=False)

        logger.info(f"✓ Exported to: {output_path} ({len(df)} rows)")

    def export_question_to_excel(
        self,
        question_id: int,
        output_path: Path,
        parameters: Optional[Dict[str, Any]] = None,
        sheet_name: str = "Data",
    ) -> None:
        """
        Export question results to Excel file.

        Args:
            question_id: Metabase question/card ID
            output_path: Path to save Excel file
            parameters: Optional parameters for the question
            sheet_name: Excel sheet name
        """
        logger.info(f"Exporting question {question_id} to Excel")

        df = self.run_question(question_id, parameters)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(output_path, sheet_name=sheet_name, index=False)

        logger.info(f"✓ Exported to: {output_path} ({len(df)} rows)")

    def list_recent_questions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List recently viewed questions.

        Args:
            limit: Maximum number of questions to return

        Returns:
            List of question dictionaries
        """
        logger.info("Fetching recent questions")

        response = self.session.get(
            f"{self.base_url}/api/activity/recent_views", params={"limit": limit}
        )
        response.raise_for_status()

        data = response.json()

        # Filter for questions/cards
        questions = [
            item for item in data if item.get('model') == 'card' and 'model_object' in item
        ]

        logger.info(f"Found {len(questions)} recent questions")

        return questions

    def get_collection(self, collection_id: int) -> Dict[str, Any]:
        """
        Get collection metadata and items.

        Args:
            collection_id: Collection ID

        Returns:
            Collection dictionary with items
        """
        logger.info(f"Fetching collection: {collection_id}")

        response = self.session.get(
            f"{self.base_url}/api/collection/{collection_id}/items"
        )
        response.raise_for_status()

        data = response.json()
        logger.info(f"Collection has {len(data.get('data', []))} items")

        return data


class MetabaseAutomation:
    """High-level automation for Metabase data pulls"""

    def __init__(self, client: MetabaseClient, output_dir: Path):
        """
        Initialize Metabase automation.

        Args:
            client: MetabaseClient instance
            output_dir: Directory to save exported data
        """
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_dashboard(
        self,
        dashboard_id: int,
        format: str = "csv",
        include_timestamp: bool = True,
    ) -> List[Path]:
        """
        Export all questions from a dashboard.

        Args:
            dashboard_id: Dashboard ID
            format: Export format ('csv' or 'excel')
            include_timestamp: Include timestamp in filenames

        Returns:
            List of exported file paths
        """
        logger.info(f"Exporting dashboard: {dashboard_id}")

        # Get dashboard metadata
        response = self.client.session.get(
            f"{self.client.base_url}/api/dashboard/{dashboard_id}"
        )
        response.raise_for_status()
        dashboard = response.json()

        dashboard_name = dashboard.get('name', f'dashboard_{dashboard_id}')
        dashboard_name = self._sanitize_filename(dashboard_name)

        # Create dashboard directory
        dashboard_dir = self.output_dir / dashboard_name
        dashboard_dir.mkdir(parents=True, exist_ok=True)

        # Export each card/question
        exported_files = []
        cards = dashboard.get('ordered_cards', [])

        logger.info(f"Dashboard has {len(cards)} cards")

        for i, card in enumerate(cards, 1):
            card_data = card.get('card')
            if not card_data:
                continue

            question_id = card_data.get('id')
            question_name = card_data.get('name', f'question_{question_id}')
            question_name = self._sanitize_filename(question_name)

            # Build filename
            timestamp = f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if include_timestamp else ""
            filename = f"{i:02d}_{question_name}{timestamp}.{format}"
            filepath = dashboard_dir / filename

            try:
                if format == "csv":
                    self.client.export_question_to_csv(question_id, filepath)
                elif format == "excel":
                    self.client.export_question_to_excel(question_id, filepath)
                else:
                    raise ValueError(f"Unsupported format: {format}")

                exported_files.append(filepath)

            except Exception as e:
                logger.error(f"Failed to export question {question_id}: {e}")

        logger.info(f"✓ Exported {len(exported_files)} files to: {dashboard_dir}")

        return exported_files

    def scheduled_export(
        self,
        question_ids: List[int],
        format: str = "csv",
        prefix: str = "scheduled",
    ) -> List[Path]:
        """
        Export multiple questions (for scheduled jobs).

        Args:
            question_ids: List of question IDs to export
            format: Export format ('csv' or 'excel')
            prefix: Prefix for output directory

        Returns:
            List of exported file paths
        """
        logger.info(f"Starting scheduled export of {len(question_ids)} questions")

        # Create timestamped directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_dir = self.output_dir / f"{prefix}_{timestamp}"
        export_dir.mkdir(parents=True, exist_ok=True)

        exported_files = []

        for question_id in question_ids:
            try:
                # Get question name
                question = self.client.get_question(question_id)
                question_name = self._sanitize_filename(
                    question.get('name', f'question_{question_id}')
                )

                filename = f"{question_name}.{format}"
                filepath = export_dir / filename

                if format == "csv":
                    self.client.export_question_to_csv(question_id, filepath)
                elif format == "excel":
                    self.client.export_question_to_excel(question_id, filepath)

                exported_files.append(filepath)

            except Exception as e:
                logger.error(f"Failed to export question {question_id}: {e}")

        logger.info(f"✓ Scheduled export complete: {len(exported_files)} files")

        return exported_files

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename by removing invalid characters"""
        import re

        # Remove or replace invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '_', name)

        # Remove leading/trailing spaces and dots
        name = name.strip(' .')

        # Limit length
        return name[:200]


def create_metabase_client_from_config(config: Dict[str, Any]) -> MetabaseClient:
    """
    Create Metabase client from configuration dictionary.

    Args:
        config: Configuration with 'metabase' section

    Returns:
        Configured MetabaseClient instance
    """
    metabase_config = config.get('metabase', {})

    if not metabase_config:
        raise ValueError("No 'metabase' configuration found")

    return MetabaseClient(
        base_url=metabase_config['base_url'],
        username=metabase_config.get('username'),
        password=metabase_config.get('password'),
        api_key=metabase_config.get('api_key'),
    )
