################################################################################
#
# Copyright (c) 2009 The MadGraph Development team and Contributors
#
# This file is a part of the MadGraph 5 project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph license which should accompany this 
# distribution.
#
# For more information, please visit: http://madgraph.phys.ucl.ac.be
#
################################################################################

"""Classes, methods, functions and regular expressions required 
for all calculations related to QCD color."""

import copy
import itertools
import operator
import re

#===============================================================================
# Regular expression objects (compiled)
#===============================================================================

# Match only valid color string object
re_color_object = re.compile(r"""^(T\(((-?\d+)(,-?\d+)*)?\)
                            |Tr\(((-?\d+)(,-?\d+)*)?\)
                            |f\(-?\d+,-?\d+,-?\d+\)
                            |d\(-?\d+,-?\d+,-?\d+\)
                            |(1/)?Nc
                            |-?(\d+/)?\d+
                            |I)$""",
                            re.VERBOSE)

# T trace T(a,b,c,...,i,i), group start is a,b,c,...
re_T_trace = re.compile(r"""^T\((?P<start>(-?\d+,)*?(-?\d+)?),?
                            (?P<id>-?\d+),(?P=id)\)$""", re.VERBOSE)

# T product T(a,...,i,j)T(b,...,j,k), group start1 is a,...,
# group start2 is b,..., group id1 is i and group id2 is k
re_T_product1 = re.compile(r"""^T\((?P<start1>(-?\d+,)*)
                                (?P<id1>-?\d+),(?P<summed>-?\d+)\)
                                T\((?P<start2>(-?\d+,)*)
                                (?P=summed),(?P<id2>-?\d+)\)$""", re.VERBOSE)

# T product T(b,...,j,k)T(a,...,i,j), group start1 is a,...,
# group start2 is b,..., group id1 is i and group id2 is k
re_T_product2 = re.compile(r"""^T\((?P<start2>(-?\d+,)*)
                                (?P<summed>-?\d+),(?P<id2>-?\d+)\)
                                T\((?P<start1>(-?\d+,)*)
                                (?P<id1>-?\d+),(?P=summed)\)$""", re.VERBOSE)

# Tr()
re_trace_0_index = re.compile(r"^Tr\(\)$")

# Tr(i), group id is i
re_trace_1_index = re.compile(r"^Tr\((?P<id>-?\d+)\)$")

# Tr(a,b,c,...), group elems is a,b,c,...
re_trace_n_indices = re.compile(r"^Tr\((?P<elems>(-?\d+,)*(-?\d+)?)\)$")

# Match a fraction (with denominator or not), group has num/den entries
re_fraction = re.compile(r"^(?P<num>-?\d+)(/(?P<den>\d+))?$")

# Match f(a,b,c) terms, groups elements are a, b and c
re_f_term = re.compile(r"^f\((?P<a>-?\d+),(?P<b>-?\d+),(?P<c>-?\d+)\)")

# Match d(a,b,c) terms, groups elements are a, b and c
re_d_term = re.compile(r"^d\((?P<a>-?\d+),(?P<b>-?\d+),(?P<c>-?\d+)\)")

# Match T(a,...,x,b,...,x,c,...,i,j), groups element are a='a,...',b='b,...,' 
# c='c,...,' (notice commas) and id1=i, id2=j
re_T_int_sum = re.compile(r"""^T\((?P<a>(-?\d+,)*)
                                (?P<x>-?\d+),
                                (?P<b>(-?\d+,)*)
                                (?P=x),
                                (?P<c>(-?\d+,)*)
                                (?P<id1>-?\d+),(?P<id2>-?\d+)\)$""", re.VERBOSE)

# Match Tr(a,...,x,b,...,x,c,...), groups element are a='a,...',b='b,...,' 
# c='c,...,' (notice commas) 
re_trace_int_sum = re.compile(r"""^Tr\((?P<a>(-?\d+,)*)
                                (?P<x>-?\d+),
                                (?P<b>(-?\d+,)*)
                                (?P=x),?
                                (?P<c>(-?\d+,)*(-?\d+)?)\)$""", re.VERBOSE)

