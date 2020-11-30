from codes import *

def test():
    n = 22
    k = 5
    m = 10

    print("n : {}, k : {}, m : {}".format(n,k,m))
    
    code1 = unary(n)
    print("unary(n): {}".format(code1))
    print("unary_decoder(code1): {}".format(unary_decoder(code1,0)))
    
    code2 = binary(n, k)
    print("binary(n, k): {}".format(code2))
    print("binary_decoder(code2, k): {}".format(binary_decoder(code2, k,0)))
    
    code3 = gamma(n)
    print("gamma(n): {}".format(code3))
    print("gamma_decoder(code3): {}".format(gamma_decoder(code3,0)))
    
    code4 = delta(n)
    print("delta(n): {}".format(code4))
    print("delta_decoder(code4): {}".format(delta_decoder(code4,0)))
    
if __name__=="__main__":
    test()
