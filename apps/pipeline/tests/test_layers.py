"""
Checks that each module imports only from its own layer or a lower one, by the six-layer map of ADR 0010,
and that a module outside the sheet package imports only cornerstone.sheet or cornerstone.sheet.base.
It reads the import lines with ast and imports no pipeline code.
"""
import ast
from collections.abc import Callable
from pathlib import Path

from rule_report import Offense, report

SRC = Path(__file__).resolve().parent.parent / "src"
# The API is its own app. Its tests run the same rule on its src, with the pipeline src beside it.
API_SRC = SRC.parent.parent / "api" / "src"
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
    "client": "model",
    "league_settings": "model",
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
    "claude_port": "provider",
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


ADR = "docs/adr/0010-six-layers-import-downward-only.md"
UPWARD_RULE = "a module imports only from its own layer or a lower one"
SHEET = f"{PACKAGE}.sheet"
# The base module holds the names that the chapters share, so a caller outside the sheet may import it too.
SHEET_ENTRIES = {SHEET, f"{SHEET}.base"}
SHEET_RULE = "outside the sheet package, a module imports only cornerstone.sheet or cornerstone.sheet.base"
SHEET_FIX = "re-export the name from cornerstone/sheet/__init__.py, or import it from cornerstone.sheet.base."


def _module_name(path: Path, src: Path) -> str:
    """The dotted name of a source file, such as cornerstone.sheet.base. A package takes the name of its folder."""
    parts = list(path.relative_to(src).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _modules(src: Path, api_src: Path | None = None) -> dict[str, Path]:
    """Every module of the pipeline package and the API package, by dotted name.

    The API package sits under api_src. With no api_src, both packages sit under src.
    """
    roots = [(src, PACKAGE), (api_src or src, API)]
    return {_module_name(path, base): path for base, root in roots for path in sorted((base / root).rglob("*.py"))}


def _repo_path(path: Path, src: Path) -> str:
    """The path of a file from the repo root, which holds src, as the report prints it."""
    return str(path.relative_to(src.parent))


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


def _every_import(tree: ast.Module) -> list[ast.Import | ast.ImportFrom]:
    """Every import in the module: at load, under TYPE_CHECKING, and inside a function, in line order."""
    found = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    return sorted(found, key=lambda node: node.lineno)


def _targets(
    name: str,
    path: Path,
    modules: dict[str, Path],
    read: Callable[[ast.Module], list[ast.Import | ast.ImportFrom]] = _top_level_imports,
) -> dict[str, int]:
    """The modules of the two packages that one module imports, each with the line of its first import.

    By default it reads only the imports at load, because only those can make an import cycle.
    With read=_every_import, it reads every import, because an import inside a function still uses the module.
    """
    package = name if path.name == "__init__.py" else name.rpartition(".")[0]
    tree = ast.parse(path.read_text())
    targets: dict[str, int] = {}
    for node in read(tree):
        if isinstance(node, ast.Import):
            bases = [alias.name for alias in node.names]
            for base in bases:
                if base in modules:
                    targets.setdefault(base, node.lineno)
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
                targets.setdefault(child, node.lineno)
            elif base in modules:
                targets.setdefault(base, node.lineno)
    targets.pop(name, None)
    return targets


def _short(name: str) -> str:
    return name.removeprefix(PACKAGE).removeprefix(".")


def _layer_of_lines() -> dict[str, int]:
    """The line of each key of LAYER_OF in this file, so a stale-entry offense names the line to remove."""
    for node in ast.parse(Path(__file__).read_text()).body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "LAYER_OF":
            assert isinstance(node.value, ast.Dict)
            return {key.value: key.lineno for key in node.value.keys
                    if isinstance(key, ast.Constant) and isinstance(key.value, str)}
    raise AssertionError("tests/test_layers.py has no LAYER_OF dict.")


def _no_layer_offenses(src: Path) -> list[Offense]:
    # A missing key has no line of its own, so the offense names line 1 of the module.
    return [Offense(
        path=_repo_path(path, src),
        line=1,
        rule_id="layers/no-layer",
        what=f"{name} has no layer in LAYER_OF.",
        rule="each module of cornerstone has one layer in LAYER_OF",
        adr=ADR,
        fix=f'add "{_short(name)}" to LAYER_OF in tests/test_layers.py, in the lowest layer its imports allow.',
    ) for name, path in _modules(src).items() if name.split(".")[0] == PACKAGE and _short(name) not in LAYER_OF]


def _stale_entry_offenses(src: Path, layer_of: dict[str, str] = LAYER_OF) -> list[Offense]:
    names = {_short(name) for name in _modules(src) if name.split(".")[0] == PACKAGE}
    lines = _layer_of_lines()
    return [Offense(
        # LAYER_OF is in this file for any src, so the path is from the root of this repo.
        path=_repo_path(Path(__file__).resolve(), SRC),
        # A key from a map other than LAYER_OF has no line in this file, so the offense names line 1.
        line=lines.get(key, 1),
        rule_id="layers/stale-entry",
        what=f'LAYER_OF names "{key}", and no module {PACKAGE}.{key} exists.',
        rule="LAYER_OF names only modules that exist",
        adr=ADR,
        fix=f'remove "{key}" from LAYER_OF, or give it the name the module has now.',
    ) for key in sorted(set(layer_of) - names)]


def _import_offenses(src: Path, api_src: Path | None = None) -> list[Offense]:
    """The upward imports, and the imports of the API package from the pipeline package."""
    modules = _modules(src, api_src)
    offenses: list[Offense] = []
    for name, path in modules.items():
        is_api = name.split(".")[0] == API
        # The report names a path from the app that holds the module.
        app_src = (api_src or src) if is_api else src
        if not is_api and _short(name) not in LAYER_OF:
            continue  # test_every_module_has_a_layer reports it.
        own = API_TOP_LAYER if is_api else LAYER_OF[_short(name)]
        for target, line in sorted(_targets(name, path, modules).items()):
            if target.split(".")[0] == API:
                if not is_api:
                    offenses.append(Offense(
                        path=_repo_path(path, app_src),
                        line=line,
                        rule_id="layers/api-import",
                        what=f"{name} imports {target}.",
                        rule="the pipeline package does not import the API package",
                        adr=ADR,
                        fix=f"move the shared name into {PACKAGE}, and import it from there in both packages.",
                    ))
                continue
            theirs = LAYER_OF.get(_short(target))
            if theirs is None:
                continue
            if LAYERS.index(theirs) > LAYERS.index(own):
                if is_api:
                    rule = f"the API package imports only from layer {API_TOP_LAYER} or a lower one"
                    fix = f"move the shared name to a module in layer {API_TOP_LAYER} or a lower one."
                else:
                    rule = UPWARD_RULE
                    fix = f"move the shared name to a module in a lower layer, or move {name} up in LAYER_OF."
                offenses.append(Offense(
                    path=_repo_path(path, app_src),
                    line=line,
                    rule_id="layers/upward-import",
                    what=f"{name} imports {target}.",
                    rule=rule,
                    adr=ADR,
                    fix=fix,
                ))
    return offenses


def _sheet_entry_offenses(src: Path) -> list[Offense]:
    """The imports of a sheet module other than the two entries, from a module outside the sheet package.

    The rule does not read tests/, so a chapter test may import its chapter module.
    """
    modules = _modules(src)
    offenses: list[Offense] = []
    for name, path in modules.items():
        if name == SHEET or name.startswith(f"{SHEET}."):
            continue
        for target, line in sorted(_targets(name, path, modules, read=_every_import).items()):
            if target.startswith(f"{SHEET}.") and target not in SHEET_ENTRIES:
                offenses.append(Offense(
                    path=_repo_path(path, src),
                    line=line,
                    rule_id="layers/sheet-entry",
                    what=f"{name} imports {target}.",
                    rule=SHEET_RULE,
                    adr=ADR,
                    fix=SHEET_FIX,
                ))
    return offenses


def test_every_module_has_a_layer():
    offenses = _no_layer_offenses(SRC)
    assert not offenses, report(offenses)


def test_the_map_names_only_modules_that_exist():
    offenses = _stale_entry_offenses(SRC)
    assert not offenses, report(offenses)


def test_no_module_imports_from_a_higher_layer():
    offenses = _import_offenses(SRC, API_SRC)
    assert not offenses, report(offenses)


def test_no_module_outside_the_sheet_imports_a_chapter_module():
    offenses = _sheet_entry_offenses(SRC)
    assert not offenses, report(offenses)


def test_the_rule_finds_a_model_module_that_imports_a_write_module(tmp_path):
    src = tmp_path / "src"
    package = src / PACKAGE
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "writer.py").write_text("")
    (package / "models.py").write_text('"""A model module."""\nimport json\n\nfrom cornerstone import writer\n')
    assert _import_offenses(src) == [Offense(
        path="src/cornerstone/models.py",
        line=4,
        rule_id="layers/upward-import",
        what="cornerstone.models imports cornerstone.writer.",
        rule=UPWARD_RULE,
        adr=ADR,
        fix="move the shared name to a module in a lower layer, or move cornerstone.models up in LAYER_OF.",
    )]


