"""
Checks that each module imports only from its own layer or a lower one, by the six-layer map of ADR 0010,
that a module outside the week sheet imports only week.sheet or week.sheet.base, that the league package imports no
app, that the facts package imports only itself and the league package, and that the analyzer, the managers, and the
week packages each import only itself, the league package, and the facts package.
It reads the import lines with ast and imports no pipeline code.
"""
import ast
from collections.abc import Callable
from pathlib import Path

from rule_report import Offense, report

SRC = Path(__file__).resolve().parent.parent / "src"
# The API is its own app. Its tests run the same rule on its src, with the pipeline src beside it.
API_SRC = SRC.parent.parent / "api" / "src"
# The league package is the shared kernel under the pipeline. The rule reads its src beside the pipeline src.
LEAGUE_SRC = SRC.parent.parent.parent / "packages" / "league" / "python" / "src"
# The facts package sits on the league package. The rule reads its src beside the pipeline src too.
FACTS_SRC = SRC.parent.parent.parent / "packages" / "facts" / "python" / "src"
# The analyzer package is a core package on the league and the facts packages. The rule reads its src too.
ANALYZER_SRC = SRC.parent.parent.parent / "packages" / "analyzer" / "python" / "src"
# The week package sits on the league and the facts packages. The rule reads its src beside the pipeline src too.
WEEK_SRC = SRC.parent.parent.parent / "packages" / "week" / "python" / "src"
# The managers package sits on the league and the facts packages. The rule reads its src beside the pipeline src too.
MANAGERS_SRC = SRC.parent.parent.parent / "packages" / "managers" / "python" / "src"
PACKAGE = "cornerstone"
API = "cornerstone_api"
LEAGUE = "league"
FACTS = "facts"
ANALYZER = "analyzer"
WEEK = "week"
MANAGERS = "managers"
# The packages under each app, and the packages that each one may import. The dependency order of decision 01 is
# league, then facts, then the core packages, so a package never imports an app or a package above it.
PACKAGE_IMPORTS = {LEAGUE: {LEAGUE}, FACTS: {LEAGUE, FACTS}, ANALYZER: {LEAGUE, FACTS, ANALYZER},
                   WEEK: {LEAGUE, FACTS, WEEK}, MANAGERS: {LEAGUE, FACTS, MANAGERS}}

# The model layer is lowest because the provider returns the models, so the provider must import them.
LAYERS = ["model", "provider", "load", "facts", "write", "output"]

# The API serves the analyzer, so it may use any layer up to write. It must never reach the page code in output.
API_TOP_LAYER = "write"

