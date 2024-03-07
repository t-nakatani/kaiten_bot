from pandas import DataFrame
from exchange import Exchange

class TradingStrategy():
    """
    ロジックをもとに売買に関わるシグナルを作成する
    """
    def __init__(self, exchange: Exchange, trading_volume: float=10, rate_of_drop:float=0.2, rate_of_pump:float=0.2, leverage: int=5):
        self.exchange = exchange
        self.trading_volume = trading_volume
        self.rate_of_drop = rate_of_drop
        self.rate_of_pump = rate_of_pump
        self.leverage = leverage
    
    async def initalize_setting(self, pair_symbol: str):
        balance_info = await self.exchange.get_balance_info('USDT')
        usdt_balance = float(balance_info[0]['coin'][0]['availableToWithdraw'])
        print('[TradingStrategy]-initalize_setting:', usdt_balance)
        # set leverage
        ret_msg = await self.exchange.set_leverage(pair_symbol, self.leverage)
        if ret_msg == 'OK':
            print(f'[TradingStrategy]-initalize_setting: leverage is set to {self.leverage}x')
        elif ret_msg == 'leverage not modified':
            print(f'[TradingStrategy]-initalize_setting: leverage is already {self.leverage}x')


        # cancel all existing orders
        await self.exchange.cancel_all_orders(pair_symbol)
        pass

    def calc_position_size(self):
        pass

    async def update_order(self):
        """
        update existing order
        """
        pass

    async def get_open_order(self, pair_symbol:str):
        """
        get existing order
        """
        orders = await self.exchange.get_order(pair_symbol)
        return orders

    async def calc_buy_price(self, pair_symbol:str, interval:str=60) -> float:
        klines:DataFrame = await self.exchange.get_klines(pair_symbol=pair_symbol, interval=interval, limit='5')
        high:float = klines['high'].astype(float).values
        highest_price:float = high.max()
        buy_price:float = highest_price * (1 - self.rate_of_drop)
        # レバレッジ部分は追加実装する必要あり
        return buy_price

    async def calc_sell_price(self, pair_symbol:str, interval:str=60) -> float:
        klines:DataFrame = await self.exchange.get_klines(pair_symbol=pair_symbol, interval=interval, limit='5')
        low:float = klines['low'].astype(float).values
        lowest_price:float = low.min()
        sell_price:float = lowest_price * (1 + self.rate_of_pump)
        return sell_price

    async def create_opening_order(self, pair_symbol) -> None:
        buy_price = await self.calc_buy_price(pair_symbol)
        ret_msg = await self.exchange.create_order(pair_symbol=pair_symbol, qty='0.01', side='Buy', price=str(int(buy_price)), reduce_only=False)
        if not ret_msg == 'OK':
            print(f"Open position: {ret_msg}")

    async def create_closing_order(self, pair_symbol) -> None:
        sell_price = await self.calc_sell_price(pair_symbol)
        ret_msg = await self.exchange.create_order(pair_symbol=pair_symbol, qty='0.01', side='Sell', price=str(int(sell_price)), reduce_only=True)
        print(f"Close position: {ret_msg}")
