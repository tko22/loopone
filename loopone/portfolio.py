import pandas as pd
from finance.technicals import get_sma, generate_sma_list, generate_ema_list
# import matplotlib.pyplot as plt
import math

#Starting Portfolio
# [ Bitcoin , Ethereum, Tether, Binance Coin, Date of Latest Transaction ]
Portfolio_holdings = [0 , 1.6, 10021.82, 500, '2018-06-22 3:51:44.660780']
coin_list = ['Bitcoin','Ethereum','Tether','Binance','Date']
new = [1 , 1.6, 10021.82, 500, '2018-06-22 3:51:44.660780']

# get latest portfolio holdings from text log
def read_portfolio():
    portfolio_log = open('Portfolio.txt','r+')

    for line in portfolio_log:  #get last line in data
        load_portfolio = line
    
    return load_portfolio

# write to latest portfolio holdings in text log
def write_portfolio( new_holdings ):
    with open('Portfolio.txt','a') as portfolio_log:
        portfolio_log.write(str(new_holdings) + '\n')

    return read_portfolio()



print(read_portfolio(),coin_list,'\n')
print(write_portfolio(new),coin_list,'\n')