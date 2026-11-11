"""
The evidence-flags command: it reads each acceptance test of a feature, its entry in EVIDENCE.md, and its files,
asks Jev the in-flow questions in one request per test, and adds each flag past its cut to FLAGS.md as open.
"""
import io
import json
import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from cornerstone.evidence_questions import Question, in_flow
from league.jev_port import Jev, JevError, JevImage

# The API takes 280 to 1568 px per side and never resizes, so code scales and cuts each shot first.
MIN_SIDE, MAX_SIDE = 280, 1568
SHOT_EXT = {"png", "jpg", "jpeg"}
VIDEO_EXT = {"webm", "mp4", "mov", "gif"}
# The API takes 32 MiB per request body, with the JSON and the multipart framing. The margin covers the question text
# and the framing of each part, so a state at the limit still fits.
REQUEST_LIMIT = 32 * 1024 * 1024
REQUEST_MARGIN = 256 * 1024
PART_FRAMING = 1024
# Jev 1.14 takes 32k tokens for the state plus one question, and 64k for the state plus all questions
# (https://docs.typesafe.ai/go/models.md, "Context length"). A live probe agrees: a state of six plain
# 1280 x 1568 tiles passed at 31,442 input tokens, and seven tiles gave `400 max_tokens_exceeded`. The budget of the
# state sits about 4,000 tokens under 32k. The margin covers the longest question and the error of the estimate.
TOKEN_BUDGET = 28_000
# A calibration run measured about one input token per 350 to 390 px of an image, and the probe
# above measured 387 px. Text costs about one token per 4 bytes, and 3 bytes a token keeps the estimate on the safe side.
PIXELS_PER_TOKEN = 380
BYTES_PER_TOKEN = 3
# A whole round has about 40 tests, and four requests at one time keep it to about a minute.
WORKERS = 4
# A title with the word Retired anywhere, or a title that starts with Skipped, gets no request.
NO_REQUEST_TITLE = re.compile(r"\bRetired\b|^Skipped\b", re.IGNORECASE)


@dataclass
class Evidence:
    """The entry of one test in EVIDENCE.md, by its keys, and the files that its `Files:` line names."""
    id: str
    title: str
    keys: dict[str, str]
    files: list[str]


@dataclass(frozen=True)
class Flag:
    """One yes past the cut of its question, as FLAGS.md holds it."""
    test: str
    question: Question
    probability: float
    reason: str

    def entry(self) -> str:
        return (f"## {self.test}, question ({self.question.key})\n\n"
                f"Question: {self.question.name}\n"
                f"Probability: {self.probability:.2f}\n"
                f"Reason: {self.reason}\n"
                f"Action: open\n")


@dataclass
class Result:
    """The outcome of one test: the keys asked, the flags, the error, the input tokens, and whether the state was cut."""
    test: str
    asked: list[str] = field(default_factory=list)
    flags: list[Flag] = field(default_factory=list)
    error: str | None = None
    tokens: int = 0
    cut: bool = False


def acceptance_tests(text: str) -> dict[str, dict[str, str]]:
    """Each test of ACCEPTANCE.md by its id: its title and each `Key: value` line, with the key in lower case."""
    tests: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    for line in text.splitlines():
        head = re.match(r"^(AT-\d+): (.*)$", line)
        if head:
            current = tests.setdefault(head.group(1), {"title": head.group(2).strip()})
        elif not line.strip():
            current = None
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip().lower()] = value.strip()
    return tests


def evidence_entries(text: str) -> dict[str, Evidence]:
    """Each entry of EVIDENCE.md by its test id. A line with no key of its own goes on to the key above it.

    A key that repeats in one entry joins its values in order with one space.

    A test of two apps can have one entry per half, such as `## AT-50 (pipeline half): ...` and `## AT-50 (site
    half)`. The halves make one entry: each key of a later half goes on a new line after the same key of the first.
    """
    entries: dict[str, Evidence] = {}
    current: Evidence | None = None
    key: str | None = None
    seen: set[str] = set()
    for line in text.splitlines():
        head = re.match(r"^## (AT-\d+)(?: \([^)]*\))?(?:: (.*))?$", line)
        if head:
            current = entries.setdefault(head.group(1), Evidence(head.group(1), "", {}, []))
            current.title = current.title or (head.group(2) or "").strip()
            key, seen = None, set()
        elif line.startswith("## "):
            current = None
        elif current is not None and (named := re.match(r"^([A-Z][A-Za-z ]*): (.*)$", line)):
            key = named.group(1).lower()
            value = named.group(2).strip()
            if key in seen:
                current.keys[key] += f" {value}"
            elif key in current.keys:
                current.keys[key] += f"\n{value}"
            else:
                current.keys[key] = value
            seen.add(key)
        elif current is not None and key is not None and line.strip():
            current.keys[key] += "\n" + line.strip()
    for entry in entries.values():
        entry.files = re.findall(r"`([^`]+)`", entry.keys.get("files", ""))
    return entries


