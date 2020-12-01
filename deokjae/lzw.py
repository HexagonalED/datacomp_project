from process import binary2int, add_bits

# return default characters
def get_all_chars():
    chars = []
    for i in range(ord('a'), ord('z')+1):
        chars.append(chr(i))
    for i in range(ord('A'), ord('Z')+1):
        chars.append(chr(i))
    for i in range(ord('0'), ord('9')+1):
        chars.append(chr(i))
    chars += ['?', '!', ' ', ',', '.', ':', ';', '\n', '\r', '\t', '>', '<', '(', ')', '/', '-', '_', '#', '=', '"', '&', "'", '+', '\\', '*', '`', '{', '}', '^', '|', '[',']']
    return chars

# trie implemented by dictionary.
class GraphNode(object):
    def __init__(self, code, key):
        self.child = {}
        self.code = code
        self.key = key

    def is_child(self, char):
        return char in self.child.keys()

    def add_child(self, char, code):
        self.child[char] = GraphNode(code, self.key+char)

# codetable implemented by GraphNode(trie).
class CodeTable(object):
    def __init__(self, max_nodes=2**8):
        # init codetable
        self.num_nodes = 0
        self.max_nodes = max_nodes
        self.code2nodes = [None for _ in range(self.max_nodes)]
        self.root = GraphNode(code=-1, key='')

    def is_full(self):
        # The last nodes is for trash codeword indicate expansion of codetable in decoding.
        return self.num_nodes == self.max_nodes - 1

    def add_node(self, node, char):
        # Check the dictionary is full or not
        if self.is_full():
            return
        # Add a new child 
        node.add_child(char, self.num_nodes)
        # modify info of codetable.
        self.code2nodes[self.num_nodes] = node.child[char]
        self.num_nodes += 1

    def expand(self):
        # expand the codetable. modify the info.
        self.code2nodes += [None for _ in range(self.max_nodes)]
        self.num_nodes = self.max_nodes
        self.max_nodes *= 2

def lzw_encode(string, given_chars, size_min=8, size_max=12):
    # init encode-length equal to size-min
    length = size_min
    # init codetable
    table = CodeTable(max_nodes=2**length)

    # Add length-1 codewords to codetable
    node = table.root
    for char in given_chars:
        table.add_node(node, char)
    
    # list saving encoding.
    binary_string = []
    
    for char in string:
        # if the current codeword + char is in code table
        if node.is_child(char):
            node = node.child[char]
        # if not
        else:
            # write the index of the current codeword
            code = node.code
            add_bits(binary_string, code, length)
            # expand codetable if it is full and encode-length < size-max
            if table.is_full() and length < size_max:
                # write the trash codeword to indicate expansion of codetable at decoding
                add_bits(binary_string, 2**length - 1, length)
                table.expand()
                length += 1
            # Add the current codeword + char to the code table
            table.add_node(node, char)
            # Set the current codeword as char.
            node = table.root
            node = node.child[char]
    
    code = node.code
    # Handle exception case that infile is empty (code = -1)
    if code >= 0:
        add_bits(binary_string, code, length)
    
    return binary_string

def lzw_decode(binary, given_chars, size_min=8, size_max=12):
    # init decode-length equal to size-min
    length = size_min
    # init codetable
    table = CodeTable(max_nodes=2**length)

    # Add length-1 codewords to codetable
    node = table.root
    for char in given_chars:
        table.add_node(node, char)

    # string saving decoded string.
    string = ''
    start = 0
    prev_code = None
    curr_code = None

    while True:
        # read encode-length bit from encoded binary bits 
        curr_code = binary2int(binary[start:start+length])
        # modify reader position
        start += length
        # if file is read all, break
        if start > len(binary):
            break
        
        # if current codeword is trash codeword, expand the code table
        if curr_code == 2**length - 1:
            length += 1
            continue
        # Handle exception case of curr_code == num_nodes,
        # which means current codeword do not exist it the codetable.  
        if not curr_code < table.num_nodes:
            # set the current codeword to prev codeword + first char of prev codeword.
            prev_node = table.code2nodes[prev_code]
            prev_key = prev_node.key
            char = prev_key[0]
            curr_key = prev_key + char
        # For other cases,
        else:
            # get current codeword from codetable.
            curr_node = table.code2nodes[curr_code]
            curr_key = curr_node.key
        # write key string to string.
        string += curr_key
        # add prev codeword + first char of current codeword to codetable.
        if prev_code is not None:
            prev_node = table.code2nodes[prev_code]
            char = curr_key[0]
            # if codetable is full, expand codetable.
            if table.is_full() and table.max_nodes < 2**size_max:
                table.expand()
            table.add_node(prev_node, char)
        # set cur code to prev code.
        prev_code = curr_code
    return string

if __name__=='__main__':
    string = 'ABAAACCBABDDDAAABBCCCAAAAA'
    prob = {'A' : 0.1, 'B' : 0.2, 'C' : 0.3, 'D' : 0.4}
    binary = lzw_encode(string, prob)
    print(binary)
    decode = lzw_decode(binary, prob)
    print(decode)
    print(string)
