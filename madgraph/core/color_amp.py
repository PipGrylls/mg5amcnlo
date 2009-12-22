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

import copy
import re

import madgraph.core.color_algebra as color_algebra

"""Classes, methods and functions required to write QCD color information 
for a diagram and build a color basis."""

class ColorBasis(dict):
    """The ColorBasis object is a dictionary created from an amplitude. Keys
    are the different color structures present in the amplitude. Values have
    the format (diag,(index c1, index c2,...), coeff, is_imaginary, Nc_power) 
    where diag is the diagram index, (index c1, index c2,...) the list of 
    indices corresponding to the chose color parts for each vertex in the 
    diagram, coeff the corresponding coefficient (a fraction), is_imaginary
    if this contribution is real or complex, and Nc_power the Nc power."""

    def colorize(self, diagram, model):
        """Takes a diagram and a model and outputs a dictionary with keys being
        color coefficient index tuples and values a color string (before 
        simplification)."""

        # The smallest value used to create new summed indices
        min_index = -1000
        # The dictionary to be output
        res_dict = {}
        # The dictionary for book keeping of replaced indices
        repl_dict = {}

        for vertex in diagram.get('vertices'):

        # SPECIAL VERTEX WITH ID = 0 -------------------------------------------
            if vertex['id'] == 0:

                # For vertex (i1,i2), replace all i2 by i1
                old_num = vertex.get('legs')[1].get('number')
                new_num = vertex.get('legs')[0].get('number')
                # Be careful i1 or i2 might have been replaced themselves
                if old_num in repl_dict.keys():
                    old_num = repl_dict[old_num]
                if new_num in repl_dict.keys():
                    new_num = repl_dict[new_num]
                # Do the replacement
                for (ind_chain, col_str_chain) in res_dict.items():
                    col_str_chain.replace_indices({old_num:new_num})
                # Return since this must be the last vertex
                return res_dict

        # NORMAL VERTICES WITH ID != 0 -----------------------------------------

            # Create a list of pdg codes entering the vertex ordered as in
            # interactions.py
            list_pdg = [part.get_pdg_code() for part in \
                   model.get_interaction(vertex.get('id')).get('particles')]

            # Create a dictionary pdg code --> leg(s)
            dict_pdg_leg = {}
            for index, leg in enumerate(vertex.get('legs')):
                curr_num = leg.get('number')
                curr_pdg = leg.get('id')
                # If this is the last leg and not the last vertex, 
                # flip part/antipart, and replace last index by a new 
                # summed index
                if index == len(vertex.get('legs')) - 1 and \
                    vertex != diagram.get('vertices')[-1]:
                    part = model.get('particle_dict')[curr_pdg]
                    curr_pdg = \
                        model.get('particle_dict')[curr_pdg].get_anti_pdg_code()
                    repl_dict[curr_num] = min_index
                    min_index = min_index - 1
                if curr_num in repl_dict.keys():
                    curr_num = repl_dict[curr_num]
                if curr_pdg in dict_pdg_leg.keys():
                    dict_pdg_leg[curr_pdg].append(curr_num)
                else:
                    dict_pdg_leg[curr_pdg] = [curr_num]

            # Create a list of associated leg number following the same order
            list_numbers = []
            for pdg_code in list_pdg:
                list_numbers.append(dict_pdg_leg[pdg_code].pop())
            # ... and the associated dictionary for replacement
            match_dict = dict(enumerate(list_numbers))

            # Update the result dict using the current vertex ColorString object
            # If more than one, create different entries
            new_res_dict = {}
            for i, col_str in \
                    enumerate(model.get_interaction(vertex['id'])['color']):
                # Build the new element
                mod_col_str = col_str.create_copy()

                # Replace summed (negative) internal indices
                list_neg = []
                for col_obj in mod_col_str:
                    list_neg.extend([ind for ind in col_obj if ind < 0])
                internal_indices_dict = {}
                # This notation is to remove duplicates
                for index in list(set(list_neg)):
                    internal_indices_dict[index] = min_index
                    min_index = min_index - 1
                mod_col_str.replace_indices(internal_indices_dict)

                # Replace other (positive) indices using the match_dic
                mod_col_str.replace_indices(match_dict)
                # If we are considering the first vertex, simply create
                # new entries
                if not res_dict:
                    new_res_dict[tuple([i])] = mod_col_str
                #... otherwise, loop over existing elements and multiply
                # the color strings
                else:
                    for ind_chain, col_str_chain in res_dict.items():
                        new_col_str_chain = col_str_chain.create_copy()
                        new_col_str_chain.product(mod_col_str)
                        new_res_dict[tuple(list(ind_chain) + [i])] = \
                            new_col_str_chain
            res_dict = new_res_dict

        # For diagrams with no id=0 vertex
        return res_dict

    def update_color_basis(self, colorize_dict, index):
        """Update the current color basis by adding information from 
        the colorize dictionary (produced by the colorize routine)
        associated to diagram with index index"""

        # loop over possible color chains
        for col_chain, col_str in colorize_dict.items():

            # Create and simplify a color factor for the conisdered chain
            col_fact = color_algebra.ColorFactor([col_str])
            col_fact = col_fact.full_simplify()

            # loop over color strings in the resulting color factor
            for col_str in col_fact:
                immutable_col_str = col_str.to_immutable()
                # if the color structure is already present in the present basis
                # update it
                basis_entry = (index,
                                col_chain,
                                col_str.coeff,
                                col_str.is_imaginary,
                                col_str.Nc_power)
                if immutable_col_str in self.keys():
                    self[immutable_col_str].append(basis_entry)
                else:
                    self[immutable_col_str] = [basis_entry]

    def build(self, amplitude, model):
        """Build the a color basis object using information contained in
        amplitude and model"""

        for index, diagram in enumerate(amplitude['diagrams']):
            colorize_dict = self.colorize(diagram, model)
            self.update_color_basis(colorize_dict, index)

    def __init__(self, *args):
        """Initialize a new color basis object, either empty or filled (0
        or 2 arguments). If two arguments are given, the first one is 
        interpreted as the amplitude and the second one as the model."""

        if len(args) not in (0, 2):
            raise ValueError, \
                "Object ColorBasis must be initialized with 0 or 2 arguments"

        if len(args) == 2:
            self.build(*args)

    def __str__(self):
        """Returns a nicely formatted string for display"""

        my_str = ""
        for k, v in self.items():
            for name, indices in k:
                my_str = my_str + name + str(indices)
            my_str = my_str + ': '
            for contrib in v:
                imag_str = ''
                if contrib[3]:
                    imag_str = 'I'
                my_str = my_str + '(diag:%i, chain:%s, coeff:%s%s, Nc:%i) ' % \
                                    (contrib[0], contrib[1], contrib[2],
                                     imag_str, contrib[3])
            my_str = my_str + '\n'
        return my_str


