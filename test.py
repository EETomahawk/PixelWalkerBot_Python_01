def a(*args):
    print(b"".join(args))


x = 0
y = 1

bx = bytes([x])
by = bytes([y])

#print(bx+by)

a(bx)