import os, sys, time
from codes import golomb_encoder, golomb_decoder, tunstall_encoder, tunstall_decoder, tunstall_tree_maker
from process import file2strlist, write_string, str2list, list2str, statistics, num2str, str2num, write_binary, read_binary
from arcode import ArithmeticCode
from lzw import lzw_encode, lzw_decode, get_all_chars
from exp_helper import check_same, get_file_size, write_pkl, read_pkl, create_dir

exp_dict = {'dnaby' : {'name' : 'dnaby', 'file_encoding' : 'utf-8'}, 
            'englishby' : {'name' : 'englishby', 'file_encoding' : 'ISO-8859-1'},
            'xmlby' : {'name' : 'xmlby', 'file_encoding' : 'utf-8'},
            'SD1' : {'name' : 'SD1', 'file_encoding' : 'ISO-8859-1'},
            'SD2' : {'name' : 'SD2', 'file_encoding' : 'ISO-8859-1'},
            'SD3' : {'name' : 'SD3', 'file_encoding' : 'ISO-8859-1'},
            'SD4' : {'name' : 'SD4', 'file_encoding' : 'ISO-8859-1'}}

def golomb(expname = 'dnaby', m=1, prefix_name='delta'):
    from codes import binary, binary_decoder, gamma, gamma_decoder, delta, delta_decoder 
    import math
    # golomb
    
    # prefix code : binary code
    if prefix_name == 'binary':
        digit = int(math.log2(m))+1
        prefix, prefix_decoder = (lambda n : binary(n,digit)), (lambda code, start : binary_decoder(code, digit, start))
    # prefix code : Elias gamma code
    elif prefix_name == 'gamma':
        prefix, prefix_decoder = gamma, gamma_decoder
    # prefix code : Elias delta code
    elif prefix_name == 'delta':
        prefix, prefix_decoder = delta, delta_decoder
    
    name = exp_dict[expname]['name']
    file_encoding = exp_dict[expname]['file_encoding']
    method = 'golomb'
    
    # set path info
    path = './dataset/{}'.format(name)
    encoderoot = './result/{}/{}/encoding/'.format(name,method)
    decoderoot = './result/{}/{}/decoding/'.format(name,method)
    csvroot = './result/{}/{}/csv/'.format(name,method)
    create_dir(encoderoot)
    create_dir(decoderoot)
    create_dir(csvroot)
    encodepath = encoderoot + '{}_{}'.format(prefix_name,m)
    decodepath = decoderoot + '{}_{}'.format(prefix_name,m)
    csvpath = csvroot + '{}_{}'.format(prefix_name,m)
    
    # < Encoding >
    time0 = time.time()
    # read file
    lines = file2strlist(path, encoding=file_encoding)
    # get probability distribution
    prob = statistics(lines)
    write_pkl(prob, encoderoot+'prob_{}_{}'.format(prefix_name,m))
    # process string to list of ints
    processed_lines = str2num(lines,prob)
    # encode list of ints to binary using golomb encoding
    encoded_lines = golomb_encoder(processed_lines,m,prefix) 
    # write binary
    write_binary(encodepath, encoded_lines) 
    time1 = time.time()
    
    # < Decoding >
    # read encoded file
    lines = read_binary(encodepath)
    prob = read_pkl(encoderoot+'prob_{}_{}'.format(prefix_name,m))
    # decode encoded file using golomb decoding
    decoded_lines = golomb_decoder(lines, m,prefix_decoder) 
    # process list of ints to string using probability distribution
    decoded_string = num2str(decoded_lines,prob)
    # write decoded string
    write_string(decoded_string, decodepath,encoding=file_encoding)
    time2 = time.time()
    
    # Save results
    result = dict()
    result['is_right'] = check_same(path,decodepath, encoding=file_encoding)
    result['original_size'] = get_file_size(path)
    result['encoded_size'] = get_file_size(encodepath) + get_file_size(encoderoot+'prob_{}_{}'.format(prefix_name,m))
    result['subfile_size'] = get_file_size(encoderoot+'prob_{}_{}'.format(prefix_name,m))
    result['compression_ratio'] = result['encoded_size'] / result['original_size'] * 100
    result['compression_ratio_only'] = get_file_size(encodepath) / result['original_size'] * 100
    result['encoding_time'] = time1 - time0
    result['decoding_time'] = time2 - time1
    print(result)
    write_pkl(result, csvpath)

