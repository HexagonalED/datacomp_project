import math

def file2strlist(path, encoding='utf8'):
    f = open(path, 'r',encoding=encoding)
    lines = []
    while True:
        line = f.readline()
        lines += line 
        if not line:
            break
    f.close()
    return lines

def write_string(string, path, encoding='utf8'):
    g = open(path, 'w', encoding=encoding)
    g.write(string)
    g.close()

def binary2byte(binary):
    return bytes(int(''.join(str(s) for s in binary[i : i + 8]), 2) for i in range(0, len(binary), 8))

def byte2binary(b):
    bstring = ''.join(format(byte, '08b') for byte in b)
    return [int(bstring[i]) for i in range(len(bstring))]

def binary2binarystring(binary):
    string = ''
    return ''.join([chr(binary[i]+ord('0')) for i in range(len(binary))])

def binarystring2binary(string):
    return [int(string[i]) for i in range(len(string))]

def binary2int(binary):
    num = 0
    for i in range(len(binary)):
        num += binary[i] * (2**i)
    return num 

def add_bits(binary, num, length):
    for i in range(length):
        r = num % 2
        binary.append(r)
        num //= 2
    return binary

def str2list(string):
    return list(string)

def list2str(l):
    return ''.join(l)

def statistics(strlist,is_print=False):
    strlen = len(strlist)
    counter = dict()
    for i in range(strlen):
        if strlist[i] not in counter.keys():
            counter[strlist[i]] = 1
        else:
            counter[strlist[i]] += 1
    for key in counter.keys():
        counter[key] /= strlen
    if is_print:
        print("statistics : ")
        print(counter)
    return counter

def num2str(line, counter):
    sorted_counter = {k: v for k, v in sorted(counter.items(), key=lambda item: -item[1])}
    string = ''
    for i in range(len(line)):
        for num in range(len(counter)):
            if line[i]==int(num):
                string += list(sorted_counter.keys())[num]
    return string

def str2num(string, counter):
    sorted_counter = {k: v for k, v in sorted(counter.items(), key=lambda item: -item[1])}
    line = []
    for i in string:
        for num in range(len(counter)):
            if i == list(sorted_counter.keys())[num]:
                line += [int(num)]
    return line

def write_binary(path, binary):
    f = open(path, 'wb')
    length = len(binary)
    buffer = [(length-1)%8+1]
    for i in range(0,length,8):
        buffer += [binary2int(binary[i:i+8])]
    binary_ = bytes(buffer)
    f.write(binary_)
    f.close()

def write_binary_test():
    path = './test'
    binary = [1,0,1,1,0,0,0] * 17
    print(binary)
    write_binary(path,binary)
        
def read_binary(path):
    f = open(path, 'rb')
    binary_ = []
    while True:
        line = f.readline()
        if not line:
            break
        binary_ += line
    buffer = list(binary_)
    binary = []
    last = buffer[0]
    for i in range(1,len(buffer)-1):
        add_bits(binary, buffer[i], 8)
    add_bits(binary, buffer[-1], last)
    f.close()
    return binary

def read_binary_test():
    path = './test'
    binary = read_binary(path)
    print(binary)

if __name__ == '__main__':
    write_binary_test()
    read_binary_test()
