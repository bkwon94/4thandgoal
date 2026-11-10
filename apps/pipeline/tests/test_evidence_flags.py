"""
Tests for `cornerstone evidence-flags`: one Jev request per acceptance test with files, an entry in FLAGS.md for
each yes past its cut, the shots as tiles that fit, and one log line. FakeJev answers, so no test calls TypeSafe.
"""
import io
import os
import shutil
from pathlib import Path

from fakes import FakeJev
from PIL import Image

from cornerstone import cli
from league.jev_port import JevError, JevImage

# The real files of easter-eggs AT-32 at the round 566d11e7, where the Judge failed it: twelve shots and two logs.
AT_32 = Path(__file__).parent / "fixtures" / "evidence_flags" / "easter-eggs"

ACCEPTANCE = """# Demo: acceptance tests

## Tests

AT-1: A clock window holds
App: pipeline
Stories: 1
Given: A test egg with the clock window 11 PM to midnight ET.
When: POST its check at a time outside the window.
Then: The answer is no match. The same check inside the window matches.
Evidence: the test output of both checks, with the time of each.

AT-2: The docs say the rule
App: pipeline
Stories: 2
Given: the docs.
When: a reader reads them.
Then: the rule is there.
Evidence: none.
"""

EVIDENCE = """# Demo: evidence

## AT-1: A clock window holds

App: pipeline
Then: The answer is no match. The same check inside the window matches.
Files: `evidence/AT-1/output.txt`
Observation: At 00:40 ET the check answered no match.

## AT-2: The docs say the rule

App: pipeline
Then: the rule is there.
Files: none
Observation: The rule is in the docs.
"""


def _scratch(root: Path, slug: str = "demo", acceptance: str = ACCEPTANCE, evidence: str = EVIDENCE) -> Path:
    """A real feature folder under `root`/.scratch, with the output file of AT-1."""
    folder = root / ".scratch" / slug
    (folder / "evidence" / "AT-1").mkdir(parents=True)
    (folder / "ACCEPTANCE.md").write_text(acceptance, encoding="utf-8")
    (folder / "EVIDENCE.md").write_text(evidence, encoding="utf-8")
    (folder / "evidence" / "AT-1" / "output.txt").write_text(
        "$ curl -s -X POST http://127.0.0.1:8080/eggs/check\n{\"match\":false}\n1 passed in 0.25s\n", encoding="utf-8")
    return folder


def _not_shown(key, question, state):
    """Each Noul gets 0.1, so question (a) flags at 0.9 and no other question flags. FakeJev counts 100 tokens a Noul."""
    return 0.1


def test_a_fact_that_no_file_shows_gets_an_open_flag_and_a_test_with_no_files_gets_no_request(tmp_path, capsys):
    folder = _scratch(tmp_path)
    jev = FakeJev(answer=_not_shown)

    code = cli.main(["evidence-flags", "demo", "--root", str(tmp_path)], jev=jev)

    out = capsys.readouterr().out
    assert code == 0
    assert len(jev.requests) == 1
    assert jev.requests[0].state["test"]["id"] == "AT-1"
    flags = (folder / "FLAGS.md").read_text(encoding="utf-8")
    assert "## AT-1, question (a)" in flags
    assert "Probability: 0.90" in flags
    assert "Action: open" in flags
    assert "Reason: " in flags
    assert "## AT-1, question (a)" in out
    assert "AT-1: asked a, b, c, d" in out
    assert "AT-2" not in flags
    assert out.strip().splitlines()[-1] == "Evidence flags: 1 tests, 1 flags, 0 errors, 600 input tokens"


def test_a_jev_error_gives_no_flag_an_error_line_and_exit_0(tmp_path, capsys):
    folder = _scratch(tmp_path)
    jev = FakeJev(error=JevError("TypeSafeError: no API key"))

    code = cli.main(["evidence-flags", "demo", "AT-1", "AT-2", "--root", str(tmp_path)], jev=jev)

    out = capsys.readouterr().out
    assert code == 0
    assert not (folder / "FLAGS.md").exists()
    assert out.count("Jev error") == 1
    assert "AT-1: Jev error, no flags: TypeSafeError: no API key" in out
    assert out.strip().splitlines()[-1] == "Evidence flags: 1 tests, 0 flags, 1 errors, 0 input tokens"


def test_a_fact_that_a_file_shows_gets_no_flag(tmp_path, capsys):
    folder = _scratch(tmp_path)

    code = cli.main(["evidence-flags", "demo", "--root", str(tmp_path)], jev=FakeJev(yes=0.95))

    assert code == 0
    assert not (folder / "FLAGS.md").exists()
    assert capsys.readouterr().out.strip().splitlines()[-1].startswith("Evidence flags: 1 tests, 0 flags, 0 errors")


def _sizes(tiles: list[JevImage]) -> list[tuple[int, int]]:
    return [Image.open(io.BytesIO(tile.png)).size for tile in tiles]