def test_the_rule_finds_a_module_with_no_layer(tmp_path):
    package = tmp_path / "src" / PACKAGE
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "extra.py").write_text("")
    offenses = _no_layer_offenses(tmp_path / "src")
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("src/cornerstone/extra.py", 1, "layers/no-layer")]


def test_the_rule_finds_a_stale_entry(tmp_path):
    package = tmp_path / "src" / PACKAGE
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    offenses = _stale_entry_offenses(tmp_path / "src", {"": "model", "models": "model"})
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("tests/test_layers.py", _layer_of_lines()["models"], "layers/stale-entry")]


def test_the_rule_finds_a_module_that_imports_a_chapter_module(tmp_path):
    src = tmp_path / "src"
    sheet = src / PACKAGE / "sheet"
    sheet.mkdir(parents=True)
    (src / PACKAGE / "__init__.py").write_text("")
    (sheet / "__init__.py").write_text("")
    (sheet / "next_week.py").write_text("")
    # The import is inside a function, so the rule must read more than the imports at load.
    (src / PACKAGE / "writer.py").write_text(
        '"""A write module."""\n\n\ndef write():\n    from cornerstone.sheet import next_week\n')
    assert _sheet_entry_offenses(src) == [Offense(
        path="src/cornerstone/writer.py",
        line=5,
        rule_id="layers/sheet-entry",
        what="cornerstone.writer imports cornerstone.sheet.next_week.",
        rule=SHEET_RULE,
        adr=ADR,
        fix=SHEET_FIX,
    )]
