"""
Modal serverless GPU worker — AI image-to-video + lip-sync (self-hosted models).

This code runs on **Modal's cloud GPUs**, not on the user's PC and not in the
Cloud Claude sandbox. It is deployed and invoked from a machine that has the
`modal` CLI and a Modal account.

────────────────────────────────────────────────────────────────────────────
LAYER 1 (this file, now): prove Modal + GPU actually work on your account.
  Run it directly — this deploys an ephemeral app, runs one GPU check, prints
  the result, and tears down:

      pip install modal
      modal token new                                  # one-time browser auth
      modal run backend/services/modal_video_worker.py

  Expect something like:
      {'cuda_available': True, 'device': 'Tesla T4', 'torch_version': '2.x.x'}

  If that prints cuda_available=True, Modal + GPU are working and we move to:

LAYER 2 (next): image-to-video (LTX-Video)  → `generate_video_clip_remote`
LAYER 3 (next): lip-sync (Wav2Lip/LivePortrait) → `apply_lipsync_remote`
LAYER 4 (next): wire into the orchestrator (run_video_generation) + assembly

We build one layer at a time and verify each on your machine before the next,
so we never stack unverified GPU code.
────────────────────────────────────────────────────────────────────────────
"""
import modal

app = modal.App("htxpunk-video-worker")

# Minimal CUDA image: PyPI torch ships the CUDA runtime; Modal provides the
# GPU + driver at run time. Enough to confirm the account/deploy/GPU path.
gpu_image = modal.Image.debian_slim(python_version="3.11").pip_install("torch")


@app.function(gpu="T4", image=gpu_image, timeout=300)
def gpu_check() -> dict:
    """Confirm a CUDA GPU is visible inside the Modal container."""
    import torch
    ok = torch.cuda.is_available()
    return {
        "cuda_available": ok,
        "device": torch.cuda.get_device_name(0) if ok else "none",
        "torch_version": torch.__version__,
    }


@app.local_entrypoint()
def main():
    """`modal run backend/services/modal_video_worker.py` → runs gpu_check."""
    print("Deploying htxpunk-video-worker and running gpu_check on a Modal GPU…")
    result = gpu_check.remote()
    print("RESULT:", result)
    if result.get("cuda_available"):
        print("✅ Modal + GPU working. Ready for Layer 2 (image-to-video).")
    else:
        print("❌ GPU not visible in the container — check the gpu= arg / Modal plan.")
