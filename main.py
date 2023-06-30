from connect_to_database import *
from live_stock_data import *
import time
import datetime
from datetime import date
import matplotlib.pyplot as plt

# Login
def login(cur):
    print("\nWelcome to the Investor's Center")
    access = False

    while access == False:
        username = input("Username: ")
        password = input("Password: ")
        
        if cur.execute(f"SELECT username FROM users WHERE username = '{username}'").fetchone():
            if cur.execute(f"SELECT password FROM users WHERE username = '{username}'").fetchone()[0] == password:
                print("Successful Login\n")
                access = True
            else:
                print("Acess Denied. Incorrect Password\n")
        else:
            print("User not found\n")

    user_id, first, last = cur.execute(f"SELECT user_id, first_name, last_name FROM users WHERE username = '{username}'").fetchone()
    print(f"Welcome, {first} {last}")
    return user_id

def sign_up(cur, con):
    # need to validate names (no numbers or special characters)
    print("\n")

    first_name = input("First name: ")
    last_name = input("Last name: ")
    valid_names = True
    
    if valid_names:
        access = False
        while access == False:
            username = input("\nUsername: ")
            if cur.execute(f"SELECT username FROM users WHERE username = '{username}'").fetchone():
                print(f"The username {username} is unavailable. Please enter another one.")
            else:
                access = True

    password = input("Password: ")
    confirm_password = input("Confirm password: ")

    while password != confirm_password:
        print("\nThe passwords provided do NOT match. Try Again.")
        password = input("Password: ")
        confirm_password = input("Confirm password: ")

    print("\nReview the following information.")
    print("--------------------------------")
    print(f"First:\t{first_name}\nLast:\t{last_name}\nUser:\t{username}\nPassword:\t{len(password) * '*'}")
    print("--------------------------------")

    print("(a) Confirm")
    print("(b) Edit")

    valid = False
    while valid == False:
        select = input("=> ")
        if select in ['a', 'A', 'b', 'B']:
            valid = True
            if select == 'b' or select == 'B':
                sign_up(cur, con)
                
    data = (first_name, last_name, username, password)
    cur.execute(f"INSERT INTO users (first_name, last_name, username, password) VALUES (?,?,?,?)", data)
    con.commit()

    user_id = cur.execute(f"SELECT user_id FROM users WHERE username = '{username}'")
    return user_id


# Logout, Closes connection to database
def logout(con):
    print("Logging out...")
    time.sleep(1)
    con.close()
    print("Logged out successfully. Goodbye.")


def read_user_info(user_id, con, cur):
    print("\nUser Information:")
    info = cur.execute(f"SELECT * FROM users WHERE user_id = '{user_id}'").fetchone()

    print(f"   Name: {info[1]} {info[2]}\n   Username: {info[3]}")

    print("\nChoose an option:\n   a) Go Back\n   b) Change username/password")

    valid = False
    while valid == False:
        select = input("=> ")
        if select in ['a', 'A', 'b', 'B']:
            valid = True
    
    if select == 'b' or select == 'B':
        edit_user_info(user_id, con, cur)

# Gives user option to edit any of their info via UPDATE of users table
def edit_user_info(user_id, con, cur):
    print("\nEnter new username and password: ")

    access = False
    while access == False:
        username = input("Username: ")
        check = cur.execute(f"SELECT user_id FROM users WHERE username = '{username}'").fetchone()
        if check and check[0] != user_id:
            print(f"The username {username} is unavailable. Please enter another one.")
        else:
            access = True

    password = input("Password: ")
    confirm_password = input("Confirm password: ")

    while password != confirm_password:
        print("The passwords provided do NOT match. Try Again.")
        password = input("Password: ")
        confirm_password = input("Confirm password: ")


    cur.execute(f"UPDATE users SET username = '{username}', password = '{password}' WHERE user_id = '{user_id}';")
    con.commit()
    
    print("Your information has been updated\n")

