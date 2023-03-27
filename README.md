# TradingBot
Creating a bot to trade crypto.

## Backtest.py
Used to implement and backtest strategies on data from Yahoo Finance.

Backtest usage: python3 backtest/Backtest.py [strategy] 
Current valid strategies are 'standard-mva' and 'rsi-2'.

Currently only test for past three years, but I plan to add customization in future versions.

## Strategies.py
Contains the implementations of each trading strategy utilized in Backtest.py

## ApiTest.py
ApiTest is used to "paper trade" i.e test the strategy on live data without using real funds.

The current version of ApiTest is not at full functionality.

ApiTest usage: python3 papertest/ApiTest.py