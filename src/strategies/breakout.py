class VolBreakout:
    def __init__(self): self.range=50
    def step(self, price=1000):
        if price>self.range*1.05:
            print(f'[BREAKOUT] Long breakout at {price}')
        elif price<self.range*0.95:
            print(f'[BREAKOUT] Short breakout at {price}')
        self.range=price
