# Two-Claude Collaboration Protocol

This repo is worked on by **two Claude instances** that talk to each other through
**comments on the active GitHub PR** (currently **PR #6**).

## The two roles

| | Cloud Claude (Claude Code) | Local Claude (Claude Desktop + Desktop Commander) |
|---|---|---|
| Runs in | a remote Linux cloud container | the owner's Windows PC (`C:\Users\booki\HTXpunk LLC\htxpunk-mv-generator`) |
| Can | author code, push to GitHub, read/comment on the PR | run the app, test, build/sign the installer, fix machine-specific issues |
| Cannot | touch the Windows PC, reach `api.cloudflare.com`, run a GUI | hold the full project history a cold start lacks |
| Triggered by | PR comments (delivered as wake events) | the human, or by reading Cloud Claude's PR comments |

Neither Claude can do the other's half. Cloud writes the code; Local runs it on the
real machine.

## How they talk — PR comments only

A **comment on the PR** is the reliable signal that wakes Cloud Claude. Raw pushes and
file edits do **not** reliably generate wake events, so: edit/push freely, but **always
drop a one-line PR comment as the doorbell.**

Comment prefixes (keep them, they make intent unambiguous):

- `REQUEST:` — Local → Cloud. A change/feature to implement. Be specific.
- `RESULT:` — Local → Cloud. What happened running/testing on the PC (paste real
  output/errors verbatim — that's what lets Cloud fix it without guessing).
- `DONE:` — Cloud → Local. Pushed; pull the branch and test. Says what to run.
- `NEED:` — Cloud → Local. A question or decision required before continuing.

## Standard loop

1. Local Claude (driven by the human) posts `REQUEST: …` on the PR.
2. Cloud Claude wakes, implements it, pushes to `claude/youthful-cray-l9yx4c`,
   and comments `DONE: pushed — run X, report back`.
3. Local Claude pulls, runs/tests on the PC, comments `RESULT: …` (success or the
   exact error).
4. Repeat until the feature works on the real machine.

## Running on the PC (Local Claude quick start)

```powershell
cd "C:\Users\booki\HTXpunk LLC\htxpunk-mv-generator"
git fetch origin
git checkout claude/youthful-cray-l9yx4c
git reset --hard origin/claude/youthful-cray-l9yx4c   # match the cloud branch exactly
```

`.env` is **gitignored** and must never be committed. It already exists on the PC with
the working keys. Minimal deps for the storyboard path:

```powershell
pip install requests Pillow sqlalchemy aiosqlite httpx imageio-ffmpeg pydantic-settings python-dotenv
```

Generate stills and view them in the app:
```powershell
cd backend
python make_wow_oh_images.py          # generates 30 frames, stops before video
uvicorn main:app --port 8000          # window A
# window B:  cd ../frontend ; npm install ; npm run dev
# open the storyboard URL the script printed
```

## Current state / what's next

- ✅ Cloudflare Workers AI (FLUX.1-schnell) image backend — verified on owner's account
- ✅ Storyboard frames viewable + manageable (redo / reorder) in the UI
- ⬜ Storyboard → animated video clips (needs a **paid** image-to-video model — decision pending)
- ⬜ One-double-click Windows installer (bundle Python backend + Electron; **Local Claude's job to build/test**)

## Secrets hygiene

Never put API keys/tokens in commits, code, or PR comments. Keys live only in the
local `.env` (gitignored). If a secret is ever pasted somewhere tracked, rotate it.