def tunstall(expname = 'dnaby', n=8):
    # tunstall
    name = exp_dict[expname]['name']
    file_encoding = exp_dict[expname]['file_encoding']
    method = 'tunstall'

    # set path info
    path = './dataset/{}'.format(name)
    encoderoot = './result/{}/{}/encoding/'.format(name,method)
    decoderoot = './result/{}/{}/decoding/'.format(name,method)
    csvroot = './result/{}/{}/csv/'.format(name,method)
    create_dir(encoderoot)
    create_dir(decoderoot)
    create_dir(csvroot)
    encodepath = encoderoot + '{}'.format(n)
    decodepath = decoderoot + '{}'.format(n)
    csvpath = csvroot + '{}'.format(n)
    
    # < Encoding >
    time0 = time.time()
    # read file
    lines = file2strlist(path, encoding=file_encoding)
    # get probability distribution
    prob = statistics(lines)
    write_pkl(prob, encoderoot+'prob_{}'.format(n))
    m = len(prob.keys())
    # derive tunstall tree using probability distribution
    leaves = tunstall_tree_maker(n, m, prob)
    # process string to list of characters
    processed_lines = str2list(lines)
    # encode list of characters to binary using tunstall encoding
    encoded_lines = tunstall_encoder(processed_lines,n,leaves)
    # write binary
    write_binary(encodepath, encoded_lines) 
    time1 = time.time()
    
    # < Decoding >
    # read encoded file
    lines = read_binary(encodepath)
    prob = read_pkl(encoderoot+'prob_{}'.format(n))
    m = len(prob.keys())
    # derive tunstall tree using probability distribution
    leaves = tunstall_tree_maker(n, m, prob)
    # decode encoded file using tunstall decoding
    decoded_lines = tunstall_decoder(lines,n,leaves)
    # process list of characters to string
    decoded_string = list2str(decoded_lines)
    # write decoded string
    write_string(decoded_string, decodepath, encoding=file_encoding)
    time2 = time.time()
    
    # Save results.
    result = dict()
    result['is_right'] = check_same(path,decodepath, encoding=file_encoding)
    result['original_size'] = get_file_size(path)
    result['encoded_size'] = get_file_size(encodepath) + get_file_size(encoderoot + 'prob_{}'.format(n))
    result['subfile_size'] = get_file_size(encoderoot+'prob_{}'.format(n))
    result['compression_ratio'] = result['encoded_size'] / result['original_size'] * 100
    result['compression_ratio_only'] = get_file_size(encodepath) / result['original_size'] * 100
    result['encoding_time'] = time1 - time0
    result['decoding_time'] = time2 - time1
    print(result)
    write_pkl(result, csvpath)

def arithmetic(expname = 'dnaby'):
    # arithmetic
    name = exp_dict[expname]['name']
    file_encoding = exp_dict[expname]['file_encoding']
    method = 'arithmetic'
    
    # set path info
    path = './dataset/{}'.format(name)
    encoderoot = './result/{}/{}/encoding/'.format(name,method)
    decoderoot = './result/{}/{}/decoding/'.format(name,method)
    csvroot = './result/{}/{}/csv/'.format(name,method)
    create_dir(encoderoot)
    create_dir(decoderoot)
    create_dir(csvroot)
    encodepath = encoderoot + '0'
    decodepath = decoderoot + '0'
    csvpath = csvroot + '0'
    
    # < Encoding >
    time0 = time.time()
    # init coder
    ar = ArithmeticCode()
    # encode file
    ar.encode_file(path, encodepath)
    time1 = time.time()
    # < Decoding >
    # init coder
    ar = ArithmeticCode()
    # decode file
    ar.decode_file(encodepath, decodepath)
    time2 = time.time()
    
    # Save results
    result = dict()
    result['is_right'] = check_same(path,decodepath, encoding=file_encoding)
    result['original_size'] = get_file_size(path)
    result['encoded_size'] = get_file_size(encodepath)
    result['compression_ratio'] = result['encoded_size'] / result['original_size'] * 100
    result['compression_ratio_only'] = get_file_size(encodepath) / result['original_size'] * 100
    result['encoding_time'] = time1 - time0
    result['decoding_time'] = time2 - time1
    print(result)
    write_pkl(result, csvpath)

def lzw_specific(expname = 'dnaby', size_min=8, size_max=12):
    # lzw_specific 
    name = exp_dict[expname]['name']
    file_encoding = exp_dict[expname]['file_encoding']
    method = 'lzw_specific'
    
    # set path info
    path = './dataset/{}'.format(name)
    encoderoot = './result/{}/{}/encoding/'.format(name,method)
    decoderoot = './result/{}/{}/decoding/'.format(name,method)
    csvroot = './result/{}/{}/csv/'.format(name,method)
    create_dir(encoderoot)
    create_dir(decoderoot)
    create_dir(csvroot)
    encodepath = encoderoot + '{}_{}'.format(size_min, size_max)
    decodepath = decoderoot + '{}_{}'.format(size_min, size_max)
    csvpath = csvroot + '{}_{}'.format(size_min, size_max)

    # < Encoding >
    time0 = time.time()
    # read file
    lines = file2strlist(path, encoding=file_encoding)
    # get chars used in datasets
    prob = statistics(lines)
    write_pkl(prob, encoderoot+'prob_{}_{}'.format(size_min,size_max))
    given_chars = list(prob.keys())
    # encode input string by lzw with given chars.
    encoded_lines = lzw_encode(lines, given_chars, size_min, size_max)
    # write file
    write_binary(encodepath, encoded_lines) 
    time1 = time.time()
    
    # < Decoding>
    # read encoded file
    lines = read_binary(encodepath)
    # get given chars.
    prob = read_pkl(encoderoot+'prob_{}_{}'.format(size_min,size_max))
    given_chars = list(prob.keys())
    # decode file.
    decoded_string = lzw_decode(lines, given_chars, size_min, size_max) 
    # write decoded string.
    write_string(decoded_string, decodepath,encoding=file_encoding)
    time2 = time.time()
    
    # Save results
    result = dict()
    result['is_right'] = check_same(path,decodepath, encoding=file_encoding)
    result['original_size'] = get_file_size(path)
    result['encoded_size'] = get_file_size(encodepath) + get_file_size(encoderoot+'prob_{}_{}'.format(size_min,size_max))
    result['subfile_size'] = get_file_size(encoderoot+'prob_{}_{}'.format(size_min,size_max))
    result['compression_ratio'] = result['encoded_size'] / result['original_size'] * 100
    result['compression_ratio_only'] = get_file_size(encodepath) / result['original_size'] * 100
    result['encoding_time'] = time1 - time0
    result['decoding_time'] = time2 - time1
    print(result)
    write_pkl(result, csvpath)

