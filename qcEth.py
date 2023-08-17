# region imports
from AlgorithmImports import *
# endregion

class SleepyGreenParrot(QCAlgorithm):

    def Initialize(self):
        # set start date and intial cash for testing
        self.SetStartDate(2019, 8, 12)
        self.SetCash(1000)

        # set Kraken as the brokerage
        self.SetBrokerageModel(BrokerageName.Kraken, AccountType.Cash)

        self.eth = self.AddCrypto("ETHUSD", Resolution.Minute)
        self.symbol = (self.eth).Symbol

        # set the information for the RSI
        RSI_Period = 2
        self.RSI_OB = 80
        self.RSI_OS = 20
        self.RSI_Ind_ETH = self.RSI("ETHUSD", RSI_Period)

        # 200 day and 5 day standard moving averages
        self.fast = self.SMA(self.symbol, 5, Resolution.Minute)
        self.slow = self.SMA(self.symbol, 200, Resolution.Minute)

        self.SetWarmUp(200)

    def OnData(self, data):
        if not self.Portfolio.Invested:
            #self.SetHoldings("ETHUSD", 1)
            ethPrice = self.Securities["ETHUSD"].Price
            if ethPrice > self.slow:
                self.SetHoldings("ETHUSD", 1)