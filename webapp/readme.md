Robust trading strategies in the futures market

A python web application where users can compare the performance of commonly used risk factors and strategies using up-to-data data from Quandl 

Data source: Quandl Wiki Continuous Futures 

[https://www.quandl.com/data/CHRIS-Wiki-Continuous-Futures](https://www.quandl.com/data/CHRIS-Wiki-Continuous-Futures)

Indecies CHRIS/CME_ES1, CHRIS/CME_YM1, CHRIS/CME_NQ1,  CHRIS/CBOE_VX1, CHRIS/LIFFE_Z1, 

FX: CHRIS/ICE_DX1, CHRIS/CME_BP1, CHRIS/CME_AD1, CHRIS/CME_JY1, CHRIS/CME_SF1, CHRIS/CME_CD1, CHRIS/CME_E71,  CHRIS/CME_NE1, CHRIS/CME_RU1, CHRIS/CME_MP1, CHRIS/CME_BR1, 

Interest rates: CHRIS/CME_ED1, CHRIS/CME_US1, CHRIS/CME_UL1, CHRIS/CME_TN1, 

Grains: CHRIS/CME_C1, CHRIS/CME_S1,  CHRIS/CME_W1, CHRIS/CME_SM1, CHRIS/CME_BO1, CHRIS/CME_O1, CHRIS/CME_RR1

Crude oil and natural gas CHRIS/CME_QM1, CHRIS/CME_BZ1, CHRIS/CME_QG1

Metals: CHRIS/CME_GC1, CHRIS/CME_SI, CHRIS/CME_HG1, CHRIS/CME_PL1, CHRIS/CME_PA1, 

Softs: CHRIS/ICE_CC1, CHRIS/ICE_SB1, CHRIS/ICE_CT1, CHRIS/ICE_KC1, CHRIS/CME_LB1, CHRIS/ICE_OJ1

Meats: CHRIS/CME_LC1, CHRIS/CME_DA1, 

Strategies: Technical Analysis, Signals from deep learning and reinforcement learning 

In-sample period: Around 1997-2018

Out-sample period 2018-now



How to backtest: Download recent data from Quandl, run the models 

Web Application: A collection of plotly applications which visualise the backtest performance 

User input: A dropdown list of selected Futures tickers, Out-of-sample start and end date(default to be today)

Price-series: Display the price data 

In-sample performance: Run the analysis from the data available time to 2018 

Out-sample performance: Run the analysis from 2018 to now 

Results table: daily holding positions for the selected futures along with PnL and other risk metrics