# Match Tr(a...,x,b,...)Tr(c...,x,d,...), groups element are a='a,...',
# b='b,...', c='c,...,' and d='d,...' (notice commas) 
re_trace_product = re.compile(r"""^Tr\((?P<a>(-?\d+,)*)
                                (?P<x>-?\d+),
                                (?P<b>(-?\d+,)*(-?\d+)?)\)
                                Tr\((?P<c>(-?\d+,)*)
                                (?P=x),?
                                (?P<d>(-?\d+,)*(-?\d+)?)\)$""", re.VERBOSE)

# Match Tr(a,...,x,b,...)T(c,...,x,d,...,i,j)
re_trace_T_product1 = re.compile(r"""^Tr\((?P<a>(-?\d+,)*)
                                (?P<x>-?\d+),
                                (?P<b>(-?\d+,)*(-?\d+)?)\)
                                T\((?P<c>(-?\d+,)*)
                                (?P=x),?
                                (?P<d>(-?\d+,)*)
                                (?P<id1>-?\d+),(?P<id2>-?\d+)\)$""", re.VERBOSE)
re_trace_T_product2 = re.compile(r"""^T\((?P<c>(-?\d+,)*)
                                (?P<x>-?\d+),?
                                (?P<d>(-?\d+,)*)
                                (?P<id1>-?\d+),(?P<id2>-?\d+)\)
                                Tr\((?P<a>(-?\d+,)*)
                                (?P=x),
                                (?P<b>(-?\d+,)*(-?\d+)?)\)$""", re.VERBOSE)


