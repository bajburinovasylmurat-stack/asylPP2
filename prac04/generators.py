def fun(max):
    cnt = 1
    while cnt <= max:
        yield cnt
        cnt += 1

ctr = fun(5)
for n in ctr:
    print(n)



def fun():
    yield 1            
    yield 2            
    yield 3            
 
# Driver code to check above generator function
for val in fun(): 
    print(val)



def fun():
    return 1 + 2 + 3

res = fun()
print(res)



sq = (x*x for x in range(1, 6))
for i in sq:
    print(i)



#ex 1
def squares(n):
    for i in range(n + 1):
        yield i * i

for num in squares(5):
    print(num)