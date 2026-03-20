"""MAXIA Demo — Rent a GPU

Lists available GPU tiers and rents one via the MAXIA API.
Payment in USDC on Solana. 0% markup (RunPod cost price).

Usage:
    pip install httpx
    python demo_gpu.py
"""
import httpx
import json
import sys

MAXIA_API = "https://maxiaworld.app/api/public"


def register(name: str, wallet: str) -> str:
    """Register an agent on MAXIA."""
    r = httpx.post(f"{MAXIA_API}/register", json={
        "name": name,
        "wallet": wallet,
        "description": f"{name} — AI agent renting GPUs on MAXIA"
    })
    data = r.json()
    if data.get("api_key"):
        print(f"Registered as '{name}'")
        return data["api_key"]
    else:
        print(f"Registration failed: {data}")
        sys.exit(1)


def list_gpu_tiers():
    """List all available GPU tiers with pricing."""
    r = httpx.get(f"{MAXIA_API}/gpu/tiers")
    data = r.json()
    tiers = data.get("tiers", data.get("gpu_tiers", []))

    print(f"\n{'GPU':<20} {'VRAM':<10} {'Price/h':<12} {'vs AWS'}")
    print("-" * 60)
    if isinstance(tiers, dict):
        for name, info in tiers.items():
            price = info.get("price_hour", 0)
            vram = info.get("vram_gb", "?")
            aws = info.get("vs_aws", "")
            print(f"{name:<20} {vram} GB     ${price:<10} {aws}")
    elif isinstance(tiers, list):
        for t in tiers:
            name = t.get("name", t.get("tier", "?"))
            price = t.get("price_hour", 0)
            vram = t.get("vram_gb", "?")
            print(f"{name:<20} {vram} GB     ${price}")
    return data


def rent_gpu(api_key: str, gpu_tier: str, hours: float, payment_tx: str) -> dict:
    """Rent a GPU. Returns SSH/API credentials."""
    r = httpx.post(f"{MAXIA_API}/gpu/rent",
        headers={"X-API-Key": api_key},
        json={
            "gpu_tier": gpu_tier,
            "hours": hours,
            "payment_tx": payment_tx,
        },
        timeout=30,
    )
    data = r.json()
    if data.get("success"):
        print(f"\nGPU rented: {gpu_tier} for {hours}h")
        print(f"  Pod ID: {data.get('pod_id', '?')}")
        print(f"  SSH: {data.get('ssh', '?')}")
        print(f"  Jupyter: {data.get('jupyter', '?')}")
        print(f"  Cost: ${data.get('cost_usdc', '?')} USDC")
    else:
        print(f"Rent failed: {data}")
    return data


def check_status(api_key: str, pod_id: str) -> dict:
    """Check GPU pod status."""
    r = httpx.get(f"{MAXIA_API}/gpu/status/{pod_id}",
        headers={"X-API-Key": api_key})
    return r.json()


if __name__ == "__main__":
    print("=" * 50)
    print("MAXIA Demo — GPU Rental")
    print("=" * 50)

    # 1. List available GPUs
    list_gpu_tiers()

    # 2. Register (if you want to rent)
    # AGENT_NAME = "DemoGPUBot"
    # WALLET = "YOUR_SOLANA_WALLET"
    # api_key = register(AGENT_NAME, WALLET)

    # 3. Rent a GPU (requires USDC payment on Solana first)
    # result = rent_gpu(api_key, "h100_sxm5", hours=2, payment_tx="YOUR_TX_SIGNATURE")

    # 4. Check status
    # status = check_status(api_key, result["pod_id"])

    print("\nTo rent: register, send USDC to MAXIA treasury, pass tx signature.")
    print(f"Docs: {MAXIA_API}/docs")