def admin(cur, con):
    print("\n----- Welcome Admin -----\n")

    valid = False
    while valid == False:
        print("   a) Remove user\n   b) Update stock prices\n   c) Add stock\n   d) Remove stock\n   e) Exit")
        select = input("=> ")
        if select in ['a', 'b', 'c', 'd', 'e']:
            if select == 'a':
                remove_user(cur, con)
            elif select == 'b':
                update_table_prices(cur, con)
            elif select == 'c':
                add_stock_to_table(cur, con)
            elif select == 'd':
                remove_stock_from_table(cur, con)
            elif select == 'e':
                print("\nGoodbye")
                valid = True
                
def remove_user(cur, con):
    user = input("Enter a user_id or username: ")
    valid = False
    while valid == False:
        if isinstance(user, int):
            if cur.execute(f"SELECT * FROM users WHERE user_id = {user}"):
                cur.execute(f"DELETE FROM users WHERE user_id = {user}")
                valid = True
            else:
                print("\nUser not in databse. Try again.")
                user = input("Enter a user_id or username: ")
        elif isinstance(user, str):
            if cur.execute(f"SELECT * FROM users WHERE username = '{user}'"):
                cur.execute(f"DELETE FROM users WHERE username = '{user}'")
                valid = True
            else:
                print("\nUser not in databse. Try again.")
                user = input("Enter a user_id or username: ")
    con.commit()

    time.sleep(1)
    print("\nUser has been removed from database\n")
    admin(cur, con)

def add_stock_to_table(cur, con):
    stock_symbol = input("Enter stock symbol: ")
    stock = yf.Ticker(stock_symbol).info

    while stock['regularMarketPrice'] == None:
        stock_symbol = input("Enter a valid stock symbol: ")
        stock = yf.Ticker(stock_symbol).info

    stock_name = stock['longName']
    stock_sector = stock['sector']
    stock_price = stock['regularMarketPrice']

    cur.execute(f"INSERT INTO assets VALUES ('{stock_symbol}', '{stock_name}', '{stock_sector}', {stock_price})")
    con.commit()

    time.sleep(1)
    print(f"{stock_name} successfully added to database")
    admin(cur, con)

def remove_stock_from_table(cur, con):
    stock_symbol = input("Enter stock symbol: ")

    valid = False
    while valid == False:
        if cur.execute(f"SELECT * FROM assets WHERE symbol = '{stock_symbol}'").fetchone():
            cur.execute(f"DELETE FROM assets WHERE symbol = '{stock_symbol}'")
            valid = True
        else:
            print("This stock is not currently in the database. Try again.")
            stock_symbol = input("Enter stock symbol: ")

    time.sleep(1)
    print(f"\n{stock_symbol} successfully removed from database")
    admin(cur, con)
    

def buy_transaction(userId,cur,con):
    
    userID = userId
    #transaction id will be 1 + tranID of last row in table
    tranID = cur.execute(f"SELECT COUNT(*) FROM transactions; ").fetchone()[0]
    tranID+=1 #new transaction ID
    #type = 'buy'
    current_day = datetime.date.today()
    date = datetime.date.strftime(current_day, "%m/%d/%Y")
    symbol = ' '
    valid_symbol = False
    while (not valid_symbol):
        
        symbol = input("Enter the symbol for the stock you'd like to purchase:")
        if cur.execute(f"SELECT 1 FROM assets WHERE Symbol = '{symbol}' ").fetchone():
            valid_symbol = True
        else:
            print(f"Stock symbol {symbol} not found")
    
    #validate num_shares
    while (True):
        
        try:
            shares_bought = int(input("Enter the number of shares:"))
            if shares_bought > 0:
                break
            else:
                print("Enter a value greater than zero")
            

        except ValueError:
            print("Enter a valid integer")
            
    price_per_share = current_price(symbol)
    usd_amount = round(shares_bought * price_per_share,2)
    data = (tranID,userID,symbol,date,shares_bought,price_per_share,usd_amount)
    print(f"You have purchased {shares_bought} shares of {symbol} at ${price_per_share}/share for a total of ${usd_amount}")
    cur.execute(f"INSERT INTO transactions (transaction_id,user_id,asset,date,num_shares,price_per_share,usd_amount)VALUES (?,?,?,?,?,?,?)",data)
    con.commit()


