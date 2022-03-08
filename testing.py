import struct

def float_to_bin(num):
    return format(struct.unpack('!I', struct.pack('!f', num))[0], '032b')

"""
0 01111111 11000010100011110101110
"""
10101000
print(float_to_bin(1.76))
if 1 or 0:
    print('yay')
if 1 or 1:
    pass