# The key is the module path under cornerstone. A package key names its __init__ file. The root package is "".
# A module of a package keeps its full name, such as "league.models".
# A "# PRD:" note marks a module that sits above its PRD layer because of the import the note names.
# The map moves no file. The note goes when the import goes.
LAYER_OF: dict[str, str] = {
    "": "model",
    "league": "model",
    "league.tunables": "model",
    # model
    "league.models": "model",
    "league.client": "model",
    "league.league_settings": "model",
    "league.paths": "model",
    "league.numbers": "model",
    "tunables": "model",
    "league.player_ids": "model",
    "league.trades": "model",
    "facts": "model",
    "facts.chapters": "model",
    "facts.names": "model",
    "facts.tokens": "model",
    "analyzer": "model",
    "analyzer.tunables": "model",
    "analyzer.errors": "model",
    "week": "model",
    "week.tunables": "model",
    "managers": "model",
    "managers.tunables": "model",
    # provider
    "league.provider": "provider",
    "league.provider.base": "provider",
    "league.provider.raw": "provider",
    "league.provider.sleeper": "provider",
    "league.nflverse": "provider",
    "league.nflverse_rows": "provider",
    "league.nflverse_expected": "provider",
    "league.nflverse_players": "provider",
    "league.nflverse_usage": "provider",
    "league.files": "provider",
    "league.chart": "provider",
    "league.claude_errors": "provider",
    "league.claude_port": "provider",
    "analyzer.ratelimit": "provider",
    # load
    "league.parse": "load",
    "league.slow_sources": "load",
    "league.points_allowed": "load",
    "league.history": "load",
    "league.ranks": "load",
    "league.standings_table": "load",
    "league.snapshot": "load",
    "league.season_inputs": "load",
    "league.live": "load",
    "league.lineup": "load",
    # facts
    "sheet": "facts",
    "sheet.rankings": "facts",
    "week.sheet": "facts",
    "week.sheet.assemble": "facts",
    "week.sheet.awards": "facts",
    "week.sheet.base": "facts",
    "week.sheet.drops": "facts",
    "week.sheet.leaders": "facts",
    "week.sheet.matchups": "facts",
    "week.sheet.next_week": "facts",
    "week.sheet.port": "facts",
    "week.sheet.standings": "facts",
    "week.sheet.week": "facts",
    "week.facts_league": "facts",
    "week.facts_matchup": "facts",
    "week.facts_nflverse": "facts",
    "odds": "facts",
    "analyzer.adjusters": "facts",
    "analyzer.rubric": "facts",
    "analyzer.cache": "facts",
    "rank_score": "facts",
    "waiver": "facts",
    "waiver_buckets": "facts",
    "waiver_drops": "facts",
    "waiver_price": "facts",
    "waiver_projection": "facts",
    "managers.entries": "facts",
    "managers.grade": "facts",
    "managers.moves": "facts",
    "managers.players": "facts",
    "managers.season": "facts",
    "power_rankings": "facts",
    "analyzer.trade_facts": "facts",
    "analyzer.finder": "facts",
    # write
    "facts.writer": "write",
    "facts.verifier": "write",
    "week.median": "write",
    "analyzer.analysis": "write",
    "analyzer.finder_reasons": "write",
    "analyzer.routes": "write",
    "waiver_research": "write",
    # output
    "render": "output",
    "week.page": "output",
    "managers.render": "output",
    "publish": "output",
    "pipeline": "output",
    "cli": "output",
}


ADR = "docs/adr/0010-six-layers-import-downward-only.md"
UPWARD_RULE = "a module imports only from its own layer or a lower one"
# The league package is the shared kernel under each app, so it never imports an app (decision 01). The facts package
# sits on the kernel, so it imports only the kernel and itself.
PACKAGE_RULES = {
    LEAGUE: "the league package imports no app",
    FACTS: "the facts package imports only the league package and itself, never an app or a core package",
    ANALYZER: "the analyzer package imports only the league package, the facts package, and itself, never an app",
    WEEK: "the week package imports only the league package, the facts package, and itself, never an app or another "
          "core package",
    MANAGERS: "the managers package imports only the league package, the facts package, and itself, never an app or "
              "another core package",
}
SHEET = f"{WEEK}.sheet"
# The base module holds the names that the chapters share, so a caller outside the sheet may import it too.
SHEET_ENTRIES = {SHEET, f"{SHEET}.base"}
SHEET_RULE = "outside the week sheet, a module imports only week.sheet or week.sheet.base"
SHEET_FIX = "re-export the name from week/sheet/__init__.py, or import it from week.sheet.base."