#===============================================================================
# ColorString
#===============================================================================
class ColorString(list):
    """Define a color string as an ordered list of strings corresponding to the
    different color structures. Different elements are implicitly linked by
    a product operator."""

    def __init__(self, init_list=None):
        """Initialization method, if init_list is given, try to fill the 
        color string with the content."""

        list.__init__(self)

        if init_list:
            if not isinstance(init_list, list):
                raise ValueError, \
                    "Object %s is not a valid list" % init_list
            for elem in init_list:
                if self.is_valid_color_object(elem):
                    self.append(elem)
                else: raise ValueError, \
                        "String %s is not a valid color object" % elem

    def is_valid_color_object(self, test_str):
        """Checks the validity of a given color object stored in 
        string test_str. Returns True if valid, False otherwise."""

        if not isinstance(test_str, str):
            raise ValueError, "Object %s is not a valid string." % str(test_str)

        # Check if the string has the right format
        if re_color_object.match(test_str):
            return True
        else:
            return False

    def append(self, mystr):
        """Appends an string, but test if valid before."""
        if not self.is_valid_color_object(mystr):
            raise ValueError, \
                        "String %s is not a valid color structure" % mystr
        else:
            list.append(self, mystr)

    def insert(self, pos, mystr):
        """Insert an string at position pos, but test if valid before."""
        if not self.is_valid_color_object(mystr):
            raise ValueError, \
                        "String %s is not a valid color structure" % mystr
        else:
            list.insert(self, pos, mystr)

    def extend(self, col_string):
        """Extend with another color string, but test if valid before."""
        if not isinstance(col_string, ColorString):
            raise ValueError, \
                        "Object %s is not a valid color string" % col_string
        else:
            list.extend(self, col_string)

    def simplify(self):
        """Simplify the current color string as much as possible, using 
        all possible identities."""

        while True:
            original = copy.copy(self)

            self.__simplify_T_traces()
            self.__simplify_T_products()
            self.__simplify_simple_traces()
            self.__simplify_trace_cyclicity()
            self.__simplify_coeffs()
            if self == original:
                break

    def __simplify_T_traces(self):
        """Apply the identity T(a,b,c,...,i,i) = Tr(a,b,c,...)"""

        for index, col_obj in enumerate(self):
            self[index] = re_T_trace.sub(lambda m: "Tr(%s)" % m.group('start'),
                                     col_obj)

    def __simplify_T_products(self):
        """Apply the identity T(a,...,i,j)T(b,...,j,k) = T(a,...,b,...,i,k)
        on the first matching pair"""

        for index1, mystr1 in enumerate(self):
            for index2, mystr2 in enumerate(self[index1 + 1:]):
                # Test both product ordering
                m = re_T_product1.match(mystr1 + mystr2)
                if not m:
                    m = re_T_product2.match(mystr1 + mystr2)
                if m:
                    s1s2i1i2 = self.__clean_commas(','.join([m.group('start1'),
                                                             m.group('start2'),
                                                             m.group('id1'),
                                                             m.group('id2')]))
                    self[index1] = "T(%s)" % s1s2i1i2
                    del self[index1 + index2 + 1]
                    return

    def __simplify_simple_traces(self):
        """Apply the identities Tr(a)=0 (AS) and Tr() = Nc (delta)"""

        for index, col_obj in enumerate(self):
            if re_trace_0_index.match(col_obj):
                self[index] = "Nc"
            if re_trace_1_index.match(col_obj):
                self[index] = "0"

    def __simplify_trace_cyclicity(self):
        """Re-order traces using cyclicity to bring smallest id in front"""

        for index, col_obj in enumerate(self):
            m = re_trace_n_indices.match(col_obj)
            if m:
                list_indices = [int(s) for s in m.group('elems').split(',')]
                pos = list_indices.index(min(list_indices))
                res_list = list_indices[pos:]
                res_list.extend(list_indices[:pos])
                self[index] = 'Tr(%s)' % ','.join([str(i) for i in res_list])

    def __simplify_coeffs(self):
        """Applies simple algebraic simplifications on scalar coefficients
        and bring the final result to the first position"""

        # Simplify factors Nc
        numNc = self.count('Nc') - self.count('1/Nc')
        while ('Nc' in self): self.remove('Nc')
        while ('1/Nc' in self): self.remove('1/Nc')
        if numNc > 0:
            for dummy in range(numNc):
                self.insert(0, 'Nc')
        elif numNc < 0:
            for dummy in range(abs(numNc)):
                self.insert(0, '1/Nc')

        # Simplify factors I
        numI = self.count('I')
        while ('I' in self): self.remove('I')
        if numI % 4 == 1:
            self.insert(0, 'I')
        elif numI % 4 == 2:
            self.insert(0, '-1')
        elif numI % 4 == 3:
            self.insert(0, 'I')
            self.insert(0, '-1')

        # Compute numerators and denominators
        numlist = []
        denlist = []
        for elem in self[:]:
            m = re_fraction.match(elem)
            if m:
                self.remove(elem)
                numlist.append(int(m.group('num')))
                if m.group('den'):
                    denlist.append(int(m.group('den')))
        numerator = reduce(operator.mul, numlist, 1)
        denominator = reduce(operator.mul, denlist, 1)

        # Deal with 0 coeff
        if numerator == 0:
            del self[:]
            self.insert(0, '0')
            return

        # Try to simplify further fractions
        dev = self.__gcd(numerator, denominator)
        numerator //= dev
        denominator //= dev

        # Output result in a correct way
        if denominator != 1:
            self.insert(0, "%i/%i" % (numerator, denominator))
        elif numerator != 1:
            self.insert(0, "%i" % numerator)

    def __gcd(self, a, b):
        """Find the gcd of two integers"""
        while b: a, b = b, a % b
        return a

    def __expand_term(self, indices, new_str1, new_str2):
        """Return two color strings built on self where all indices in the
        list indices have been removed and, for the first index of the list, 
        replaced once by new_str1 and once bynew_str2."""

        str1 = copy.copy(self)
        str2 = copy.copy(self)

        # Remove indices, pay attention to the shift induced by del
        for i, index in enumerate(indices):
            del str1[index - i]
            del str2[index - i]

        # Insert new element at the position given by the first index
        for i, elem in enumerate(new_str1):
            str1.insert(indices[0] + i, elem)
        for i, elem in enumerate(new_str2):
            str2.insert(indices[0] + i, elem)

        return [str1, str2]


    def expand_composite_terms(self):
        """Expand the first encountered composite term like f,d,... 
        and returns the corresponding list of ColorString objects. 
        This method will NOT modify the current color string. If nothing
        to expand is found, returns an empty list."""

        for index, col_obj in enumerate(self):

            # Deal with d terms
            m = re_d_term.match(col_obj)
            if m:
                return self.__expand_term([index], ['2', 'Tr(%s,%s,%s)' % \
                                                      (m.group('a'),
                                                       m.group('b'),
                                                       m.group('c'))],
                                                 ['2', 'Tr(%s,%s,%s)' % \
                                                      (m.group('c'),
                                                       m.group('b'),
                                                       m.group('a'))])
            # Deal with f terms
            m = re_f_term.match(col_obj)
            if m:
                return self.__expand_term([index], ['-2', 'I',
                                                    'Tr(%s,%s,%s)' % \
                                                      (m.group('a'),
                                                       m.group('b'),
                                                       m.group('c'))],
                                                 ['2', 'I', 'Tr(%s,%s,%s)' % \
                                                      (m.group('c'),
                                                       m.group('b'),
                                                       m.group('a'))])

        return []

    def expand_T_internal_sum(self):
        """Expand the first encountered term with an internal sum in T's using
        T(a,x,b,x,c,i,j) = 1/2(T(a,c,i,j)Tr(b)-1/Nc T(a,b,c,i,j)) and 
        returns the corresponding list of ColorString objects. 
        This method will NOT modify the current color string. If nothing
        to expand is found, returns an empty list."""

        for index, col_obj in enumerate(self):

            m = re_T_int_sum.match(col_obj)
            if m:

                # Since we don't know exactly if the commas are consistently
                # written, we have to build and clean the index strings
                # before actually writing them
                # --> to be refactored ?
                b = self.__clean_commas(m.group('b'))
                aci1i2 = self.__clean_commas(','.join([m.group('a'),
                                                       m.group('c'),
                                                       m.group('id1'),
                                                       m.group('id2')]))
                abci1i2 = self.__clean_commas(','.join([m.group('a'),
                                                        m.group('b'),
                                                       m.group('c'),
                                                       m.group('id1'),
                                                       m.group('id2')]))
                return self.__expand_term([index], ['1/2',
                                                    'T(%s)' % aci1i2,
                                                    'Tr(%s)' % b],
                                                   ['-1/2',
                                                    '1/Nc',
                                                    'T(%s)' % abci1i2])
        return []

    def expand_trace_internal_sum(self):
        """Expand the first encountered term with an internal sum in a trace
        using Tr(a,x,b,x,c) = 1/2(T(a,c)Tr(b)-1/Nc T(a,b,c)) and 
        returns the corresponding list of ColorString objects. 
        This method will NOT modify the current color string. If nothing
        to expand is found, returns an empty list."""

        for index, col_obj in enumerate(self):

            m = re_trace_int_sum.match(col_obj)
            if m:

                b = self.__clean_commas(m.group('b'))
                ac = self.__clean_commas(','.join([m.group('a'),
                                                   m.group('c')]))
                abc = self.__clean_commas(','.join([m.group('a'),
                                                    m.group('b'),
                                                    m.group('c')]))
                return self.__expand_term([index], ['1/2', 'Tr(%s)' % ac,
                                                       'Tr(%s)' % b],
                                                 ['-1/2', '1/Nc',
                                                  'Tr(%s)' % abc])
        return []

    def expand_trace_product(self):
        """Expand the first encountered product of two traces with a summed
        indices using Tr(a,x,b)Tr(c,x,d) = 1/2(Tr(a,d,c,b)-1/Nc Tr(a,b)Tr(c,d))
        and returns the corresponding list of ColorString objects. 
        This method will NOT modify the current color string. If nothing
        to expand is found, returns an empty list."""

        for index1, mystr1 in enumerate(self):
            for index2, mystr2 in enumerate(self[index1 + 1:]):
                m = re_trace_product.match(mystr1 + mystr2)
                if m:
                    adcb = self.__clean_commas(','.join([m.group('a'),
                                                         m.group('d'),
                                                         m.group('c'),
                                                         m.group('b')]))
                    ab = self.__clean_commas(m.group('a') + ',' + m.group('b'))
                    cd = self.__clean_commas(m.group('c') + ',' + m.group('d'))
                    return self.__expand_term([index1, index1 + index2 + 1],
                                              ['1/2', 'Tr(%s)' % adcb],
                                              ['-1/2', '1/Nc',
                                                  'Tr(%s)' % ab,
                                                  'Tr(%s)' % cd])
        return []

    def expand_trace_T_product(self):
        """Expand the first encountered product of one trace and one T with 
        a summed indices using 
        Tr(a,x,b)T(c,x,d,i,j) = 1/2(T(c,b,a,d,i,j)-1/Nc Tr(a,b)T(c,d,i,j))
        and returns the corresponding list of ColorString objects. 
        This method will NOT modify the current color string. If nothing
        to expand is found, returns an empty list."""

        for index1, mystr1 in enumerate(self):
            for index2, mystr2 in enumerate(self[index1 + 1:]):
                m = re_trace_T_product1.match(mystr1 + mystr2)
                if not m:
                    m = re_trace_T_product2.match(mystr1 + mystr2)
                if m:
                    cbadi1i2 = self.__clean_commas(','.join([m.group('c'),
                                                           m.group('b'),
                                                           m.group('a'),
                                                           m.group('d'),
                                                           m.group('id1'),
                                                           m.group('id2')]))
                    ab = self.__clean_commas(','.join([m.group('a'),
                                                       m.group('b')]))
                    cdi1i2 = self.__clean_commas(','.join([m.group('c'),
                                                           m.group('d'),
                                                           m.group('id1'),
                                                           m.group('id2')]))
                    return self.__expand_term([index1, index1 + index2 + 1],
                                              ['1/2',
                                               'T(%s)' % cbadi1i2],
                                              ['-1/2', '1/Nc',
                                               'Tr(%s)' % ab,
                                               'T(%s)' % cdi1i2])
        return []

    def __clean_commas(self, string):
            """Return a string built on string where multiple commas
            and commas at the beginning/end have been removed.
            For example ,1,2,,,3,4,5, --> 1,2,3,4,5"""

            my_str = string.lstrip(',')
            my_str = my_str.rstrip(',')

            while True:
                cop_str = my_str
                my_str = my_str.replace(',,', ',')
                if cop_str == my_str:
                    break
            return my_str

    def extract_coeff(self):
        """Returns a tuple with first value being a color string with only
        numerical coefficients, and the second one a color string 
        with the rest"""

        # col_str = copy.copy(self)

        if self and re_fraction.match(self[0]):
            coeff_str = self[0]
            if len(self) > 1:
                col_str = ColorString(self[1:])
            else:
                col_str = ColorString()
            return (coeff_str, col_str)
        else:
            return ('1', self)


    def is_similar(self, col_str):
        """Test if self is similar to col_str, i.e. if they have the same
        tensorial structure (taking into account possible renaming of 
        summed indices, permutations, ...) and identical powers of Nc/I"""

        #col_str1 = copy.copy(self)
        #col_str2 = copy.copy(col_str)


        # Get rid of coefficients
        col_str1 = self.extract_coeff()[1]
        col_str2 = col_str.extract_coeff()[1]


        if col_str1 == ColorString() or col_str2 == ColorString():
            if col_str1 == ColorString() and col_str2 == ColorString():
                return True
            else:
                return False

        # test all permutations of str2
