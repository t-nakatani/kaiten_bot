from exchange import Exchange
from trading_strategy import TradingStrategy

class KaitenBot():
    """
    ロジックに沿ってトレードを行う最上位クラス
    """
    def __init__(self, client, strategy_params:dict):
        self.exchange = Exchange(client)
        self.trading_strategy = TradingStrategy(
            self.exchange,
            strategy_params['trading_volume'],
            strategy_params['rate_of_drop'],
            strategy_params['rate_of_pump'],
            strategy_params['leverage']
        )
    
    async def run(self, pair_symbol):

        # 0. cancel all orders
        await self.trading_strategy.initalize_setting(pair_symbol)

        # 1. check position
        positions = await self.exchange.get_position()
        current_position = None
        for position in positions:
            if position['symbol'] == pair_symbol:
                current_position = position
                print('current_position:', current_position)
                break

        # order = await self.trading_strategy.get_open_order(pair_symbol)
        # if order:
        #     print(f'There is {len(order)} orders in {pair_symbol}')
        # else:
        #     print(f'There is no orders in {pair_symbol}')

        # 2. create_order
        if current_position is None:
            # ポジションがない場合：新規ポジションを開く
            await self.trading_strategy.create_opening_order(pair_symbol)
        else:
            # ポジションがある場合：既存のポジションをクローズする
            await self.trading_strategy.create_closing_order(pair_symbol)

        order = await self.trading_strategy.get_open_order(pair_symbol)
        if order:
            print(f'There is {len(order)} orders in {pair_symbol}')
        else:
            print(f'There is no orders in {pair_symbol}')
