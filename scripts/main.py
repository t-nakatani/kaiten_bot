import os
import asyncio
import pybotters
from dotenv import load_dotenv
from utils import get_current_time

from kaiten_bot import KaitenBot


load_dotenv('.env')

apis = {
    'bybit': [os.getenv('API_KEY'), os.getenv('API_SECRET')]
}

strategy_parmas = {
    'trading_volume': float(os.getenv('volume')), 
    'leverage': os.getenv('leverage'),
    'rate_of_drop': float(os.getenv('rate_of_drop')),
    'rate_of_pump': float(os.getenv('rate_of_pump'))
}

pair_symbol = os.getenv('pair_symbol')

async def main():
    async with pybotters.Client(apis=apis, base_url='https://api.bybit.com') as client:
        print('strategy_parmas:', strategy_parmas, '\n')
        kaiten_bot = KaitenBot(client, strategy_parmas)
        await kaiten_bot.run(pair_symbol)

print(f'==================================  {get_current_time()}  ==================================')
asyncio.run(main())
print('\n')