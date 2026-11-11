# 01: The Jev port carries an image

Spec: `.scratch/evidence-flags/PRD.md`. Acceptance test AT-13, and Implementation Decisions "The image type and the cut of a shot".

**App:** pipeline.

**What to build:** A caller of the `Jev` port can put a PNG image in a state with no import of the SDK. The TypeSafe adapter sends it as an image, and `FakeJev` takes it and keeps it in its requests. The weekly build and the analyzer work as before.

**Blocked by:** none.

**Status:** done

- [x] The port has its own image type for PNG bytes, and only the TypeSafe adapter imports `typesafe_sdk` outside tests (AT-13).
- [x] The adapter wraps each image of a state in the SDK image type before the call.
- [x] A test of `FakeJev` with a state that holds an image passes, and the request keeps the image.
- [x] One live call by hand with a small real screenshot gives an answer, and its input tokens show in the output.
- [x] `make check-fast` passes for the pipeline and the packages.
