# 03: The questions for motion, cut-off text, and the Observation

Spec: `.scratch/evidence-flags/PRD.md`. Acceptance tests AT-1 and AT-2, and Implementation Decisions "The questions module".

**App:** pipeline.

**What to build:** `evidence-flags` asks three more questions in the same request. (b) motion: code first finds a video or timed frames among the files, and Jev answers only whether the test asks for motion and whether a text log holds animation values. (c) cut-off text: one more draft, scoped to the text that the Then line names. (d) the Observation: one Noul per sentence of the Observation asks if the files show it, and a second asks if it reports a result that the Then line asks for. Start from the drafts in the notes of decision tickets 02 and 06. Load the `typesafe:typesafe-ai` skill before any change to a question.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] On easter-eggs AT-32 at `566d11e7`, the live run writes a (b) entry at 0.7 or more (AT-1).
- [ ] On easter-eggs AT-54 at `9582a573`, the live run writes a (d) entry at 0.7 or more (AT-2).
- [ ] Each question has its text, its criteria, and its cut in the one questions module.
- [ ] A CLI test with `FakeJev` shows that a test with a video gets no (b) flag, with no Jev question about the video.
- [ ] A CLI test shows one (d) question per sentence of an Observation of three sentences.