def _module_name(path: Path, src: Path) -> str:
    """The dotted name of a source file, such as cornerstone.sheet.base. A package takes the name of its folder."""
    parts = list(path.relative_to(src).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _modules(src: Path, api_src: Path | None = None, league_src: Path | None = None,
             facts_src: Path | None = None, analyzer_src: Path | None = None,
             week_src: Path | None = None, managers_src: Path | None = None) -> dict[str, Path]:
    """Every module of the pipeline package, the API package, and each package, by name.

    The API package sits under api_src, the league package under league_src, the facts package under facts_src, the
    analyzer package under analyzer_src, the week package under week_src, and the managers package under
    managers_src. With none, each sits under src.
    """
    roots = [(src, PACKAGE), (api_src or src, API), (league_src or src, LEAGUE), (facts_src or src, FACTS),
             (analyzer_src or src, ANALYZER), (week_src or src, WEEK), (managers_src or src, MANAGERS)]
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


def _layered(name: str) -> bool:
    """True for a module of the pipeline or of a package, the ones that LAYER_OF maps."""
    return name.split(".")[0] in (PACKAGE, LEAGUE, FACTS, ANALYZER, WEEK, MANAGERS)


def _src_of(name: str, src: Path, api_src: Path | None, league_src: Path | None,
            facts_src: Path | None = None, analyzer_src: Path | None = None, week_src: Path | None = None,
            managers_src: Path | None = None) -> Path:
    """The src folder that holds the module, so the report names a path from its own app or package."""
    top = name.split(".")[0]
    if top == API:
        return api_src or src
    if top == LEAGUE:
        return league_src or src
    if top == FACTS:
        return facts_src or src
    if top == ANALYZER:
        return analyzer_src or src
    if top == WEEK:
        return week_src or src
    if top == MANAGERS:
        return managers_src or src
    return src


def _no_layer_offenses(src: Path, league_src: Path | None = None, facts_src: Path | None = None,
                       analyzer_src: Path | None = None, week_src: Path | None = None,
                       managers_src: Path | None = None) -> list[Offense]:
    # A missing key has no line of its own, so the offense names line 1 of the module.
    return [Offense(
        path=_repo_path(path, _src_of(name, src, None, league_src, facts_src, analyzer_src, week_src, managers_src)),
        line=1,
        rule_id="layers/no-layer",
        what=f"{name} has no layer in LAYER_OF.",
        rule="each module of cornerstone and league has one layer in LAYER_OF",
        adr=ADR,
        fix=f'add "{_short(name)}" to LAYER_OF in tests/test_layers.py, in the lowest layer its imports allow.',
    ) for name, path in _modules(src, league_src=league_src, facts_src=facts_src, analyzer_src=analyzer_src,
                                 week_src=week_src, managers_src=managers_src).items()
        if _layered(name) and _short(name) not in LAYER_OF]


def _stale_entry_offenses(src: Path, layer_of: dict[str, str] = LAYER_OF, league_src: Path | None = None,
                          facts_src: Path | None = None, analyzer_src: Path | None = None,
                          week_src: Path | None = None, managers_src: Path | None = None) -> list[Offense]:
    modules = _modules(src, league_src=league_src, facts_src=facts_src, analyzer_src=analyzer_src, week_src=week_src,
                       managers_src=managers_src)
    names = {_short(name) for name in modules if _layered(name)}
    lines = _layer_of_lines()
    return [Offense(
        # LAYER_OF is in this file for any src, so the path is from the root of this repo.
        path=_repo_path(Path(__file__).resolve(), SRC),
        # A key from a map other than LAYER_OF has no line in this file, so the offense names line 1.
        line=lines.get(key, 1),
        rule_id="layers/stale-entry",
        what=f'LAYER_OF names "{key}", and no module {key if key.split(".")[0] in PACKAGE_IMPORTS else f"{PACKAGE}.{key}"} exists.',
        rule="LAYER_OF names only modules that exist",
        adr=ADR,
        fix=f'remove "{key}" from LAYER_OF, or give it the name the module has now.',
    ) for key in sorted(set(layer_of) - names)]


def _import_offenses(src: Path, api_src: Path | None = None, league_src: Path | None = None,
                     facts_src: Path | None = None, analyzer_src: Path | None = None,
                     week_src: Path | None = None, managers_src: Path | None = None) -> list[Offense]:
    """The upward imports, the imports of the API package from the pipeline package, and the imports of each package
    that PACKAGE_IMPORTS does not allow."""
    modules = _modules(src, api_src, league_src, facts_src, analyzer_src, week_src, managers_src)
    offenses: list[Offense] = []
    for name, path in modules.items():
        is_api = name.split(".")[0] == API
        # The report names a path from the app or the package that holds the module.
        app_src = _src_of(name, src, api_src, league_src, facts_src, analyzer_src, week_src, managers_src)
        if not is_api and _short(name) not in LAYER_OF:
            continue  # test_every_module_has_a_layer reports it.
        own = API_TOP_LAYER if is_api else LAYER_OF[_short(name)]
        for target, line in sorted(_targets(name, path, modules).items()):
            top = name.split(".")[0]
            if top in PACKAGE_IMPORTS and target.split(".")[0] not in PACKAGE_IMPORTS[top]:
                offenses.append(Offense(
                    path=_repo_path(path, app_src),
                    line=line,
                    rule_id="layers/kernel-import",
                    what=f"{name} imports {target}.",
                    rule=PACKAGE_RULES[top],
                    adr=ADR,
                    fix=f"move the shared name into {LEAGUE}, or move {name} out of the {top} package.",
                ))
                continue
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


def _sheet_entry_offenses(src: Path, week_src: Path | None = None) -> list[Offense]:
    """The imports of a sheet module other than the two entries, from a module outside the week sheet.

    The rule does not read tests/, so a chapter test may import its chapter module.
    """
    modules = _modules(src, week_src=week_src)
    offenses: list[Offense] = []
    for name, path in modules.items():
        if name == SHEET or name.startswith(f"{SHEET}."):
            continue
        for target, line in sorted(_targets(name, path, modules, read=_every_import).items()):
            if target.startswith(f"{SHEET}.") and target not in SHEET_ENTRIES:
                offenses.append(Offense(
                    path=_repo_path(path, _src_of(name, src, None, None, None, week_src=week_src)),
                    line=line,
                    rule_id="layers/sheet-entry",
                    what=f"{name} imports {target}.",
                    rule=SHEET_RULE,
                    adr=ADR,
                    fix=SHEET_FIX,
                ))
    return offenses


def test_every_module_has_a_layer():
    offenses = _no_layer_offenses(SRC, LEAGUE_SRC, FACTS_SRC, ANALYZER_SRC, WEEK_SRC, MANAGERS_SRC)
    assert not offenses, report(offenses)


def test_the_map_names_only_modules_that_exist():
    offenses = _stale_entry_offenses(SRC, league_src=LEAGUE_SRC, facts_src=FACTS_SRC, analyzer_src=ANALYZER_SRC,
                                     week_src=WEEK_SRC, managers_src=MANAGERS_SRC)
    assert not offenses, report(offenses)


def test_no_module_imports_from_a_higher_layer():
    offenses = _import_offenses(SRC, API_SRC, LEAGUE_SRC, FACTS_SRC, ANALYZER_SRC, WEEK_SRC, MANAGERS_SRC)
    assert not offenses, report(offenses)


def test_no_module_outside_the_sheet_imports_a_chapter_module():
    offenses = _sheet_entry_offenses(SRC, WEEK_SRC)
    assert not offenses, report(offenses)


def test_the_rule_finds_a_model_module_that_imports_a_write_module(tmp_path):
    src = tmp_path / "src"
    package = src / PACKAGE
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "waiver_research.py").write_text("")
    (package / "tunables.py").write_text(
        '"""A model module."""\nimport json\n\nfrom cornerstone import waiver_research\n')
    assert _import_offenses(src) == [Offense(
        path="src/cornerstone/tunables.py",
        line=4,
        rule_id="layers/upward-import",
        what="cornerstone.tunables imports cornerstone.waiver_research.",
        rule=UPWARD_RULE,
        adr=ADR,
        fix="move the shared name to a module in a lower layer, or move cornerstone.tunables up in LAYER_OF.",
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
    offenses = _stale_entry_offenses(tmp_path / "src", {"": "model", "tunables": "model"})
    assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
        ("tests/test_layers.py", _layer_of_lines()["tunables"], "layers/stale-entry")]


def test_the_rule_finds_a_module_that_imports_a_chapter_module(tmp_path):
    src = tmp_path / "src"
    sheet = src / WEEK / "sheet"
    sheet.mkdir(parents=True)
    (src / PACKAGE).mkdir()
    (src / PACKAGE / "__init__.py").write_text("")
    (src / WEEK / "__init__.py").write_text("")
    (sheet / "__init__.py").write_text("")
    (sheet / "next_week.py").write_text("")
    # The import is inside a function, so the rule must read more than the imports at load.
    (src / PACKAGE / "writer.py").write_text(
        '"""A write module."""\n\n\ndef write():\n    from week.sheet import next_week\n')
    assert _sheet_entry_offenses(src) == [Offense(
        path="src/cornerstone/writer.py",
        line=5,
        rule_id="layers/sheet-entry",
        what="cornerstone.writer imports week.sheet.next_week.",
        rule=SHEET_RULE,
        adr=ADR,
        fix=SHEET_FIX,
    )]


def test_the_rule_finds_a_league_module_that_imports_the_pipeline(tmp_path):
    src = tmp_path / "src"
    league = tmp_path / "league_src" / LEAGUE
    for package in (src / PACKAGE, league):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (src / PACKAGE / "writer.py").write_text("")
    (league / "models.py").write_text('"""A kernel module."""\nfrom cornerstone import writer\n')
    offenses = _import_offenses(src, league_src=tmp_path / "league_src")
    assert [(offense.path, offense.line, offense.rule_id, offense.what) for offense in offenses] == [
        ("league_src/league/models.py", 2, "layers/kernel-import", "league.models imports cornerstone.writer.")]


def test_the_rule_finds_a_facts_module_that_imports_the_pipeline_but_not_one_that_imports_league(tmp_path):
    src = tmp_path / "src"
    league = tmp_path / "league_src" / LEAGUE
    facts = tmp_path / "facts_src" / FACTS
    for package in (src / PACKAGE, league, facts):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (src / PACKAGE / "pipeline.py").write_text("")
    (league / "models.py").write_text("")
    (facts / "names.py").write_text("")
    (facts / "writer.py").write_text(
        '"""A facts module."""\nfrom cornerstone import pipeline\nfrom facts import names\nfrom league import models\n')
    offenses = _import_offenses(src, league_src=tmp_path / "league_src", facts_src=tmp_path / "facts_src")
    assert [(offense.path, offense.line, offense.rule_id, offense.what) for offense in offenses] == [
        ("facts_src/facts/writer.py", 2, "layers/kernel-import", "facts.writer imports cornerstone.pipeline.")]


def test_the_rule_finds_an_analyzer_module_that_imports_an_app_but_not_one_that_imports_facts(tmp_path):
    src = tmp_path / "src"
    league = tmp_path / "league_src" / LEAGUE
    facts = tmp_path / "facts_src" / FACTS
    analyzer = tmp_path / "analyzer_src" / ANALYZER
    api = tmp_path / "api_src" / API
    for package in (src / PACKAGE, league, facts, analyzer, api):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (api / "settings.py").write_text("")
    (league / "models.py").write_text("")
    (facts / "names.py").write_text("")
    (analyzer / "tunables.py").write_text("")
    (analyzer / "errors.py").write_text(
        '"""An analyzer module."""\nfrom cornerstone_api import settings\nfrom facts import names\nfrom league import models\n')
    offenses = _import_offenses(src, api_src=tmp_path / "api_src", league_src=tmp_path / "league_src",
                                facts_src=tmp_path / "facts_src", analyzer_src=tmp_path / "analyzer_src")
    assert [(offense.path, offense.line, offense.rule_id, offense.what) for offense in offenses] == [
        ("analyzer_src/analyzer/errors.py", 2, "layers/kernel-import", "analyzer.errors imports cornerstone_api.settings.")]


def test_the_rule_finds_a_week_module_that_imports_the_pipeline_but_not_one_that_imports_facts(tmp_path):
    src = tmp_path / "src"
    week = tmp_path / "week_src" / WEEK
    facts = tmp_path / "facts_src" / FACTS
    for package in (src / PACKAGE, week, facts):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (src / PACKAGE / "odds.py").write_text("")
    (facts / "tokens.py").write_text("")
    (week / "median.py").write_text(
        '"""A week module."""\nfrom cornerstone import odds\nfrom facts import tokens\n')
    offenses = _import_offenses(src, facts_src=tmp_path / "facts_src", week_src=tmp_path / "week_src")
    assert [(offense.path, offense.line, offense.rule_id, offense.what) for offense in offenses] == [
        ("week_src/week/median.py", 2, "layers/kernel-import", "week.median imports cornerstone.odds.")]


def test_the_rule_finds_a_managers_module_that_imports_a_core_package_but_not_one_that_imports_facts(tmp_path):
    src = tmp_path / "src"
    managers = tmp_path / "managers_src" / MANAGERS
    week = tmp_path / "week_src" / WEEK
    facts = tmp_path / "facts_src" / FACTS
    for package in (src / PACKAGE, managers, week, facts):
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    (week / "page.py").write_text("")
    (facts / "tokens.py").write_text("")
    (managers / "entries.py").write_text(
        '"""A managers module."""\nfrom week import page\nfrom facts import tokens\n')
    offenses = _import_offenses(src, facts_src=tmp_path / "facts_src", week_src=tmp_path / "week_src",
                                managers_src=tmp_path / "managers_src")
    assert [(offense.path, offense.line, offense.rule_id, offense.what) for offense in offenses] == [
        ("managers_src/managers/entries.py", 2, "layers/kernel-import", "managers.entries imports week.page.")]
