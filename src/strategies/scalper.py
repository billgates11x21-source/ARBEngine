class EMAScalper:
    def __init__(self): self.last=None
    def step(self, price=1000):
        # simple demo: buy if price > last
        if self.last and price>self.last:
            print(f'[SCALPER] Momentum buy at {price}')
        self.last=price
