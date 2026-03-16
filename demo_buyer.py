"""MAXIA Demo Buyer Agent

Registers on MAXIA, discovers available services, and buys one.

Usage:
    pip install httpx
    python demo_buyer.py
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
        "description": f"{name} — AI agent buying services on MAXIA"
    })
    data = r.json()
    if data.get("api_key"):
        print(f"✓ Registered as '{name}'")
        return data["api_key"]
    else:
        print(f"✗ Registration failed: {data}")
        sys.exit(1)


def discover(capability: str, max_price: float = 10.0) -> list:
    """Find services by capability."""
    r = httpx.get(f"{MAXIA_API}/discover", params={
        "capability": capability,
        "max_price": max_price,
    })
    data = r.json()
    agents = data.get("agents", [])
    print(f"\n🔍 Found {len(agents)} services for '{capability}':")
    for a in agents:
        print(f"   • {a['name']} by {a['seller']} — ${a['price_usdc']} USDC (★{a.get('rating', 5)})")
    return agents


def execute(api_key: str, service_id: str, prompt: str, payment_tx: str = "") -> dict:
    """Buy and execute a service."""
    r = httpx.post(f"{MAXIA_API}/execute",
        headers={"X-API-Key": api_key},
        json={
            "service_id": service_id,
            "prompt": prompt,
            "payment_tx": payment_tx,
        },
        timeout=30,
    )
    data = r.json()
    if data.get("success"):
        print(f"\n✓ Service executed!")
        print(f"  Service: {data['service']}")
        print(f"  Seller: {data['seller']}")
        print(f"  Price: ${data['price_usdc']} USDC")
        print(f"  Commission: ${data['commission_usdc']} USDC")
        print(f"  Result: {data.get('result', 'pending')[:200]}")
        print(f"  Payment verified: {data.get('payment_verified', False)}")
        if not data.get("payment_verified"):
            print(f"\n  💡 To pay: send ${data['price_usdc']} USDC to {data.get('treasury_wallet', '')}")
            print(f"     Then pass the tx signature as payment_tx")
    else:
        print(f"✗ Execution failed: {data}")
    return data


if __name__ == "__main__":
    print("=" * 50)
    print("MAXIA Demo Buyer Agent")
    print("=" * 50)

    # Configuration — CHANGE THESE
    AGENT_NAME = "DemoBuyerBot"
    WALLET = "YOUR_SOLANA_WALLET_ADDRESS"

    # 1. Register
    api_key = register(AGENT_NAME, WALLET)

    # 2. Discover services
    services = discover("sentiment")

    if not services:
        # Try broader search
        services = discover("")

    if not services:
        print("\nNo services available. Try again later.")
        sys.exit(0)

    # 3. Buy the cheapest one
    cheapest = min(services, key=lambda s: s["price_usdc"])
    print(f"\n💰 Buying: {cheapest['name']} from {cheapest['seller']}")

    result = execute(
        api_key=api_key,
        service_id=cheapest["service_id"],
        prompt="Analyze the current sentiment for Bitcoin based on social media",
    )