def _in_range(size: tuple[int, int]) -> bool:
    return all(280 <= side <= 1568 for side in size)


def test_every_real_shot_of_a_test_goes_to_jev_as_tiles_that_fit(tmp_path, capsys):
    shutil.copytree(AT_32, tmp_path / ".scratch" / "easter-eggs")
    jev = FakeJev(answer=_by_prefix(c_=0.05))

    code = cli.main(["evidence-flags", "easter-eggs", "AT-32", "--root", str(tmp_path)], jev=jev)

    assert code == 0
    assert capsys.readouterr().out.strip().splitlines()[-1].startswith("Evidence flags: 1 tests, 0 flags, 0 errors")
    evidence = jev.requests[0].state["evidence"]
    listed = [path for path in evidence["file_names"] if path.endswith(".png")]
    assert len(listed) == 12
    assert list(evidence["screenshots"]) == listed
    for path, tiles in evidence["screenshots"].items():
        sizes = _sizes(tiles)
        # The list of each shot with its tile count and sizes is evidence of AT-10, so the run with -s prints it.
        print(path, len(tiles), sizes)
        assert sizes and all(_in_range(size) for size in sizes)
    # Each text file goes in full.
    steps = (AT_32 / "evidence" / "AT-32" / "steps.txt").read_text(encoding="utf-8")
    assert evidence["text_files"]["evidence/AT-32/steps.txt"] == steps


def _png(path: Path, width: int, height: int, noise: bool = False) -> None:
    """A real PNG. Noise does not compress, so a noise shot of 1568 px a side is about 7 MiB."""
    if noise:
        image = Image.frombytes("RGB", (width, height), os.urandom(width * height * 3))
    else:
        image = Image.new("RGB", (width, height), (40, 80, 120))
    image.save(path, format="PNG")


def _one_test(root: Path, shots: list[str]) -> Path:
    """A feature folder with one site test whose files are `shots`, each under evidence/AT-1/."""
    folder = root / ".scratch" / "demo"
    (folder / "evidence" / "AT-1").mkdir(parents=True)
    (folder / "ACCEPTANCE.md").write_text(ACCEPTANCE, encoding="utf-8")
    files = ", ".join(f"`evidence/AT-1/{name}`" for name in shots)
    (folder / "EVIDENCE.md").write_text(
        f"## AT-1: A clock window holds\n\nApp: site\nFiles: {files}\nObservation: The shots show it.\n",
        encoding="utf-8")
    return folder


def test_a_tall_wide_or_small_shot_is_scaled_and_cut_into_tiles_that_fit(tmp_path):
    folder = _one_test(tmp_path, ["tall.png", "wide.png", "small.png"])
    _png(folder / "evidence" / "AT-1" / "tall.png", 375, 4000)
    _png(folder / "evidence" / "AT-1" / "wide.png", 2560, 1800)
    _png(folder / "evidence" / "AT-1" / "small.png", 200, 100)
    jev = FakeJev(yes=0.95)

    cli.main(["evidence-flags", "demo", "--root", str(tmp_path)], jev=jev)

    shots = jev.requests[0].state["evidence"]["screenshots"]
    assert all(_in_range(size) for tiles in shots.values() for size in _sizes(tiles))
    # 4000 px cuts at 1568 and 3136, and the last 864 px make a third tile.
    assert _sizes(shots["evidence/AT-1/tall.png"]) == [(375, 1568), (375, 1568), (375, 864)]
    assert _sizes(shots["evidence/AT-1/wide.png"]) == [(1568, 1102)]
    assert _sizes(shots["evidence/AT-1/small.png"]) == [(280, 280)]


def test_a_state_over_32_mib_sends_the_shots_that_fit_in_the_order_of_files_and_logs_the_cut(tmp_path, capsys):
    names = [f"shot-{n}.png" for n in range(1, 7)]
    folder = _one_test(tmp_path, ["steps.txt", *names])
    (folder / "evidence" / "AT-1" / "steps.txt").write_text("1. Open the page.\n", encoding="utf-8")
    for name in names:
        _png(folder / "evidence" / "AT-1" / name, 1568, 1568, noise=True)
    jev = FakeJev(yes=0.95)

    code = cli.main(["evidence-flags", "demo", "--root", str(tmp_path)], jev=jev)

    assert code == 0
    evidence = jev.requests[0].state["evidence"]
    sent = list(evidence["screenshots"])
    assert 0 < len(sent) < len(names)
    assert sent == [f"evidence/AT-1/{name}" for name in names[:len(sent)]]
    assert evidence["text_files"] == {"evidence/AT-1/steps.txt": "1. Open the page.\n"}
    assert capsys.readouterr().out.strip().splitlines()[-1].endswith(", 1 cut")


