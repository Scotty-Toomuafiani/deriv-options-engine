import asyncio
import websockets
import json
import os
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("DERIV_TOKEN")
price_history = []
is_in_trade = False  # Safety switch

async def place_trade(websocket, contract_type):
    global is_in_trade
    is_in_trade = True
    
    print(f"🚀 SIGNAL DETECTED: Placing $0.35 {contract_type} trade...")
    
    # 1. Propose the contract
    proposal_msg = {
        "proposal": 1,
        "amount": 0.35,
        "basis": "stake",
        "contract_type": contract_type,
        "currency": "USD",
        "duration": 5,
        "duration_unit": "t",
        "symbol": "R_25"
    }
    
    await websocket.send(json.dumps(proposal_msg))
    res = json.loads(await websocket.recv())
    
    if "proposal" in res:
        proposal_id = res["proposal"]["id"]
        # 2. Buy the contract
        await websocket.send(json.dumps({"buy": proposal_id, "price": 0.35}))
        buy_res = json.loads(await websocket.recv())
        
        if "buy" in buy_res:
            print(f"✅ Trade Live! ID: {buy_res['buy']['contract_id']}")
            print("⏳ Sleeping for 60s to avoid over-trading...")
            await asyncio.sleep(60)
        else:
            print(f"❌ Buy Error: {buy_res.get('error', {}).get('message')}")
    
    is_in_trade = False

async def main_engine():
    uri = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({"authorize": API_TOKEN}))
        auth_data = json.loads(await websocket.recv())
        print(f"✅ Connected: {auth_data['authorize']['fullname']}")

        # Subscribe
        await websocket.send(json.dumps({"ticks": "R_25", "subscribe": 1}))

        async for message in websocket:
            data = json.loads(message)
            if "tick" in data:
                price_history.append(data["tick"]["quote"])
                if len(price_history) > 200: price_history.pop(0)

                if len(price_history) >= 200 and not is_in_trade:
                    df = pd.DataFrame(price_history, columns=['close'])
                    rsi = ta.rsi(df['close'], length=14).iloc[-1]
                    ema_200 = ta.ema(df['close'], length=200).iloc[-1]
                    current_price = price_history[-1]
                    trend = "UP" if current_price > ema_200 else "DOWN"

                    print(f"📊 Price: {current_price} | RSI: {rsi:.2f} | Trend: {trend}", end="\r")

                    # EXECUTION LOGIC
                    if rsi < 30 and trend == "UP":
                        await place_trade(websocket, "CALL")
                    elif rsi > 70 and trend == "DOWN":
                        await place_trade(websocket, "PUT")
                else:
                    if not is_in_trade:
                        print(f"⏳ Calibrating Engine... ({len(price_history)}/200)", end="\r")

if __name__ == "__main__":
    asyncio.run(main_engine())