import os, pickle

# check files of path1 and path2 have same contents
def check_same(path1, path2, encoding='utf8'):
    f = open(path1, 'r', encoding=encoding)
    g = open(path2, 'r', encoding=encoding)
    while True:
        line1 = f.readline()
        line2 = g.readline()
        if line1 and line1==line2:
            continue
        if line1 and line1!=line2:
            print("{} and {} has different contents".format(path1,path2))
            return 0
        if not line1:
            if line1==line2:
                print("{} and {} has same contents".format(path1,path2))
                return 1
            if line1!=line2:
                print("{} and {} has different contents".format(path1,path2))
                return 0

def check_same_test():
    check_same('./dataset/dnaby','./result/dnaby/golomb/decoding/1')

# get file size of path
def get_file_size(path):
    return os.stat(path).st_size

def get_file_size_test():
    print(get_file_size('./dataset/dnaby'))

# read pkl file in path
def read_pkl(path, encoding='ASCII'):
    '''read path(pkl) and return files
    Dependency : pickle
    Args:
        path - string
               ends with pkl
    Return:
        pickle content
    '''
    print("Pickle is read from %s"%path)
    with open(path, 'rb') as f: return pickle.load(f, encoding=encoding)

# write pkl file of content to path
def write_pkl(content, path):
    '''write content on path with path
    Dependency : pickle
    Args:
        content - object to be saved
        path - string
                ends with pkl
    '''
    with open(path, 'wb') as f:
        print("Pickle is written on %s"%path)
        try: pickle.dump(content, f)
        except OverflowError: pickle.dump(content, f, protocol=4)

# create directory of name dirname
def create_dir(dirname):
   '''create directory named dirname
   Dependency : os
   Args:
       dirname - string
                 directory named
   '''
   if not os.path.exists(dirname):
       print("Creating %s"%dirname)
       try:
           os.makedirs(dirname)
       except FileExistsError:
           pass
   else:
       print("Already %s exists"%dirname)

# write dictionary of lists to path 
def write_multi_array(dict_, path):
    keys = [str(v) for v in dict_.keys()]
    content_matrix = list()

    content_matrix.append(keys)
    length = len(dict_[keys[0]])
    for idx in range(length):
        tmp_row = list()
        for key in keys:
            tmp_row.append(str(dict_[key][idx]))
        content_matrix.append(tmp_row)
    print(content_matrix)

    with open(path, 'w') as f:
        content_matrix_write(content_matrix, f)

# get invert matrix of matrix
def invert_matrix(matrix):
    nrow = len(matrix)
    ncol = len(matrix[0])
    matrix_i = [[matrix[r][c] for r in range(nrow)] for c in range(ncol)]
    return matrix_i

# write matrix to f.
def content_matrix_write(matrix, f, invert=False):
    if invert:
        matrix = invert_matrix(matrix)
    nrow = len(matrix)
    ncol = len(matrix[0])
    max_col_size = list()
    for c in range(ncol):
        tmp = 0
        for r in range(nrow):
            col_size = len(matrix[r][c])
            if tmp < col_size: tmp=col_size
        max_col_size.append(tmp)

    for c in range(ncol):
        for r in range(nrow):
            matrix[r][c]=" "*(max_col_size[c]-len(matrix[r][c]))+matrix[r][c]

    for r in range(nrow):
        f.write(','.join(matrix[r])+'\n')

if __name__ == '__main__':
    check_same_test()
    get_file_size_test()