#        for str2_permut in itertools.permutations(col_str2):
#            if col_str1 == ColorString(list(str2_permut)):
#                return True
#        return False
        if col_str1 == col_str2:
            return True
        else:
            return False

    def add(self, col_str):
        """Add two color similar strings, i.e. returns a new color string with
        numerical coefficients added."""

        col_str1 = copy.copy(self)
        col_str2 = copy.copy(col_str)

        # Separate coefficients
        coeff1, col_str1 = col_str1.extract_coeff()
        coeff2, col_str2 = col_str2.extract_coeff()

        # Extract numerators and denominators
        match1 = re_fraction.match(coeff1)
        match2 = re_fraction.match(coeff2)

        num1 = int(match1.group('num'))
        num2 = int(match2.group('num'))

        if match1.group('den'):
            den1 = int(match1.group('den'))
        else:
            den1 = 1

        if match2.group('den'):
            den2 = int(match2.group('den'))
        else:
            den2 = 1

        # Simplify the fraction
        numerator = num1 * den2 + num2 * den1
        denominator = den1 * den2

        dev = self.__gcd(numerator, denominator)
        numerator //= dev
        denominator //= dev

        # Output the result with the correct format (1 is not output)
        out_str = ColorString()
        if denominator != 1:
            out_str.append("%i/%i" % (numerator, denominator))
        elif numerator != 1:
            out_str.append("%i" % numerator)
        out_str.extend(col_str1)

        return out_str


