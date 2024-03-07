import math
import datetime

def get_current_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return current_time

def adjust_price(price, price_tick):
    round_price = max(0, int(-math.log10(price_tick)))
    adjusted_price = round((price // price_tick) * price_tick, round_price)
    return int(adjusted_price) if adjusted_price.is_integer() else adjusted_price

def adjust_qty(qty, qty_step):
    round_qty = max(0, int(-math.log10(qty_step)))
    adjusted_qty = round((qty // qty_step) * qty_step, round_qty)
    return int(adjusted_qty) if adjusted_qty.is_integer() else adjusted_qty
