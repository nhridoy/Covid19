import psycopg2
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import create_engine

### Date Time ###
dt = datetime.now()
dates = dt.date()
times = dt.time()
date = dates.strftime("%Y-%m-%d")
time = times.strftime('%I:%M %p')

### Creating Database ###
Host = 'ec2-107-20-153-39.compute-1.amazonaws.com'
Database = 'd733kp4iefrk3c'
User = 'kbjvpsitqsewlk'
Port = '5432'
Password = 'b60dfaa659edc207777782569ba293c529de7c54e62ea542b3767a9aac75feee'
URI = 'postgres://kbjvpsitqsewlk:b60dfaa659edc207777782569ba293c529de7c54e62ea542b3767a9aac75feee@ec2-107-20-153-39.compute-1.amazonaws.com:5432/d733kp4iefrk3c'

con = psycopg2.connect(f"dbname='{Database}' user='{User}' password='{Password}' host='{Host}' port='{Port}'")
cur = con.cursor()
engine = create_engine(f'{URI}://{User}:{Password}@{Host}:{Port}/{Database}')

### CREATE Date TABLE ###
cur.execute("CREATE TABLE if NOT EXISTS d_t (datee TEXT, timee TEXT)")
con.commit()
### INSERT Date DATA ###
cur.execute("INSERT INTO d_t (datee, timee) VALUES (%s,%s)", (date, time))
con.commit()
### VIEW Date DATA ###
cur.execute("SELECT * from d_t")
row = cur.fetchall()
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
        # url = "owid-covid-data.csv"
        df = pd.read_csv(url)
        col = list(df)
        df.to_sql("covid", engine)
        con.commit()

        ### DELETING Date DATA ###
        cur.execute("DELETE from d_t")
        con.commit()
        ### INSERT Date DATA ###
        cur.execute("INSERT INTO d_t (datee, timee) VALUES (%s,%s)", (date, time))
        con.commit()

        ### Viewing Table Column Names ###
        '''names = list(map(lambda x: x[0], cur.description))
        print(names)'''
        con.commit()
        con.commit()
        print("Executed")

    ### VIEW Date DATA ###
    dtdb = pd.read_sql_query("SELECT * FROM d_t", con)

    ### VIEW Covid DATA ###
    db = pd.read_sql_query("SELECT * FROM covid", con)

    return dtdb, db



