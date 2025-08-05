"""
stl_exporter.py

Module for authenticating with the Onshape API, retrieving part IDs by name,
and exporting STL geometry using the Onshape part ID.

This is designed for integration into geometry processing pipelines where parts
are programmatically retrieved from Onshape and converted into usable mesh formats.

Functions:
- create_session: Initializes an authenticated session with custom headers.
- get_part_id: Looks up the part ID for a named part within a given document.
- fetch_stl_content: Downloads raw STL content from Onshape.
- load_stl: High-level function that retrieves STL bytes for a named part.

Author: Marvin Frommer
Date: 2025-07-27
"""

import logging
import requests
import os

from src.constants import BASE_URL, PART_HEADERS, STL_HEADERS

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


def get_part_id(
    part_name: str,
    document_id: str,
    workspace_id: str,
    element_id: str,
    session: requests.Session,
    base_url: str = BASE_URL,
    headers: dict = PART_HEADERS
) -> str:
    """
    Fetch the internal Onshape part ID for a given part name.

    Args:
        part_name (str): The human-readable name of the part as shown in Onshape.
        document_id (str): The Onshape document ID.
        workspace_id (str): The workspace ID (not version/microversion).
        element_id (str): The element (tab) ID containing the part studio.
        session (requests.Session): Authenticated requests session.
        base_url (str, optional): Onshape API base URL.
        headers (dict, optional): Headers for the request.

    Returns:
        str: The part ID (used in subsequent API calls).

    Raises:
        ValueError: If the part name is not found in the document.
    """
    parts_url = f"{base_url}/parts/d/{document_id}/w/{workspace_id}/e/{element_id}"
    original_headers = session.headers.copy()
    session.headers.update(headers)

    try:
        response = session.get(parts_url)
        response.raise_for_status()
        for part in response.json():
            if part["name"] == part_name:
                logger.info(f"Found part '{part_name}' with ID: {part['partId']}")
                return part["partId"]
        raise ValueError(f"Part '{part_name}' not found in the specified document.")
    finally:
        session.headers = original_headers


def fetch_stl_content(
    document_id: str,
    workspace_id: str,
    element_id: str,
    part_id: str,
    session: requests.Session,
    base_url: str = BASE_URL,
) -> bytes:
    """
    Download STL geometry data for a given part as raw bytes.

    Args:
        document_id (str): Onshape document ID.
        workspace_id (str): Onshape workspace ID.
        element_id (str): Onshape element (tab) ID.
        part_id (str): Onshape internal part ID.
        session (requests.Session): Authenticated session.
        base_url (str, optional): Onshape API base URL.

    Returns:
        bytes: The binary STL data.

    Raises:
        RuntimeError: If STL download fails or no redirect is provided.
    """
    url = f"{base_url}/parts/d/{document_id}/w/{workspace_id}/e/{element_id}/partid/{part_id}/stl"

    try:
        response = session.get(url, allow_redirects=False)
        response.raise_for_status()

        if response.status_code in (302, 307):
            redirect_url = response.headers.get("Location")
            if not redirect_url:
                raise RuntimeError("Redirect expected but 'Location' header is missing.")

            logger.info(f"Following redirect to: {redirect_url}")
            stl_response = session.get(redirect_url)
            stl_response.raise_for_status()

            logger.info("STL content fetched successfully.")
            return stl_response.content
        else:
            raise RuntimeError(f"Unexpected response status code: {response.status_code}")

    except requests.RequestException as e:
        logger.error(f"Failed to fetch STL content: {e}")
        raise RuntimeError("Failed to fetch STL content.") from e


def load_stl(
    part_name: str,
    document_id: str,
    workspace_id: str,
    element_id: str,
    access_key: str,
    secret_key: str
) -> bytes:
    """
    High-level function to retrieve STL content for a part using its name.

    Args:
        part_name (str): Name of the part in Onshape.
        document_id (str): Onshape document ID.
        workspace_id (str): Workspace ID containing the part studio.
        element_id (str): Element ID containing the part.
        access_key (str): Onshape access key.
        secret_key (str): Onshape secret key.

    Returns:
        bytes: Binary STL data suitable for saving or further processing.

    Raises:
        ValueError: If the part name is not found.
        RuntimeError: If the STL content cannot be retrieved.
    """
    logger.debug("Creating session for part ID lookup.")
    parts_session = create_session(access_key, secret_key, PART_HEADERS)
    part_id = get_part_id(part_name, document_id, workspace_id, element_id, parts_session)

    logger.debug("Creating session for STL fetch.")
    stl_session = create_session(access_key, secret_key, STL_HEADERS)
    content = fetch_stl_content(document_id, workspace_id, element_id, part_id, stl_session)
    return content
