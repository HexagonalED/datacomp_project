How to run (execute each command at right directory)

static_huffman : python3 main.py <path to input file>

adaptive_huffman : 
  encoding : python3 encode.py <path to input file>
  decoding : python3 decode.py <path to original file>
Encoded, and decoded filenames are fixed relatively to original input file

LZ77 : 
 encoding : python3 encoder.py <path to input file> <lookahead buffer size (pow to 2)>
 decoding : python3 decoder.py <lookahead buffer size (pow to 2)> <path to original file>
