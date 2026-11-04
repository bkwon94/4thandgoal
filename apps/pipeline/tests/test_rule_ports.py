"""
Checks that no test patches a port: the Claude call or the provider. A test passes the fake from tests/fakes.py.
It reads each monkeypatch.setattr call in tests/ with ast and imports no pipeline code. See ADR 0015.
"""
import ast
from pathlib import Path

from rule_report import Offense, report

ROOT = Path(__file__).resolve().parent.parent
ADR = "docs/adr/0015-a-port-has-one-fake.md"
RULE = "no test patches a port, such as the Claude call or the provider"
FIX = "pass a FakeWriter or a FixtureProvider from tests/fakes.py, or an httpx.MockTransport, in place of the patch."

# The modules of the two ports. A patch of a name in one of them, or of a name imported from one, patches a port.
# league.provider covers league.provider.sleeper.
PORT_MODULES = ("facts.writer", "league.claude_port", "league.provider")
# The Claude calls, the state fetch, and the two port instances, under any module, such as cli.WRITER.
# The Provider methods join them from the protocol.
CALL_NAMES = {"claude_call", "analyzer_call", "parse_call", "_get_client", "fetch_state", "WRITER", "SLEEPER"}
# The provider port lives in the league package, the shared kernel.
PROVIDER_BASE = ROOT.parent.parent / "packages" / "league" / "python" / "src" / "league" / "provider" / "base.py"


def _provider_methods(base: Path = PROVIDER_BASE) -> set[str]:
    """The method names of the Provider protocol, read from its source, so a new fetch joins the rule by itself."""
    for node in ast.parse(base.read_text()).body:
        if isinstance(node, ast.ClassDef) and node.name == "Provider":
            return {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
    raise AssertionError(f"{base} has no Provider class.")


def _is_port_module(dotted: str) -> bool:
    return any(dotted == module or dotted.startswith(f"{module}.") for module in PORT_MODULES)


def _imported_names(tree: ast.Module) -> dict[str, str]:
    """The dotted source of each name that the file imports at any depth, such as league.provider.sleeper."""
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # "import a.b" binds a, and "import a.b as c" binds c to a.b.
                if alias.asname:
                    names[alias.asname] = alias.name
                else:
                    names[alias.name.split(".")[0]] = alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for alias in node.names:
                names[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return names


def _source(target: ast.expr, imported: dict[str, str]) -> str:
    """The dotted source of `a.b.c`, with the import of `a` in place of `a`. An unknown name stays as it is."""
    parts: list[str] = []
    while isinstance(target, ast.Attribute):
        parts.insert(0, target.attr)
        target = target.value
    if not isinstance(target, ast.Name):
        return ""
    return ".".join([imported.get(target.id, target.id), *parts])


def _is_setattr(node: ast.Call) -> bool:
    func = node.func
    return (isinstance(func, ast.Attribute) and func.attr == "setattr"
            and isinstance(func.value, ast.Name) and func.value.id == "monkeypatch")


def _patch_offenses(root: Path, base: Path = PROVIDER_BASE) -> list[Offense]:
    banned = CALL_NAMES | _provider_methods(base)
    offenses: list[Offense] = []
    for path in sorted((root / "tests").rglob("*.py")):
        tree = ast.parse(path.read_text())
        imported = _imported_names(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not _is_setattr(node) or not node.args:
                continue
            target = node.args[0]
            if isinstance(target, ast.Constant) and isinstance(target.value, str):
                # The string form, monkeypatch.setattr("a.b.name", value), names the module and the attribute.
                where, attribute, source = target.value, target.value.rpartition(".")[2], target.value
            else:
                second = node.args[1] if len(node.args) > 1 else None
                attribute = second.value if isinstance(second, ast.Constant) and isinstance(second.value, str) else ""
                where, source = f"{ast.unparse(target)}.{attribute}", _source(target, imported)
            port = _is_port_module(source)
            if port or attribute in banned:
                offenses.append(Offense(
                    path=path.relative_to(root).as_posix(),
                    line=node.lineno,
                    rule_id="ports/monkeypatch",
                    what=f"The test patches {where}.",
                    rule=RULE,
                    adr=ADR,
                    fix=FIX,
                ))
    # ast.walk goes by depth, not by line, so the sort puts the report in line order.
    return sorted(offenses, key=lambda offense: (offense.path, offense.line))


def test_no_test_patches_a_port():
    offenses = _patch_offenses(ROOT)
    assert not offenses, report(offenses)


def test_the_rule_reads_the_provider_methods_from_the_protocol():
    assert {"fetch_week", "fetch_live", "fetch_past_leg"} <= _provider_methods()


def test_the_rule_finds_a_patch_of_the_claude_call(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_cli.py").write_text(
        '"""A CLI test."""\nfrom cornerstone import cli\n\n\ndef test_build(monkeypatch):\n'
        '    monkeypatch.setattr(cli, "claude_call", f)\n')
    assert _patch_offenses(tmp_path) == [Offense(
        path="tests/test_cli.py",
        line=6,
        rule_id="ports/monkeypatch",
        what="The test patches cli.claude_call.",
        rule=RULE,
        adr=ADR,
        fix=FIX,
    )]


def test_the_rule_finds_a_name_from_a_port_module_a_string_target_and_a_port_instance_but_not_a_build_step(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_fetch.py").write_text(
        '"""A fetch test."""\nfrom cornerstone import cli, pipeline\n\n\ndef test_fetch(monkeypatch):\n'
        '    from league.provider import sleeper\n\n'
        '    monkeypatch.setattr(sleeper, "_get", f)\n'
        '    monkeypatch.setattr("facts.writer.MODEL", "x")\n'
        '    monkeypatch.setattr(cli, "WRITER", w)\n'
        '    monkeypatch.setattr(cli, "SLEEPER", p)\n'
        '    monkeypatch.setattr(pipeline, "fetch_nflverse", f)\n')
    assert [(offense.line, offense.what) for offense in _patch_offenses(tmp_path)] == [
        (8, "The test patches sleeper._get."), (9, "The test patches facts.writer.MODEL."),
        (10, "The test patches cli.WRITER."), (11, "The test patches cli.SLEEPER.")]
