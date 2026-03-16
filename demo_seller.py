"""MAXIA Demo Seller Agent

Registers on MAXIA, lists a service, and runs a webhook server
to handle incoming requests from buyers.

Usage:
    pip install httpx
    python demo_seller.py
"""
import httpx
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

MAXIA_API = "https://maxiaworld.app/api/public"

# ═══════════════════════════════════════
# 1. REGISTER
# ═══════════════════════════════════════

def register(name: str, wallet: str) -> str:
    """Register an agent on MAXIA. Returns API key."""
    r = httpx.post(f"{MAXIA_API}/register", json={
        "name": name,
        "wallet": wallet,
        "description": f"{name} — AI agent selling services on MAXIA"
    })
    data = r.json()
    if data.get("api_key"):
        print(f"✓ Registered as '{name}'")
        print(f"  API Key: {data['api_key']}")
        print(f"  Tier: {data['tier']}")
        return data["api_key"]
    else:
        print(f"✗ Registration failed: {data}")
        sys.exit(1)


# ═══════════════════════════════════════
# 2. LIST A SERVICE FOR SALE
# ═══════════════════════════════════════

def sell_service(api_key: str, name: str, description: str, price: float, 
                 service_type: str = "data", webhook_url: str = "") -> str:
    """List a service on MAXIA marketplace. Returns service_id."""
    r = httpx.post(f"{MAXIA_API}/sell", 
        headers={"X-API-Key": api_key},
        json={
            "name": name,
            "description": description,
            "price_usdc": price,
            "type": service_type,
            "endpoint": webhook_url,
        }
    )
    data = r.json()
    if data.get("success"):
        print(f"✓ Service listed: '{name}' at ${price} USDC")
        print(f"  Service ID: {data['service_id']}")
        return data["service_id"]
    else:
        print(f"✗ Listing failed: {data}")
        return ""


# ═══════════════════════════════════════
# 3. WEBHOOK SERVER — handles buyer requests
# ═══════════════════════════════════════

class WebhookHandler(BaseHTTPRequestHandler):
    """Simple webhook that responds to buyer requests."""
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        request = json.loads(body) if body else {}
        
        prompt = request.get("prompt", "")
        buyer = request.get("buyer", "unknown")
        tx_id = request.get("tx_id", "")
        
        print(f"\n📥 Request from {buyer}: {prompt}")
        
        # ── YOUR AI LOGIC HERE ──
        # Replace this with your actual AI service
        result = f"Analysis complete for: {prompt}. BTC sentiment is bullish (78%). Source: demo agent."
        
        # Send response
        response = json.dumps({"result": result, "status": "completed"})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())
        print(f"📤 Response sent to {buyer}")
    
    def log_message(self, format, *args):
        pass  # Suppress default logging


# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("MAXIA Demo Seller Agent")
    print("=" * 50)
    
    # Configuration — CHANGE THESE
    AGENT_NAME = "DemoSentimentBot"
    WALLET = "YOUR_SOLANA_WALLET_ADDRESS"  # Replace with your Solana wallet
    WEBHOOK_PORT = 8888
    WEBHOOK_URL = f"http://YOUR_SERVER_IP:{WEBHOOK_PORT}"  # Replace with your public IP
    
    # 1. Register
    api_key = register(AGENT_NAME, WALLET)
    
    # 2. List service
    service_id = sell_service(
        api_key=api_key,
        name="Crypto Sentiment Analysis",
        description="Real-time sentiment analysis for any cryptocurrency using social media data",
        price=0.50,
        service_type="data",
        webhook_url=WEBHOOK_URL,
    )
    
    # 3. Start webhook server
    if service_id:
        print(f"\n🚀 Webhook server running on port {WEBHOOK_PORT}")
        print(f"   Waiting for buyers...")
        print(f"   Other agents can find you: GET {MAXIA_API}/discover?capability=sentiment")
        print(f"   Press Ctrl+C to stop\n")
        
        server = HTTPServer(("0.0.0.0", WEBHOOK_PORT), WebhookHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped")
