import pandas as pd
from finance.technicals import get_sma, generate_sma_list, generate_ema_list


data_file = "backtest-data.xlsx"

df = pd.read_excel(data_file)

# PSEUDOCODE BACKTEST

# generate percent changes per minute into the dataframe
def generate_return_change_list( input ):
    percent_change_list = []
    for i in range(0, len(input["close_price"])):
        if i == len(input["close_price"]) -1 :
            percent_change_list.append( 1 ) #go to next loop
        #divide current price divided by the previous price minus one
        #insert to front of list
        else:
            percent_change_list.append(input["close_price"][i] / input["close_price"][i+1] - 1 )
    return percent_change_list

# generate list of time-weighted return for entire price series
def backtest( df ):

    ## generate return series
    gen_list = generate_return_change_list( df )

    ## replace return series with new time-weighted return from the back
    for x in range( len(df["close_price"]) - 1, 0 , -1 ):

        ## if we're on the oldest item, set it to 1
        if x == len(df["close_price"]) - 1:
            gen_list[len(df["close_price"])] = 1
        else:
            gen_list[x] = gen_list[x+1] * ( 1 + gen_list[x] )

    return gen_list


# def MA_backtest( df )
#     for x in range( 0 , len( df["close"] ))
    

# gives a return series in chronological order (not flipped time)
def generate_return_list( df ):
    return_change = generate_return_change_list(df)
    # tw_return = generate_return_list(df)
    trade_signal = []
    return_list = [1] * len(return_change)

    # long (1) if EMA > SMA 
    # short (0) if SMA > EMA
    for x in range( 0 , len( df["close_price"] ) ):
        if( df["ema_history"][x] > df["sma_history"][x] ):
            trade_signal.append( 1 )
        else:
            trade_signal.append( 0 )
    
    print("Equals Trade Signal?" , pd.Series(trade_signal).equals(df["Trade signal"]))
    for x in range( len( df["close_price"]) - 2 , -1, -1 ):
        if trade_signal[x] == 0:
            return_list[x] = return_list[x+1]    
        else:
            # buy trade signal
            return_list[x] = return_list[x+1] * (1 + return_change[x])
            # return_list.insert( 0, return_list[x+1] * ( 1 + return_change[len( return_change ) - x - 1] ))
        
    return pd.Series(return_list)
    

print(generate_return_list(df)[227])
lek = generate_return_list(df)
# import ipdb; ipdb.set_trace()
print("Equals Return?", lek.equals(df["TW Return"]))
# print(generate_return_change_list(df))
for idx in range(0,len(lek)):
    if lek[idx] != df["TW Return"][idx]:
        print(f"Different at idx: {idx}.... values: code: {lek[idx]} excel: {df['TW Return'][idx]}")
print("RETURN SERIES: ", lek[0])