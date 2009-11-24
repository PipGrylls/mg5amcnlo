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

"""Unit test library for the color related routines in the core library"""

import unittest

import madgraph.core.color as color

#===============================================================================
# ColorStringTest
#===============================================================================
class ColorStringTest(unittest.TestCase):
    """Test class for code parts related to ColorString objects"""

    def test_validity(self):
        """Test the color string validity check"""

        my_color_str = color.ColorString()

        valid_strings = ["T(101,102)",
                         "T(1,101,102)",
                         "T(1,2,3,4,101,102)",
                         "Tr()",
                         "Tr(1,2,3,4)",
                         "f(1,2,3)",
                         "d(1,2,3)",
                         "Nc", "1/Nc", "I",
                         "0", "1", "-1", "1/2", "-123/345"]

        for valid_str in valid_strings:
            self.assert_(my_color_str.is_valid_color_object(valid_str))

        wrong_strings = ["T(101,102",
                         "T 1,101,102)",
                         "T(1, 101, 102)",
                         "k(1,2,3)",
                         "d((1,2,3))",
                         "d(1,2,3,)",
                         "T(1.2)",
                         "-2/Nc",
                         'Tr(3,)']

        for wrong_str in wrong_strings:
            self.assertFalse(my_color_str.is_valid_color_object(wrong_str))

    def test_init(self):
        """Test the color string initialization"""

        wrong_lists = [['T(101,102)', 1],
                       ['T(101,102)', 'k(1,2,3)'],
                       'T(101,102)']

        for wrg_list in wrong_lists:
            self.assertRaises(ValueError,
                              color.ColorString,
                              wrg_list)

    def test_manip(self):
        """Test the color string manipulation (append, insert and extend)"""

        my_color_string = color.ColorString(['T(101,102)'])

        self.assertRaises(ValueError,
                          my_color_string.append,
                          'k(1,2,3)')
        self.assertRaises(ValueError,
                          my_color_string.insert,
                          0, 'k(1,2,3)')
        self.assertRaises(ValueError,
                          my_color_string.extend,
                          ['k(1,2,3)'])
    
    def test_T_traces(self):
        """Test identity T(a,b,c,...,i,i) = Tr(a,b,c,...)"""
        
        my_color_string = color.ColorString(['T(1,2,3,101,101)'])
        
        my_color_string.simplify()
        
        self.assertEqual(my_color_string,
                         color.ColorString(['Tr(1,2,3)']))
    
    def test_T_products(self):
        """Test identity T(a,...,i,j)T(b,...,j,k) = T(a,...,b,...,i,k)"""
        
        my_color_string = color.ColorString(['T(4,102,103)',
                                             'T(1,2,3,101,102)',
                                             'T(103,104)',
                                             'T(5,6,104,105)'])
        
        my_color_string.simplify()
        
        self.assertEqual(my_color_string,
                         color.ColorString(['T(1,2,3,4,5,6,101,105)']))
    
    def test_simple_traces(self):
        """Test identities Tr(1)=0, Tr()=Nc"""
        
        my_color_string = color.ColorString(['Tr(1)'])
        
        my_color_string.simplify()
        
        self.assertEqual(my_color_string,
                         color.ColorString(['0']))
        
        my_color_string = color.ColorString(['Tr()'])
        
        my_color_string.simplify()
        
        self.assertEqual(my_color_string,
                         color.ColorString(['Nc']))
    
    def test_trace_cyclicity(self):
        """Test trace cyclicity"""
        
        my_color_string = color.ColorString(['Tr(5,2,3,4,1)'])
        
        my_color_string.simplify()
        
        self.assertEqual(my_color_string,
                         color.ColorString(['Tr(1,5,2,3,4)']))
        
    def test_coeff_simplify(self):
        """Test color string coefficient simplification"""

        # Test Nc simplification
        my_color_string = color.ColorString(['Nc'] * 5 + \
                                            ['f(1,2,3)'] + \
                                            ['1/Nc'] * 3)

        my_color_string.simplify()

        self.assertEqual(my_color_string, color.ColorString(['Nc',
                                                             'Nc',
                                                             'f(1,2,3)']))

        # Test factors I simplification
        my_color_string = color.ColorString(['I'] * 4)
        my_color_string.simplify()
        self.assertEqual(my_color_string, color.ColorString([]))

        my_color_string = color.ColorString(['I'] * 5)
        my_color_string.simplify()
        self.assertEqual(my_color_string, color.ColorString(['I']))

        my_color_string = color.ColorString(['I'] * 6)
        my_color_string.simplify()
        self.assertEqual(my_color_string, color.ColorString(['-1']))

        my_color_string = color.ColorString(['I'] * 7)
        my_color_string.simplify()
        self.assertEqual(my_color_string, color.ColorString(['-1', 'I']))

        # Test numbers simplification
        my_color_string = color.ColorString(['-1/2', '2/3', '2', '-3'])
        my_color_string.simplify()
        self.assertEqual(my_color_string, color.ColorString(['2']))

        # Mix everything
        my_color_string = color.ColorString(['Nc', 'I', '-4', 'I', '1/Nc',
                                             'I', 'Nc', 'd(1,2,3)',
                                             '2/3', '-2/8'])
        my_color_string.simplify()
        self.assertEqual(my_color_string,
                         color.ColorString(['-2/3', 'I', 'Nc', 'd(1,2,3)']))

    def test_expand_composite(self):
        """Test color string expansion in the presence of terms like f, d, ...
        """

        my_color_string1 = color.ColorString(['T(1,2)',
                                              'd(3,4,-5)',
                                              'T(-5,6,7)'])

        my_color_string2 = color.ColorString(['T(1,2)',
                                              'f(3,4,5)',
                                              'T(5,6,7)'])

        self.assertEqual(my_color_string1.expand_composite_terms(),
                         [color.ColorString(['T(1,2)',
                                             '2',
                                             'Tr(3,4,-5)',
                                             'T(-5,6,7)']),
                          color.ColorString(['T(1,2)',
                                             '2',
                                             'Tr(-5,4,3)',
                                             'T(-5,6,7)'])])

        self.assertEqual(my_color_string2.expand_composite_terms(),
                         [color.ColorString(['T(1,2)',
                                             '-2', 'I',
                                             'Tr(3,4,5)',
                                             'T(5,6,7)']),
                          color.ColorString(['T(1,2)',
                                             '2', 'I',
                                             'Tr(5,4,3)',
                                             'T(5,6,7)'])])
    
    def test_expand_T_int_sum(self):
        """Test color string expansion for T(a,x,b,x,c,i,j)"""
        
        my_color_string = color.ColorString(['T(1,2)',
                                              'T(1,2,101,3,101,4,5,6,102,103)',
                                              'T(-5,6,7)'])
        
        self.assertEqual(my_color_string.expand_T_internal_sum(),
                        [color.ColorString(['T(1,2)',
                                             '1/2', 'T(1,2,4,5,6,102,103)',
                                             'Tr(3)',
                                             'T(-5,6,7)']),
                         color.ColorString(['T(1,2)',
                                             '-1/2', '1/Nc',
                                             'T(1,2,3,4,5,6,102,103)',
                                             'T(-5,6,7)'])])
        
        my_color_string = color.ColorString(['T(1,2)',
                                              'T(101,101,102,103)',
                                              'T(-5,6,7)'])
        
        self.assertEqual(my_color_string.expand_T_internal_sum(),
                        [color.ColorString(['T(1,2)',
                                             '1/2', 'T(102,103)',
                                             'Tr()',
                                             'T(-5,6,7)']),
                         color.ColorString(['T(1,2)',
                                             '-1/2', '1/Nc',
                                             'T(102,103)',
                                             'T(-5,6,7)'])])
    
    def test_expand_trace_int_sum(self):
        """Test color string expansion for Tr(a,x,b,x,c)"""
        
        my_color_string = color.ColorString(['T(1,2)',
                                              'Tr(1,2,101,3,101,4,5,6)',
                                              'T(-5,6,7)'])
        
        self.assertEqual(my_color_string.expand_trace_internal_sum(),
                        [color.ColorString(['T(1,2)',
                                             '1/2', 'Tr(1,2,4,5,6)',
                                             'Tr(3)',
                                             'T(-5,6,7)']),
                         color.ColorString(['T(1,2)',
                                             '-1/2', '1/Nc',
                                             'Tr(1,2,3,4,5,6)',
                                             'T(-5,6,7)'])])
        
        my_color_string = color.ColorString(['T(1,2)',
                                              'Tr(1,2,101,101)',
                                              'T(-5,6,7)'])
        
        self.assertEqual(my_color_string.expand_trace_internal_sum(),
                        [color.ColorString(['T(1,2)',
                                             '1/2', 'Tr(1,2)',
                                             'Tr()',
                                             'T(-5,6,7)']),
                         color.ColorString(['T(1,2)',
                                             '-1/2', '1/Nc',
                                             'Tr(1,2)',
                                             'T(-5,6,7)'])])
        

        
