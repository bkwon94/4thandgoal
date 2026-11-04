"""
Tests for the voice of the writer: the default voice of the facts package and the voice of a client prompts folder.
Each test reads the real prompt files. A test client lives in a temp folder, never under clients/.
"""
from pathlib import Path

from facts.writer import DEFAULT_PROMPTS, VOICE_FILES, load_prompt

REPO = Path(__file__).resolve().parents[4]
CPC_VOICE = REPO / "clients" / "cpc" / "prompts"


def test_the_default_voice_and_the_rule_prompts_of_the_writer_live_in_the_facts_package():
    names = {path.name for path in DEFAULT_PROMPTS.iterdir()}
    assert names == {"tone.md", "vocabulary.md", "writer.md", "verifier.md"}
    assert DEFAULT_PROMPTS.parent.name == "facts"


def test_a_client_with_no_prompts_folder_gets_the_default_voice(tmp_path):
    voice_dir = tmp_path / "client" / "prompts"
    for name in VOICE_FILES:
        assert load_prompt(voice_dir, name) == (DEFAULT_PROMPTS / name).read_text(encoding="utf-8").strip()


def test_a_client_prompts_folder_overrides_only_the_two_voice_files(tmp_path):
    for name in ("tone.md", "vocabulary.md", "writer.md", "verifier.md"):
        (tmp_path / name).write_text(f"Client {name}.\n", encoding="utf-8")
    assert load_prompt(tmp_path, "tone.md") == "Client tone.md."
    assert load_prompt(tmp_path, "vocabulary.md") == "Client vocabulary.md."
    assert load_prompt(tmp_path, "writer.md") == (DEFAULT_PROMPTS / "writer.md").read_text(encoding="utf-8").strip()
    assert load_prompt(tmp_path, "verifier.md") == (DEFAULT_PROMPTS / "verifier.md").read_text(encoding="utf-8").strip()


def test_a_rule_prompt_comes_from_the_folder_of_the_package_that_owns_it(tmp_path):
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "rubric.md").write_text("The rubric of another package.\n", encoding="utf-8")
    (tmp_path / "rubric.md").write_text("A client rubric.\n", encoding="utf-8")
    assert load_prompt(tmp_path, "rubric.md", rules_dir=rules) == "The rubric of another package."


def test_cpc_keeps_its_voice_in_its_client_folder():
    for name in VOICE_FILES:
        assert load_prompt(CPC_VOICE, name) == (CPC_VOICE / name).read_text(encoding="utf-8").strip()
