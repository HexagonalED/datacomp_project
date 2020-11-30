import math

# read file in path. return list of characters.
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

# write string to path.
def write_string(string, path, encoding='utf8'):
    g = open(path, 'w', encoding=encoding)
    g.write(string)
    g.close()

# string to list of characters
def str2list(string):
    return list(string)

# list of characters to string
def list2str(l):
    return ''.join(l)

# return character counter of list of characters
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

# integer list to string using character counter. 
def num2str(line, counter):
    # sort counter by counts
    sorted_counter = {k: v for k, v in sorted(counter.items(), key=lambda item: -item[1])}
    string = ''
    for i in range(len(line)):
        for num in range(len(counter)):
            # give smaller integers to characters of higher count
            if line[i]==int(num):
                string += list(sorted_counter.keys())[num]
    return string

# string to integer list using character counter.
def str2num(string, counter):
    sorted_counter = {k: v for k, v in sorted(counter.items(), key=lambda item: -item[1])}
    line = []
    for i in string:
        for num in range(len(counter)):
            if i == list(sorted_counter.keys())[num]:
                line += [int(num)]
    return line

# write binary list to path
# use byte unit. save the length of last bits additionally.
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

# read binary list from path
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

# convert binary list to integer
def binary2int(binary):
    num = 0
    for i in range(len(binary)):
        num += binary[i] * (2**i)
    return num 

# add bits correspond to num to binary list.
def add_bits(binary, num, length):
    for i in range(length):
        r = num % 2
        binary.append(r)
        num //= 2
    return binary


if __name__ == '__main__':
    write_binary_test()
    read_binary_test()