#
#    def test_traces_simplify(self):
#        """Test color string trace simplification"""
#
#        my_color_string1 = color.ColorString(['T(101,101)',
#                                             'T(102,103)',
#                                             'T(1,-101,-101)',
#                                             'T(2,104,105)'])
#
#        my_color_string2 = color.ColorString(['0'])
#
#        my_color_string1.simplify()
#
#        self.assertEqual(my_color_string1, my_color_string2)
#
#    def test_delta_simplify(self):
#        """Test color string delta simplification"""
#
#        my_color_string1 = color.ColorString(['T(101,-102)',
#                                              'f(1,2,3)',
#                                              'T(103,-102,104)', 'Nc'])
#
#        my_color_string2 = color.ColorString(['Nc', 'T(103,101,104)',
#                                              'f(1,2,3)'])
#
#        my_color_string1.simplify()
#
#        self.assertEqual(my_color_string1, my_color_string2)
#
#        my_color_string1 = color.ColorString(['T(101,102)',
#                                              'f(1,2,3)',
#                                              'T(103,104,101)'])
#
#        my_color_string2 = color.ColorString(['T(103,104,102)',
#                                              'f(1,2,3)'])
#
#        my_color_string1.simplify()
#
#        self.assertEqual(my_color_string1, my_color_string2)
#
#        my_color_string1 = color.ColorString(['T(-101,102)',
#                                              'f(1,2,3)',
#                                              'T(103,104,-101)',
#                                              'T(105,104)'])
#
#        my_color_string2 = color.ColorString(['T(103,105,102)',
#                                              'f(1,2,3)'])
#
#        my_color_string1.simplify()
#
#        self.assertEqual(my_color_string1, my_color_string2)
#
#    def test_coeff_simplify(self):
#        """Test color string coefficient simplification"""
#
#        # Test Nc simplification
#        my_color_string = color.ColorString(['Nc'] * 5 + \
#                                            ['f(1,2,3)'] + \
#                                            ['1/Nc'] * 3)
#
#        my_color_string.simplify()
#
#        self.assertEqual(my_color_string, color.ColorString(['Nc',
#                                                             'Nc',
#                                                             'f(1,2,3)']))
#
#        # Test factors I simplification
#        my_color_string = color.ColorString(['I'] * 4)
#        my_color_string.simplify()
#        self.assertEqual(my_color_string, color.ColorString([]))
#
#        my_color_string = color.ColorString(['I'] * 5)
#        my_color_string.simplify()
#        self.assertEqual(my_color_string, color.ColorString(['I']))
#
#        my_color_string = color.ColorString(['I'] * 6)
#        my_color_string.simplify()
#        self.assertEqual(my_color_string, color.ColorString(['-1']))
#
#        my_color_string = color.ColorString(['I'] * 7)
#        my_color_string.simplify()
#        self.assertEqual(my_color_string, color.ColorString(['-1', 'I']))
#
#        # Test numbers simplification
#        my_color_string = color.ColorString(['-1/2', '2/3', '2', '-3'])
#        my_color_string.simplify()
#        self.assertEqual(my_color_string, color.ColorString(['2']))
#
#        # Mix everything
#        my_color_string = color.ColorString(['Nc', 'I', '-4', 'I', '1/Nc',
#                                             'I', 'Nc', 'd(1,2,3)',
#                                             '2/3', '-2/8'])
#        my_color_string.simplify()
#        self.assertEqual(my_color_string,
#                         color.ColorString(['-2/3', 'I', 'Nc', 'd(1,2,3)']))
#
#    def test_expand_composite(self):
#        """Test color string expansion in the presence of terms like f, d, ...
#        """
#
#        my_color_string1 = color.ColorString(['T(1,2)',
#                                              'd(3,4,-5)',
#                                              'T(-5,6,7)'])
#
#        my_color_string2 = color.ColorString(['T(1,2)',
#                                              'f(3,4,5)',
#                                              'T(5,6,7)'])
#
#        self.assertEqual(my_color_string1.expand_composite_terms(),
#                         [color.ColorString(['T(1,2)',
#                                             '2',
#                                             'T(3,-6,-7)',
#                                             'T(4,-7,-8)',
#                                             'T(-5,-8,-6)',
#                                             'T(-5,6,7)']),
#                          color.ColorString(['T(1,2)',
#                                             '2',
#                                             'T(-5,-6,-7)',
#                                             'T(4,-7,-8)',
#                                             'T(3,-8,-6)',
#                                             'T(-5,6,7)'])])
#
#        self.assertEqual(my_color_string2.expand_composite_terms(-4),
#                         [color.ColorString(['T(1,2)',
#                                             '-2',
#                                             'I',
#                                             'T(3,-4,-5)',
#                                             'T(4,-5,-6)',
#                                             'T(5,-6,-4)',
#                                             'T(5,6,7)']),
#                          color.ColorString(['T(1,2)',
#                                             '2',
#                                             'I',
#                                             'T(5,-4,-5)',
#                                             'T(4,-5,-6)',
#                                             'T(3,-6,-4)',
#                                             'T(5,6,7)'])])
#
#    def test_golden_rule(self):
#        """Test color string golden rule implementation"""
#
#        my_color_string1 = color.ColorString(['T(1,2)',
#                                              'T(3,4,5)',
#                                              'd(6,-7,-8)',
#                                              'T(3,-7,-8)'])
#
#        self.assertEqual(my_color_string1.apply_golden_rule(),
#                         [color.ColorString(['T(1,2)',
#                                             '1/2',
#                                             'T(4,-8)',
#                                             'T(-7,5)',
#                                             'd(6,-7,-8)']),
#                          color.ColorString(['T(1,2)',
#                                             '-1/2',
#                                             '1/Nc',
#                                             'T(4,5)',
#                                             'T(-7,-8)',
#                                             'd(6,-7,-8)'])])
#
#    def test_is_similar(self):
#        """Test the similarity between two color strings"""
#
#        my_color_string1 = color.ColorString(['-2',
#                                              '1/Nc',
#                                              'T(1,2)',
#                                              'd(6,-7,-8)',
#                                              'T(3,-7,-8)',
#                                              'T(3,4,5)'])
#
#        my_color_string2 = color.ColorString(['-1/2',
#                                              '1/Nc',
#                                              'T(1,2)',
#                                              'T(-1,4,5)',
#                                              'd(6,-2,-3)',
#                                              'T(-1,-2,-3)'])
#
#        my_color_string3 = color.ColorString(['-1/2',
#                                              '1/Nc',
#                                              'T(1,2)',
#                                              'T(-1,4,5)',
#                                              'd(6,-3,-2)',
#                                              'T(-1,-2,-3)'])
#
#        self.assert_(my_color_string1.is_similar(my_color_string2))
#        self.assertFalse(my_color_string1.is_similar(my_color_string3))
#
#        my_color_string1 = color.ColorString(['-2',
#                                              'Nc'])
#
#        my_color_string2 = color.ColorString(['3',
#                                              'Nc'])
#
#        self.assert_(my_color_string1.is_similar(my_color_string2))
#
#    def test_add(self):
#        """Test the addition of two similar color strings"""
#
#        my_color_string1 = color.ColorString(['-4/6',
#                                              'Nc'])
#
#        my_color_string2 = color.ColorString(['8/3',
#                                              'Nc'])
#
#        my_color_string3 = color.ColorString(['2',
#                                              'Nc'])
#
#        my_color_string4 = color.ColorString(['-2',
#                                              'Nc'])
#
#        my_color_string5 = color.ColorString(['0',
#                                              'Nc'])
#
#        self.assertEqual(my_color_string1.add(my_color_string2),
#                         my_color_string3)
#
#        self.assertEqual(my_color_string3.add(my_color_string4),
#                         my_color_string5)
#
#
#
##===============================================================================
## ColorFactorTest
##===============================================================================
#class ColorFactorTest(unittest.TestCase):
#    """Test class for code parts related to ColorFactor objects"""
#
#    def test_colorfactor_init(self):
#        """Test the color factor initialization"""
#
#        wrong_lists = [1, ['T(101,102)', 'k(1,2,3)']]
#
#        for wrg_list in wrong_lists:
#            self.assertRaises(ValueError,
#                              color.ColorFactor,
#                              wrg_list)
#
#    def test_colorfactor_manip(self):
#        """Test the color factor manipulation (append, insert and extend)"""
#
#        my_color_factor = color.ColorFactor([color.ColorString(['T(101,102)'])])
#
#        self.assertRaises(ValueError,
#                          my_color_factor.append,
#                          1)
#        self.assertRaises(ValueError,
#                          my_color_factor.insert,
#                          0, 1)
#        self.assertRaises(ValueError,
#                          my_color_factor.extend,
#                          [1])
#
#    def test_simplify(self):
#        """Test the color factor simplify algorithm"""
#
#        my_color_factor = color.ColorFactor([color.ColorString(['f(1,2,3)',
#                                                                'f(1,2,3)'
#                                                                ])])
#
#        my_color_factor.simplify()
#        print my_color_factor