def gets_request(entry: Evidence, accepted: dict[str, str] | None = None) -> bool:
    """A test at `Files: none`, a skipped test, and a retired test get no request.

    The title of the test in EVIDENCE.md and its title in ACCEPTANCE.md both count.
    """
    titles = (entry.title, (accepted or {}).get("title", ""))
    return bool(entry.files) and not any(NO_REQUEST_TITLE.search(title) for title in titles)


def tiles(data: bytes) -> list[JevImage]:
    """The shot scaled to a width of 280 to 1568 px, then cut from the top into tiles of 1568 px or less in height.

    A shot shorter than 280 px gets white below it. A last tile under 280 px starts higher, so it overlaps the tile
    above it and keeps each side in range.
    """
    image = Image.open(io.BytesIO(data)).convert("RGB")
    width, height = image.size
    if width > MAX_SIDE or width < MIN_SIDE:
        scaled = MAX_SIDE if width > MAX_SIDE else MIN_SIDE
        image = image.resize((scaled, max(1, round(height * scaled / width))), Image.Resampling.LANCZOS)
    width, height = image.size
    if height < MIN_SIDE:
        canvas = Image.new("RGB", (width, MIN_SIDE), "white")
        canvas.paste(image, (0, 0))
        image, height = canvas, MIN_SIDE
    out = []
    for top in range(0, height, MAX_SIDE):
        start = top if height - top >= MIN_SIDE else height - MIN_SIDE
        buffer = io.BytesIO()
        image.crop((0, start, width, min(start + MAX_SIDE, height))).save(buffer, format="PNG")
        out.append(JevImage(buffer.getvalue()))
    return out


def _pixels(image: JevImage) -> int:
    width, height = Image.open(io.BytesIO(image.png)).size
    return width * height


