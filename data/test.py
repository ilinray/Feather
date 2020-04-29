
def f():
    for i in range(10):
        yield i

print(1 in f())