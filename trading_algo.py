__author__ = 'jams'

from datetime import datetime
import sys
import portfolio

class TradingAlgoJams:
    # stop limit -> trigger sell signal
    stop_limit = 0.25 # drop 25% maximum value

    # add limit -> trigger a buy signal
    add_limit = 0.33 # rise 33% purchase price

    def __init__(self,file_name):
        self.my_pf = portfolio.MyPortfolio(file_name)

    def run(self):
        sell_signals = []
        buy_signals = []

        # 1) update all assets
        self.my_pf.update_close_prices(update_xml=False)

        # 2) update stop price and add units price for all asset
        for asset in self.my_pf.portfolio:
            asset.stop_price = (1-self.stop_limit)*asset.maximum_close['value']
            asset.add_units_price = (1+self.add_limit)*asset.purchase_price['value']
            # 3) write signals
            if asset.previous_close['value'] <= asset.stop_price:
                sell_signals.append('{} {} -> sell'.format(
                    asset.asset_id,asset.name))
            if asset.previous_close['value'] >= asset.add_units_price:
                buy_signals.append('{} {} -> buy'.format(
                    asset.asset_id,asset.name))

        # 3) write xml file
        self.my_pf.update_xml_file()

        # 4) write signals file
        signals_file_name = 'trading_signals-' + \
                            datetime.now().strftime('%Y-%m-%d--%H-%M-%S') + \
                            '.txt'

        # 5) print output
        print(sell_signals)
        print(buy_signals)

if __name__ == '__main__':
    app = TradingAlgoJams(sys.argv[1])
    app.run()