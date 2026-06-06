import ast
from pathlib import Path


REQUIRED = {
    "MODULE_ID",
    "MODULE_VERSION",
    "MODULE_REVISION",
    "MODULE_API_VERSION",
    "MODULE_COMPATIBILITY",
    "MODULE_STATUS",
}


def test_physplot_modules_have_revision_metadata():
    for path in Path("physplot").rglob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assigned = {
            target.id
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        assert REQUIRED <= assigned, f"{path} missing {REQUIRED - assigned}"
