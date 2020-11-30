from process import binary2int, add_bits

def get_all_chars():
    chars = []
    for i in range(ord('a'), ord('z')+1):
        chars.append(chr(i))
    for i in range(ord('A'), ord('Z')+1):
        chars.append(chr(i))
    for i in range(ord('0'), ord('9')+1):
        chars.append(chr(i))
    chars += ['?', '!', ' ', ',', '.', ':', ';', '\n', '\r', '\t']
    return chars

class GraphNode(object):
    def __init__(self, code, key):
        self.child = {}
        self.code = code
        self.key = key

    def is_child(self, char):
        return char in self.child.keys()

    def add_child(self, char, code):
        self.child[char] = GraphNode(code, self.key+char)

class CodeTable(object):
    def __init__(self, max_nodes=2**8):
        # Initial config
        self.num_nodes = 0
        self.max_nodes = max_nodes
        self.code2nodes = [None for _ in range(self.max_nodes)]
        self.root = GraphNode(code=-1, key='')

    def is_full(self):
        # The last index is for expansion
        return self.num_nodes == self.max_nodes - 1

    def add_node(self, node, char):
        # If the dictionary is full, then return
        if self.is_full():
            return
        # Add a new child
        node.add_child(char, self.num_nodes)
        # Change the config
        self.code2nodes[self.num_nodes] = node.child[char]
        self.num_nodes += 1

    def expand(self):
        # Change the config
        self.code2nodes += [None for _ in range(self.max_nodes)]
        self.num_nodes = self.max_nodes
        self.max_nodes *= 2

def lzw_encode(string, given_chars, size_min=8, size_max=12):
    
    length = size_min
    table = CodeTable(max_nodes=2**length)

    # Add single nodes
    node = table.root
    for char in given_chars:
        table.add_node(node, char)

    binary_string = []
    
    for char in string:
        # If the current node + char is in the table
        if node.is_child(char):
            node = node.child[char]
        # Otherwise
        else:
            # Write the index of the current node
            code = node.code
            add_bits(binary_string, code, length)
            # Expand dictionary if it is full
            if table.is_full() and length < size_max:
                # Write the dummy index
                add_bits(binary_string, 2**length - 1, length)
                table.expand()
                length += 1
            # Add the current node + char to the dictionary
            table.add_node(node, char)
            # Set the current node to char (always exists)
            node = table.root
            node = node.child[char]
    
    code = node.code
    # Consider the case where the infile is empty. If the index is keyid then write the index
    if code >= 0:
        add_bits(binary_string, code, length)
    
    return binary_string

def lzw_decode(binary, given_chars, size_min=8, size_max=12):
    
    length = size_min
    table = CodeTable(max_nodes=2**length)

    # Add single nodes
    node = table.root
    for char in given_chars:
        table.add_node(node, char)
    string = ''
    start = 0
    prev_code = None
    curr_code = None
    while True:
        curr_code = binary2int(binary[start:start+length])
        start += length
        if start > len(binary):
            break

        if curr_code == 2**length - 1:
            length += 1
            continue
        if not curr_code < table.num_nodes:
            prev_node = table.code2nodes[prev_code]
            prev_key = prev_node.key
            char = prev_key[0]
            curr_key = prev_key + char
        else:
            curr_node = table.code2nodes[curr_code]
            curr_key = curr_node.key
        string += curr_key
        if prev_code is not None:
            prev_node = table.code2nodes[prev_code]
            char = curr_key[0]
            if table.is_full() and table.max_nodes < 2**size_max:
                table.expand()
            table.add_node(prev_node, char)
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
