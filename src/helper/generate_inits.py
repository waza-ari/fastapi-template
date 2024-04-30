"""
This script will auto-generate the __init__.py files for schemas, models and crud.
"""

import ast
import os
from pathlib import Path

# Get parent directory of this script
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define dirs we want to do this for
dirs = ["schemas", "models", "crud"]

for folder in dirs:
    # Within the app/ directory, get all python files and extract class names
    modules = list(Path(os.path.join(parent_dir, "app/" + folder)).rglob("*.py"))

    # create result array
    result = {}

    for module in modules:
        # Skip if __init__.py
        if "__init__" in module.name or "base.py" in module.name or "mixins.py" in module.name:
            continue

        # Load file content
        with open(module) as f:
            node = ast.parse(f.read())

        # Get all class names
        classes = [
            n.name for n in node.body if isinstance(n, ast.ClassDef) and n.name not in ["BaseModel", "Base", "CRUDBase"]
        ]

        # For crud, show assignments instead
        if folder == "crud":
            classes = [n.targets[0].id for n in node.body if isinstance(n, ast.Assign)]

        # Continue if there's no classes
        if len(classes) == 0:
            continue

        # extract module name
        module_name = str(module).split("app/" + folder + "/")[1].replace("/", ".").replace(".py", "")

        # Create result entry
        result[module_name] = classes

    # Write __init__.py files
    with open(os.path.join(parent_dir, "app/" + folder + "/__init__.py"), "w") as f:
        f.write("# ruff: noqa: F401\n")
        f.write("# This file is auto-generated by generate_inits.py\n")

        # Pre-Import statements
        if folder == "models":
            f.write("\nimport sqlalchemy\n\n")

        for module, classes in result.items():
            # Filter "log" from classes if its in there
            if "log" in classes:
                classes.remove("log")

            f.write(f"from .{module} import ")
            f.write(", ".join(classes))
            f.write("\n")

        # For schemas add update_forward_refs
        if folder == "schemas":
            f.write("\n")
            for module, classes in result.items():
                for class_name in classes:
                    f.write(f"{class_name}.model_rebuild()\n")

        if folder == "models":
            f.write("\n")
            f.write("sqlalchemy.orm.configure_mappers()\n")

        # Write __all__ variable
        f.write("\n\n__all__ = [\n")
        for module, classes in result.items():
            for class_name in classes:
                f.write(f'    "{class_name}",\n')
        f.write("]\n")