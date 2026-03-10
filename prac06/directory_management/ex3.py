import os
f = os.listdir("prac06/directory_management")
for i in f:
    if i.endswith(".py"):
        print(i)