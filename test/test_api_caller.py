import os

from src.stl_exporter import export_step


if __name__ == "__main__":
    document_id = os.environ.get("DOCUMENT_ID")
    workspace_id = os.environ.get("WORKSPACE_ID")
    element_id = os.environ.get("ELEMENT_ID")
    access_key = os.environ.get("ACCESS_KEY")
    secret_key = os.environ.get("SECRET_KEY")

    print(export_step(document_id, workspace_id, element_id, access_key, secret_key))