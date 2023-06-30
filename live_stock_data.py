import yfinance as yf
from tkinter import * 
import pendulum
import itertools
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from threading import Thread
import datetime
from datetime import date

UPDATE_PRICE = []

def display_info(userId, cur, con):
    valid_symbol = False
    while (not valid_symbol):
        stock_symbol = input("\nEnter the symbol for the stock you'd like to purchase: ")
        if cur.execute(f"SELECT 1 FROM assets WHERE Symbol = '{stock_symbol}' ").fetchone():
            valid_symbol = True
        else:
            print(f"Stock symbol {stock_symbol} not found")

    stock_sector = cur.execute(f"SELECT sector FROM assets WHERE symbol = '{stock_symbol}'").fetchone()

    stock_info = yf.Ticker(stock_symbol).info

    root = Tk()
    root.geometry("700x700")
    root.wm_title("Stock Information")
    
    label_name = Label(root, text=stock_info['longName'], padx=10, font=("Arial", 36, "bold"))
    label_symbol =  Label(root, text=stock_symbol, padx=10, font=("Arial", 24))
    label_sector = Label(root, text=stock_sector, padx=10, font=("Arial", 16))
    label_price = Label(root, text=stock_info['regularMarketPrice'], padx=10, pady=14, font=("Modern 24"))

    historical_price(stock_symbol, "1d", "1m", root)

    button_1d = Button(root, text="1D", padx=8, command=lambda: historical_price(stock_symbol, "1d", "1m", root))
    button_1m = Button(root, text="1M", padx=8, command=lambda: historical_price(stock_symbol, "1mo", "1d", root))
    button_6m = Button(root, text="6M", padx=8, command=lambda: historical_price(stock_symbol, "6mo", "1d", root))
    button_1y = Button(root, text="1Y", padx=8, command=lambda: historical_price(stock_symbol, "1y", "1d", root))
    button_5y = Button(root, text="5Y", padx=8, command=lambda: historical_price(stock_symbol, "5y", "1wk", root))


    label_name.grid(row=0, column =0, columnspan=5, sticky="w")
    label_symbol.grid(row=1, column=0, sticky="w")
    label_sector.grid(row=2, column=0, sticky="w")
    

    button_1d.grid(row=4, column=0, padx=14, pady=5)
    button_1m.grid(row=4, column=1, padx=14, pady=5)
    button_6m.grid(row=4, column=2, padx=14, pady=5)
    button_1y.grid(row=4, column=3, padx=14, pady=5)
    button_5y.grid(row=4, column=4, padx=14, pady=5)
    label_price.grid(row=3, column=0)

    num_shares = StringVar()
    shares_entry = Entry(root, textvariable=num_shares, width=5, fg="grey").grid(row=6, column=2, pady=15)
    print(num_shares.get())
   

    label_purchase = Label(root, text="Number of shares: ").grid(row=6, column=1, pady=15, sticky="e")
    button_purchase = Button(root, text="Invest", command=lambda: buy_transaction(userId, stock_symbol, num_shares.get(), root, cur, con)).grid(row=6, column=3, pady=15)
    

    root.mainloop()

def historical_price(stock_symbol, time_period, time_interval, root):
    price_history = yf.Ticker(stock_symbol).history(period=time_period, interval=time_interval, actions=False)

    time_series = list(price_history['Open'])
    dates = list(price_history.index)
    dt_list = [pendulum.parse(str(dt)).float_timestamp for dt in list(price_history.index)] 

    fig = Figure(figsize = (6.5, 3), dpi = 100)
    
    axes = fig.add_subplot(111)
    axes.plot(dates, time_series)
    axes.set_title(stock_symbol)

    canvas = FigureCanvasTkAgg(fig, root)  
    canvas.draw()
    canvas.get_tk_widget().grid(row=5, columnspan=5, padx=12, pady=6)

    start = time_series[0]
    end = current_price(stock_symbol)

    diff = round(end - start, 2)
    perc_diff = round((diff / start) * 100, 2)

    if diff >= 0:
        label_change = Label(root, text=f"+{diff} ({perc_diff}%)", font=("modern", 16), fg="#00CC00")
    else:
        label_change = Label(root, text=f"-{diff} ({perc_diff}%)", font=("modern", 16), fg="#FF0000")
  
    label_change.grid(row=3, column=1, sticky="w")


def buy_transaction(userId, symbol, num_shares, root, cur, con):
    
    userID = userId
    #transaction id will be 1 + tranID of last row in table
    tranID = cur.execute(f"SELECT COUNT(*) FROM transactions; ").fetchone()[0]
    tranID+=1 #new transaction ID
    #type = 'buy'
    current_day = datetime.date.today()
    date = datetime.date.strftime(current_day, "%m/%d/%Y")
    
    num_shares = int(num_shares)
            
    price_per_share = current_price(symbol)
    usd_amount = round(num_shares * price_per_share,2)
    data = (tranID, userID, symbol, date, num_shares, price_per_share, usd_amount)
    print(f"You have purchased {num_shares} shares of {symbol} at ${price_per_share}/share for a total of ${usd_amount}\n")
    cur.execute(f"INSERT INTO transactions (transaction_id,user_id,asset,date,num_shares,price_per_share,usd_amount)VALUES (?,?,?,?,?,?,?)",data)
    con.commit()

    label_purchase = Label(root, text=f"You have purchased {num_shares} shares of {symbol} at ${price_per_share}/share for a total of ${usd_amount}", font=("Arial", 12))
    label_purchase.grid(row=7,columnspan=5)

def current_price(stock_symbol):
    stock_info = yf.Ticker(stock_symbol).info
    cur_price = stock_info['regularMarketPrice']
    return cur_price

def pull_live_prices(stock_list):
    for stock in stock_list:
        cur_price = current_price(stock)
        UPDATE_PRICE.append((stock, cur_price))


def update_table_prices(cur, con):
    stocks = cur.execute("SELECT symbol FROM assets").fetchall()

    stocks = list(itertools.chain(*stocks))

    threads = []
    start = 0
    inc = (len(stocks) // 10) + 1
    end = inc

    for i in range(1,11):
        stock_seg = stocks[start: end]
        t = Thread(target=pull_live_prices, args=(stock_seg,))
        threads.append(t)
        t.start()

        start = end
        end += inc
        if end > len(stocks)-1:
            end = len(stocks)

    for t in threads:
        t.join()

    for x in UPDATE_PRICE:
        symbol = x[0]
        cur_price = x[1]
        if cur_price == None:
            cur.execute(f"DELETE FROM assets WHERE symbol = '{symbol}'")
        else:
            cur.execute(f"UPDATE assets SET price = {cur_price} WHERE symbol = '{symbol}'")
    con.commit()
    print("\nSuccessfully updated stock prices.\n")
