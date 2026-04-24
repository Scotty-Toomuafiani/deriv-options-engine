import asyncio
import websockets
import json
import os
import datetime
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

# --- CONFIGURATION & SECURITY ---
load_dotenv()
API_TOKEN = os.getenv("DERIV_TOKEN")
price_history = []
is_in_trade = False

def log_trade(contract_type, price, rsi, trend, balance):
    """Saves trade data for future AI pattern analysis."""
    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "type": contract_type,
        "entry_price": price,
        "rsi_at_entry": round(rsi, 2),
        "trend_filter": trend,
        "account_balance": balance,
        "status": "EXECUTED"
    }
    try:
        with open("trade_history.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        print("\n📝 Data stored in trade_history.json for AI analysis.")
    except Exception as e:
        print(f"⚠️ Log Error: {e}")

async def place_trade(websocket, contract_type, rsi, trend):
    global is_in_trade
    is_in_trade = True
    
    # Check balance for the audit log
    await websocket.send(json.dumps({"balance": 1}))
    bal_res = json.loads(await websocket.recv())
    current_bal = bal_res.get("balance", {}).get("balance", 0)

    print(f"\n🚀 SIGNAL: {contract_type} | RSI: {rsi:.2f} | Trend: {trend}")
    
    proposal = {
        "proposal": 1, "amount": 0.35, "basis": "stake",
        "contract_type": contract_type, "currency": "USD",
        "duration": 5, "duration_unit": "t", "symbol": "R_25"
    }
    
    await websocket.send(json.dumps(proposal))
    res = json.loads(await websocket.recv())
    
    if "proposal" in res:
        await websocket.send(json.dumps({"buy": res["proposal"]["id"], "price": 0.35}))
        log_trade(contract_type, 0.35, rsi, trend, current_bal)
        print("⏳ Strategy Cooldown: 60 seconds...")
        await asyncio.sleep(60)
    
    is_in_trade = False

async def main_engine():
    uri = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    
    # We add ping settings here to keep the connection "alive" during the 60s cooldown
    async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as websocket:
        await websocket.send(json.dumps({"authorize": API_TOKEN}))
        await websocket.recv()
        print("🤖 Engine Online. Watching Volatility 25...")

        await websocket.send(json.dumps({"ticks": "R_25", "subscribe": 1}))

        async for message in websocket:
            # ... the rest of your code remains the same ...
            data = json.loads(message)
            if "tick" in data:
                price_history.append(data["tick"]["quote"])
                if len(price_history) > 200: price_history.pop(0)

                if len(price_history) >= 200 and not is_in_trade:
                    df = pd.DataFrame(price_history, columns=['close'])
                    rsi = ta.rsi(df['close'], length=14).iloc[-1]
                    ema = ta.ema(df['close'], length=200).iloc[-1]
                    cur_price = price_history[-1]
                    trend = "UP" if cur_price > ema else "DOWN"

                    print(f"📊 P: {cur_price} | RSI: {rsi:.2f} | T: {trend}", end="\r")

                    if rsi < 30 and trend == "UP":
                        await place_trade(websocket, "CALL", rsi, trend)
                    elif rsi > 70 and trend == "DOWN":
                        await place_trade(websocket, "PUT", rsi, trend)
                else:
                    if not is_in_trade:
                        print(f"⏳ Calibrating: {len(price_history)}/200", end="\r")

if __name__ == "__main__":
    asyncio.run(main_engine())
    