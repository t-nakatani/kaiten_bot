from pandas import DataFrame
from exchange import Exchange

from utils import adjust_price, adjust_qty

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
        self.symbol_info = {}
    
    async def initalize_setting(self, pair_symbol: str):
        # cancel all existing orders
        await self.exchange.cancel_all_orders(pair_symbol)

        # set leverage
        ret_msg = await self.exchange.set_leverage(pair_symbol, self.leverage)
        if ret_msg == 'OK':
            print(f'[TradingStrategy]-initalize_setting: leverage is set to {self.leverage}x')
        elif ret_msg == 'leverage not modified':
            print(f'[TradingStrategy]-initalize_setting: leverage is already {self.leverage}x')

        balance_info = await self.exchange.get_balance_info('USDT')
        usdt_balance = float(balance_info[0]['coin'][0]['availableToWithdraw'])
        print('[TradingStrategy]-initalize_setting:', usdt_balance)

        self.trading_volume = min(self.trading_volume, usdt_balance * int(self.leverage)) * 0.95
        print(f'[TradingStrategy]-initalize_setting: trading_volume is set to {self.trading_volume}')

        price_tick, qty_step = await self.exchange.get_symbol_info(pair_symbol)
        self.symbol_info = {'price_tick': price_tick, 'qty_step': qty_step}

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
        adjusted_price = adjust_price(buy_price, self.symbol_info['price_tick'])
        adjusted_qty = adjust_qty(self.trading_volume / buy_price, self.symbol_info['qty_step'], 0.01)

        ret_msg = await self.exchange.create_order(pair_symbol=pair_symbol, qty=str(adjusted_qty), side='Buy', price=str(adjusted_price), reduce_only=False)
        if not ret_msg == 'OK':
            print(f'[TradingStrategy]-create_opening_order: {pair_symbol} {adjusted_qty} {adjusted_price} {ret_msg}')
        return

    async def create_closing_order(self, pair_symbol) -> None:
        sell_price = await self.calc_sell_price(pair_symbol)
        adjusted_price = adjust_price(sell_price, self.symbol_info['price_tick'])
        adjusted_qty = adjust_qty(self.trading_volume / sell_price, self.symbol_info['qty_step'], 0.01)

        ret_msg = await self.exchange.create_order(pair_symbol=pair_symbol, qty=adjusted_qty, side='Sell', price=str(adjusted_price), reduce_only=True)
        if not ret_msg == 'OK':
            print(f'[TradingStrategy]-create_closing_order: {pair_symbol} {adjusted_qty} {adjusted_price} {ret_msg}')
        return