def _by_prefix(default: float = 0.95, **answers: float):
    """An `answer` callback for FakeJev: each Noul whose key starts with a name of `answers` gets that value."""
    def answer(key, question, state):
        return next((value for prefix, value in answers.items() if key.startswith(prefix)), default)
    return answer


def test_motion_with_only_still_shots_gets_a_b_flag(tmp_path, capsys):
    shutil.copytree(AT_32, tmp_path / ".scratch" / "easter-eggs")
    jev = FakeJev(answer=_by_prefix(b_asks_motion=0.95, b_logs_motion=0.05, c_=0.05, d_rel=0.05))

    code = cli.main(["evidence-flags", "easter-eggs", "AT-32", "--root", str(tmp_path)], jev=jev)

    assert code == 0
    flags = (tmp_path / ".scratch" / "easter-eggs" / "FLAGS.md").read_text(encoding="utf-8")
    assert "## AT-32, question (b)" in flags
    assert "Probability: 0.90" in flags
    assert "question (a)" not in flags and "question (c)" not in flags and "question (d)" not in flags


def test_a_test_with_a_video_or_timed_frames_gets_no_b_flag_and_no_question_about_it(tmp_path, capsys):
    for case, names in {"video": ["clip.webm", "end.png"],
                        "frames": ["frame-0ms-375.png", "frame-400ms-375.png"]}.items():
        root = tmp_path / case
        folder = _one_test(root, names)
        for name in names:
            if name.endswith(".png"):
                _png(folder / "evidence" / "AT-1" / name, 375, 600)
            else:
                (folder / "evidence" / "AT-1" / name).write_bytes(b"\x1a\x45\xdf\xa3 webm")
        jev = FakeJev(answer=_by_prefix(default=0.05, a_=0.95, d_shown=0.95))

        code = cli.main(["evidence-flags", "demo", "--root", str(root)], jev=jev)

        assert code == 0
        questions = jev.requests[0].questions
        assert not [key for key in questions if key.startswith("b_")]
        assert not [key for key, q in questions.items() if "video" in f"{q.instructions} {q.yes} {q.no}".lower()]
        assert not (folder / "FLAGS.md").exists()


THREE_SENTENCES = (
    "At 00:40 ET the check answered no match. At 23:30 ET the same check matched. "
    "The run took 17 s.")


def test_an_observation_of_three_sentences_gets_one_d_question_per_sentence(tmp_path, capsys):
    folder = _scratch(tmp_path, evidence=EVIDENCE.replace(
        "Observation: At 00:40 ET the check answered no match.", f"Observation: {THREE_SENTENCES}"))

    def answer(key, question, state):
        # Each sentence reports a result. Only the third one is in no file.
        if key.startswith("d_shown_"):
            return 0.05 if "17 s" in str(question.instructions) else 0.95
        return 0.95 if key.startswith(("a_", "d_rel_")) else 0.05
    jev = FakeJev(answer=answer)

    code = cli.main(["evidence-flags", "demo", "--root", str(tmp_path)], jev=jev)

    assert code == 0
    questions = jev.requests[0].questions
    shown = [q.instructions for key, q in questions.items() if key.startswith("d_shown_")]
    relevant = [q.instructions for key, q in questions.items() if key.startswith("d_rel_")]
    assert len(shown) == 3 and len(relevant) == 3
    for sentence in ("At 00:40 ET the check answered no match.", "At 23:30 ET the same check matched.",
                     "The run took 17 s."):
        assert sum(sentence in str(text) for text in shown) == 1
        assert sum(sentence in str(text) for text in relevant) == 1
    flags = (folder / "FLAGS.md").read_text(encoding="utf-8")
    assert "## AT-1, question (d)" in flags
    assert "Probability: 0.90" in flags
    assert "The run took 17 s." in flags


def test_a_shot_with_the_then_text_cut_off_gets_a_c_flag_with_one_question_per_shot(tmp_path, capsys):
    names = ["tuesday-375-light.png", "tuesday-1280-light.png"]
    folder = _one_test(tmp_path, names)
    for name in names:
        _png(folder / "evidence" / "AT-1" / name, 375, 600)

    def answer(key, question, state):
        # Only the phone shot cuts the text of the Then line.
        if key.startswith("c_"):
            return 0.95 if "375" in str(question.instructions) else 0.05
        return 0.95 if key.startswith(("a_", "d_shown")) else 0.05
    jev = FakeJev(answer=answer)

    code = cli.main(["evidence-flags", "demo", "--root", str(tmp_path)], jev=jev)

    assert code == 0
    shot_questions = [q for key, q in jev.requests[0].questions.items() if key.startswith("c_")]
    assert len(shot_questions) == 2
    assert all("Then line" in str(q.instructions) for q in shot_questions)
    flags = (folder / "FLAGS.md").read_text(encoding="utf-8")
    assert "## AT-1, question (c)" in flags
    assert "Probability: 0.95" in flags
    assert "evidence/AT-1/tuesday-375-light.png" in flags
    assert "tuesday-1280" not in flags
