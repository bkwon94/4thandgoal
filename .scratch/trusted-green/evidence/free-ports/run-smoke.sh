# Runs one smoke run of "Week report" and "Passphrase" in one worktree, and tries once more after the Next.js SecurityFatalError.
# Usage: sh run-smoke.sh <worktree> <smoke folder> <console log>
export PATH="$HOME/.nvm/versions/node/v24.15.0/bin:$PATH"
cd "$1" || exit 1
for try in 1 2; do
  echo "try $try start $(date '+%H:%M:%S')" >> "$3.times"
  pnpm --dir apps/site smoke --out "$2" "Week report" "Passphrase" > "$3" 2>&1
  status=$?
  echo "try $try end $(date '+%H:%M:%S') exit $status" >> "$3.times"
  grep -q SecurityFatalError "$3" || break
done
exit $status
