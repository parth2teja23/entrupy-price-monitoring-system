import asyncio
from datetime import datetime

async def notify_price_change(product_id: int, product_name: str, old_price: float, new_price: float):
    """
    Simulates a background task that sends a webhook or email notification
    to interested consumers when a monitored product changes its price.
    """
    print(f"\n[{datetime.now().isoformat()}] 🔔 BACKGROUND TASK START: Analyzing price shift for '{product_name}' (ID: {product_id})")
    
    # Simulate network I/O delay (e.g. sending an email or webhook)
    await asyncio.sleep(2)
    
    price_diff = abs(new_price - old_price)
    
    if new_price < old_price:
        print(f"[{datetime.now().isoformat()}] 🚨 NOTIFICATION SENT: PRICE DROP! '{product_name}' dropped by ${price_diff:.2f} (Now ${new_price:.2f}).\n")
    else:
        print(f"[{datetime.now().isoformat()}] 📈 NOTIFICATION SENT: PRICE INCREASE! '{product_name}' jumped by ${price_diff:.2f} (Now ${new_price:.2f}).\n")