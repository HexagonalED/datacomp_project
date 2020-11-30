"""Use arithmetic coding to compress and decompress files.
************************************************************************
    File    : arcode.py
    Purpose : This file implements a simple class for compressing and
              decompressing files using the arithmetic coding algorithm.
              This implementation is not intended to be the best,
              fastest, smallest, or any other performance related
              adjective.  It is intended produced the same results as
              my ANSI C arithmetic coding library.
    Author  : Michael Dipperstein
    Date    : July 21, 2010
************************************************************************
arcode: A python module that uses arithmetic coding to compress and
        decompress files.
Copyright (C) 2010
      Michael Dipperstein (mdipperstein@gmail.com)
This file implements the arcode module.
Arcode is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.
Arcode is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import bitfile
import os

EOF_CHAR = 256

# number of bits used to compute running code values
PRECISION = 16

# mask to clear the msb of probability values
MSB_MASK = ((1 << (PRECISION - 1)) - 1)

# 2 bits less than precision. keeps lower and upper bounds from crossing
MAX_PROBABILITY = (1 << (PRECISION - 2))

class ArithmeticCode:
    def __init__(self):
        self._lower = 0             # lower bound of current code range
        self._upper = 0xFFFF        # upper bound of current code range

        self._code = 0              # current MSBs of encode input stream

        self._underflow_bits = 0    # current underflow bit count

        # The probability lower and upper ranges for each symbol
        self._ranges = [0 for i in range(self.upper(EOF_CHAR) + 1)]

        self._cumulative_prob = 0   # cumulative probability  of all ranges

        self._infile = None
        self._outfile = None

    @staticmethod
    def mask_bit(x):
        return (1 << (PRECISION - (1 + x)))

    @staticmethod
    def lower(c):
        if isinstance(c, (str, bytes)):     # handle strings
            return ord(c)
        return c

    @staticmethod
    def upper(c):
        if isinstance(c, (str, bytes)):     # handle strings
            return ord(c) + 1
        return c + 1

    def encode_file(self, input_file_name, output_file_name):

        # read through input file and compute ranges
        self._infile = open(input_file_name, 'rb')
        self.build_probability_range_list()
        self._infile.seek(0)

        # write header with ranges to output file
        self._outfile = bitfile.BitFile()
        self._outfile.open(output_file_name, 'wb')
        self.write_header()

        # encode file 1 byte at at time
        c = self._infile.read(1)
        while (len(c) != 0):
            self.apply_symbol_range(c)
            self.write_encoded_bits()
            c = self._infile.read(1)

        self._infile.close()
        self.apply_symbol_range(EOF_CHAR)   # encode an EOF
        self.write_encoded_bits()

        self.write_remaining()              # write out least significant bits
        self._outfile.close()

    def build_probability_range_list(self):
        # start with no symbols counted
        count_array = [0 for i in range(EOF_CHAR)]

        c = self._infile.read(1)
        while (len(c) != 0):
            count_array[ord(c)] += 1
            c = self._infile.read(1)

        total_count = sum(count_array)

        # rescale counts to be < MAX_PROBABILITY
        if total_count >= MAX_PROBABILITY:
            rescale_value = (total_count // MAX_PROBABILITY) + 1

            for index, value in enumerate(count_array):
                if value > rescale_value:
                    count_array[index] = value // rescale_value
                elif value != 0:
                    count_array[index] = 1

        # copy scaled symbol counts to range list upper range (add EOF)
        self._ranges = [0] + count_array + [1]
        self._cumulative_prob = sum(count_array)

        # convert counts to a range of probabilities
        self.symbol_count_to_probability_ranges()

    def symbol_count_to_probability_ranges(self):
        self._ranges[0] = 0                     # absolute lower bound is 0
        self._ranges[self.upper(EOF_CHAR)] = 1  # add one EOF character
        self._cumulative_prob += 1

        for c in range(EOF_CHAR + 1):
            self._ranges[c + 1] += self._ranges[c]

    def write_header(self):
        previous = 0

        for c in range(EOF_CHAR):
            if self._ranges[self.upper(c)] > previous:
                # some of these symbols will be encoded
                self._outfile.put_char(c)

                # calculate symbol count
                previous = (self._ranges[self.upper(c)] - previous)

                # write out PRECISION - 2 bit count
                self._outfile.put_bits(previous, (PRECISION - 2))

                # current upper range is previous for the next character
                previous = self._ranges[self.upper(c)]

        # now write end of table (zero count)
        self._outfile.put_char(0)
        previous = 0
        self._outfile.put_bits(previous, (PRECISION - 2))

    def apply_symbol_range(self, symbol):
        curr_range = self._upper - self._lower + 1      # current range

        # scale the upper range of the symbol being coded
        rescaled = self._ranges[self.upper(symbol)] * curr_range
        rescaled //= self._cumulative_prob

        # new upper = old lower + rescaled new upper - 1
        self._upper = self._lower + rescaled - 1

        # scale lower range of the symbol being coded
        rescaled = self._ranges[self.lower(symbol)] * curr_range
        rescaled //= self._cumulative_prob

        # new lower = old lower + rescaled new lower
        self._lower = self._lower + rescaled

    def write_encoded_bits(self):

        mask_bit_zero = self.mask_bit(0)
        mask_bit_one = self.mask_bit(1)

        while True:
            if (self._upper ^ ~self._lower) & mask_bit_zero:
                # MSBs match, write them to output file
                self._outfile.put_bit((self._upper & mask_bit_zero) != 0)

                # we can write out underflow bits too
                while self._underflow_bits > 0:
                    self._outfile.put_bit((self._upper & mask_bit_zero) == 0)
                    self._underflow_bits -= 1

            elif (~self._upper & self._lower) & mask_bit_one:
                # ******************************************************
                # Possible underflow condition: neither MSBs nor second
                # MSBs match.  It must be the case that lower and upper
                # have MSBs of 01 and 10.  Remove 2nd MSB from lower and
                # upper.
                # ******************************************************
                self._underflow_bits += 1
                self._lower &= ~(mask_bit_zero | mask_bit_one)
                self._upper |= mask_bit_one

                # ******************************************************
                # The shifts below make the rest of the bit removal
                # work.  If you don't believe me try it yourself.
                # ******************************************************
            else:
                return              # nothing left to do

            # **********************************************************
            # Mask off old MSB and shift in new LSB.  Remember that
            # lower has all 0s beyond it's end and upper has all 1s
            # beyond it's end.
            # **********************************************************
            self._lower &= MSB_MASK
            self._lower <<= 1
            self._upper &= MSB_MASK
            self._upper <<= 1
            self._upper |= 0x0001

    def write_remaining(self):
        if self._outfile is None:
            raise ArithmeticCodeError('No output file opened for encoding.')

        mask_bit_one = self.mask_bit(1)
        self._outfile.put_bit((self._lower & mask_bit_one) != 0)

        # write out any unwritten underflow bits
        self._underflow_bits += 1
        for i in range(self._underflow_bits):
            self._outfile.put_bit((self._lower & mask_bit_one) == 0)

    def decode_file(self, input_file_name, output_file_name):
        if (self._infile is not None) or (self._outfile is not None):
            raise ValueError('I/O operation on opened file.')

        # open input and build probability ranges from header in file
        self._infile = bitfile.BitFile()
        self._infile.open(input_file_name, 'rb')

        self.read_header()  # build probability ranges from header in file

        # read start of code and initialize bounds
        self.initialize_decoder()

        self._outfile = open(output_file_name, 'wb')

        # decode one symbol at a time
        while True:
            # get the unscaled probability of the current symbol
            unscaled = self.get_unscaled_code()

            # figure out which symbol has the above probability
            c = self.get_symbol_from_probability(unscaled)
            if c == EOF_CHAR:
                # no more symbols
                break

            ba = bytearray(1)
            ba[0] = c
            self._outfile.write(ba)

            # factor out symbol
            self.apply_symbol_range(c)
            self.read_encoded_bits()

        self._outfile.close()
        self._infile.close()

    def read_header(self):
        self._cumulative_prob = 0
        self._ranges = [0 for i in range(self.upper(EOF_CHAR) + 1)]
        count = 0

        # read [character, probability] sets
        while True:
            c = ord(self._infile.get_char())

            # read (PRECISION - 2) bit count
            count = self._infile.get_bits(PRECISION - 2)

            if count == 0:
                # 0 count means end of header
                break
            elif self._ranges[self.upper(c)] != 0:
                raise ArithmeticCodeError(
                    'Duplicate entry for ' +
                    hex(c) + ' in header.')

            self._ranges[self.upper(c)] = count
            self._cumulative_prob += count

        # convert counts to range list
        self.symbol_count_to_probability_ranges()

    def initialize_decoder(self):
        self._code = 0

        # read PRECISION MSBs of code one bit at a time
        for i in range(PRECISION):
            self._code <<= 1

            try:
                next_bit = self._infile.get_bit()
            except EOFError:
                # Encoded file out of data bits, just shift bits.
                pass
            except:
                raise       # other exception.  Let calling code handle it.
            else:
                self._code |= next_bit

        # start with full probability range [0%, 100%)
        self._lower = 0
        self._upper = 0xFFFF        # all ones

    def get_unscaled_code(self):
        range = self._upper - self._lower + 1

        # reverse the scaling operations from apply_symbol_range
        unscaled = self._code - self._lower + 1
        unscaled = unscaled * self._cumulative_prob - 1
        unscaled //= range
        return unscaled

    def get_symbol_from_probability(self, probability):
        # initialize indices for binary search
        first = 0
        last = self.upper(EOF_CHAR)
        middle = last // 2

        # binary search
        while (last >= first):
            if probability < self._ranges[self.lower(middle)]:
                # lower bound is higher than probability
                last = middle - 1
                middle = first + ((last - first) // 2)
            elif probability >= self._ranges[self.upper(middle)]:
                # upper bound is lower than probability
                first = middle + 1
                middle = first + ((last - first) // 2)
            else:
                # we must have found the right value
                return middle

        # error: none of the ranges include the probability
        raise ValueError('Probability not in range.')

    def read_encoded_bits(self):
        mask_bit_zero = self.mask_bit(0)
        mask_bit_one = self.mask_bit(1)

        while True:
            if (self._upper ^ ~self._lower) & mask_bit_zero:
                # MSBs match, allow them to be shifted out
                pass
            elif (~self._upper & self._lower) & mask_bit_one:
                # ******************************************************
                # Possible underflow condition: neither MSBs nor second
                # MSBs match.  It must be the case that lower and upper
                # have MSBs of 01 and 10.  Remove 2nd MSB from lower and
                # upper.
                # ******************************************************
                self._lower &= ~(mask_bit_zero | mask_bit_one)
                self._upper |= mask_bit_one
                self._code ^= mask_bit_one

                # the shifts below make the rest of the bit removal work
            else:
                # nothing to shift out
                return

            # **********************************************************
            # Mask off old MSB and shift in new LSB.  Remember that
            # lower has all 0s beyond it's end and upper has all 1s
            # beyond it's end.
            # **********************************************************
            self._lower &= MSB_MASK
            self._lower <<= 1
            self._upper &= MSB_MASK
            self._upper <<= 1
            self._upper |= 1
            self._code &= MSB_MASK
            self._code <<= 1

            try:
                next_bit = self._infile.get_bit()
            except EOFError:
                pass        # either out of bits or error occurred.
            except:
                raise       # other exception.  Let calling code handle it.
            else:
                self._code |= next_bit



if __name__=='__main__':
    ar = ArithmeticCode()
    input_file='dataset/englishby'
    encode_file=input_file+'_arithmetic_encoding'
    decode_file=input_file+'_arithmetic_decoding'
    ar.encode_file(input_file, encode_file)
    ar = ArithmeticCode()
    ar.decode_file(encode_file, decode_file)
