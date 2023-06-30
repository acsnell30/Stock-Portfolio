import sqlite3
import pandas as pd


#Import the given csvs

conn2 = sqlite3.connect('data/stock_tables.db')
cur = conn2.cursor()


#create table for stocks
cur.execute(''' CREATE TABLE stocks(assetID INTEGER PRIMARY KEY AUTOINCREMENT,


symbol VARCHAR(10),
name VARCHAR(50),
sector VARCHAR(70))
;''')
stocks = pd.read_csv('data/stock_data.csv')
#stocks.drop(columns=['Sector'])
stocks.rename(columns= {'Symbol':'symbol','Name':'name','Sector':'sector'}, inplace=True)
stocks.to_sql('stocks',conn2, if_exists='append',index= True,index_label='assetID')

#create user table
cur.execute('''CREATE TABLE users(
   userID INTEGER PRIMARY KEY AUTOINCREMENT,
   first_name           NVARCHAR(30)      NOT NULL,
   last_name            NVARCHAR(30)       NOT NULL,
   username        VARCHAR(50)  NOT NULL,
   password			VARCHAR(50) NOT NULL
  );''')

  #insert values
cur.execute('''INSERT INTO users(
	first_name,
	last_name,
	username,
	password)
VALUES
	(
		'Blake',
		'Tan',
		'btan',
		'tgif128'
	),
	
		(
		'George',
		'Hamill',
		'ghamill',
		'Gr67B2'
	),
	
	(
		'Mike',
		'Judge',
		'mjudge',
		'tgslhIm'
	),

	(
		'Braun',
		'Tango',
		'btango',
		'YRes34>'
	),	
	
	(
		'Mike',
		'Judge',
		'mjudge',
		'tgslhIm'
	),

	(
		'Bruce',
		'Camp',
		'bcamp',
		'yg$%s2'
	),	

	(
		'Bill',
		'Frank',
		'bfrank',
		'brin238'
	),

	(
		'Bo',
		'Jangle',
		'bjangle',
		'pass19Tree'
	),

	(
		'Tom',
		'Brady',
		'tbrady',
		'bucs2020'
	),

	(
		'Joe',
		'Malley',
		'jmalley',
		'password'
	),

	(
		'Joe',
		'Mixon',
		'jmixon',
		'test213'
	),
	(
		'Rick',
		'Malley',
		'rmalley',
		'password'
	),
	(
		'Tim',
		'Goal',
		'tgoal',
		'gh5Er'
	),
	(
		'Mason',
		'Mixon',
		'mmixon',
		'password'
	),
	(
		'Josh',
		'Gordon',
		'jgordon',
		'Tread'
	),
	(
		'Clint',
		'Eastwool',
		'ceastwool',
		'Western'
	),
	(
		'Mc',
		'Donald',
		'mdonald',
		'fastfood'
	),
	(
		'Brine',
		'Drain',
		'bdrain',
		'erzTq5k'
	),
	(
		'Apple',
		'Simpson',
		'asimpson',
		'fr3ozenty'
	),
	(
		'Thed',
		'Cran',
		'tcran',
		'G12Summit'
	);''')

conn2.commit()