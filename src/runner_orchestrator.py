import time
from src.strategies.arb_engine import ArbEngine
from src.strategies.scalper import EMAScalper
from src.strategies.breakout import VolBreakout
from src.strategies.liquidity import LiquidityArb
from src.strategies.crossagg import CrossAggArb

class Orchestrator:
    def __init__(self):
        self.arb=ArbEngine()
        self.scalper=EMAScalper()
        self.breakout=VolBreakout()
        self.liquidity=LiquidityArb()
        self.crossagg=CrossAggArb()

    def run(self):
        tick=0
        while True:
            tick+=1
            print(f'--- cycle {tick} ---')
            # always run Albatross
            self.arb.step(token='ETH')
            # rotate other strategies
            if tick%2==0: self.scalper.step(price=1000+tick)
            if tick%3==0: self.breakout.step(price=1000+tick)
            if tick%4==0: self.liquidity.step()
            if tick%5==0: self.crossagg.step()
            time.sleep(1)

if __name__=='__main__':
    Orchestrator().run()
