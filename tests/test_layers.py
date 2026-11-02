"""
Checks that each module imports only from its own layer or a lower one, by the six-layer map of ADR 0007.
It reads the import lines with ast and imports no pipeline code.
"""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
PACKAGE = "cornerstone"
API = "cornerstone_api"

# The model layer is lowest because the provider returns the models, so the provider must import them.
LAYERS = ["model", "provider", "load", "facts", "write", "output"]

# The API serves the analyzer, so it may use any layer up to write. It must never reach the page code in output.
API_TOP_LAYER = "write"

# The key is the module path under cornerstone. A package key names its __init__ file. The root package is "".
# A "# PRD:" note marks a module that sits above its PRD layer because of the import the note names.
# The map moves no file. The note goes when the import goes.
LAYER_OF: dict[str, str] = {
    "": "model",
    # model
    "models": "model",
    "config": "model",
    "paths": "model",
    "numbers": "model",
    "names": "model",
    "tunables": "model",
    "player_ids": "model",
    "trades": "model",
    # provider
    "provider": "provider",
    "provider.base": "provider",
    "provider.raw": "provider",
    "provider.sleeper": "provider",
    "nflverse": "provider",
    "nflverse_rows": "provider",
    "nflverse_expected": "provider",
    "nflverse_players": "provider",
    "nflverse_usage": "provider",
    "files": "provider",
    "chart": "provider",
    "claude_errors": "provider",
    # load
    "parse": "load",
    "slow_sources": "load",
    "points_allowed": "load",
    "history": "load",
    "ranks": "load",
    "standings_table": "load",
    "snapshot": "load",
    "season_inputs": "load",
    "live": "load",
    # facts
    "sheet": "facts",
    "sheet.assemble": "facts",
    "sheet.awards": "facts",
    "sheet.base": "facts",
    "sheet.drops": "facts",
    "sheet.leaders": "facts",
    "sheet.matchups": "facts",
    "sheet.next_week": "facts",
    "sheet.rankings": "facts",
    "sheet.standings": "facts",
    "sheet.week": "facts",
    "odds": "facts",
    "adjusters": "facts",
    "rubric": "facts",
    "rank_score": "facts",
    "waiver": "facts",
    "waiver_buckets": "facts",
    "waiver_drops": "facts",
    "waiver_price": "facts",
    "waiver_projection": "facts",
    "managers": "facts",
    "manager_grade": "facts",
    "manager_moves": "facts",
    "manager_players": "facts",
    "manager_season": "facts",
    "power_rankings": "facts",
    "trade_facts": "facts",
    "facts_league": "facts",
    "facts_matchup": "facts",
    "facts_nflverse": "facts",
    "finder": "facts",
    # write
    "writer": "write",
    "verifier": "write",
    "analysis": "write",
    "finder_reasons": "write",
    "waiver_research": "write",
    # output
    "render": "output",
    "publish": "output",
    "pipeline": "output",
    "cli": "output",
}


def _module_name(path: Path) -> str:
    """The dotted name of a source file, such as cornerstone.sheet.base. A package takes the name of its folder."""
    parts = list(path.relative_to(SRC).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _modules() -> dict[str, Path]:
    """Every module of the pipeline package and the API package, by dotted name."""
    return {_module_name(path): path for root in (PACKAGE, API) for path in sorted((SRC / root).rglob("*.py"))}


def _is_type_checking(test: ast.expr) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")


def _top_level_imports(tree: ast.Module) -> list[ast.Import | ast.ImportFrom]:
    """The imports that run when the module loads.

    An import under TYPE_CHECKING or inside a function does not run at load, so it cannot make an import cycle.
    """
    found: list[ast.Import | ast.ImportFrom] = []
    nodes: list[ast.stmt] = list(tree.body)
    while nodes:
        node = nodes.pop(0)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            found.append(node)
        elif isinstance(node, ast.If):
            if not _is_type_checking(node.test):
                nodes.extend(node.body)
            nodes.extend(node.orelse)
        elif isinstance(node, ast.Try):
            nodes.extend(node.body + node.orelse + node.finalbody)
            for handler in node.handlers:
                nodes.extend(handler.body)
        elif isinstance(node, (ast.With, ast.ClassDef)):
            nodes.extend(node.body)
    return found


def _targets(name: str, path: Path, modules: dict[str, Path]) -> set[str]:
    """The modules of the two packages that one module imports at load."""
    package = name if path.name == "__init__.py" else name.rpartition(".")[0]
    targets: set[str] = set()
    for node in _top_level_imports(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            bases = [alias.name for alias in node.names]
            for base in bases:
                if base in modules:
                    targets.add(base)
            continue
        base = node.module or ""
        if node.level:
            anchor = package.split(".")
            anchor = anchor[:len(anchor) - (node.level - 1)]
            base = ".".join(anchor + ([base] if base else []))
        for alias in node.names:
            # "from cornerstone import sheet" imports the module cornerstone.sheet, not only the package.
            child = f"{base}.{alias.name}"
            if child in modules:
                targets.add(child)
            elif base in modules:
                targets.add(base)
    targets.discard(name)
    return targets


def _short(name: str) -> str:
    return name.removeprefix(PACKAGE).removeprefix(".")


def test_every_module_has_a_layer():
    missing = [path for name, path in _modules().items()
               if name.split(".")[0] == PACKAGE and _short(name) not in LAYER_OF]
    assert not missing, (
        f"{[str(path.relative_to(SRC)) for path in missing]} has no layer. "
        f"Add it to LAYER_OF in tests/test_layers.py, in the lowest layer its imports allow. See ADR 0007.")


def test_the_map_names_only_modules_that_exist():
    names = {_short(name) for name in _modules() if name.split(".")[0] == PACKAGE}
    stale = sorted(set(LAYER_OF) - names)
    assert not stale, f"LAYER_OF in tests/test_layers.py names modules that do not exist: {stale}. Remove them."


def test_no_module_imports_from_a_higher_layer():
    modules = _modules()
    breaches: list[str] = []
    for name, path in modules.items():
        is_api = name.split(".")[0] == API
        if not is_api and _short(name) not in LAYER_OF:
            continue  # test_every_module_has_a_layer reports it.
        own = API_TOP_LAYER if is_api else LAYER_OF[_short(name)]
        for target in sorted(_targets(name, path, modules)):
            if target.split(".")[0] == API:
                if not is_api:
                    breaches.append(f"{name} -> {target}: the pipeline must not import the API package")
                continue
            theirs = LAYER_OF.get(_short(target))
            if theirs is None:
                continue
            if LAYERS.index(theirs) > LAYERS.index(own):
                who = "the API, which may import every layer below output" if is_api else f"layer {own}"
                breaches.append(
                    f"{name} -> {target}: an upward import. {name} is in {who}. {target} is in layer {theirs}.")
    assert not breaches, "Each module imports only from its own layer or a lower one. See ADR 0007.\n" + "\n".join(
        breaches)
