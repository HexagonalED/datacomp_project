from exp_helper import read_pkl, write_multi_array, create_dir

path = './result/SD1/arithmetic/csv/0'
dlist = ['dnaby', 'englishby', 'xmlby', 'SD1', 'SD2', 'SD3', 'SD4']
create_dir('./result_csv/')
def golomb():
    for d in dlist:
        saveroot = './result_csv/{}_{}_result.csv'.format(d,'golomb')

        root = './result/{}/{}/csv/'.format(d,'golomb')
        if d == 'SD1':
            example = read_pkl(root + 'binary_20')
        else:
            example = read_pkl(root + 'binary_1')

        r = dict()
        r['prefix'] = list()
        r['m'] = list()
        for key in example.keys():
            r[key] = list()
        for prefix_name in ['binary', 'gamma', 'delta']:
            if d == 'SD1':
                for m in [20,25,30,35,40]:
                    path = root + '{}_{}'.format(prefix_name,int(m))
                    try:
                        result = read_pkl(path)
                        for key in result.keys():
                            r[key].append(result[key])
                        r['prefix'].append(prefix_name)
                        r['m'].append(m)
                    except:
                        print('prefix : {}, m : {} no reault'.format(prefix_name,m))
            else:
                for m in range(1,10):
                    path = root + '{}_{}'.format(prefix_name,int(m))
                    try:
                        result = read_pkl(path)
                        for key in result.keys():
                            r[key].append(result[key])
                        r['prefix'].append(prefix_name)
                        r['m'].append(m)
                    except:
                        print('prefix : {}, m : {} no reault'.format(prefix_name,m))

        write_multi_array(r, saveroot)

def tunstall():
    for d in dlist:
        saveroot = './result_csv/{}_{}_result.csv'.format(d,'tunstall')
        root = './result/{}/{}/csv/'.format(d,'tunstall')
        example = read_pkl(root + '5')

        r = dict()

        r['n'] = list()
        for key in example.keys():
            r[key] = list()
        for n in range(5,15):
            path = root + '{}'.format(int(n))
            try:
                result = read_pkl(path)
                for key in result.keys():
                    r[key].append(result[key])
                r['n'].append(n)
            except:
                print('n: {} no reault'.format(n))
        write_multi_array(r, saveroot)

def arithmetic():
    for d in dlist:
        saveroot = './result_csv/{}_{}_result.csv'.format(d,'arithmetic')
        root = './result/{}/{}/csv/'.format(d,'arithmetic')
        example = read_pkl(root + '0')

        r = dict()

        for key in example.keys():
            r[key] = list()
        path = root + '{}'.format(0)
        result = read_pkl(path)
        for key in result.keys():
            r[key].append(result[key])
        write_multi_array(r, saveroot)

def lzw_specific():
    for d in dlist:
        saveroot = './result_csv/{}_{}_result.csv'.format(d,'lzw_specific')
        root = './result/{}/{}/csv/'.format(d,'lzw_specific')
        example = read_pkl(root + '10_10')

        r = dict()

        r['size_min'] = list()
        r['size_max'] = list()
        for key in example.keys():
            r[key] = list()
        for size_min in range(5,12):
            for size_max in range(5,16):
                path = root + '{}_{}'.format(int(size_min),int(size_max))
                try:
                    result = read_pkl(path)
                    for key in result.keys():
                        r[key].append(result[key])
                    r['size_min'].append(size_min)
                    r['size_max'].append(size_max)
                except:
                    print('{}, {} no reault'.format(size_min, size_max))
        write_multi_array(r, saveroot)

def lzw():
    for d in ['dnaby','xmlby']:
        saveroot = './result_csv/{}_{}_result.csv'.format(d,'lzw')
        root = './result/{}/{}/csv/'.format(d,'lzw')
        example = read_pkl(root + '10_10')

        r = dict()

        r['size_min'] = list()
        r['size_max'] = list()
        for key in example.keys():
            r[key] = list()
        for size_min in range(8,12):
            for size_max in range(8,16):
                path = root + '{}_{}'.format(int(size_min),int(size_max))
                try:
                    result = read_pkl(path)
                    for key in result.keys():
                        r[key].append(result[key])
                    r['size_min'].append(size_min)
                    r['size_max'].append(size_max)
                except:
                    print('{}, {} no reault'.format(size_min, size_max))
        write_multi_array(r, saveroot)

if __name__ == '__main__':
    golomb()
    tunstall()
    arithmetic()
    lzw_specific()
    lzw()
