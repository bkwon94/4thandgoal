"""
Runs shell commands at the same time and prints the output of each one as one block when it ends, with its name and time.
Run `python3 -B scripts/parallel.py NAME COMMAND [NAME COMMAND ...]`. The exit code is 1 when a command fails.
"""
import subprocess
import sys
import threading
import time


def run_job(name: str, command: str, done: list, ended: threading.Condition) -> None:
    start = time.monotonic()
    # stderr joins stdout, so a block keeps the order of the lines of its command.
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with ended:
        done.append((name, result.returncode, result.stdout, time.monotonic() - start))
        ended.notify()


def main(args: list[str]) -> int:
    if not args or len(args) % 2:
        print("usage: parallel.py NAME COMMAND [NAME COMMAND ...]", file=sys.stderr)
        return 2
    jobs = list(zip(args[0::2], args[1::2]))
    # A list and a condition hold the ended jobs, not the queue module, because scripts/queue.py shadows that module
    # when Python runs a file of this folder.
    done: list = []
    ended = threading.Condition()
    for name, command in jobs:
        threading.Thread(target=run_job, args=(name, command, done, ended), daemon=True).start()
    failed = False
    # Each block prints whole when its job ends, so the lines of two jobs never mix.
    for _ in jobs:
        with ended:
            ended.wait_for(lambda: done)
            name, code, output, secs = done.pop(0)
        sys.stdout.write(output)
        if code == 0:
            print(f"==> {name}: ok ({secs:.1f} s)", flush=True)
        else:
            failed = True
            print(f"==> {name}: FAILED with exit code {code} ({secs:.1f} s)", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
