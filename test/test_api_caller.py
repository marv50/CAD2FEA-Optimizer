from src.stl_exporter import export_stl


if __name__ == "__main__":
    document_id = "09cf0ee61914100ec39440a9"
    workspace_id = "07172f0d512ee81101f9c748"
    element_id = "df4b6b0423cad0839d8cffd7"
    part_name = "Part 2"  # Replace with actual part name
    access_key = "Gd67t87dCpZlJJYJ8vKt0YkJ"
    secret_key = "qYdka9JYsmglCkn557fpDBDuZbEVJf11h4VXVFwLAzedE2ji"

    download_path = "data/output.stl"
    export_stl(part_name, download_path, document_id, workspace_id, element_id, access_key, secret_key)