import traceback
from src.config import load_state, save_state
from src.utils.resilience import SmartSession, CircuitBreaker

session = SmartSession()
cb = CircuitBreaker()

class ArbEngine:
    def __init__(self):
        self.state = load_state()
        self.balance = {'BTC': 100000, 'ETH': 100000, 'ALT': 500000}  # demo balances

    def simulate(self, token, price_spread, fee_pct, gas_cost):
        loan_ratio = 0.8 if token in ['BTC','ETH'] else 0.9
        reserve_ratio = 0.2 if token in ['BTC','ETH'] else 0.1
        loan_amt = self.balance['BTC']*loan_ratio if token=='BTC' else                    self.balance['ETH']*loan_ratio if token=='ETH' else                    self.balance['ALT']*loan_ratio
        fees = loan_amt*fee_pct + loan_amt*gas_cost
        profit = loan_amt*price_spread - fees
        return profit, loan_amt

    @cb
    def step(self, token='ETH', price_spread=0.005, fee_pct=0.001, gas_cost=0.0002):
        try:
            profit, loan_amt = self.simulate(token, price_spread, fee_pct, gas_cost)
            if profit>0:
                print(f'[EXECUTE] {token} arb with loan {loan_amt}, profit {profit:.2f}')
                self.state['last_trade']={'token':token,'profit':profit}
                save_state(self.state)
            else:
                print(f'[SKIP] {token} unprofitable (profit={profit:.2f})')
        except Exception as e:
            print('Error:', e, traceback.format_exc())
