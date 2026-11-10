# Notes: does TypeSafe Jev take images, and with what limits?

Research for decision ticket 01. Sources are the installed SDK source and the official TypeSafe docs, read on 2026-11-10. No call went to the live API.

## Answer

Yes. Jev takes images. `jev-latest` points to Jev 1.14, and Jev 1.13 and 1.14 both accept PNG and JPEG still images. An image can go in the `state`, in the question `instructions`, or in the criteria of every question kind: Noul, Choice, Score, and Box. The limits are 16 MiB per image file and 32 MiB per request body. Each side must be 280 to 1568 pixels, and the API rejects an image out of range. It does not resize it. An image counts as input tokens at the text price. The docs give no rule yet to estimate the tokens of one image. The installed `typesafe-sdk` 0.7.5 is the first version with image support, so no upgrade is necessary. The `Jev` port must change: it now takes only a text state dict, and it must also take image bytes.

Paths below are relative to the worktree. `SDK/` means `.venv/lib/python3.11/site-packages/typesafe_sdk/`.

## 1. Field, type, and format

The wire request:

- The request has a top-level field `assets: dict[str, Asset]`. It holds media assets keyed by an opaque placeholder. The API replaces each placeholder "wherever it appears as or inside a string in state, question instructions, or criteria". The schema says "Image assets require a vision-language model." Source: `SDK/_schemas/models.py` lines 264-269.
- An `Asset` has `type: "image"`, `format`, `data_base64`, and `part`. With `part`, the image is a part of a `multipart/form-data` body, and `data_base64` is ignored. Source: `SDK/_schemas/models.py` lines 18-26.
- The `format` enum has `png`, `jpg`, and `jpeg` only. Source: `SDK/_schemas/models.py` lines 12-15.
- The docs accept "PNG or JPEG, still images only. Animated PNGs are rejected." Convert GIF, WebP, or HEIC to PNG or JPEG first. Source: https://docs.typesafe.ai/go/images.md
- The docs recommend multipart. Base64 in the JSON is the fallback. The docs say nothing about an image URL, so a URL input is not confirmed. Source: https://docs.typesafe.ai/go/images.md

The Python SDK:

- The class is `typesafe_sdk.Image`. It takes raw bytes, any buffer, or a file path. `Image.from_base64` and `Image.from_pil` also make one. Source: `SDK/_core/assets.py` lines 73-191.
- `Asset` is an alias of `Image`. "currently only images are supported". Source: `SDK/_core/assets.py` lines 273-274.
- The SDK recognizes PNG and JPEG by the file signature. It sends any other bytes as `application/octet-stream`, and the API detects the format. Source: `SDK/_core/assets.py` lines 24-28 and 345-349.
- An `Image` can go anywhere that `Content` goes, inside a dict or a list too. Source: `SDK/_core/content_types.py` lines 13-21.
- `system_one` takes an optional `assets=` mapping. `attach_assets` lets an f-string carry the reference `str(image)`. Source: `SDK/_core/client/sync/client.py` lines 111-143 and 146-192.
- The SDK always sends images as multipart: a JSON part named `request`, then one part `asset-<n>` for each image. Source: `SDK/_core/endpoints.py` lines 53-87.

## 2. Limits

| Limit | Value | Source |
| --- | --- | --- |
| Images per request | No fixed count. The byte limits and the context length set it. | https://docs.typesafe.ai/go/images.md |
| Bytes per image file | 16 MiB | https://docs.typesafe.ai/go/images.md |
| Bytes per request body | 32 MiB, with the JSON, base64, and multipart framing | https://docs.typesafe.ai/go/images.md |
| Width and height | 280 to 1568 pixels each | https://docs.typesafe.ai/go/images.md |
| Total pixels | 78,400 to 2,458,624 | https://docs.typesafe.ai/go/images.md |
| Resize | None. The API rejects an image out of range. Scale the longest side to 1568 pixels or less. | https://docs.typesafe.ai/go/images.md |
| Context | 64k tokens per request and 32k per question. A long-context header raises both to 262k. | https://docs.typesafe.ai/go/models.md |
| Cost | Each image counts as input tokens at the text price. No separate image charge. Price is $0.042 per Mtok of input. Output is free. | https://docs.typesafe.ai/go/images.md and https://docs.typesafe.ai/go/models.md |
| Tokens per image | Not confirmed. The docs say "We'll be providing guidance on estimating image token usage soon." | https://docs.typesafe.ai/go/images.md |

The pixel limits matter for this ticket. A full-page screenshot at 375 by 2000 CSS pixels fails the 1568 limit. A 1280-wide screenshot at a device pixel ratio of 2 is 2560 pixels wide, so it also fails. The caller must crop or scale each screenshot first. The SDK itself checks only that the data is not empty. It checks no size. Source: `SDK/_core/assets.py` lines 259-270.

## 3. Question kinds

- The docs say "Every question type accepts images". Choice options, Score levels, and Noul true and false definitions can each hold an image. Source: https://docs.typesafe.ai/go/images.md
- The SDK types agree. Noul `instructions` and `criteria.true` and `criteria.false`, Choice `instructions` and `criteria`, and Score `instructions` and `criteria` are all `Content`, and `Content` can be an asset. Source: `SDK/_core/question_types.py` lines 14-23, 36-80, and 95-139.
- Box locates a thing "in the request's image" and returns its edges as fractions of the image height and width. Source: `SDK/_core/question_types.py` lines 142-164 and `SDK/_core/response_types.py` lines 62-74.
- Box needs Jev 1.14. The other kinds work on Jev 1.13 and 1.14. Source: https://docs.typesafe.ai/go/images.md
- `jev-latest` points to `jev-1.14.0` now, so all four kinds work with the alias the repo uses. Source: https://docs.typesafe.ai/go/models.md and `packages/league/python/src/league/jev.py` line 10.

## 4. SDK version

- The repo pins `typesafe-sdk>=0.7.5`. Source: `packages/league/python/pyproject.toml` line 16.
- `uv.lock` and the `.venv` both hold 0.7.5. Source: `uv.lock` lines 1162-1163 and `.venv/lib/python3.11/site-packages/typesafe_sdk-0.7.5.dist-info/METADATA` line 3.
- The changelog shows that 0.7.5, from 2026-10-14, added `Image` assets, `Box` questions, and `attach_assets`. 0.7.5 is also the latest release. Source: https://docs.typesafe.ai/go/python-changelog
- No upgrade is necessary. The optional `pil` extra adds `Image.from_pil`. The repo does not need it if it passes PNG bytes. Source: `.venv/lib/python3.11/site-packages/typesafe_sdk-0.7.5.dist-info/METADATA` line 66.

## 5. Change to the `Jev` port

`Jev.ask` takes `state: dict` and `NoulQuestion.instructions: dict | str`, and the port forbids an SDK import above the adapter. Source: `packages/league/python/src/league/jev_port.py` lines 16-42. The port needs its own image type, for example PNG bytes with a name, that a state dict or a question may hold. The adapter `TypeSafeJev.ask` then wraps each one in `typesafe_sdk.Image` before it calls `system_one`. Source: `packages/league/python/src/league/jev.py` lines 22-35. The caller, not the port, must crop or scale each screenshot to 280 to 1568 pixels on each side, because the API rejects an image out of range. `FakeJev` in `tests/fakes.py` must also accept the image type.
