Requirements : python 3.5
How to run:
1. Golomb
    - python compression.py --method golomb 
2. Tunstall
    - python compression.py --method tunstall
3. Arithmetic
    - python compression.py --method arithmetic
4. LZW (compression with default alphabets)
    - python compression.py --method lzw
5. LZW-specific (compression with given chars)
    - python compression.py --method lzw_specific

After the experimetns ended, you can get csv file from result pkl files by running
    - python read_result.py
