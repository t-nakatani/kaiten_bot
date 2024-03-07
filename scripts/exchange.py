import pandas as pd

class Exchange():
    """
    取引所と直接APIのやり取りを行う
    """
    def __init__(self, client):
        self.client = client
        pass
    
    async def get_klines(self, pair_symbol:str, interval:str='60', limit:str='5') -> pd.DataFrame:
        """
        /v5/market/kline
        ローソク足(kline)を取得
        """
        async with self.client.get(
            f"/v5/market/kline?category=linear&interval=60&symbol={pair_symbol}&interval={interval}&limit={limit}"
        ) as resp:
            content = await resp.json()

        klines = content['result']['list']
        klines = pd.DataFrame(klines)
        klines.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']

        return klines

    async def get_latest_price(self, pair_symbol:str):
        """"""""
        klines = await self.get_klines(pair_symbol, interval='1', limit='1')
        latest_price = float(klines['close'].values[-1])
        return latest_price

    async def get_order(self, pair_symbol:str):
        async with self.client.get(
            f"/v5/order/realtime?category=linear&symbol={pair_symbol}&limit=50"  # max limit == 50
        ) as resp:
            content = await resp.json()
        orders = content['result']['list']
        # print(f'exchange.get_order: {orders}')
        return orders


    async def get_symbol_info(self, pair_symbol):
        """銘柄の情報を取得"""
        async with self.client.get(f"/v5/market/instruments-info?category=linear&symbol={pair_symbol}") as resp:
            content = await resp.json()
            symbol_info = content['result']
            price_tick = float(symbol_info['list'][0]['priceFilter']['tickSize'])
            qty_step = float(symbol_info['list'][0]['lotSizeFilter']['qtyStep'])
            return (price_tick, qty_step)

    async def get_balance_info(self, coin: str='USDT') -> float:
        """残高を取得"""
        async with self.client.get(f"/v5/account/wallet-balance?accountType=UNIFIED&coin={coin}") as resp:
            content = await resp.json()
            # print('[exchange]-get_balance:', content)
            return content['result']['list']

    async def get_position(self):
        async with self.client.get("/v5/position/list?category=linear&settleCoin=USDT") as resp:
            content = await resp.json()
            symbol_list = [{'symbol': json['symbol'], 'side': json['side'], 'size': json['size']} for json in content['result']['list']]
            return symbol_list

    async def set_leverage(self, pair_symbol:str, leverage:int):
        """
        https://bybit-exchange.github.io/docs/v5/position/leverage
        """
        data = {
            'category': "linear", 
            'symbol': pair_symbol,
            'buyLeverage': leverage,
            'sellLeverage': leverage,
        }
        async with self.client.post("/v5/position/set-leverage", data=data) as resp:
            content = await resp.json()
            # print('[exchange]-set_leverage:', content)
            return content['retMsg']

    async def create_order(self, pair_symbol, qty, side='Buy', price=None, reduce_only=False):
        data = data={
                'category': "linear",
                'symbol': pair_symbol,
                'side': side,
                'orderType': 'Limit',
                'price': price,
                'qty': qty,
                'reduceOnly': reduce_only,
        }
        async with self.client.post("/v5/order/create", data=data) as resp:
            content = await resp.json()
            if content['retCode'] == 0:
                print('[exchange]-create_order:', content['result'])
            return content['retMsg']

    async def cancel_all_orders(self, pair_symbol):
        data = data={'category': "linear", 'symbol': pair_symbol}
        async with self.client.post("/v5/order/cancel-all", data=data) as resp:
            content = await resp.json()
            if content['retCode'] == 0:
                print('[exchange]-cancel_all_orders:', content['result'])
            return content['retMsg']
