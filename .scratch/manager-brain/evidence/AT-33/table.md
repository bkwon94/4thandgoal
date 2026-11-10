# AT-33: 10 cold presses at 6ba706cf

$ grep 'Press of' <folder>/log.txt   # for each folder below; each server is a plain API on port 8081 (see server.txt)

| Press | Folder | Server | Result cache | time | cost | claude_calls | Press of line |
| --- | --- | --- | --- | --- | --- | --- | --- |
| analyze | `analyze/` | a | new folder cache-6ba7-a, first press of the server | 30.9s | $0.0685 | 1 | `Press of analyze for cpc: time=30.9s cost=$0.0685 claude_calls=1` |
| analyze | `analyze-2/` | d | new folder cache-6ba7-d, empty | 25.8s | $0.0553 | 1 | `Press of analyze for cpc: time=25.8s cost=$0.0553 claude_calls=1` |
| analyze | `analyze-3/` | d | cache-6ba7-d, saved result deleted before the press | 25.7s | $0.0581 | 1 | `Press of analyze for cpc: time=25.7s cost=$0.0581 claude_calls=1` |
| analyze | `analyze-4/` | d | cache-6ba7-d, saved result deleted before the press | 20.7s | $0.0525 | 1 | `Press of analyze for cpc: time=20.7s cost=$0.0525 claude_calls=1` |
| analyze | `analyze-5/` | d | cache-6ba7-d, saved result deleted before the press | 22.3s | $0.0524 | 1 | `Press of analyze for cpc: time=22.3s cost=$0.0524 claude_calls=1` |
| find | `find-1/` | a | cache-6ba7-a, no find result saved yet | 20.2s | $0.0739 | 1 | `Press of find for cpc: time=20.2s cost=$0.0739 claude_calls=1` |
| find | `find-2/` | b | new folder cache-6ba7-b, empty | 25.9s | $0.0749 | 1 | `Press of find for cpc: time=25.9s cost=$0.0749 claude_calls=1` |
| find | `find-3/` | c | new folder cache-6ba7-c, empty | 32.3s | $0.0910 | 2 | `Press of find for cpc: time=32.3s cost=$0.0910 claude_calls=2` |
| find | `find-4/` | d | cache-6ba7-d, saved result deleted before the press | 24.1s | $0.0780 | 1 | `Press of find for cpc: time=24.1s cost=$0.0780 claude_calls=1` |
| find | `find-5/` | d | cache-6ba7-d, saved result deleted before the press | 25.6s | $0.0816 | 1 | `Press of find for cpc: time=25.6s cost=$0.0816 claude_calls=1` |