#===============================================================================
# ColorFactor
#===============================================================================
class ColorFactor(list):
    """A list of ColorString object used to store the final result of a given
    color factor calculation. Different elements are implicitly linked by a
    sum operator.
    """

    def __init__(self, init_list=None):
        """Creates a new ColorFactor object. If a list of ColorString
        is given, add them."""

        list.__init__(self)

        if init_list is not None:
            if isinstance(init_list, list):
                for object in init_list:
                    self.append(object)
            else:
                raise ValueError, \
                    "Object %s is not a valid list" % repr(init_list)

    def append(self, object):
        """Appends an ColorString, but test if valid before."""
        if not isinstance(object, ColorString):
            raise ValueError, \
                "Object %s is not a valid ColorString" % repr(object)
        else:
            list.append(self, object)

    def insert(self, pos, object):
        """Insert an ColorString at position pos, but test if valid before."""
        if not isinstance(object, ColorString):
            raise ValueError, \
                "Object %s is not a valid ColorString" % repr(object)
        else:
            list.insert(self, pos, object)

    def extend(self, col_factor):
        """Extend with another ColorFactor, but test if valid before."""
        if not isinstance(col_factor, ColorFactor):
            raise ValueError, \
                        "Object %s is not a valid ColorFactor" % col_factor
        else:
            list.extend(self, col_factor)

    def __collect(self):
        """Do a final simplification by grouping terms which are similars"""

        # Try all combinations
        for i1, col_str1 in enumerate(self[:]):
            for i2, col_str2 in enumerate(self[i1 + 1:]):
                if col_str1.is_similar(col_str2):
                    self[i1] = self[i1].add(col_str2)
                    self[i1 + i2 + 1] = ColorString(['0'])

        for elem in self:
            elem.simplify()

        while(ColorString(['0']) in self): self.remove(ColorString(['0']))

    def simplify(self):
        """Simplify the current ColorFactor. First apply simplification rules
        on all ColorStrings, then expand first composite terms and apply the
        golden rule. Iterate until the result does not change anymore"""

        while True:
            original = copy.copy(self)

            # Expand one f/d if possible
            for index, col_str in enumerate(self[:]):
                result = col_str.expand_composite_terms()
                if result:
                    self[index] = ColorString(['0'])
                    self.append(result[0])
                    self.append(result[1])

            # Apply rules
            for index, col_str in enumerate(self[:]):
                result = col_str.expand_T_internal_sum()
                if not result:
                    result = col_str.expand_trace_internal_sum()
                if not result:
                    result = col_str.expand_trace_product()
                if not result:
                    result = col_str.expand_trace_T_product()
                if result:
                    self[index] = ColorString(['0'])
                    self.append(result[0])
                    self.append(result[1])
            # Simplify
            for col_str in self:
                col_str.simplify()

            # Remove zeros
            while(ColorString(['0']) in self): self.remove(ColorString(['0']))

            self.__collect()

            # Iterate until the result does not change anymore
            if self == original:
                break


