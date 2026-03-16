"""MAXIA Webhook Server

Standalone webhook that handles requests from MAXIA marketplace.
Run this on a server with a public IP.

Usage:
    python demo_webhook.py

MAXIA will POST to this server when a buyer purchases your service:
    {
        "prompt": "Analyze BTC sentiment",
        "buyer": "BuyerBotName",
        "service_id": "your-service-id",
        "tx_id": "transaction-id"
    }

Your server should return:
    {
        "result": "Your analysis result here"
    }
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class MaxiaWebhook(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # Read request
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        
        prompt = body.get("prompt", "")
        buyer = body.get("buyer", "unknown")
        
        print(f"📥 [{buyer}] {prompt}")
        
        # ═══════════════════════════════════════
        # YOUR AI LOGIC HERE
        # Replace this with your actual service
        # ═══════════════════════════════════════
        
        result = process_request(prompt)
        
        # Send response
        response = json.dumps({"result": result})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())
        print(f"📤 Responded to {buyer}")
    
    def log_message(self, format, *args):
        pass


def process_request(prompt: str) -> str:
    """Your AI service logic. Replace this."""
    
    # Example: simple keyword-based sentiment
    prompt_lower = prompt.lower()
    
    if "btc" in prompt_lower or "bitcoin" in prompt_lower:
        return "BTC sentiment: Bullish (72%). Social volume up 15%. Key drivers: ETF inflows, institutional buying."
    elif "sol" in prompt_lower or "solana" in prompt_lower:
        return "SOL sentiment: Very Bullish (81%). Developer activity high. DeFi TVL growing."
    elif "eth" in prompt_lower or "ethereum" in prompt_lower:
        return "ETH sentiment: Neutral (55%). L2 activity increasing but gas fees stable."
    else:
        return f"Analysis for '{prompt}': Moderate activity detected. Recommend monitoring for 24h."


if __name__ == "__main__":
    PORT = 8888
    print(f"🚀 MAXIA Webhook running on port {PORT}")
    print(f"   Register your service with endpoint: http://YOUR_IP:{PORT}")
    print(f"   Press Ctrl+C to stop\n")
    
    server = HTTPServer(("0.0.0.0", PORT), MaxiaWebhook)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Stopped")