#piechart of user portfolio
def pie_chart(userID,cur):
    #get shares and symbols
    shares = cur.execute(f"SELECT asset,num_shares,usd_amount,date FROM transactions WHERE user_id = {userID};").fetchall()
    # calculate the total spent on transactions and net loss/gain
    line_dates = []
    line_amounts = []
    line_stocks = []



    total = 0
    stock_dictionary = {}
    for s in shares:

        #add to dates and bar for bar chart
        line_dates.append(s[3])
        line_amounts.append(s[2])
        line_stocks.append(s[0]+"\n"+s[3])


        total += s[2]
        stock_name =s[0] 
        if stock_name not in stock_dictionary.keys():
            #tie stock symbol to num_shares
            stock_dictionary[stock_name] = s[1]
        elif stock_name in stock_dictionary.keys():
            stock_dictionary[stock_name] += s[1]

    #data for pie chart
    names = []
    values = []
    account_val = 0
    net = 0
    net_out = ''
    for x,y in stock_dictionary.items():
        names.append(x)
        print(x)
        #get the current stock price of those items
        sql = f"SELECT Price FROM assets WHERE Symbol = '{x}'"
        if cur.execute(sql).fetchone():

            curr_price = cur.execute(sql).fetchone()[0]
        else:
            curr_price = current_price(x)
        total_val = y * curr_price #current_price(x)
        total_val = round(total_val,2)
        account_val+= total_val
        values.append(total_val)
    wedges,text,autotext = plt.pie(values,labels=names,autopct='%.1f%%')
    if account_val <= total:
        net = total - account_val
        net = round(net,2)
        net_out = f"   Net Loss: ${net}"
    else:
        net = account_val - total
        net = round(net,2)
        net_out = f"   Net Gain: ${net}"

    account_val = round(account_val,2)
    
    plt.legend(wedges,values,title="Total Values")
    plt.axis('equal')
    plt.title(f"My Portfolio  ($ {account_val})  {net_out}")
    plt.show()

    #make bar chart
    plt.bar(line_stocks,line_amounts)
    plt.title('Transaction History')
    plt.xlabel('Dates')
    plt.ylabel('Amount')
    plt.show()
    
def stat_queries(userId,cur):
    #let user select mean, min,max median std dev. of num_shares, price_per_share,usd_amount
    print("Select a column from transactions to perform a query:")
    columns = [i[1] for i in cur.execute('PRAGMA table_info(transactions)')]
    columns = columns[-3:]
    x = 1
    for c in columns:
        print(f"{x}). {c}")
        x += 1
    user_choice = input("=> ")
    
    while user_choice != '1' and user_choice != '2' and user_choice != '3':
        print("Enter a valid integer")
        user_choice = input("=> ")

    selected_column = columns[int(user_choice)-1]

    stat_options = ['avg','min','max']
    x=1
    
    print(f"Select a statistical query for {selected_column}")
    for s in stat_options:
        print(f"{x}). {s}")
        x += 1
    
    stat_choice = input("=>")
    
    while stat_choice != '1' and stat_choice != '2' and stat_choice != '3':
        print("Enter a valid integer")
        stat_choice = input("=> ")
    
    selected_stat = stat_options[int(stat_choice)-1]

    sql = ''

    if selected_stat == 'avg':
        sql = f'SELECT AVG({selected_column}) FROM transactions '
    if selected_stat == 'min':
        sql = f'SELECT MIN({selected_column}) FROM transactions '
    if selected_stat == 'max':
        sql = f'SELECT MAX({selected_column}) FROM transactions '

    out_string = str(round(cur.execute(sql).fetchone()[0],2))
    print(f'The {selected_stat} of {selected_column}: {out_string}')

