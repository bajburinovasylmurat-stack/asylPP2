import datetime

x = datetime.datetime.now()

print(x)




import datetime

x = datetime.datetime.now()

print(x.year)
print(x.strftime("%A"))



import datetime

x = datetime.datetime(2020, 5, 17)

print(x)


import datetime

x = datetime.datetime(2018, 6, 1)

print(x.strftime("%B"))





#Exercise
#1
from datetime import datetime, timedelta

def Asik():
    t = datetime.now()
    r = t - timedelta(days=5)
    print(r)

Asik()

#ex2


def hi():
    today = datetime.now().date()
    print(today - timedelta(days=1))
    print(today)
    print(today + timedelta(days=1))

hi()


#ex3
def remove():
    now = datetime.now()
    print(now.replace(microsecond=0))

remove()

#ex4
def difference():
    d1 = datetime(2026, 2, 20, 10, 0, 0)
    d2 = datetime(2026, 2, 24, 12, 30, 0)
    
    d = d2 - d1
    print(d.total_seconds())

difference()

