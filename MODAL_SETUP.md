# Modal Video Engine — Setup & Layered Build

We're adding **AI image-to-video + lip-sync** via [Modal](https://modal.com)
serverless GPUs (`VIDEO_BACKEND=modal`). Cloud Claude can't reach Modal, so this
is deployed and verified on a machine with the `modal` CLI (Local Claude / owner).

We build in **layers**, verifying each on a real machine before the next — so we
never stack unverified GPU code.

## One-time setup

```bash
pip install modal
modal token new        # opens a browser; authorizes this machine (writes ~/.modal.toml)
```

Modal's free tier includes monthly compute credits — plenty for iterating on clips.

## Layer 1 — prove Modal + GPU work (do this first)

```bash
modal run backend/services/modal_video_worker.py
```

Expected output:
```
RESULT: {'cuda_available': True, 'device': 'Tesla T4', 'torch_version': '2.x.x'}
✅ Modal + GPU working. Ready for Layer 2 (image-to-video).
```

- ✅ `cuda_available: True` → Modal + GPU confirmed. Report back and Cloud Claude ships Layer 2.
- ❌ any error (auth, install, no GPU) → paste it back; that's what Cloud Claude fixes next.

**Report the result as a `RESULT:` comment on PR #6.**

## The layered plan

| Layer | What | Verify by |
|-------|------|-----------|
| 1 | Modal + GPU sanity (`gpu_check`) | `modal run …` prints `cuda_available: True` |
| 2 | Image-to-video (`generate_video_clip_remote`, LTX-Video) | one still → one short motion clip |
| 3 | Lip-sync (`apply_lipsync_remote`, Wav2Lip/LivePortrait) | one talking face → mouth matches a vocal clip |
| 4 | Pipeline wiring (`run_video_generation` in the orchestrator) + audio slicing + assembly | full WOW OH! render with lip-sync |

Each layer is a separate push + a separate `RESULT:` check. No layer starts until
the previous one is confirmed working on a real machine.

## Config (already added)

`.env` (see `.env.example`):
```
VIDEO_BACKEND=modal        # ffmpeg (stills) | modal (AI video + lip-sync)
LIPSYNC_ENABLED=true
MODAL_TOKEN_ID=            # from `modal token new` (or leave blank; modal reads ~/.modal.toml)
MODAL_TOKEN_SECRET=
```

Tokens are gitignored via `.env` and must never be committed.