def users_where_join(userID,cur):
    user_cols =  [i[1] for i in cur.execute('PRAGMA table_info(users)')]
    trans_cols = [i[1] for i in cur.execute('PRAGMA table_info(transactions)')]
    user_cols.remove('password')
    all_cols = user_cols +(trans_cols)
    
    print("Please select 1 of the following:")
    print("1). View my detailed transactions")
    print("2). filter transactions")
    choice = input("=>")
    while choice != '1' and choice != '2':
        choice = input("Enter 1 or 2 =>")
    
    if choice == '1':
        sql = (f"SELECT transaction_id,asset,Name,Sector, date,num_shares,price_per_share,usd_amount FROM assets INNER JOIN transactions on assets.Symbol = transactions.asset WHERE transactions.user_id = {userID}")
        output = cur.execute(sql).fetchall()
        for o in output:
            print(f'tranID:{o[0]} Symbol:{o[1]} Name:{o[2]} Sector:{o[3]} Date:{o[4]} Number of Shares:{o[5]} Price:{o[6]} Amount:{o[7]}')


    if choice == '2':


    
        print("Enter the column you would like to filter by.")
        print("User Table\n")
        for x in user_cols:
            print(x)


        print("\Transaction Table\n")
        for x in trans_cols:
            print(x)
        selected_col = input("=>")

        while selected_col not in all_cols:
            selected_col = input("Enter a valid column :")

        query = input(f"WHERE {selected_col} ")
        sql = (f"SELECT users.user_id,first_name,last_name,username,transaction_id,asset,date,num_shares,price_per_share,usd_amount FROM users INNER JOIN transactions on users.user_id = transactions.user_id WHERE {selected_col} {query}")

        valid_query = False
        while not valid_query: 
        
            if cur.execute(sql).fetchall():
                output = cur.execute(sql).fetchall()
                print("user_id, first_name, last_name, username, transaction_id, asset, date, num_shares, price_per_share, usd_amount")
                for o in output:
                    print(f'userID: {o[0]} Name:{o[1]} {o[2]} Username:{o[3]}\nTransactionID: {o[4]}   Asset: {o[5]} Date: {o[6]}\nNumber of Shares: {o[7]} Price per Share: {o[8]} Amount:{o[9]}\n\n')
                valid_query = True
            else:
                print("invalid query try again")

def display_user_options():
    print("\nChoose an option:")     
    print("a) Change username/password")
    print("b) Purchase Stock")
    print("c) View your Portfolio")
    print("d) View Transaction Stats")
    print("e) Filter Transactions")
    print("f) Log Out")           

def main():
    con, cur = connect_database('stock_market.db')
    load_csv('users', 'users.csv', con, cur)
    load_csv('assets', 'stock_data.csv', con, cur)
    load_csv('transactions', 'transactions.csv', con, cur)
    
    valid = False
    while valid == False:
        print("\nChoose an option:")
        print("   a) Login\n   b) Sign Up\n   c) Admin\n   d) Exit")
        select = input("=> ")
        if select in ['a', 'b', 'c', 'd']:
            valid = True
            if select == 'a' or select == 'b':
                
                if select == 'a':
                    user_id = login(cur)
                else:
                    user_id = sign_up(cur,con)
                
                display_user_options()
                user_choice = input("=> ")
                while True:
                    
                    if user_choice == 'a':
                        edit_user_info(user_id,con,cur)
                    elif user_choice == 'b':
                        display_info(user_id, cur, con)
                    elif user_choice == 'c':
                        pie_chart(user_id,cur)
                    elif user_choice == 'd':
                        stat_queries(user_id,cur)
                    elif user_choice == 'e':
                        users_where_join(user_id,cur)
                    elif user_choice == 'f':
                        logout(con)
                        break
                    
                    display_user_options()
                    user_choice = input("=> ")
            
            elif select == 'c':
                admin(cur, con)
            elif select == 'd':
                print("Goodbye")
    

main()

