"""
Run the real API with uvicorn, and save each Finder pick sheet and pick prompt that the real code builds to a JSON file.
The wrap only records the return values of offer_sheet and build_pick_prompt; it changes no input and no output.
"""
import json
import os
import sys
from dataclasses import asdict, is_dataclass

import uvicorn
from analyzer import finder_pick

OUT = os.environ["SHEET_LOG"]
_offer_sheet = finder_pick.offer_sheet
_build_pick_prompt = finder_pick.build_pick_prompt


def _plain(value):
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return str(value)


def _save(record: dict) -> None:
    with open(OUT, "a") as f:
        f.write(json.dumps(record, default=_plain) + "\n")


def offer_sheet(offer, snapshot, news):
    sheet = _offer_sheet(offer, snapshot, news)
    _save({"kind": "offer_sheet", "offer_id": offer.offer_id, "trade": offer.trade,
           "sheet": {fid: {"text": f.text} for fid, f in sheet.items()}})
    return sheet


def build_pick_prompt(*args, **kwargs):
    prompt = _build_pick_prompt(*args, **kwargs)
    _save({"kind": "pick_prompt", "prompt": prompt})
    return prompt


finder_pick.offer_sheet = offer_sheet
finder_pick.build_pick_prompt = build_pick_prompt

if __name__ == "__main__":
    uvicorn.run("cornerstone_api.app:app_from_env", factory=True, port=int(sys.argv[1]))
