"""
Run the real local API of the repo on one port, with the INFO log of the app on, and log each sheet the Advisor reads.
With BLOCK_NEWS=1 the Sleeper news host of this process points at a closed local port, so every news fetch fails.
"""
import logging
import os
import sys

import uvicorn

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("evidence")

import analyzer.advisor as advisor  # noqa: E402
import league.provider.sleeper as sleeper  # noqa: E402

if os.environ.get("BLOCK_NEWS") == "1":
    # Port 9 on the local machine is closed, so a connect fails at once, as a blocked host does.
    sleeper.UNOFFICIAL_URL = "https://127.0.0.1:9"
    log.info("The news host of this process is %s, a closed port", sleeper.UNOFFICIAL_URL)

real_sheet = advisor.advisor_sheet


def logged_sheet(trade, snapshot, jev, news):
    """The real sheet, unchanged, with one log line per fact, so the evidence holds the sheet of each press."""
    facts = real_sheet(trade, snapshot, jev, news)
    log.info("SHEET of the press: week %s, chart week %s, %d facts", snapshot.week,
             snapshot.chart.week if snapshot.chart else None, len(facts))
    for fid, f in facts.items():
        log.info("SHEET %s: %s | numbers=%s", fid, f.text, f.numbers)
    return facts


advisor.advisor_sheet = logged_sheet

if __name__ == "__main__":
    uvicorn.run("cornerstone_api.app:app_from_env", factory=True, host="127.0.0.1", port=int(sys.argv[1]))
