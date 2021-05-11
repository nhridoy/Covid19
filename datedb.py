import sqlite3
from datetime import datetime
from dateutil.parser import parse

### Date Time ###
dt = datetime.now()
dates = dt.date()
times = dt.time()
date = dates.strftime("%Y-%m-%d")
time = times.strftime('%I:%M %p')

print((dates))
print((times))

### CREATE Date DB ###
con2 = sqlite3.connect("date.db")
cur2 = con2.cursor()
### CREATE Date TABLE ###
cur2.execute("CREATE TABLE if NOT EXISTS d_t (datee, timee)")
con2.commit()
### VIEW Date DATA ###
cur2.execute("SELECT * from d_t")
row = cur2.fetchall()
print(type((row[0][0])))
old_date = row[0][0]
print(f"Old Date: {old_date}")
old_date = parse(old_date)
new_date = parse(str(dates))
print(f"Old Date: {old_date}")
print(f"New Date: {new_date}")

def in_date(date, time):
    if old_date < new_date:
        ### DELETING Date DATA ###
        cur2.execute("DELETE from d_t")
        con2.commit()
        ### INSERT Date DATA ###
        cur2.execute("INSERT INTO d_t (datee, timee) VALUES (?,?)", (date, time))
        con2.commit()
        ### VIEW DATA
        cur2.execute("SELECT * from d_t")
        row = cur2.fetchall()
        print(type((row[0][0])))


in_date(date, time)
