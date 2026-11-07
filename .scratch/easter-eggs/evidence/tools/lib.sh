# The shared helpers of the API evidence of easter-eggs. Source it from a step script.
# Each helper writes the command after "$ " and then its output into the file OUT.
API=http://127.0.0.1:8080
E=$API/clients/cpc/eggs
J='Content-Type: application/json'
KEY='X-Commissioner-Key: localkey'
PASS='X-League-Passphrase: localtest'
EV=/Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/easter-eggs/.scratch/easter-eggs/evidence

# run <command...>: write the command and its output, with the HTTP status, to OUT.
run() {
  printf '$ %s\n' "$*" >> "$OUT"
  eval "$@" >> "$OUT" 2>&1
  printf '\n\n' >> "$OUT"
}
# note <text>: write a note line to OUT.
note() { printf '# %s\n' "$*" >> "$OUT"; }
# board_counts: the counts of the board, one line.
board_counts() { curl -s $E/board | python3 -c "import json,sys; b=json.load(sys.stdin); print(json.dumps(b['counts']))"; }
# token <page> <target> <action> <conditions json>: the claim token of a check, or nothing.
token() { curl -s -X POST $E/check -H "$J" -d "{\"page\":\"$1\",\"target\":\"$2\",\"action\":\"$3\",\"conditions\":$4}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('token',''))"; }