def lzw(expname = 'dnaby', size_min=8, size_max=12):
    # lzw
    name = exp_dict[expname]['name']
    file_encoding = exp_dict[expname]['file_encoding']
    method = 'lzw'

    # set path info
    path = './dataset/{}'.format(name)
    encoderoot = './result/{}/{}/encoding/'.format(name,method)
    decoderoot = './result/{}/{}/decoding/'.format(name,method)
    csvroot = './result/{}/{}/csv/'.format(name,method)
    create_dir(encoderoot)
    create_dir(decoderoot)
    create_dir(csvroot)
    encodepath = encoderoot + '{}_{}'.format(size_min, size_max)
    decodepath = decoderoot + '{}_{}'.format(size_min, size_max)
    csvpath = csvroot + '{}_{}'.format(size_min, size_max)
    
    # < Encoding >
    time0 = time.time()
    # read file
    lines = file2strlist(path, encoding=file_encoding)
    # Get default chars
    all_chars = get_all_chars()
    # Encode file by lzw with default chars
    encoded_lines = lzw_encode(lines, all_chars, size_min, size_max)
    # write encoded string.
    write_binary(encodepath, encoded_lines) 
    time1 = time.time()
    
    # < Decoding >
    # read encoded file
    lines = read_binary(encodepath)
    # Decode file by lzw with default chars 
    decoded_string = lzw_decode(lines, all_chars, size_min, size_max) 
    # write decoded string
    write_string(decoded_string, decodepath,encoding=file_encoding)
    time2 = time.time()
    
    # Save results.
    result = dict()
    result['is_right'] = check_same(path,decodepath, encoding=file_encoding)
    result['original_size'] = get_file_size(path)
    result['encoded_size'] = get_file_size(encodepath)
    result['compression_ratio'] = result['encoded_size'] / result['original_size'] * 100
    result['compression_ratio_only'] = get_file_size(encodepath) / result['original_size'] * 100
    result['encoding_time'] = time1 - time0
    result['decoding_time'] = time2 - time1
    print(result)
    write_pkl(result, csvpath)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", default='golomb', help='the name of method', type=str)
    args = parser.parse_args()
    def exp_golomb():
        for expname in exp_dict.keys():
            for prefix_name in ['binary','gamma','delta']:
                for m in range(1,10):
                    try:
                        golomb(expname, m, prefix_name)
                    except:
                        print("expname : {}, m : {} is bad".format(expname, m))
    def exp_tunstall():
        for expname in exp_dict.keys():
            for n in range(5,15):
                try:
                    tunstall(expname, n)
                except:
                    print("expname : {}, n : {} is bad".format(expname, n))
    def exp_arithmetic():
        for expname in exp_dict.keys():
            try:
                arithmetic(expname)
            except:
                print("expname : {} is bad".format(expname))
    def exp_lzw_specific():
        for expname in exp_dict.keys():
            for size_min in range(5,12):
                for size_max in range(5,16):
                    if size_min <= size_max:
                        try:
                            lzw_specific(expname, size_min, size_max)
                        except:
                            print("expname : {}, size_min : {}, size_max : {} is bad".format(expname, size_min, size_max))
    def exp_lzw():
        for expname in exp_dict.keys():
            for size_min in range(8,12):
                for size_max in range(8,16):
                    if size_min <= size_max:
                        try:
                            lzw(expname, size_min, size_max)
                        except:
                            print("expname : {}, size_min : {}, size_max : {} is bad".format(expname, size_min, size_max))
    if args.method == 'golomb':
        exp_golomb()
    elif args.method == 'tunstall':
        exp_tunstall()
    elif args.method == 'arithmetic':
        exp_arithmetic()
    elif args.method == 'lzw_specific':
        exp_lzw_specific()
    elif args.method == 'lzw':
        exp_lzw()
    elif args.method == 'debug':
        golomb('SD4',7)
        tunstall('SD4',8)
        arithmetic('SD4')
        lzw_specific('SD4')

