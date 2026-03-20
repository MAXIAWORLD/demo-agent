"""MAXIA Demo — Trade Tokenized Stocks

Lists available tokenized stocks (AAPL, TSLA, NVDA, etc.),
gets live prices, and buys fractional shares with USDC on Solana.

Usage:
    pip install httpx
    python demo_stocks.py
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
        "description": f"{name} — AI agent trading stocks on MAXIA"
    })
    data = r.json()
    if data.get("api_key"):
        print(f"Registered as '{name}'")
        return data["api_key"]
    else:
        print(f"Registration failed: {data}")
        sys.exit(1)


def list_stocks():
    """List all available tokenized stocks."""
    r = httpx.get(f"{MAXIA_API}/stocks")
    data = r.json()
    stocks = data.get("stocks", [])

    print(f"\n{'Symbol':<8} {'Name':<25} {'Price':<12} {'Sector'}")
    print("-" * 60)
    for s in stocks:
        price = s.get("price_usd", 0)
        print(f"{s['symbol']:<8} {s['name'][:24]:<25} ${price:<10.2f} {s.get('sector', '')}")

    print(f"\n{len(stocks)} stocks available. Commission: 0.05% - 0.5%")
    return data


def get_price(symbol: str) -> dict:
    """Get real-time price of a stock."""
    r = httpx.get(f"{MAXIA_API}/stocks/price/{symbol}")
    data = r.json()
    if not data.get("error"):
        print(f"\n{symbol}: ${data.get('price_usd', 0):.2f}")
    else:
        print(f"Error: {data['error']}")
    return data


def buy_stock(api_key: str, symbol: str, amount_usdc: float, payment_tx: str) -> dict:
    """Buy fractional shares of a tokenized stock."""
    r = httpx.post(f"{MAXIA_API}/stocks/buy",
        headers={"X-API-Key": api_key},
        json={
            "symbol": symbol,
            "amount_usdc": amount_usdc,
            "payment_tx": payment_tx,
        },
        timeout=30,
    )
    data = r.json()
    if data.get("success"):
        print(f"\nBought {data.get('shares', 0):.4f} shares of {symbol}")
        print(f"  Price: ${data.get('price_per_share', 0):.2f}/share")
        print(f"  Total: ${amount_usdc} USDC")
        print(f"  Commission: ${data.get('commission_usdc', 0):.4f} USDC ({data.get('commission_bps', 0)/100:.2f}%)")
    else:
        print(f"Buy failed: {data}")
    return data


def get_portfolio(api_key: str) -> dict:
    """View stock portfolio."""
    r = httpx.get(f"{MAXIA_API}/stocks/portfolio",
        headers={"X-API-Key": api_key})
    data = r.json()
    holdings = data.get("holdings", [])
    if holdings:
        print(f"\n{'Symbol':<8} {'Shares':<12} {'Value'}")
        print("-" * 35)
        for h in holdings:
            print(f"{h['symbol']:<8} {h['shares']:<12.4f} ${h.get('value_usd', 0):.2f}")
        print(f"\nTotal: ${data.get('total_value_usd', 0):.2f}")
    else:
        print("\nNo holdings yet.")
    return data


if __name__ == "__main__":
    print("=" * 50)
    print("MAXIA Demo — Tokenized Stocks")
    print("=" * 50)

    # 1. List all stocks
    list_stocks()

    # 2. Get a specific price
    get_price("AAPL")
    get_price("TSLA")

    # 3. To buy: register, send USDC, pass tx signature
    # api_key = register("DemoStockBot", "YOUR_WALLET")
    # buy_stock(api_key, "AAPL", 10.0, "YOUR_TX_SIGNATURE")
    # get_portfolio(api_key)

    print(f"\nTo trade: register, send USDC to MAXIA treasury, pass tx signature.")
    print(f"Docs: {MAXIA_API}/docs")