def _kind(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return "shot" if ext in SHOT_EXT else "video" if ext in VIDEO_EXT else "text"


def build_state(test_id: str, accepted: dict[str, str], entry: Evidence, folder: Path) -> tuple[dict, bool]:
    """The state of one test, and True when a file did not fit in one request.

    The state holds the test, the Observation, the list of files, the text files, and the shots as tiles.
    The text files go first, then the shots, each in the order of `Files:`. A file goes in while the state stays
    under the request limit in bytes and the token budget. The first file of its kind that does not fit stops that kind.
    """
    texts: list[str] = []
    videos, missing, shots = [], [], []
    for path in entry.files:
        file = folder / path
        if not file.is_file():
            missing.append(path)
        elif _kind(path) == "video":
            videos.append(path)
        elif _kind(path) == "shot":
            shots.append(path)
        else:
            texts.append(path)
    text_files: dict[str, str] = {}
    evidence: dict = {"file_names": entry.files, "text_files": text_files, "video_files": videos}
    # An empty list can read as a signal, so the state names missing files only when there are some.
    if missing:
        evidence["missing_files"] = missing
    state = {
        "test": {"id": test_id, "title": accepted.get("title", entry.title), "app": accepted.get("app"),
                 "given": accepted.get("given"), "when": accepted.get("when"),
                 "then": accepted.get("then") or entry.keys.get("then", ""),
                 "evidence_asked": accepted.get("evidence")},
        "agent_observation": entry.keys.get("observation", ""),
        "evidence": evidence,
    }
    text_size = len(json.dumps(state).encode("utf-8"))
    size = text_size + REQUEST_MARGIN
    tokens = text_size / BYTES_PER_TOKEN
    cut = False
    for path in texts:
        content = (folder / path).read_text(encoding="utf-8", errors="replace")
        more = len(json.dumps({path: content}).encode("utf-8"))
        if size + more > REQUEST_LIMIT or tokens + more / BYTES_PER_TOKEN > TOKEN_BUDGET:
            cut = True
            break
        text_files[path] = content
        size += more
        tokens += more / BYTES_PER_TOKEN
    screenshots: dict[str, list[JevImage]] = {}
    for path in shots:
        parts = tiles((folder / path).read_bytes())
        more = sum(len(part.png) + PART_FRAMING for part in parts) + len(path)
        more_tokens = sum(_pixels(part) for part in parts) / PIXELS_PER_TOKEN + len(path) / BYTES_PER_TOKEN
        if size + more > REQUEST_LIMIT or tokens + more_tokens > TOKEN_BUDGET:
            cut = True
            break
        screenshots[path] = parts
        size += more
        tokens += more_tokens
    evidence["screenshots"] = screenshots
    return state, cut


def ask_test(test_id: str, accepted: dict[str, str], entry: Evidence, folder: Path, jev: Jev,
             questions: tuple[Question, ...]) -> Result:
    """One request with every in-flow question of the test. A JevError gives no flag and an error in the result."""
    result = Result(test=test_id, asked=[question.key for question in questions])
    state, result.cut = build_state(test_id, accepted, entry, folder)
    nouls = {question.key: question.nouls(state) for question in questions}
    try:
        response = jev.ask(state, {key: noul for each in nouls.values() for key, noul in each.items()})
    except JevError as err:
        result.error = str(err)
        return result
    result.tokens = response.input_tokens or 0
    for question in questions:
        probability, reason = question.flag({key: response.nouls[key] for key in nouls[question.key]}, state)
        if probability >= question.cut:
            result.flags.append(Flag(test_id, question, probability, reason))
    return result


def write_flags(path: Path, slug: str, flags: list[Flag]) -> None:
    """Add each flag to FLAGS.md as an open entry. A run with no flag leaves the file as it is."""
    if not flags:
        return
    text = path.read_text(encoding="utf-8") if path.exists() else (
        f"# {slug}: Evidence flags\n\nThe agent sets the action of each entry: `recorded again`, `fix group`, "
        "`disagree: <one line>`, or `open`. The Judge never reads this file.\n")
    path.write_text(text.rstrip("\n") + "\n\n" + "\n".join(flag.entry() for flag in flags), encoding="utf-8")


def log_line(results: list[Result]) -> str:
    """The one line of counts of a run. A cut state adds the count of cut tests."""
    line = (f"Evidence flags: {len(results)} tests, {sum(len(r.flags) for r in results)} flags, "
            f"{sum(1 for r in results if r.error is not None)} errors, {sum(r.tokens for r in results)} input tokens")
    cut = sum(1 for r in results if r.cut)
    return line + (f", {cut} cut" if cut else "")


def run_evidence_flags(root: Path, slug: str, test_ids: list[str], jev: Jev,
                       echo: Callable[[str], None] = print) -> int:
    """Ask Jev about each test of `slug` under `root`/.scratch, write FLAGS.md, and print each flag and the log line.

    With no test ids, it reads every test that has an entry in EVIDENCE.md. It exits 0 on a Jev error, because a
    vendor outage never blocks the evidence stage. It exits 2 when the feature folder or a file of it is missing.
    """
    folder = root / ".scratch" / slug
    if not (folder / "EVIDENCE.md").is_file() or not (folder / "ACCEPTANCE.md").is_file():
        echo(f"No EVIDENCE.md and ACCEPTANCE.md in {folder}.")
        return 2
    accepted = acceptance_tests((folder / "ACCEPTANCE.md").read_text(encoding="utf-8"))
    entries = evidence_entries((folder / "EVIDENCE.md").read_text(encoding="utf-8"))
    for missing in [each for each in test_ids if each not in entries]:
        echo(f"{missing} has no entry in EVIDENCE.md, so it gets no request.")
    chosen = [entries[each] for each in (test_ids or list(entries)) if each in entries]
    asked = [entry for entry in chosen if gets_request(entry, accepted.get(entry.id, {}))]
    questions = in_flow()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(
            lambda entry: ask_test(entry.id, accepted.get(entry.id, {}), entry, folder, jev, questions), asked))
    flags = [flag for result in results for flag in result.flags]
    write_flags(folder / "FLAGS.md", slug, flags)
    for result in results:
        echo(f"{result.test}: asked {', '.join(result.asked)}")
        if result.error is not None:
            echo(f"{result.test}: Jev error, no flags: {result.error}")
        for flag in result.flags:
            echo(flag.entry())
    echo(log_line(results))
    return 0
