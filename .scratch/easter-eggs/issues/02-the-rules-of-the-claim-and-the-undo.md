# 02: The rules of the claim and the undo

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-6, AT-7, AT-9, AT-10, AT-11, AT-12, and AT-17.

**App:** pipeline

**What to build:** The claim route of the API follows every rule of the spec. The first claim wins a tie. The API refuses a claim for the commissioner, a letter with no open slot, a block when the letter fits, and an egg word with a winner. A block counts as found. The commissioner undoes a claim with one make target.

**Blocked by:** 01

**Status:** done

- [x] Two claims of one egg at once give one winner. The other answers that another manager claimed first.
- [x] The API refuses a claim for the roster of the commissioner of the package values.
- [x] The API refuses a letter into an egg word whose slots for that letter the manager holds.
- [x] A block is accepted only when the letter fits no open egg word of the manager. The board counts it as found and shows it nowhere else.
- [x] The claim that fills an egg word names the winner on the board. That egg word then takes no more letters.
- [ ] `make egg-undo CLIENT=cpc EGG=<id>` sets the undo time of the claim. The egg is live again, and the claims table keeps the row.
- [x] The API tests cover each rule through the FastAPI test client with a temp SQLite file.

## Comments
- Closed by the merge of PR #19.
