import sys, math

# unary coding : integer n -> binary list (1^n 0)
def unary(n):
    return [1]*n+[0]

# unary decoder block for code[start:]
def unary_decoder(code,start,debug=False):
    for n in range(start,len(code)):
        if code[n] == 0:
            if debug:
                print("unary : {}. {}, {}".format(n-start,n+1,start))
            return (n-start), int(n+1)

# binary coding : integer n -> binary list (binary rep of length k)
def binary(n,k,debug=False):
    if debug:
        if n>=2**k:
            print("n is bigger than 2^k -1")
        elif n<0:
            print("n is smaller than 0")
    code = [0]*k
    for i in range(k):
        code[i] = n % 2
        n //= 2
    return code

# binary decoder block for coce[start:]
def binary_decoder(code,k,start,debug=False):
    n = 0
    for b in range(start,start+int(k)):
        n += code[b] * (2**(b-start))
    if debug:
        print("binary : {}. {}, {}".format(n,start+k,start))
    return n, int(start+k)

# Elias gamma coding : integer n -> binary list (unary(k) + binary(n-2^k+1,k) for k = [log2(n+1)])
def gamma(n):
    k = int(math.log2(n+1))
    return unary(k) + binary(n-2**k+1,k)

# Elias gamma decoder block for code[start:]
def gamma_decoder(code,start):
    k, start = unary_decoder(code,start)
    m, start = binary_decoder(code,k,start)
    n = m + 2**k - 1
    return n, start

# Elias delta coding : integer n -> binary list (gamma(k) + binary(n-2^k+1,k) for k = [log2(n+1)])
def delta(n):
    k = int(math.log2(n+1))
    return gamma(k) + binary(n-2**k+1,k)

# Eliad delta decoder block for code[start:]
def delta_decoder(code,start):
    k, start = gamma_decoder(code,start)
    m, start = binary_decoder(code,k,start)
    n = m + 2**k - 1
    return n, start

# Golomb coding : integer n -> binary list (unary(q) + prefix(r) for n = qm+r)
def golomb(n, m, prefix=delta):
    q = n // m
    r = n - q * m
    return unary(q) + prefix(r)

# Golomb encoder : integer list -> binary list
def golomb_encoder(code, m, prefix=delta):
    encode = []
    for i in range(len(code)):
        encode+=golomb(code[i],m,prefix)
    return encode

# Golomb decoder block for code[start:]
def golomb_decoder_block(code, m, start, prefix_decoder=delta_decoder,debug=False):
    if debug :
        print("--------------")
        print(code[start:])
    q, start = unary_decoder(code,start)
    if debug: print(q,start)
    r, start = prefix_decoder(code,start)
    if debug: print(r,start)
    n = q * m + r
    return n, start

# Golomb decoder : binary list -> integer list 
def golomb_decoder(code, m, prefix_decoder=delta_decoder):
    start = 0
    decoded_lines = []
    while start < len(code)-1:
        n, start = golomb_decoder_block(code,m,start,prefix_decoder)
        decoded_lines += [n]
    return decoded_lines

# Tunstall tree maker
def tunstall_tree_maker(n, m, prob):
    leaves = []
    # function that return probability of codeword l.
    def prob_list(l,prob):
        val = 1
        for i in l:
            val *= prob[i]
        return val
    # append length-1 codewords to leaves
    for i in prob.keys():
        leaves.append([i])
    
    while(len(leaves)<=2**n-m):
        mprob = 0
        # find leaf 'ml' which have biggest probability
        for l in leaves:
            probl = prob_list(l,prob)
            if probl > mprob:
                ml = l
                mprob = probl
        # add leaves which is children of leaf 'ml' which have biggest probability
        for i in prob.keys():
            leaves.append(ml.copy()+[i])
        # remove 'ml'.
        leaves.remove(ml)
    return leaves

# tunstall encoder block for code[start:]
def tunstall(code, n, start, leaves):    
    for i in range(start+1,len(code)+1):
        if code[start:i] in leaves:
            if i==len(code):
                return binary(leaves.index(code[start:i]),n)+binary(i-start,n), i
            return binary(leaves.index(code[start:i]),n), i
    # Handle exception case of last encoding case.
    # Find leaf(codeword) which has code as prefix code
    # and return the length of code additionally.
    for leaf in leaves:
        for i in range(len(leaf)):
            if code[start:] == leaf[:i]:
                return binary(leaves.index(leaf),n) + binary(i, n), len(code)

# tunstall encoder : integer list -> binary list
def tunstall_encoder(code, n, leaves):
    start = 0
    encode = []
    while start<len(code):
        encode_block, start = tunstall(code, n, start, leaves)
        encode += encode_block
    return encode

# tunstall decoder block for code[start:]
def tunstall_decoder_block(code, n, start, leaves):
    num, start = binary_decoder(code, n, start)
    # Handle exception case when decoding last part.
    if start == len(code)-n:
        # decode additionally encoded bits in line 123 to get length of code in decoded leaf
        i, start = binary_decoder(code, n, start)
        # and return leaf[:i].
        return leaves[num][:i], start
    return leaves[num], start

# tunstall decoder : binary list -> integer list
def tunstall_decoder(code, n, leaves):
    start = 0
    decoded_lines = []
    while start < len(code)-1:
        codeblock, start = tunstall_decoder_block(code,n,start,leaves)
        decoded_lines += codeblock
    return decoded_lines

