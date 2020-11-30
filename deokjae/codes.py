import sys, math

def unary(n):
    return [1]*n+[0]

def unary_decoder(code,start,debug=False):
    for n in range(start,len(code)):
        if code[n] == 0:
            if debug:
                print("unary : {}. {}, {}".format(n-start,n+1,start))
            return (n-start), int(n+1)

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

def binary_decoder(code,k,start,debug=False):
    n = 0
    for b in range(start,start+int(k)):
        n += code[b] * (2**(b-start))
    if debug:
        print("binary : {}. {}, {}".format(n,start+k,start))
    return n, int(start+k)

def gamma(n):
    k = int(math.log2(n+1))
    return unary(k) + binary(n-2**k+1,k)

def gamma_decoder(code,start):
    k, start = unary_decoder(code,start)
    m, start = binary_decoder(code,k,start)
    n = m + 2**k - 1
    return n, start

def delta(n):
    k = int(math.log2(n+1))
    return gamma(k) + binary(n-2**k+1,k)

def delta_decoder(code,start):
    k, start = gamma_decoder(code,start)
    m, start = binary_decoder(code,k,start)
    n = m + 2**k - 1
    return n, start

def golomb(n, m, prefix=delta):
    q = n // m
    r = n - q * m
    return unary(q) + prefix(r)

def golomb_encoder(code, m, prefix=delta):
    encode = []
    for i in range(len(code)):
        encode+=golomb(code[i],m,prefix)
    return encode

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

def golomb_decoder(code, m, prefix_decoder=delta_decoder):
    start = 0
    decoded_lines = []
    while start < len(code)-1:
        n, start = golomb_decoder_block(code,m,start,prefix_decoder)
        decoded_lines += [n]
    return decoded_lines

def tunstall_tree_maker(n, m, prob):
    leaves = []
    
    def prob_list(l,prob):
        val = 1
        for i in l:
            val *= prob[i]
        return val
    
    for i in prob.keys():
        leaves.append([i])
    
    while(len(leaves)<=2**n-m):
        mprob = 0
        for l in leaves:
            probl = prob_list(l,prob)
            if probl > mprob:
                ml = l
                mprob = probl
        for i in prob.keys():
            leaves.append(ml.copy()+[i])
        leaves.remove(ml)
    return leaves

def tunstall(code, n, start, leaves):    
    for i in range(start+1,len(code)+1):
        if code[start:i] in leaves:
            if i==len(code):
                return binary(leaves.index(code[start:i]),n)+binary(i-start,n), i
            return binary(leaves.index(code[start:i]),n), i
    #print("last encoding scarce")

    for leaf in leaves:
        for i in range(len(leaf)):
            if code[start:] == leaf[:i]:
                return binary(leaves.index(leaf),n) + binary(i, n), len(code)

def tunstall_encoder(code, n, leaves):
    start = 0
    encode = []
    while start<len(code):
        encode_block, start = tunstall(code, n, start, leaves)
        if len(encode_block) > n:
            pass
            #print("last encoded well")
        encode += encode_block
    return encode

def tunstall_decoder_block(code, n, start, leaves):
    num, start = binary_decoder(code, n, start)
    if start == len(code)-n:
        i, start = binary_decoder(code, n, start)
        return leaves[num][:i], start
    return leaves[num], start

def tunstall_decoder(code, n, leaves):
    start = 0
    decoded_lines = []
    while start < len(code)-1:
        codeblock, start = tunstall_decoder_block(code,n,start,leaves)
        decoded_lines += codeblock
    return decoded_lines

def arithmetic(word, prob):
    low, high = 0.0, 1.0
    cdf = [0.0]
    for c in prob.keys():
        cdf.append(cdf[-1]+prob[c])
        
    for c in word:
        ran = high - low
        high = low + ran * cdf[list(prob.keys()).index(c)+1]
        low = low + ran * cdf[list(prob.keys()).index(c)]
    return low

def arithmetic_decoder(value, strlen, prob):
    low, high = 0.0, 1.0
    x = 0
    word = []
    cdf = [0.0]
    for c in prob.keys():
        cdf.append(cdf[-1]+prob[c])
    while (strlen != len(word) or value !=0):
        for idx, val in enumerate(cdf):
            if val > value:
                word.append(list(prob.keys())[idx-1])
                value = (value - cdf[idx-1]) / (cdf[idx] - cdf[idx-1])
                break
    return word
