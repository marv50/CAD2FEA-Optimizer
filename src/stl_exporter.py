"""
partstudio_exporter.py

Module for authenticating with the Onshape API and exporting entire part studios
as STEP files using the Onshape part studio export endpoint.

This is designed for integration into geometry processing pipelines where entire
part studios are programmatically retrieved from Onshape and converted into usable formats.

Functions:
- create_session: Initializes an authenticated session with custom headers.
- fetch_step_content: Downloads raw STEP content from Onshape part studio.
- export_partstudio: High-level function that retrieves STEP bytes for an entire part studio.

Author: Marvin Frommer
Date: 2025-07-27
"""

import logging
import requests
import os

from src.constants import BASE_URL, STEP_HEADERS

logger = logging.getLogger(__name__)


def create_session(access_key: str, secret_key: str, headers: dict) -> requests.Session:
    """
    Create an authenticated HTTP session using Onshape API credentials.

    Args:
        access_key (str): Onshape API access key.
        secret_key (str): Onshape API secret key.
        headers (dict): Headers to apply to the session (e.g., accept or content-type).

    Returns:
        requests.Session: Configured session with credentials and headers.
    """
    session = requests.Session()
    session.auth = (access_key, secret_key)
    session.headers.update(headers)
    return session


def fetch_step_content(
    document_id: str,
    workspace_id: str,
    element_id: str,
    session: requests.Session,
    base_url: str = BASE_URL,
) -> bytes:
    """
    Download STEP geometry data for an entire part studio as raw bytes.

    Args:
        document_id (str): Onshape document ID.
        workspace_id (str): Onshape workspace ID.
        element_id (str): Onshape element (tab) ID for the part studio.
        session (requests.Session): Authenticated session.
        base_url (str, optional): Onshape API base URL.

    Returns:
        bytes: The binary STEP data.

    Raises:
        RuntimeError: If STEP download fails or no redirect is provided.
    """
    url = f"{base_url}/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/export/step"

    try:
        response = session.get(url, allow_redirects=False)
        response.raise_for_status()

        if response.status_code in (302, 307):
            redirect_url = response.headers.get("Location")
            if not redirect_url:
                raise RuntimeError("Redirect expected but 'Location' header is missing.")

            logger.info(f"Following redirect to: {redirect_url}")
            step_response = session.get(redirect_url)
            step_response.raise_for_status()

            logger.info("STEP content fetched successfully.")
            return step_response.content
        else:
            raise RuntimeError(f"Unexpected response status code: {response.status_code}")

    except requests.RequestException as e:
        logger.error(f"Failed to fetch STEP content: {e}")
        raise RuntimeError("Failed to fetch STEP content.") from e


def export_step(
    document_id: str,
    workspace_id: str,
    element_id: str,
    access_key: str,
    secret_key: str
) -> bytes:
    """
    High-level function to retrieve STEP content for an entire part studio.

    Args:
        document_id (str): Onshape document ID.
        workspace_id (str): Workspace ID containing the part studio.
        element_id (str): Element ID of the part studio to export.
        access_key (str): Onshape access key.
        secret_key (str): Onshape secret key.

    Returns:
        bytes: Binary STEP data suitable for saving or further processing.

    Raises:
        RuntimeError: If the STEP content cannot be retrieved.
    """
    logger.debug("Creating session for part studio export.")
    session = create_session(access_key, secret_key, STEP_HEADERS)
    content = fetch_step_content(document_id, workspace_id, element_id, session)
    return content