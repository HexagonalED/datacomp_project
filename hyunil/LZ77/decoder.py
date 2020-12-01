import struct
import os
import sys
import time



def decoder(name, out, search):
	MAX_SEARCH = search
	file = open(name,"rb")
	input = file.read()

	chararray = ""
	i=0

	while i<len(input):

		#unpack, every 3 bytes (x,y,z)
		(offset_and_length, char)= struct.unpack(">Hc", input[i:i+3])

		#shift right, get offset (length dissapears)
		offset = offset_and_length >> 6

		#substract by offset000000, gives length value
		length = offset_and_length - (offset<<6)

		#print "swag"
		#print offset
		#print length

	 	i=i+3

	 	#case is (0,0,c)
		if(offset == 0) and (length == 0):
			chararray += char

		#case is (x,y,c)
		else:
			iterator = len(chararray) - MAX_SEARCH
			if iterator <0:
				iterator = offset
			else:
				iterator += offset
 			for pointer in range(length):
				chararray += chararray[iterator+pointer]
			chararray += char


	out.write(chararray)

def main():
	MAX_SEARCH = int(sys.argv[1])
	file_type = sys.argv[2]
	processed = open(file_type+".lz77.decompressed","w")
	decoder(file_type+".lz77",processed, MAX_SEARCH)
	processed.close

if __name__== "__main__":
    start = time.time()
    main()
    print("decode time:",time.time()-start)
