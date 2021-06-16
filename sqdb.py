import sqlite3
import pandas as pd
from datetime import datetime
from dateutil.parser import parse

### Date Time ###
dt = datetime.now()
dates = dt.date()
times = dt.time()
date = dates.strftime("%Y-%m-%d")
time = times.strftime('%I:%M %p')

### Creating Database ###
con = sqlite3.connect("covid-data.db", check_same_thread=False)
cur = con.cursor()

### CREATE Date DB ###
con2 = sqlite3.connect("date.db", check_same_thread=False)
cur2 = con2.cursor()
### CREATE Date TABLE ###
cur2.execute("CREATE TABLE if NOT EXISTS d_t (datee, timee)")
con2.commit()
### VIEW Date DATA ###
cur2.execute("SELECT * from d_t")
row = cur2.fetchall()
old_date = row[0][0]
old_time = row[0][1]
old_time = (f"{old_date} {old_time}")
### Converting String Date to DateTime Object ###
old_date = parse(old_date)
old_time = parse(old_time)
new_date = parse(str(dates))
new_time = parse(time)
print(f"Old Date: {old_date}")
print(f"New Date: {new_date}")

if old_date == new_date:
    old_time = datetime.strptime(str(old_time), "%Y-%m-%d %H:%M:%S")
    new_time = datetime.strptime(str(new_time), "%Y-%m-%d %H:%M:%S")
    comp_time = new_time-old_time
    static_time = datetime.strptime(f"{date} 04:00:00", "%Y-%m-%d %H:%M:%S")
    comp_time = datetime.strptime(f"{date} {comp_time}", "%Y-%m-%d %H:%M:%S")

    print(f"Old Time: {(old_time)}")
    print(f"New Time: {(new_time)}")
    print(f"Static Time: {(static_time)}")
    print(f"Comp Time: {(comp_time)}")
    print(static_time <= comp_time)



def in_date(date, time):
    if old_date != new_date or static_time <= comp_time:
        ### Loading Data From Web ###
        url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
        # url = "owid-covid-data (1).csv"
        df = pd.read_csv(url)
        col = list(df)

        ### Creating Table ###
        cur.execute(
            "CREATE TABLE if NOT EXISTS covid ({},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},"
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},"
            "{},{},{} )".format(*col))
        con.commit()

        ### Intering Values from csv to Table ###
        cur.execute("DELETE from covid")
        con.commit()
        df.to_sql("covid", con, if_exists='append', index=False)


        ### DELETING Date DATA ###
        cur2.execute("DELETE from d_t")
        con2.commit()
        ### INSERT Date DATA ###
        cur2.execute("INSERT INTO d_t (datee, timee) VALUES (?,?)", (date, time))
        con2.commit()

        ### Viewing Table Column Names ###
        '''names = list(map(lambda x: x[0], cur.description))
        print(names)'''
        con2.commit()
        con.commit()
        print("Executed")

    ### VIEW Date DATA ###
    dtdb = pd.read_sql_query("SELECT * FROM d_t", con2)

    ### VIEW Covid DATA ###
    db = pd.read_sql_query("SELECT * FROM covid", con)

    return dtdb, db
