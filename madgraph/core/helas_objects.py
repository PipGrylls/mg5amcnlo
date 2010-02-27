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

import array
import copy
import logging
import re
import itertools
import math

import madgraph.core.base_objects as base_objects
import madgraph.core.diagram_generation as diagram_generation
import madgraph.core.color_amp as color_amp
import madgraph.core.color_algebra as color

"""Definitions of objects used to generate Helas calls
(language-independent): HelasWavefunction, HelasAmplitude,
HelasDiagram for the generation of wavefunctions and amplitudes,
HelasMatrixElement and HelasMultiProcess for generation of complete
matrix elements for single and multiple processes; and HelasModel,
which is the language-independent base class for the language-specific
classes for writing Helas calls, found in the iolibs directory"""

#===============================================================================
# 
#===============================================================================

logger = logging.getLogger('helas_objects')

#===============================================================================
# HelasWavefunction
#===============================================================================
class HelasWavefunction(base_objects.PhysicsObject):
    """HelasWavefunction object, has the information necessary for
    writing a call to a HELAS wavefunction routine: the PDG number,
    all relevant particle information, a list of mother wavefunctions,
    interaction id, all relevant interaction information, fermion flow
    state, wavefunction number
    """

    def default_setup(self):
        """Default values for all properties"""

        # Properties related to the particle propagator
        # For an electron, would have the following values
        # pdg_code = 11
        # name = 'e-'
        # antiname = 'e+'
        # spin = '1'   defined as 2 x spin + 1  
        # color = '1'  1= singlet, 3 = triplet, 8=octet
        # mass = 'zero'
        # width = 'zero'
        # is_part = 'true'    Particle not antiparticle
        # self_antipart='false'   gluon, photo, h, or majorana would be true
        self['pdg_code'] = 0
        self['name'] = 'none'
        self['antiname'] = 'none'
        self['spin'] = 1
        self['color'] = 1
        self['mass'] = 'zero'
        self['width'] = 'zero'
        self['is_part'] = True
        self['self_antipart'] = False
        # Properties related to the interaction generating the propagator
        # For an e- produced from an e+e-A vertex would have the following
        # proporties:
        # interaction_id = the id of the interaction in the model
        # pdg_codes = the pdg_codes property of the interaction, [11, -11, 22]
        # inter_color = the 'color' property of the interaction: []
        # lorentz = the 'lorentz' property of the interaction: ['']
        # couplings = the coupling names from the interaction: {(0,0):'MGVX12'}
        self['interaction_id'] = 0
        self['pdg_codes'] = []
        self['inter_color'] = None
        self['lorentz'] = ''
        self['coupling'] = 'none'
        # The Lorentz and color index used in this wavefunction
        self['coupl_key'] = (0, 0)
        # Properties relating to the leg/vertex
        # state = initial/final (for external bosons),
        #         intermediate (for intermediate bosons),
        #         incoming/outgoing (for fermions)
        # number_external = the 'number' property of the corresponding Leg,
        #                   corresponds to the number of the first external
        #                   particle contributing to this leg
        # fermionflow = 1    fermions have +-1 for flow (bosons always +1),
        #                    -1 is used only if there is a fermion flow clash
        #                    due to a Majorana particle 
        self['state'] = 'incoming'
        self['mothers'] = HelasWavefunctionList()
        self['number_external'] = 0
        self['number'] = 0
        self['fermionflow'] = 1
        # The decay flag is used in processes with defined decay chains,
        # to indicate that this wavefunction has a decay defined
        self['decay'] = False

    # Customized constructor
    def __init__(self, *arguments):
        """Allow generating a HelasWavefunction from a Leg
        """

        if len(arguments) > 2:
            if isinstance(arguments[0], base_objects.Leg) and \
                   isinstance(arguments[1], int) and \
                   isinstance(arguments[2], base_objects.Model):
                super(HelasWavefunction, self).__init__()
                leg = arguments[0]
                interaction_id = arguments[1]
                model = arguments[2]
                # decay_ids is the pdg codes for particles with decay
                # chains defined
                decay_ids = []
                if len(arguments) > 3:
                    decay_ids = arguments[3]
                self.set('pdg_code', leg.get('id'), model)
                self.set('number_external', leg.get('number'))
                self.set('number', leg.get('number'))
                self.set('state', leg.get('state'))
                # Need to set 'decay' to True for particles which will be
                # decayed later, in order to not combine such processes
                # although they might have identical matrix elements before
                # the decay is applied
                if self['state'] == 'final' and self['pdg_code'] in decay_ids:
                    self.set('decay', True)

                # Set fermion flow state. Initial particle and final
                # antiparticle are incoming, and vice versa for
                # outgoing
                if self.is_fermion():
                    if leg.get('state') == 'initial' and \
                           self.get('is_part') or \
                           leg.get('state') == 'final' and \
                           not self.get('is_part'):
                        self.set('state', 'incoming')
                    else:
                        self.set('state', 'outgoing')
                self.set('interaction_id', interaction_id, model)
        elif arguments:
            super(HelasWavefunction, self).__init__(arguments[0])
        else:
            super(HelasWavefunction, self).__init__()

    def filter(self, name, value):
        """Filter for valid wavefunction property values."""

        if name == 'pdg_code':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                      "%s is not a valid pdg_code for wavefunction" % \
                      str(value)

        if name in ['name', 'antiname']:
            # Must start with a letter, followed by letters,  digits,
            # - and + only
            p = re.compile('\A[a-zA-Z]+[\w]*[\-\+]*~?\Z')
            if not p.match(value):
                raise self.PhysicsObjectError, \
                        "%s is not a valid particle name" % value

        if name is 'spin':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                    "Spin %s is not an integer" % repr(value)
            if value < 1 or value > 5:
                raise self.PhysicsObjectError, \
                   "Spin %i is smaller than one" % value

        if name is 'color':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                    "Color %s is not an integer" % repr(value)
            if value not in [1, 3, 6, 8]:
                raise self.PhysicsObjectError, \
                   "Color %i is not valid" % value

        if name in ['mass', 'width']:
            # Must start with a letter, followed by letters, digits or _
            p = re.compile('\A[a-zA-Z]+[\w\_]*\Z')
            if not p.match(value):
                raise self.PhysicsObjectError, \
                        "%s is not a valid name for mass/width variable" % \
                        value

        if name in ['is_part', 'self_antipart']:
            if not isinstance(value, bool):
                raise self.PhysicsObjectError, \
                    "%s tag %s is not a boolean" % (name, repr(value))

        if name == 'interaction_id':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer " % str(value) + \
                        " for wavefunction interaction id"

        if name == 'pdg_codes':
            #Should be a list of strings
            if not isinstance(value, list):
                raise self.PhysicsObjectError, \
                        "%s is not a valid list of integers" % str(value)
            for mystr in value:
                if not isinstance(mystr, int):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid integer" % str(mystr)

        if name == 'inter_color':
            # Should be None or a color string
            if value and not isinstance(value, color.ColorString):
                    raise self.PhysicsObjectError, \
                            "%s is not a valid Color String" % str(value)

        if name == 'lorentz':
            #Should be a string
            if not isinstance(value, str):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid string" % str(value)

        if name == 'coupling':
            #Should be a string
            if not isinstance(value, str):
                raise self.PhysicsObjectError, \
                        "%s is not a valid coupling string" % \
                                                                str(value)

        if name == 'coupl_key':
            if not isinstance(value, tuple):
                raise self.PhysicsObjectError, \
                      "%s is not a valid tuple" % str(value)
            if len(value) != 2:
                raise self.PhysicsObjectError, \
                      "%s is not a valid tuple with 2 elements" % str(value)
            if not isinstance(value[0], int) or not isinstance(value[1], int):
                raise self.PhysicsObjectError, \
                      "%s is not a valid tuple of integer" % str(value)

        if name == 'state':
            if not isinstance(value, str):
                raise self.PhysicsObjectError, \
                        "%s is not a valid string for wavefunction state" % \
                                                                    str(value)
            if value not in ['incoming', 'outgoing',
                             'intermediate', 'initial', 'final']:
                raise self.PhysicsObjectError, \
                        "%s is not a valid wavefunction " % str(value) + \
                        "state (incoming|outgoing|intermediate)"
        if name in ['fermionflow']:
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer" % str(value)
            if not value in [-1, 1]:
                raise self.PhysicsObjectError, \
                        "%s is not a valid sign (must be -1 or 1)" % str(value)

        if name in ['number_external', 'number']:
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer" % str(value) + \
                        " for wavefunction number"

        if name == 'mothers':
            if not isinstance(value, HelasWavefunctionList):
                raise self.PhysicsObjectError, \
                      "%s is not a valid list of mothers for wavefunction" % \
                      str(value)

        return True

    # Enhanced set function, where we can append a model

    def set(self, *arguments):
        """When setting interaction_id, if model is given (in tuple),
        set all other interaction properties. When setting pdg_code,
        if model is given, set all other particle properties."""

        if len(arguments) < 2:
            raise self.PhysicsObjectError, \
                  "Too few arguments for set"

        name = arguments[0]
        value = arguments[1]

        if len(arguments) > 2 and \
               isinstance(value, int) and \
               isinstance(arguments[2], base_objects.Model):
            model = arguments[2]
            if name == 'interaction_id':
                self.set('interaction_id', value)
                if value > 0:
                    inter = model.get('interaction_dict')[value]
                    self.set('pdg_codes',
                             [part.get_pdg_code() for part in \
                              inter.get('particles')])
                    # Note that the following values might change, if
                    # the relevant color/lorentz/coupling is not index 0
                    if inter.get('color'):
                        self.set('inter_color', inter.get('color')[0])
                    if inter.get('lorentz'):
                        self.set('lorentz', inter.get('lorentz')[0])
                    if inter.get('couplings'):
                        self.set('coupling', inter.get('couplings').values()[0])
                return True
            elif name == 'pdg_code':
                self.set('pdg_code', value)
                part = model.get('particle_dict')[value]
                self.set('name', part.get('name'))
                self.set('antiname', part.get('antiname'))
                self.set('spin', part.get('spin'))
                self.set('color', part.get('color'))
                self.set('mass', part.get('mass'))
                self.set('width', part.get('width'))
                self.set('is_part', part.get('is_part'))
                self.set('self_antipart', part.get('self_antipart'))
                return True
            else:
                raise self.PhysicsObjectError, \
                      "%s not allowed name for 3-argument set", name
        else:
            return super(HelasWavefunction, self).set(name, value)

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['pdg_code', 'name', 'antiname', 'spin', 'color',
                'mass', 'width', 'is_part', 'self_antipart',
                'interaction_id', 'pdg_codes', 'inter_color', 'lorentz',
                'coupling', 'coupl_key', 'state', 'number_external',
                'number', 'fermionflow', 'mothers']

    # Helper functions

    def is_fermion(self):
        return self.get('spin') % 2 == 0

    def is_boson(self):
        return not self.is_fermion()

    def to_array(self):
        """Generate an array with the information needed to uniquely
        determine if a wavefunction has been used before: interaction
        id and mother wavefunction numbers."""

        # Identification based on interaction id
        array_rep = array.array('i', [self['interaction_id']])
        # Need the coupling key, to distinguish between
        # wavefunctions from the same interaction but different
        # Lorentz or color structures
        array_rep.extend(list(self['coupl_key']))
        # Finally, the mother numbers
        array_rep.extend([mother.get('number') for \
                          mother in self['mothers']])
        return array_rep

    def get_pdg_code_outgoing(self):
        """Generate the corresponding pdg_code for an outgoing particle,
        taking into account fermion flow, for mother wavefunctions"""

        if self.get('self_antipart'):
            #This is its own antiparticle e.g. a gluon
            return self.get('pdg_code')

        if self.is_boson():
            # This is a boson
            return self.get('pdg_code')

        if (self.get('state') == 'incoming' and self.get('is_part') \
                or self.get('state') == 'outgoing' and not self.get('is_part')):
            return - self.get('pdg_code')
        else:
            return self.get('pdg_code')

    def get_pdg_code_incoming(self):
        """Generate the corresponding pdg_code for an incoming particle,
        taking into account fermion flow, for mother wavefunctions"""

        if self.get('self_antipart'):
            #This is its own antiparticle e.g. gluon
            return self.get('pdg_code')

        if self.is_boson():
            # This is a boson
            return - self.get('pdg_code')

        if (self.get('state') == 'outgoing' and self.get('is_part') \
                or self.get('state') == 'incoming' and not self.get('is_part')):
            return - self.get('pdg_code')
        else:
            return self.get('pdg_code')

    def set_scalar_coupling_sign(self, model):
        """Check if we need to add a minus sign due to non-identical
        bosons in HVS type couplings"""

        inter = model.get('interaction_dict')[self.get('interaction_id')]
        if [p.get('spin') for p in \
                   inter.get('particles')] == [3, 1, 1]:
            particles = inter.get('particles')
            #                   lambda p1, p2: p1.get('spin') - p2.get('spin'))
            if particles[1].get_pdg_code() != particles[2].get_pdg_code() \
                   and self.get('pdg_code') == \
                       particles[1].get_anti_pdg_code():
                # We need a minus sign in front of the coupling
                self.set('coupling', '-' + self.get('coupling'))


    def set_state_and_particle(self, model):
        """Set incoming/outgoing state according to mother states and
        Lorentz structure of the interaction, and set PDG code
        according to the particles in the interaction"""

        if not isinstance(model, base_objects.Model):
            raise self.PhysicsObjectError, \
                  "%s is not a valid model for call to set_state_and_particle" \
                  % repr(model)
        # Start by setting the state of the wavefunction
        if self.is_boson():
            # For boson, set state to intermediate
            self.set('state', 'intermediate')
        else:
            # For fermion, set state to same as other fermion (in the right way)
            mother_fermions = filter(lambda wf: wf.is_fermion(),
                                     self.get('mothers'))
            if len(mother_fermions) != 1:
                raise self.PhysicsObjectError, \
                      """Multifermion vertices not implemented.
                      Please decompose your vertex into 2-fermion
                      vertices to get fermion flow correct."""

            if len(filter(lambda wf: wf.get_with_flow('state') == 'incoming',
                          self.get('mothers'))) > \
                          len(filter(lambda wf: \
                                     wf.get_with_flow('state') == 'outgoing',
                          self.get('mothers'))):
                # If more incoming than outgoing mothers,
                # Pick one with incoming state as mother and set flow
                # Note that this needs to be done more properly if we have
                # 4-fermion vertices
                mother = filter(lambda wf: \
                                wf.get_with_flow('state') == 'incoming',
                                self.get('mothers'))[0]
            else:
                # If more outgoing than incoming mothers,
                # Pick one with outgoing state as mother and set flow
                # Note that this needs to be done more properly if we have
                # 4-fermion vertices
                mother = filter(lambda wf: \
                                wf.get_with_flow('state') == 'outgoing',
                                self.get('mothers'))[0]
            if not self.get('self_antipart'):
                self.set('state', mother.get('state'))
                self.set('fermionflow', mother.get('fermionflow'))
            else:
                self.set('state', mother.get_with_flow('state'))
                self.set('is_part', mother.get_with_flow('is_part'))

        # We want the particle created here to go into the next
        # vertex, so we need to flip identity for incoming
        # antiparticle and outgoing particle.
        if not self.get('self_antipart') and \
               (self.get('state') == 'incoming' and not self.get('is_part') \
                or self.get('state') == 'outgoing' and self.get('is_part')):
            self.set('pdg_code', -self.get('pdg_code'), model)

        return True

    def check_and_fix_fermion_flow(self,
                                   wavefunctions,
                                   diagram_wavefunctions,
                                   external_wavefunctions,
                                   wf_number):
        """Check for clashing fermion flow (N(incoming) !=
        N(outgoing)) in mothers. This can happen when there is a
        Majorana particle in the diagram, which can flip the fermion
        flow. This is detected either by a wavefunctions or an
        amplitude, with 2 fermion mothers with same state.

        In this case, we need to follow the fermion lines of the
        mother wavefunctions until we find the outermost Majorana
        fermion. For all fermions along the line up to (but not
        including) the Majorana fermion, we need to flip incoming <->
        outgoing and particle id. For all fermions after the Majorana
        fermion, we need to flip the fermionflow property (1 <-> -1).

        The reason for this is that in the Helas calls, we need to
        keep track of where the actual fermion flow clash happens
        (i.e., at the outermost Majorana), as well as having the
        correct fermion flow for all particles along the fermion line.

        This is done by the mothers using
        HelasWavefunctionList.check_and_fix_fermion_flow, which in
        turn calls the recursive function
        check_majorana_and_flip_flow to trace the fermion lines.
        """

        # Use the HelasWavefunctionList helper function
        # Have to keep track of wavefunction number, since we might
        # need to add new wavefunctions.
        wf_number = self.get('mothers').check_and_fix_fermion_flow(\
                                   wavefunctions,
                                   diagram_wavefunctions,
                                   external_wavefunctions,
                                   self.get_with_flow('state'),
                                   wf_number)
        return self, wf_number

    def check_majorana_and_flip_flow(self, found_majorana,
                                     wavefunctions,
                                     diagram_wavefunctions,
                                     external_wavefunctions,
                                     wf_number):
        """Recursive function. Check for Majorana fermion. If found,
        continue down to external leg, then flip all the fermion flows
        on the way back up, in the correct way:
        Only flip fermionflow after the last Majorana fermion; for
        wavefunctions before the last Majorana fermion, instead flip
        particle identities and state. Return the new (or old)
        wavefunction, and the present wavefunction number.
        """

        if not found_majorana:
            found_majorana = self.get('self_antipart')

        new_wf = self
        flip_flow = False
        flip_sign = False

        # Stop recursion at the external leg
        mothers = copy.copy(self.get('mothers'))
        if not mothers:
            if not self.get('self_antipart'):
                flip_flow = found_majorana
            else:
                flip_sign = found_majorana
        else:
            # Follow fermion flow up through tree
            fermion_mother = filter(lambda wf: wf.is_fermion() and
                                     wf.get_with_flow('state') == \
                                     self.get_with_flow('state'),
                                     mothers)

            if len(fermion_mother) > 1:
                raise self.PhysicsObjectError, \
                      "6-fermion vertices not yet implemented"
            if len(fermion_mother) == 0:
                raise self.PhysicsObjectError, \
                      "Previous unresolved fermion flow in mother chain"

            # Perform recursion by calling on mother
            new_mother, wf_number = fermion_mother[0].\
                                    check_majorana_and_flip_flow(\
                                         found_majorana,
                                         wavefunctions,
                                         diagram_wavefunctions,
                                         external_wavefunctions,
                                         wf_number)

            # If this is Majorana and mother has different fermion
            # flow, it means that we should from now on in the chain
            # flip the particle id and flow state.
            # Otherwise, if mother has different fermion flow, flip
            # flow
            flip_flow = new_mother.get('fermionflow') != \
                        self.get('fermionflow') and \
                        not self.get('self_antipart')
            flip_sign = new_mother.get('fermionflow') != \
                        self.get('fermionflow') and \
                        self.get('self_antipart') or \
                        new_mother.get('state') != self.get('state')

            # Replace old mother with new mother
            mothers[mothers.index(fermion_mother[0])] = new_mother

        # Flip sign if needed
        if flip_flow or flip_sign:
            if self in wavefunctions:
                # Need to create a new copy, since we don't want to change
                # the wavefunction for previous diagrams
                new_wf = copy.copy(self)
                # Update wavefunction number
                wf_number = wf_number + 1
                new_wf.set('number', wf_number)
                new_wf.set('mothers', mothers)
                diagram_wavefunctions.append(new_wf)

            # Now flip flow or sign
            if flip_flow:
                # Flip fermion flow
                new_wf.set('fermionflow', -new_wf.get('fermionflow'))

            if flip_sign:
                # Flip state and particle identity
                # (to keep particle identity * flow state)
                new_wf.set('state', filter(lambda state: \
                                           state != new_wf.get('state'),
                                           ['incoming', 'outgoing'])[0])
                new_wf.set('is_part', not new_wf.get('is_part'))
                if not new_wf.get('self_antipart'):
                    new_wf.set('pdg_code', -new_wf.get('pdg_code'))

            try:
                # Use the copy in wavefunctions instead.
                # Remove this copy from diagram_wavefunctions
                new_wf = wavefunctions[wavefunctions.index(new_wf)]
                diagram_wavefunctions.remove(new_wf)
                # Since we reuse the old wavefunction, reset wf_number
                wf_number = wf_number - 1
            except ValueError:
                pass

        # Return the new (or old) wavefunction, and the new
        # wavefunction number
        return new_wf, wf_number

    def get_fermion_order(self):
        """Recursive function to get a list of fermion numbers
        corresponding to the order of fermions along fermion lines
        connected to this wavefunction, in the form [n1,n2,...] for a
        boson, and [N,[n1,n2,...]] for a fermion line"""

        # End recursion if external wavefunction
        if not self.get('mothers'):
            if self.is_fermion():
                return [self.get('number_external'), []]
            else:
                return []

        # Pick out fermion mothers
        out_fermions = filter(lambda wf: wf.get_with_flow('state') == \
                              'outgoing', self.get('mothers'))
        in_fermions = filter(lambda wf: wf.get_with_flow('state') == \
                             'incoming', self.get('mothers'))
        # Pick out bosons
        bosons = filter(lambda wf: wf.is_boson(), self.get('mothers'))

        if self.is_boson() and len(in_fermions) + len(out_fermions) > 2\
               or self.is_fermion() and \
               len(in_fermions) + len(out_fermions) > 1:
            raise self.PhysicsObjectError, \
                  "Multifermion vertices not implemented"

        fermion_number_list = []

        for boson in bosons:
            # Bosons return a list [n1,n2,...]
            fermion_number_list.extend(boson.get_fermion_order())

        if self.is_fermion():
            # Fermions return the result N from their mother
            # and the list from bosons, so [N,[n1,n2,...]]
            fermion_mother = filter(lambda wf: wf.is_fermion(),
                                    self.get('mothers'))[0]
            mother_list = fermion_mother.get_fermion_order()
            fermion_number_list.extend(mother_list[1])
            return [mother_list[0], fermion_number_list]
        elif in_fermions and out_fermions:
            # Combine the incoming and outgoing fermion numbers
            # and add the bosonic numbers: [NI,NO,n1,n2,...]
            in_list = in_fermions[0].get_fermion_order()
            out_list = out_fermions[0].get_fermion_order()
            # Combine to get [N1,N2,n1,n2,...]
            fermion_number_list.append(in_list[0])
            fermion_number_list.append(out_list[0])
            fermion_number_list.extend(in_list[1])
            fermion_number_list.extend(out_list[1])
        elif len(in_fermions) != len(out_fermions):
            raise self.HelasWavefunctionError, \
                  "Error: %d incoming fermions != %d outgoing fermions" % \
                  (len(in_fermions), len(out_fermions))


        return fermion_number_list

    def needs_hermitian_conjugate(self):
        """Returns true if any of the mothers have negative
        fermionflow"""

        return any([wf.get('fermionflow') < 0 for wf in \
                    self.get('mothers')])

    def get_with_flow(self, name):
        """Generate the is_part and state needed for writing out
        wavefunctions, taking into account the fermion flow"""

        if self.get('fermionflow') > 0:
            # Just return (spin, state)
            return self.get(name)

        # If fermionflow is -1, need to flip particle identity and state
        if name == 'is_part':
            return not self.get('is_part')
        if name == 'state':
            return filter(lambda state: state != self.get('state'),
                          ['incoming', 'outgoing'])[0]
        return self.get(name)

    def get_spin_state_number(self):
        """Returns the number corresponding to the spin state, with a
        minus sign for incoming fermions"""

        state_number = {'incoming':-1, 'outgoing': 1,
                        'intermediate': 1, 'initial': 1, 'final': 1}
        return self.get('fermionflow') * \
               state_number[self.get('state')] * \
               self.get('spin')

    def get_call_key(self):
        """Generate the (spin, state) tuple used as key for the helas call
        dictionaries in HelasModel"""

        res = []
        for mother in self.get('mothers'):
            res.append(mother.get_spin_state_number())

        # Sort according to spin and flow direction
        res.sort()

        res.append(self.get_spin_state_number())

        # Check if we need to append a charge conjugation flag
        if self.needs_hermitian_conjugate():
            res.append('C')

        return (tuple(res), self.get('lorentz'))

    # Overloaded operators

    def __eq__(self, other):
        """Overloading the equality operator, to make comparison easy
        when checking if wavefunction is already written, or when
        checking for identical processes. Note that the number for
        this wavefunction, the pdg code, and the interaction id are
        irrelevant, while the numbers for the mothers are important.
        """

        if not isinstance(other, HelasWavefunction):
            return False

        # Check relevant directly defined properties
        if self['number_external'] != other['number_external'] or \
           self['spin'] != other['spin'] or \
           self['self_antipart'] != other['self_antipart'] or \
           self['fermionflow'] != other['fermionflow'] or \
           self['mass'] != other['mass'] or \
           self['width'] != other['width'] or \
           self['color'] != other['color'] or \
           self['lorentz'] != other['lorentz'] or \
           self['coupling'] != other['coupling'] or \
           self['state'] != other['state'] or \
           self['decay'] != other['decay'] or \
           self['decay'] and self['pdg_code'] != other['pdg_code']:
            return False

        # Check that mothers have the same numbers (only relevant info)
        return [ mother.get('number') for mother in self['mothers'] ] == \
               [ mother.get('number') for mother in other['mothers'] ]

    def __ne__(self, other):
        """Overloading the nonequality operator, to make comparison easy"""
        return not self.__eq__(other)

#===============================================================================
# HelasWavefunctionList
#===============================================================================
class HelasWavefunctionList(base_objects.PhysicsObjectList):
    """List of HelasWavefunction objects. This class has the routine
    check_and_fix_fermion_flow, which checks for fermion flow clashes
    among the mothers of an amplitude or wavefunction.
    """

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasWavefunction for the list."""

        return isinstance(obj, HelasWavefunction)

    # Helper functions

    def check_and_fix_fermion_flow(self,
                                   wavefunctions,
                                   diagram_wavefunctions,
                                   external_wavefunctions,
                                   my_state,
                                   wf_number):
        """Check for clashing fermion flow (N(incoming) !=
        N(outgoing)). If found, we need to trace back through the
        mother structure (only looking at fermions), until we find a
        Majorana fermion. Then flip fermion flow along this line all
        the way from the initial clash to the external fermion (in the
        right way, see check_majorana_and_flip_flow), and consider an
        incoming particle with fermionflow -1 as outgoing (and vice
        versa). Continue until we have N(incoming) = N(outgoing).
        
        Since the wavefunction number might get updated, return new
        wavefunction number.
        """

        # Clash is defined by whether the mothers have N(incoming) !=
        # N(outgoing) after this state has been subtracted
        mother_states = [ wf.get_with_flow('state') for wf in \
                          self ]
        try:
            mother_states.remove(my_state)
        except ValueError:
            pass

        Nincoming = len(filter(lambda state: state == 'incoming',
                               mother_states))
        Noutgoing = len(filter(lambda state: state == 'outgoing',
                               mother_states))

        if Nincoming == Noutgoing:
            return wf_number

        fermion_mothers = filter(lambda wf: wf.is_fermion(),
                                 self)
        if my_state in ['incoming', 'outgoing'] and len(fermion_mothers) > 1\
           or len(fermion_mothers) > 2:
            raise self.PhysicsObjectListError, \
                      """Multifermion vertices not implemented.
                      Please decompose your vertex into 2-fermion
                      vertices to get fermion flow correct."""

        for mother in fermion_mothers:
            if Nincoming > Noutgoing and \
               mother.get_with_flow('state') == 'outgoing' or \
               Nincoming < Noutgoing and \
               mother.get_with_flow('state') == 'incoming' or \
               Nincoming == Noutgoing:
                # This is not a problematic leg
                continue

            # Call recursive function to check for Majorana fermions
            # and flip fermionflow if found
            found_majorana = False

            new_mother, wf_number = mother.check_majorana_and_flip_flow(\
                                                found_majorana,
                                                wavefunctions,
                                                diagram_wavefunctions,
                                                external_wavefunctions,
                                                wf_number)
            # Replace old mother with new mother
            self[self.index(mother)] = new_mother

            # Update counters
            mother_states = [ wf.get_with_flow('state') for wf in \
                             self ]
            try:
                mother_states.remove(my_state)
            except ValueError:
                pass

            Nincoming = len(filter(lambda state: state == 'incoming',
                                       mother_states))
            Noutgoing = len(filter(lambda state: state == 'outgoing',
                                       mother_states))

        if Nincoming != Noutgoing:
            raise self.PhysicsObjectListError, \
                  "Failed to fix fermion flow, %d != %d" % \
                  (Nincoming, Noutgoing)

        return wf_number

#===============================================================================
# HelasAmplitude
#===============================================================================
class HelasAmplitude(base_objects.PhysicsObject):
    """HelasAmplitude object, has the information necessary for
    writing a call to a HELAS amplitude routine:a list of mother wavefunctions,
    interaction id, amplitude number
    """

    def default_setup(self):
        """Default values for all properties"""

        # Properties related to the interaction generating the propagator
        self['interaction_id'] = 0
        self['pdg_codes'] = []
        self['inter_color'] = None
        self['lorentz'] = ''
        self['coupling'] = 'none'
        # Properties relating to the vertex
        self['number'] = 0
        self['fermionfactor'] = 0
        self['color_indices'] = []
        self['mothers'] = HelasWavefunctionList()

    # Customized constructor
    def __init__(self, *arguments):
        """Allow generating a HelasAmplitude from a Vertex
        """

        if len(arguments) > 1:
            if isinstance(arguments[0], base_objects.Vertex) and \
               isinstance(arguments[1], base_objects.Model):
                super(HelasAmplitude, self).__init__()
                self.set('interaction_id',
                         arguments[0].get('id'), arguments[1])
        elif arguments:
            super(HelasAmplitude, self).__init__(arguments[0])
        else:
            super(HelasAmplitude, self).__init__()

    def filter(self, name, value):
        """Filter for valid property values."""

        if name == 'interaction_id':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for interaction id" % \
                        str(value)

        if name == 'pdg_codes':
            #Should be a list of integers
            if not isinstance(value, list):
                raise self.PhysicsObjectError, \
                        "%s is not a valid list of integers" % str(value)
            for mystr in value:
                if not isinstance(mystr, int):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid integer" % str(mystr)

        if name == 'inter_color':
            # Should be None or a color string
            if value and not isinstance(value, color.ColorString):
                    raise self.PhysicsObjectError, \
                            "%s is not a valid Color String" % str(value)

        if name == 'lorentz':
            #Should be a string
            if not isinstance(value, str):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid string" % str(value)

        if name == 'coupling':
            #Should be a string
            if not isinstance(value, str):
                raise self.PhysicsObjectError, \
                        "%s is not a valid coupling string" % \
                                                                str(value)

        if name == 'number':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for amplitude number" % \
                        str(value)

        if name == 'fermionfactor':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for fermionfactor" % \
                        str(value)
            if not value in [-1, 0, 1]:
                raise self.PhysicsObjectError, \
                        "%s is not a valid fermion factor (-1, 0 or 1)" % \
                        str(value)

        if name == 'color_indices':
            #Should be a list of integers
            if not isinstance(value, list):
                raise self.PhysicsObjectError, \
                        "%s is not a valid list of integers" % str(value)
            for mystr in value:
                if not isinstance(mystr, int):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid integer" % str(mystr)

        if name == 'mothers':
            if not isinstance(value, HelasWavefunctionList):
                raise self.PhysicsObjectError, \
                      "%s is not a valid list of mothers for amplitude" % \
                      str(value)

        return True

    # Enhanced get function
    def get(self, name):
        """Get the value of the property name."""

        if name == 'fermionfactor' and not self[name]:
            self.calculate_fermionfactor()

        return super(HelasAmplitude, self).get(name)

    # Enhanced set function, where we can append a model

    def set(self, *arguments):
        """When setting interaction_id, if model is given (in tuple),
        set all other interaction properties. When setting pdg_code,
        if model is given, set all other particle properties."""

        if len(arguments) < 2:
            raise self.PhysicsObjectError, \
                  "Too few arguments for set"

        name = arguments[0]
        value = arguments[1]

        if len(arguments) > 2 and \
               isinstance(value, int) and \
               isinstance(arguments[2], base_objects.Model):
            if name == 'interaction_id':
                self.set('interaction_id', value)
                if value > 0:
                    inter = arguments[2].get('interaction_dict')[value]
                    self.set('pdg_codes',
                             [part.get_pdg_code() for part in \
                              inter.get('particles')])
                    # Note that the following values might change, if
                    # the relevant color/lorentz/coupling is not index 0
                    if inter.get('color'):
                        self.set('inter_color', inter.get('color')[0])
                    if inter.get('lorentz'):
                        self.set('lorentz', inter.get('lorentz')[0])
                    if inter.get('couplings'):
                        self.set('coupling', inter.get('couplings').values()[0])
                return True
            else:
                raise self.PhysicsObjectError, \
                      "%s not allowed name for 3-argument set", name
        else:
            return super(HelasAmplitude, self).set(name, value)

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['interaction_id', 'pdg_codes', 'inter_color', 'lorentz',
                'coupling', 'number', 'color_indices', 'fermionfactor',
                'mothers']


    # Helper functions

    def check_and_fix_fermion_flow(self,
                                   wavefunctions,
                                   diagram_wavefunctions,
                                   external_wavefunctions,
                                   wf_number):
        """Check for clashing fermion flow (N(incoming) !=
        N(outgoing)) in mothers. For documentation, check
        HelasWavefunction.check_and_fix_fermion_flow.
        """

        return self.get('mothers').check_and_fix_fermion_flow(\
                                   wavefunctions,
                                   diagram_wavefunctions,
                                   external_wavefunctions,
                                   'nostate',
                                   wf_number)

    def needs_hermitian_conjugate(self):
        """Returns true if any of the mothers have negative
        fermionflow"""

        return any([wf.get('fermionflow') < 0 for wf in \
                    self.get('mothers')])

    def get_call_key(self):
        """Generate the (spin, state) tuples used as key for the helas call
        dictionaries in HelasModel"""

        res = []
        for mother in self.get('mothers'):
            res.append(mother.get_spin_state_number())

        # Sort according to spin and flow direction
        res.sort()

        # Check if we need to append a charge conjugation flag
        if self.needs_hermitian_conjugate():
            res.append('C')

        return (tuple(res), self.get('lorentz'))

    def calculate_fermionfactor(self):
        """Calculate the fermion factor for the diagram corresponding
        to this amplitude"""

        # Pick out fermion mothers
        out_fermions = filter(lambda wf: wf.get_with_flow('state') == \
                              'outgoing', self.get('mothers'))
        in_fermions = filter(lambda wf: wf.get_with_flow('state') == \
                             'incoming', self.get('mothers'))
        # Pick out bosons
        bosons = filter(lambda wf: wf.is_boson(), self.get('mothers'))

        if len(in_fermions) + len(out_fermions) > 2:
            raise self.PhysicsObjectError, \
                  "Multifermion vertices not implemented"

        fermion_number_list = []

        for boson in bosons:
            # Bosons return a list [n1,n2,...]
            fermion_number_list.extend(boson.get_fermion_order())

        if in_fermions and out_fermions:
            # Fermions return the result N from their mother
            # and the list from bosons, so [N,[n1,n2,...]]
            in_list = in_fermions[0].get_fermion_order()
            out_list = out_fermions[0].get_fermion_order()
            # Combine to get [N1,N2,n1,n2,...]
            fermion_number_list.append(in_list[0])
            fermion_number_list.append(out_list[0])
            fermion_number_list.extend(in_list[1])
            fermion_number_list.extend(out_list[1])
        elif len(in_fermions) != len(out_fermions):
            raise self.HelasWavefunctionError, \
                  "Error: %d incoming fermions != %d outgoing fermions" % \
                  (len(in_fermions), len(out_fermions))

        self['fermionfactor'] = self.sign_flips_to_order(fermion_number_list)

    def sign_flips_to_order(self, fermions):
        """Gives the sign corresponding to the number of flips needed
        to place the fermion numbers in order"""

        # Perform bubble sort on the fermions, and keep track of
        # the number of flips that are needed

        nflips = 0

        for i in range(len(fermions) - 1):
            for j in range(i + 1, len(fermions)):
                if fermions[j] < fermions[i]:
                    tmp = fermions[i]
                    fermions[i] = fermions[j]
                    fermions[j] = tmp
                    nflips = nflips + 1

        return (-1) ** nflips

    # Comparison between different amplitudes, to allow check for
    # identical processes. Note that we are then not interested in
    # interaction id, but in all other properties.
    def __eq__(self, other):
        """Comparison between different amplitudes, to allow check for
        identical processes.
        """

        if not isinstance(other, HelasAmplitude):
            return False

        # Check relevant directly defined properties
        if self['lorentz'] != other['lorentz'] or \
           self['coupling'] != other['coupling'] or \
           self['number'] != other['number']:
            return False

        # Check that mothers have the same numbers (only relevant info)
        return [ mother.get('number') for mother in self['mothers'] ] == \
               [ mother.get('number') for mother in other['mothers'] ]

    def __ne__(self, other):
        """Overloading the nonequality operator, to make comparison easy"""
        return not self.__eq__(other)

#===============================================================================
# HelasAmplitudeList
#===============================================================================
class HelasAmplitudeList(base_objects.PhysicsObjectList):
    """List of HelasAmplitude objects
    """

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasAmplitude for the list."""

        return isinstance(obj, HelasAmplitude)


#===============================================================================
# HelasDiagram
#===============================================================================
class HelasDiagram(base_objects.PhysicsObject):
    """HelasDiagram: list of HelasWavefunctions and a HelasAmplitude,
    plus the fermion factor associated with the corresponding diagram.
    """

    def default_setup(self):
        """Default values for all properties"""

        self['wavefunctions'] = HelasWavefunctionList()
        # One diagram can have several amplitudes, if there are
        # different Lorentz or color structures associated with this
        # diagram
        self['amplitudes'] = HelasAmplitudeList()

    def filter(self, name, value):
        """Filter for valid diagram property values."""

        if name == 'wavefunctions':
            if not isinstance(value, HelasWavefunctionList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasWavefunctionList object" % \
                        str(value)
        if name == 'amplitudes':
            if not isinstance(value, HelasAmplitudeList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasAmplitudeList object" % \
                        str(value)

        return True

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['wavefunctions', 'amplitudes']

#===============================================================================
# HelasDiagramList
#===============================================================================
class HelasDiagramList(base_objects.PhysicsObjectList):
    """List of HelasDiagram objects
    """

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasDiagram for the list."""

        return isinstance(obj, HelasDiagram)

#===============================================================================
# HelasMatrixElement
#===============================================================================
class HelasMatrixElement(base_objects.PhysicsObject):
    """HelasMatrixElement: list of processes with identical Helas
    calls, and the list of HelasDiagrams associated with the processes.

    If initiated with an Amplitude, HelasMatrixElement calls
    generate_helas_diagrams, which goes through the diagrams of the
    Amplitude and generates the corresponding Helas calls, taking into
    account possible fermion flow clashes due to Majorana
    particles. The optional optimization argument determines whether
    optimization is used (optimization = 1, default), for maximum
    recycling of wavefunctions, or no optimization (optimization = 0)
    when each diagram is written independently of all previous
    diagrams (this is useful for running with restricted memory,
    e.g. on a GPU). For processes with many diagrams, the total number
    or wavefunctions after optimization is ~15% of the number of
    amplitudes (diagrams).

    By default, it will also generate the color information (color
    basis and color matrix) corresponding to the Amplitude.
    """

    def default_setup(self):
        """Default values for all properties"""

        self['processes'] = base_objects.ProcessList()
        self['diagrams'] = HelasDiagramList()
        self['identical_particle_factor'] = 0
        self['color_basis'] = color_amp.ColorBasis()
        self['color_matrix'] = color_amp.ColorMatrix(color_amp.ColorBasis())

    def filter(self, name, value):
        """Filter for valid diagram property values."""

        if name == 'processes':
            if not isinstance(value, base_objects.ProcessList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid ProcessList object" % str(value)
        if name == 'diagrams':
            if not isinstance(value, HelasDiagramList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasDiagramList object" % str(value)
        if name == 'identical_particle_factor':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid int object" % str(value)
        if name == 'color_basis':
            if not isinstance(value, color_amp.ColorBasis):
                raise self.PhysicsObjectError, \
                        "%s is not a valid ColorBasis object" % str(value)
        if name == 'color_matrix':
            if not isinstance(value, color_amp.ColorMatrix):
                raise self.PhysicsObjectError, \
                        "%s is not a valid ColorMatrix object" % str(value)
        return True

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['processes', 'identical_particle_factor',
                'diagrams', 'color_basis', 'color_matrix']

    # Customized constructor
    def __init__(self, amplitude=None, optimization=1,
                 decay_ids = [], gen_color=True):
        """Constructor for the HelasMatrixElement. In particular allows
        generating a HelasMatrixElement from an Amplitude, with
        automatic generation of the necessary wavefunctions
        """

        if amplitude != None:
            if isinstance(amplitude, diagram_generation.Amplitude):
                super(HelasMatrixElement, self).__init__()
                self.get('processes').append(amplitude.get('process'))
                self.generate_helas_diagrams(amplitude, optimization, decay_ids)
                self.calculate_fermionfactors()
                self.calculate_identical_particle_factors()
                if gen_color:
                    self.get('color_basis').build(amplitude)
                    self.set('color_matrix',
                             color_amp.ColorMatrix(self.get('color_basis')))
            else:
                # In this case, try to use amplitude as a dictionary
                super(HelasMatrixElement, self).__init__(amplitude)
        else:
            super(HelasMatrixElement, self).__init__()

    # Comparison between different amplitudes, to allow check for
    # identical processes. Note that we are then not interested in
    # interaction id, but in all other properties.
    def __eq__(self, other):
        """Comparison between different matrix elements, to allow check for
        identical processes.
        """

        if not isinstance(other, HelasMatrixElement):
            return False

        # If no processes, this is an empty matrix element
        if not self['processes'] and not other['processes']:
            return True

        # Should only check if diagrams and process id are identical
        # Except in case of decay processes: then also initial state
        # must be the same
        if self['processes'] and not other['processes'] or \
               self['processes'] and \
               self['processes'][0]['id'] != other['processes'][0]['id'] or \
               self['processes'][0]['is_decay_chain'] or \
               other['processes'][0]['is_decay_chain'] or \
               self['identical_particle_factor'] != \
                           other['identical_particle_factor'] or \
               self['diagrams'] != other['diagrams']:
            return False

        return True

    def __ne__(self, other):
        """Overloading the nonequality operator, to make comparison easy"""
        return not self.__eq__(other)

    def generate_helas_diagrams(self, amplitude, optimization = 1,
                                decay_ids = []):
        """Starting from a list of Diagrams from the diagram
        generation, generate the corresponding HelasDiagrams, i.e.,
        the wave functions and amplitudes. Choose between default
        optimization (= 1, maximum recycling of wavefunctions) or no
        optimization (= 0, no recycling of wavefunctions, useful for
        GPU calculations with very restricted memory).

        Note that we need special treatment for decay chains, since
        the end product then is a wavefunction, not an amplitude.

        WARNING! For decay chains, we will need extra check for
        fermion flow clashes when the chains are sewn together! This
        can be done by making sure that the incoming/outgoing state
        corresponds between the wf in the core diagram and the wf in
        the decay chain.
        """

        if not isinstance(amplitude, diagram_generation.Amplitude) or \
               not isinstance(optimization, int):
            raise self.PhysicsObjectError, \
                  "Missing or erraneous arguments for generate_helas_diagrams"

        diagram_list = amplitude.get('diagrams')
        process = amplitude.get('process')

        model = process.get('model')
        if not diagram_list:
            return

        # All the previously defined wavefunctions
        wavefunctions = []
        # List of minimal information for comparison with previous
        # wavefunctions
        wf_mother_arrays = []
        # Keep track of wavefunction number
        wf_number = 0

        # Generate wavefunctions for the external particles
        external_wavefunctions = dict([(leg.get('number'),
                                        HelasWavefunction(leg, 0, model,
                                                          decay_ids)) \
                                       for leg in process.get('legs')])
               
        # Initially, have one wavefunction for each external leg.
        wf_number = len(process.get('legs'))

        # For initial state bosons, need to flip PDG code (if has antipart)
        # since all bosons should be treated as outgoing
        for key in external_wavefunctions.keys():
            wf = external_wavefunctions[key]
            if wf.is_boson() and wf.get('state') == 'initial' and \
               not wf.get('self_antipart'):
                wf.set('pdg_code', -wf.get('pdg_code'))
                wf.set('is_part', not wf.get('is_part'))

        # Now go through the diagrams, looking for undefined wavefunctions

        helas_diagrams = HelasDiagramList()

        # Keep track of amplitude number
        amplitude_number = 0

        for diagram in diagram_list:

            # List of dictionaries from leg number to wave function,
            # keeps track of the present position in the tree.
            # Need one dictionary per coupling multiplicity (diagram)
            number_to_wavefunctions = [{}]

            # Need to keep track of the color structures for each amplitude
            color_lists = [[]]

            # Initialize wavefunctions for this diagram
            diagram_wavefunctions = HelasWavefunctionList()

            vertices = copy.copy(diagram.get('vertices'))

            # Single out last vertex, since this will give amplitude
            lastvx = vertices.pop()

            # Check if last vertex is identity vertex
            if not process.get('is_decay_chain') and lastvx.get('id') == 0:
                # Need to "glue together" last and next-to-last
                # vertext, by replacing the (incoming) last leg of the
                # next-to-last vertex with the (outgoing) leg in the
                # last vertex
                nexttolastvertex = copy.deepcopy(vertices.pop())
                legs = nexttolastvertex.get('legs')
                ntlnumber = legs[-1].get('number')
                lastleg = filter(lambda leg: leg.get('number') != ntlnumber,
                                 lastvx.get('legs'))[0]
                # Replace the last leg of nexttolastvertex
                legs[-1] = lastleg
                lastvx = nexttolastvertex

            # Go through all vertices except the last and create
            # wavefunctions
            for vertex in vertices:

                # In case there are diagrams with multiple Lorentz/color 
                # structures, we need to keep track of the wavefunctions
                # for each such structure separately, and generate
                # one HelasDiagram for each structure.
                # We use the array number_to_wavefunctions to keep
                # track of this, with one dictionary per chain of
                # wavefunctions
                # Note that all wavefunctions relating to this diagram
                # will be written out before the first amplitude is written.
                new_number_to_wavefunctions = []
                new_color_lists = []
                for number_wf_dict, color_list in zip(number_to_wavefunctions,
                                                     color_lists):
                    legs = copy.copy(vertex.get('legs'))
                    last_leg = legs.pop()
                    # Generate list of mothers from legs
                    mothers = self.getmothers(legs, number_wf_dict,
                                              external_wavefunctions,
                                              wavefunctions,
                                              diagram_wavefunctions)
                    inter = model.get('interaction_dict')[vertex.get('id')]

                    # Now generate new wavefunction for the last leg

                    # Need one amplitude for each Lorentz/color structure,
                    # i.e. for each coupling
                    for coupl_key in inter.get('couplings').keys():
                        wf = HelasWavefunction(last_leg, vertex.get('id'), model)
                        wf.set('coupling', inter.get('couplings')[coupl_key])
                        # Special feature: For HVS vertices with the two
                        # scalars different, we need extra minus sign in front
                        # of coupling for one of the two scalars since the HVS
                        # is asymmetric in the two scalars
                        if wf.get('spin') == 1:
                            wf.set_scalar_coupling_sign(model)
                        if inter.get('color'):
                            wf.set('inter_color', inter.get('color')[coupl_key[0]])
                        wf.set('lorentz', inter.get('lorentz')[coupl_key[1]])
                        wf.set('coupl_key', coupl_key)
                        wf.set('mothers', mothers)
                        # Need to set incoming/outgoing and
                        # particle/antiparticle according to the fermion flow
                        # of mothers
                        wf.set_state_and_particle(model)
                        # Need to check for clashing fermion flow due to
                        # Majorana fermions, and modify if necessary
                        # Also need to keep track of the wavefunction number.
                        wf, wf_number = wf.check_and_fix_fermion_flow(\
                                                   wavefunctions,
                                                   diagram_wavefunctions,
                                                   external_wavefunctions,
                                                   wf_number)

                        # Create new copy of number_wf_dict
                        new_number_wf_dict = copy.copy(number_wf_dict)

                        # Store wavefunction
                        if not wf in diagram_wavefunctions:
                            # Update wf number
                            wf_number = wf_number + 1
                            wf.set('number', wf_number)
                            try:
                                # Use wf_mother_arrays to locate existing
                                # wavefunction
                                wf = wavefunctions[wf_mother_arrays.index(\
                                wf.to_array())]
                                # Since we reuse the old wavefunction, reset
                                # wf_number
                                wf_number = wf_number - 1
                            except ValueError:
                                diagram_wavefunctions.append(wf)

                            new_number_wf_dict[last_leg.get('number')] = wf

                        # Store the new copy of number_wf_dict
                        new_number_to_wavefunctions.append(\
                                                        new_number_wf_dict)
                        # Add color index and store new copy of color_lists
                        new_color_list = copy.copy(color_list)
                        new_color_list.append(coupl_key[0])
                        new_color_lists.append(new_color_list)

                number_to_wavefunctions = new_number_to_wavefunctions
                color_lists = new_color_lists

            # Generate all amplitudes corresponding to the different
            # copies of this diagram
            helas_diagram = HelasDiagram()
            for number_wf_dict, color_list in zip(number_to_wavefunctions,
                                                  color_lists):
                # Find mothers for the amplitude
                legs = lastvx.get('legs')
                mothers = self.getmothers(legs, number_wf_dict,
                                          external_wavefunctions,
                                          wavefunctions,
                                          diagram_wavefunctions)
                # Need to check for clashing fermion flow due to
                # Majorana fermions, and modify if necessary
                wf_number = mothers.check_and_fix_fermion_flow(wavefunctions,
                                              diagram_wavefunctions,
                                              external_wavefunctions,
                                              'nostate',
                                              wf_number)
                # Sort the wavefunctions according to number
                diagram_wavefunctions.sort(lambda wf1, wf2: \
                              wf1.get('number') - wf2.get('number'))

                # Now generate HelasAmplitudes from the last vertex.
                if lastvx.get('id'):
                    inter = model.get('interaction_dict')[lastvx.get('id')]
                    keys = inter.get('couplings').keys()
                else:
                    # Special case for decay chain - amplitude is just a
                    # placeholder for replaced wavefunction
                    inter = None
                    keys = [(0,0)]
                for i, coupl_key in enumerate(keys):
                    amp = HelasAmplitude(lastvx, model)
                    if inter:
                        amp.set('coupling', inter.get('couplings')[coupl_key])
                        amp.set('lorentz', inter.get('lorentz')[\
                                coupl_key[1]])
                        if inter.get('color'):
                            amp.set('inter_color', inter.get('color')[\
                                coupl_key[0]])
                    amp.set('mothers', mothers)
                    amplitude_number = amplitude_number + 1
                    amp.set('number', amplitude_number)
                    # Add the list with color indices to the amplitude
                    new_color_list = copy.copy(color_list)
                    if inter:
                        new_color_list.append(coupl_key[0])
                    amp.set('color_indices', new_color_list)
                    # Generate HelasDiagram

                    helas_diagram.get('amplitudes').append(amp)
                    if diagram_wavefunctions and not \
                                       helas_diagram.get('wavefunctions'):
                        helas_diagram.set('wavefunctions',
                                          diagram_wavefunctions)

                if optimization:
                    wavefunctions.extend(diagram_wavefunctions)
                    wf_mother_arrays.extend([wf.to_array() for wf \
                                             in diagram_wavefunctions])
                else:
                    wf_number = len(process.get('legs'))
            # Append this diagram in the diagram list
            helas_diagrams.append(helas_diagram)


        self.set('diagrams', helas_diagrams)

    def insert_decay_chains(self, decay_dict):
        """Insert the decay chains decays into this matrix element,
        using the recursive function insert_decay
        """
        
        # We need to keep track of how the
        # wavefunction numbers change
        replace_dict = dict([(number,number) for number in \
                             decay_dict.keys()])

        # Iteratively replace all legs that have decays
        for number in decay_dict.keys():
            
            self.insert_decay(number,
                              decay_dict[number],
                              replace_dict)
            
            # Calculate identical particle factors for
            # this matrix element
            self.identical_decay_chain_factor(decay_dict.values())

        
    def insert_decay(self, wf_number, decay, replace_dict):
        """Insert a decay chain wavefunction into the matrix element.
        Note that:
        1) All wavefunction numbers must be shifted
        2) All amplitudes and all wavefunctions using the decaying wf
           must be copied as many times as there are diagrams in the
           decay matrix element
        3) In the presence of Majorana particles, we must make sure
           to flip fermion flow for the decay process if needed.
        """
        
        decay_element = copy.deepcopy(decay)
        # Avoid Python copying the complete model
        # every time using deepcopy
        decay_element.get('processes')[0].set('model', \
                                decay.get('processes')[0].get('model'))
        
        # Insert the decay process in the process
        for process in self.get('processes'):
            process.get('decay_chains').append( \
                decay_element.get('processes')[0])

        # Pick out wavefunctions and amplitudes
        wavefunctions = sum([diagram.get('wavefunctions') for \
                             diagram in self['diagrams']],[])
        amplitudes = sum([diagram.get('amplitudes') for \
                          diagram in self['diagrams']],[])

        # Keep track of the numbers for the wavefunctions we will need
        # to replace later by simply keeping track of the
        # wavefunctions in question
        replace_wf_dict = dict([(number,
                            filter(lambda wf: wf.get('number') \
                                        == replace_dict[number],
                                        wavefunctions)[0]) for number in \
                                replace_dict.keys()])

        # Create a list of all the wavefunctions in the decay
        decay_wfs = sum([diagram.get('wavefunctions') for \
                         diagram in decay_element.get('diagrams')],[])
        # Remove the unwanted initial state wavefunction
        decay_wfs.remove(filter(lambda wf: \
                                wf.get('number_external') == 1,
                                decay_wfs)[0])
        
        # The wavefunctions which will replace the present wfs are
        # the second mother in the decay_chain amplitudes
        final_wfs = [amp.get('mothers')[1] for amp in \
                    sum([diagram.get('amplitudes') for \
                         diagram in decay_element.get('diagrams')],[])]

        # Find the external wfs to be replaced. There should only be
        # one, unless we have multiple fermion flows in the process
        replace_wfs = filter(lambda wf: not wf.get('mothers') and \
                             wf.get('number') == \
                             replace_dict[wf_number],
                             wavefunctions)
        
        for old_wf in replace_wfs:
            # We need to replace and multiply this wf, as well as all
            # wfs that have it as mother, and all their wfs, and
            # finally multiply all amplitudes

            diagrams = filter(lambda diag: old_wf.get('number') in \
                         [wf.get('number') for wf in diag.get('wavefunctions')],
                         self.get('diagrams'))

            new_wfs = copy.copy(decay_wfs)
            # NEED TO INCLUDE CHECK FOR FERMION FLOW DIRECTION HERE!

            # Pick out the final wavefunctions in the decay chain,
            # which are going to replace the existing final state
            # wavefunction old_wf
            new_final_wfs = filter(lambda wf: wf in final_wfs, new_wfs)

            # new_final_wfs will be inserted by replace_wavefunctions,
            # so remove from new_wfs
            for wf in new_final_wfs:
                new_wfs.remove(wf)

            # External wavefunction offset for new wfs
            incr_new = old_wf.get('number_external') - \
                       new_wfs[0].get('number_external')
            # External wavefunction offset for old wfs
            incr_old = \
                     len(decay_element.get('processes')[0].get('legs')) - 2
            # Renumber the new wavefunctions
            i = old_wf.get('number')
            for wf in new_wfs:
                wf.set('number', i)
                wf.set('number_external', wf.get('number_external') + incr_new)
                i = i + 1
            for wf in new_final_wfs:
                wf.set('number', i)
                wf.set('number_external',
                       wf.get('number_external') + incr_new)
                i = i + 1
            # Renumber the old wavefunctions above the replaced one
            i = i - len(new_final_wfs)
            for wf in wavefunctions[wavefunctions.index(old_wf):]:
                wf.set('number', i)
                # Increase external wavefunction number appropriately
                if wf.get('number_external') > old_wf.get('number_external'):
                    wf.set('number_external', wf.get('number_external') + \
                           incr_old)
                i = i + 1

            # Insert the new wavefunctions, excluding the final ones
            # (which are used to replace the existing final state wfs)
            # into wavefunctions and diagram
            wavefunctions = wavefunctions[0:wavefunctions.index(old_wf)] + \
                            new_wfs + wavefunctions[wavefunctions.index(old_wf):]
            for diagram in diagrams:
                diagram_wfs = diagram.get('wavefunctions')
                diagram_wfs = diagram_wfs[0:diagram_wfs.index(old_wf)] + \
                              new_wfs + diagram_wfs[diagram_wfs.index(old_wf):]
            
                diagram.set('wavefunctions', HelasWavefunctionList(diagram_wfs))
            
            # Multiply wavefunctions and insert mothers using a
            # recursive function
            self.replace_wavefunctions(old_wf,
                                       new_final_wfs,
                                       wavefunctions,
                                       amplitudes)

            # Update replace_dict
            for key in replace_dict.keys():
                replace_dict[key] = replace_wf_dict[key].get('number')


    def replace_wavefunctions(self, old_wf, new_wfs, wavefunctions, amplitudes):
        """Recursive function to replace old_wf with new_wfs, and multiply
        all wavefunctions or amplitudes that use old_wf."""

        # Update wavefunction numbers
        # Here we know that the wf number corresponds to the list order
        for wf in wavefunctions[old_wf.get('number'):]:
            wf.set('number', wf.get('number') + len(new_wfs) - 1)

        # Insert the new wavefunctions into wavefunctions and diagrams
        wavefunctions = wavefunctions[0:old_wf.get('number')-1] + \
                        new_wfs + wavefunctions[old_wf.get('number'):]

        # Pick out the diagrams which has the old_wf
        diagrams = filter(lambda diag: old_wf.get('number') in \
                         [wf.get('number') for wf in diag.get('wavefunctions')],
                         self.get('diagrams'))

        # Update diagram wavefunctions
        for diagram in diagrams:
            diagram_wfs = diagram.get('wavefunctions')
            diagram_wfs = diagram_wfs[:old_wf.get('number')-1] + \
                          new_wfs + diagram_wfs[old_wf.get('number'):]
            diagram.set('wavefunctions', HelasWavefunctionList(diagram_wfs))
        
        # Find amplitudes which are daughters of old_wf
        daughter_amps = filter(lambda amp: old_wf.get('number') in \
                                [wf.get('number') for wf in amp.get('mothers')],
                               amplitudes)
        # Create new copies, to insert the new wfs instead
        new_daughter_amps = [ [ amp ] * len(new_wfs) for amp in daughter_amps]
        new_daughter_amps = [ [ copy.copy(amp) for amp in amp_list] \
                              for amp_list in new_daughter_amps ]

        for old_amp, new_amps in zip(daughter_amps, new_daughter_amps):
            # Replace the old mother with the new ones
            for i, (daughter, new_wf) in enumerate(zip(new_amps, new_wfs)):
                mothers = copy.copy(daughter.get('mothers'))
                index = [wf.get('number') for wf in mothers].index(\
                    old_wf.get('number'))
                # Update mother
                mothers[index] = new_wf
                daughter.set('mothers', mothers)
                # Update amp numbers for replaced amp
                daughter.set('number', old_amp.get('number') + i)
                
            # Update amplitudes numbers for all other amplitudes
            for amp in amplitudes[amplitudes.index(old_amp) + 1:]:
                amp.set('number', amp.get('number') + len(new_wfs) - 1)

            # Insert the new amplitudes into amplitudes and diagrams
            amplitudes = amplitudes[0:amplitudes.index(old_amp)] + \
                         new_amps + amplitudes[amplitudes.index(old_amp) + 1:]

            # For now, keep old diagrams and just multiply the
            # amplitudes. This should be changed.
            diagrams = filter(lambda diag: old_amp in diag.get('amplitudes'),
                              self.get('diagrams'))
            for diagram in diagrams:
                diagram_amps = diagram.get('amplitudes')
                diagram_amps = diagram_amps[0:diagram_amps.index(old_amp)] + \
                              new_amps + diagram_amps[\
                                    diagram_amps.index(old_amp) + 1:]
                diagram.set('amplitudes', HelasAmplitudeList(diagram_amps))

        # Find wavefunctions that are daughters of old_wf
        daughter_wfs = filter(lambda wf: old_wf.get('number') in \
                              [wf1.get('number') for wf1 in wf.get('mothers')],
                              wavefunctions)
        
        # Create new copies, to insert the new wfs instead
        new_daughter_wfs = [ [ wf ] * len(new_wfs) for wf in daughter_wfs]
        new_daughter_wfs = [ [ copy.copy(wf) for wf in wf_list] \
                             for wf_list in new_daughter_wfs ]
        
        for daughter_ind, wfs in enumerate(new_daughter_wfs):
            # Replace the old mother with the new ones, update wf numbers
            for i, (daughter, new_wf) in enumerate(zip(wfs, new_wfs)):
                mothers = copy.copy(daughter.get('mothers'))
                index = [wf.get('number') for wf in mothers].index(\
                    old_wf.get('number'))
                mothers[index] = new_wf
                daughter.set('mothers', mothers)
                daughter.set('number', daughter.get('number') + i)
            # This is where recursion happens
            self.replace_wavefunctions(daughter_wfs[daughter_ind],
                                       wfs, wavefunctions, amplitudes)

    def identical_decay_chain_factor(self, decay_chains):
        """Calculate the denominator factor from identical decay chains"""

        final_legs = [leg.get('id') for leg in \
                      filter(lambda leg: leg.get('state') == 'final', \
                              self.get('processes')[0].get('legs'))]

        # Leg ids for legs being replaced by decay chains
        decay_ids = [decay.get('legs')[0].get('id') for decay in \
                     self.get('processes')[0].get('decay_chains')]

        # Find all leg ids which are not being replaced by decay chains
        non_decay_legs = filter(lambda id: id not in decay_ids,
                                final_legs)

        # Identical particle factor for legs not being decayed
        identical_indices = {}
        for id in non_decay_legs:
            if id in identical_indices:
                identical_indices[id] = \
                                    identical_indices[id] + 1
            else:
                identical_indices[id] = 1
        non_chain_factor = reduce(lambda x, y: x * y,
                                  [ math.factorial(val) for val in \
                                    identical_indices.values() ], 1)
        
        # Identical particle factor for decay chains
        # Go through chains to find identical ones
        chains = copy.copy(decay_chains)
        iden_chains_factor = 1
        while chains:
            ident_copies = 1
            first_chain = chains.pop(0)
            i = 0
            while i < len(chains):
                chain = chains[i]
                if HelasMatrixElement.check_equal_decay_processes(\
                                                 first_chain, chain):
                    ident_copies = ident_copies + 1
                    chains.pop(i)
                else:
                    i = i + 1
            iden_chains_factor = iden_chains_factor * \
                                 math.factorial(ident_copies)
        
        self['identical_particle_factor'] = non_chain_factor * \
                                    iden_chains_factor * \
                                    reduce(lambda x1, x2: x1 * x2,
                                    [me.get('identical_particle_factor') \
                                     for me in decay_chains], 1)
        
    def calculate_fermionfactors(self):
        """Generate the fermion factors for all diagrams in the amplitude
        """

        for diagram in self.get('diagrams'):
            for amplitude in diagram.get('amplitudes'):
                amplitude.get('fermionfactor')

    def calculate_identical_particle_factors(self):
        """Calculate the denominator factor for identical final state particles
        """

        final_legs = filter(lambda leg: leg.get('state') == 'final', \
                              self.get('processes')[0].get('legs'))

        identical_indices = {}
        for leg in final_legs:
            if leg.get('id') in identical_indices:
                identical_indices[leg.get('id')] = \
                                    identical_indices[leg.get('id')] + 1
            else:
                identical_indices[leg.get('id')] = 1
        self["identical_particle_factor"] = reduce(lambda x, y: x * y,
                                          [ math.factorial(val) for val in \
                                            identical_indices.values() ])

    # Helper methods

    def getmothers(self, legs, number_to_wavefunctions,
                   external_wavefunctions, wavefunctions,
                   diagram_wavefunctions):
        """Generate list of mothers from number_to_wavefunctions and
        external_wavefunctions"""

        mothers = HelasWavefunctionList()

        for leg in legs:
            try:
                # The mother is an existing wavefunction
                wf = number_to_wavefunctions[leg.get('number')]
            except KeyError:
                # This is an external leg, pick from external_wavefunctions
                wf = external_wavefunctions[leg.get('number')]
                number_to_wavefunctions[leg.get('number')] = wf
                if not wf in wavefunctions and not wf in diagram_wavefunctions:
                    diagram_wavefunctions.append(wf)
            mothers.append(wf)

        return mothers

    def get_number_of_wavefunctions(self):
        """Gives the total number of wavefunctions for this ME"""

        return sum([ len(d.get('wavefunctions')) for d in \
                       self.get('diagrams')])

    def get_number_of_amplitudes(self):
        """Gives the total number of amplitudes for this ME"""

        return sum([ len(d.get('amplitudes')) for d in \
                       self.get('diagrams')])

    def get_nexternal_ninitial(self):
        """Gives (number or external particles, number of
        incoming particles)"""

        return (len(self.get('processes')[0].get('legs')),
                self.get('processes')[0].get_ninitial())

    def get_helicity_combinations(self):
        """Gives the number of helicity combinations for external
        wavefunctions"""

        if not self.get('processes'):
            return None

        model = self.get('processes')[0].get('model')

        return reduce(lambda x, y: x * y,
                      [ len(model.get('particle_dict')[leg.get('id')].\
                            get_helicity_states())\
                        for leg in self.get('processes')[0].get('legs') ])

    def get_helicity_matrix(self):
        """Gives the helicity matrix for external wavefunctions"""

        if not self.get('processes'):
            return None

        process = self.get('processes')[0]
        model = process.get('model')

        return apply(itertools.product, [ model.get('particle_dict')[\
                                         leg.get('id')].get_helicity_states()\
                                         for leg in process.get('legs') ])

    def get_denominator_factor(self):
        """Calculate the denominator factor due to:
        Averaging initial state color and spin, and
        identical final state particles"""

        model = self.get('processes')[0].get('model')

        initial_legs = filter(lambda leg: leg.get('state') == 'initial', \
                              self.get('processes')[0].get('legs'))

        spin_factor = reduce(lambda x, y: x * y,
                             [ len(model.get('particle_dict')[leg.get('id')].\
                                   get_helicity_states())\
                               for leg in initial_legs ])

        color_factor = reduce(lambda x, y: x * y,
                              [ model.get('particle_dict')[leg.get('id')].\
                                    get('color')\
                                for leg in initial_legs ])

        return spin_factor * color_factor * self['identical_particle_factor']

    @staticmethod
    def check_equal_decay_processes(decay1, decay2):
        """Check if two single-sided decay processes
        (HelasMatrixElements) are equal.

        Note that this has to be called before any combination of
        processes has occured.
        
        Since a decay processes for a decay chain is always generated
        such that all final state legs are completely contracted
        before the initial state leg is included, all the diagrams
        will have identical wave function, independently of the order
        of final state particles.
        
        Note that we assume that the process definitions have all
        external particles, corresponding to the external
        wavefunctions.
        """

        if len(decay1.get('processes')) != 1 or \
           len(decay2.get('processes')) != 1:
            raise HelasMatrixElement.PhysicsObjectError, \
                  "Can compare only single process HelasMatrixElements"

        if len(filter(lambda leg: leg.get('state') == 'initial',\
                      decay1.get('processes')[0].get('legs'))) != 1 or \
           len(filter(lambda leg: leg.get('state') == 'initial',\
                      decay2.get('processes')[0].get('legs'))) != 1:
            raise HelasMatrixElement.PhysicsObjectError, \
                  "Call to check_decay_processes_equal requires " + \
                  "both processes to be unique"

        # Compare bulk process properties (number of external legs,
        # identity factors, number of diagrams, number of wavefunctions
        # initial leg, final state legs
        if len(decay1.get('processes')[0].get("legs")) != \
           len(decay1.get('processes')[0].get("legs")) or \
           len(decay1.get('diagrams')) != len(decay2.get('diagrams')) or \
           decay1.get('identical_particle_factor') != \
           decay2.get('identical_particle_factor') or \
           sum(len(d.get('wavefunctions')) for d in \
               decay1.get('diagrams')) != \
           sum(len(d.get('wavefunctions')) for d in \
               decay2.get('diagrams')) or \
           decay1.get('processes')[0].get('legs')[0].get('id') != \
           decay2.get('processes')[0].get('legs')[0].get('id') or \
           sorted([leg.get('id') for leg in \
                   decay1.get('processes')[0].get('legs')[1:]]) != \
           sorted([leg.get('id') for leg in \
                   decay2.get('processes')[0].get('legs')[1:]]):                   
            return False

        # Run a quick check to see if the processes are already
        # identical (i.e., the wavefunctions are in the same order)
        if [leg.get('id') for leg in \
            decay1.get('processes')[0].get('legs')] == \
           [leg.get('id') for leg in \
            decay2.get('processes')[0].get('legs')] and \
            decay1 == decay2:
            return True

        # Now check if all diagrams are identical. This is done by a
        # recursive function starting from the last wavefunction
        # (corresponding to the initial state), since it is the
        # same steps for each level in mother wavefunctions
        
        amplitudes2 = copy.copy(reduce(lambda a1, d2: a1 + \
                                       d2.get('amplitudes'),
                                       decay2.get('diagrams'), []))

        for amplitude1 in reduce(lambda a1, d2: a1 + d2.get('amplitudes'),
                                  decay1.get('diagrams'), []):
            foundamplitude = False
            for amplitude2 in amplitudes2:
                if HelasMatrixElement.check_equal_wavefunctions(\
                   amplitude1.get('mothers')[-1],
                   amplitude2.get('mothers')[-1]):
                    foundamplitude = True
                    # Remove amplitude2, since it has already been matched
                    amplitudes2.remove(amplitude2)
                    break
            if not foundamplitude:
                return False
        
        return True

    @staticmethod
    def check_equal_wavefunctions(wf1, wf2):
        """Recursive function to check if two wavefunctions are equal.
        First check that mothers have identical pdg codes, then repeat for
        all mothers with identical pdg codes."""

        # End recursion with False if the wavefunctions do not have
        # the same mother pdgs
        if sorted([wf.get('pdg_code') for wf in wf1.get('mothers')]) != \
           sorted([wf.get('pdg_code') for wf in wf2.get('mothers')]):
            return False

        # End recursion with True if these are external wavefunctions
        # (note that we have already checked that the pdgs are
        # identical)
        if not wf1.get('mothers') and not wf2.get('mothers'):
            return True

        mothers2 = copy.copy(wf2.get('mothers'))

        for mother1 in wf1.get('mothers'):
            # Compare mother1 with all mothers in wf2 that have not
            # yet been used and have identical pdg codes
            equalmothers = filter(lambda wf: wf.get('pdg_code') == \
                                  mother1.get('pdg_code'),
                                  mothers2)
            foundmother = False
            for mother2 in equalmothers:
                if HelasMatrixElement.check_equal_wavefunctions(\
                    mother1, mother2):
                    foundmother = True
                    # Remove mother2, since it has already been matched
                    mothers2.remove(mother2)
                    break
            if not foundmother:
                return False

        return True
    

#===============================================================================
# HelasMatrixElementList
#===============================================================================
class HelasMatrixElementList(base_objects.PhysicsObjectList):
    """List of HelasMatrixElement objects
    """

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasMatrixElement for the list."""

        return isinstance(obj, HelasMatrixElement)

#===============================================================================
# HelasDecayChainProcess
#===============================================================================
class HelasDecayChainProcess(base_objects.PhysicsObject):
    """HelasDecayChainProcess: If initiated with a
    DecayChainAmplitude object, generates the HelasMatrixElements for
    the core process(es) and decay chains"""

    def default_setup(self):
        """Default values for all properties"""

        self['core_processes'] = HelasMatrixElementList()
        self['decay_chains'] = HelasDecayChainProcessList()

    def filter(self, name, value):
        """Filter for valid process property values."""

        if name == 'core_processes':
            if not isinstance(value, HelasMatrixElementList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasMatrixElementList object" % \
                        str(value)

        if name == 'decay_chains':
            if not isinstance(value, HelasDecayChainProcessList):
                raise self.PhysicsObjectError, \
                     "%s is not a valid HelasDecayChainProcessList object" % \
                     str(value)

        return True

    def get_sorted_keys(self):
        """Return process property names as a nicely sorted list."""

        return ['core_processes', 'decay_chains']

    def __init__(self, argument=None):
        """Allow initialization with DecayChainAmplitude"""

        if isinstance(argument, diagram_generation.DecayChainAmplitude):
            super(HelasDecayChainProcess, self).__init__()
            self.generate_matrix_elements(argument)
        elif argument:
            # call the mother routine
            super(HelasDecayChainProcess, self).__init__(argument)
        else:
            # call the mother routine
            super(HelasDecayChainProcess, self).__init__()

    def generate_matrix_elements(self, dc_amplitude):
        """Generate the HelasMatrixElements for the core processes and
        decay processes (separately)"""

        if not isinstance(dc_amplitude, diagram_generation.DecayChainAmplitude):
            raise base_objects.PhysicsObjectError,\
                  "%s is not a valid DecayChainAmplitude" % dc_amplitude

        matrix_elements = self['core_processes']
        
        # Extract the pdg codes of all particles decayed by decay chains
        # since these should not be combined in a MultiProcess
        decay_ids = dc_amplitude.get_decay_ids()

        for amplitude in dc_amplitude.get('amplitudes'):
            logger.info("Generating Helas calls for %s" % \
                        amplitude.get('process').nice_string().\
                                            replace('Process', 'process'))
            matrix_element = HelasMatrixElement(amplitude,
                                                decay_ids=decay_ids,
                                                gen_color=False)

            try:
                # If an identical matrix element is already in the list,
                # then simply add this process to the list of
                # processes for that matrix element
                other_processes = matrix_elements[\
                    matrix_elements.index(matrix_element)].get('processes')
                logger.info("Combining process with %s" % \
                      other_processes[0].nice_string().replace('Process: ', ''))
                other_processes.append(amplitude.get('process'))
            except ValueError:
                # Otherwise, if the matrix element has any diagrams,
                # add this matrix element.
                if matrix_element.get('processes') and \
                       matrix_element.get('diagrams'):
                    matrix_elements.append(matrix_element)

        for decay_chain in dc_amplitude.get('decay_chains'):
            self['decay_chains'].append(HelasDecayChainProcess(\
                decay_chain))

    def combine_decay_chain_processes(self):
        """Recursive function to generate complete
        HelasMatrixElements, combining the core process with the decay
        chains. If there are several identical final state particles
        and only one decay chain defined, apply this decay chain to
        all copies. If there are several decay chains defined for the
        same particle, apply them in order of the FS particles and the
        defined decay chains."""

        # End recursion when there are no more decay chains
        if not self['decay_chains']:
            # Just return the list of matrix elements
            return self['core_processes']

        # This is where recursion happens

        # decay_elements is a list of HelasMatrixElementLists with
        # all decay processes
        decay_elements = []
        
        for decay_chain in self['decay_chains']:
            # This is where recursion happens
            decay_elements.append(decay_chain.combine_decay_chain_processes())

        # Store the result in matrix_elements
        matrix_elements = HelasMatrixElementList()

        # List of list of ids for the initial state legs in all decay
        # processes
        decay_is_ids = [[element.get('processes')[0].get_initial_ids()[0] \
                         for element in elements]
                         for elements in decay_elements]

        for core_process in self['core_processes']:
            # Get all final state legs
            fs_legs = core_process.get('processes')[0].get_final_legs()
            fs_ids = [leg.get('id') for leg in fs_legs]
            decay_lists = []
            # Loop over unique final state particle ids
            for fs_id in set(fs_ids):
                # Check if the particle id for this leg has a decay
                # chain defined
                if not any([any([id == fs_id for id \
                            in is_ids]) for is_ids in decay_is_ids]):
                    continue
                # decay_list has the leg numbers and decays for this
                # fs particle id
                decay_list = []
                # Now check if the number of decay chains with
                # this particle id is the same as the number of
                # identical particles in the core process - if so,
                # use one chain for each of the identical
                # particles. Otherwise, use all combinations of
                # decay chains for the particles.

                # Indices for the decay chain lists which contain at
                # least one decay for this final state
                chain_indices = filter(lambda index: fs_id in \
                                                   decay_is_ids[index],
                                       range(len(decay_is_ids)))

                my_fs_legs = filter(lambda leg: leg.get('id') == fs_id,
                                    fs_legs)
                leg_numbers = [leg.get('number') for leg in my_fs_legs]

                if len(leg_numbers) > 1 and \
                       len(leg_numbers) == len(chain_indices):

                    # The decay of the different fs parts is given
                    # by the different decay chains, respectively
                    # Chains is a list of matrix element lists
                    chains = []
                    for index in chain_indices:
                        decay_chains = decay_elements[index]
                        chains.append(filter(lambda me: \
                                             me.get('processes')[0].\
                                             get_initial_ids()[0] == fs_id,
                                             decay_chains))

                    # Combine decays for this final state type
                    for element in itertools.product(*chains):
                        decay_list.append([[n, d] for [n, d] in \
                                           zip(leg_numbers, element)])

                else:
                    # We let the particles decay according to the
                    # first decay list only
                    proc_index = chain_indices[0]

                    # Generate all combinations of decay chains with
                    # the given decays, without double counting
                    decay_indices = filter(lambda index: fs_id == \
                                           decay_is_ids[proc_index][index],
                                       range(len(decay_is_ids[proc_index])))
                    

                    red_decay_ids = []
                    decay_ids = [decay_indices] * len(leg_numbers)
                    # Combine all decays for this final state type,
                    # without double counting
                    for prod in itertools.product(*decay_ids):
                        
                        # Remove double counting between final states
                        if tuple(sorted(prod)) in red_decay_ids:
                            continue

                        # Specify decay processes in the matrix element process
                        red_decay_ids.append(tuple(sorted(prod)));

                        # Pick out the decays for this iteration
                        decays = [decay_elements[proc_index][chain_index] \
                                  for chain_index in prod]

                        decay_list.append([[n, d] for [n, d] in \
                                           zip(leg_numbers, decays)])

                decay_lists.append(decay_list)

            # Finally combine all decays for this process,
            # and combine them, decay by decay
            for decays in itertools.product(*decay_lists):

                # Generate a dictionary from leg number to decay process
                decay_dict = dict(sum(decays, []))

                # Make sure to not modify the original matrix element
                matrix_element = copy.deepcopy(core_process)
                # Avoid Python copying the complete model
                # every time using deepcopy
                matrix_element.get('processes')[0].set('model', \
                                core_process.get('processes')[0].get('model'))

                # Insert the decay chains
                matrix_element.insert_decay_chains(decay_dict)

                try:
                    # If an identical matrix element is already in the list,
                    # then simply add this process to the list of
                    # processes for that matrix element
                    other_processes = matrix_elements[\
                    matrix_elements.index(matrix_element)].get('processes')
                    logger.info("Combining process with %s" % \
                      other_processes[0].nice_string().replace('Process: ', ''))
                    other_processes.extend(matrix_element.get('processes'))
                except ValueError:
                    # Otherwise, if the matrix element has any diagrams,
                    # add this matrix element.
                    if matrix_element.get('processes') and \
                           matrix_element.get('diagrams'):
                        matrix_elements.append(matrix_element)
                        
        return matrix_elements

#===============================================================================
# HelasDecayChainProcessList
#===============================================================================
class HelasDecayChainProcessList(base_objects.PhysicsObjectList):
    """List of HelasDecayChainProcess objects
    """

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasDecayChainProcess for the list."""

        return isinstance(obj, HelasDecayChainProcess)

#===============================================================================
# HelasMultiProcess
#===============================================================================
class HelasMultiProcess(base_objects.PhysicsObject):
    """HelasMultiProcess: If initiated with an AmplitudeList,
    generates the HelasMatrixElements for the Amplitudes, identifying
    processes with identical matrix elements"""

    def default_setup(self):
        """Default values for all properties"""

        self['matrix_elements'] = HelasMatrixElementList()

    def filter(self, name, value):
        """Filter for valid process property values."""

        if name == 'matrix_elements':
            if not isinstance(value, HelasMatrixElementList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasMatrixElementList object" % str(value)

        return True

    def get_sorted_keys(self):
        """Return process property names as a nicely sorted list."""

        return ['matrix_elements']

    def __init__(self, argument=None):
        """Allow initialization with AmplitudeList"""

        if isinstance(argument, diagram_generation.AmplitudeList):
            super(HelasMultiProcess, self).__init__()
            self.generate_matrix_elements(argument)
        elif isinstance(argument, diagram_generation.MultiProcess):
            super(HelasMultiProcess, self).__init__()
            self.generate_matrix_elements(argument.get('amplitudes'))
        elif argument:
            # call the mother routine
            super(HelasMultiProcess, self).__init__(argument)
        else:
            # call the mother routine
            super(HelasMultiProcess, self).__init__()

    def generate_matrix_elements(self, amplitudes):
        """Generate the HelasMatrixElements for the Amplitudes,
        identifying processes with identical matrix elements, as
        defined by HelasMatrixElement.__eq__"""

        if not isinstance(amplitudes, diagram_generation.AmplitudeList):
            raise self.PhysicsObjectError, \
                  "%s is not valid AmplitudeList" % repr(amplitudes)

        # Keep track of already generated color objects, to reuse as
        # much as possible
        list_colorize = []
        list_color_basis = []
        list_color_matrices = []

        matrix_elements = self.get('matrix_elements')

        for amplitude in amplitudes:
            logger.info("Generating Helas calls for %s" % \
                         amplitude.get('process').nice_string().replace('Process', 'process'))
            if isinstance(amplitude, diagram_generation.DecayChainAmplitude):
                matrix_element_list = HelasDecayChainProcess(amplitude,
                                                             gen_color=False)
            else:
                matrix_element_list = [HelasMatrixElement(amplitude,
                                                          gen_color=False)]
            for matrix_element in matrix_element_list:
                try:
                    # If an identical matrix element is already in the list,
                    # then simply add this process to the list of
                    # processes for that matrix element
                    other_processes = matrix_elements[\
                    matrix_elements.index(matrix_element)].get('processes')
                    logger.info("Combining process with %s" % \
                      other_processes[0].nice_string().replace('Process: ', ''))
                    other_processes.extend(matrix_element.get('processes'))
                except ValueError:
                    # Otherwise, if the matrix element has any diagrams,
                    # add this matrix element.
                    if matrix_element.get('processes') and \
                           matrix_element.get('diagrams'):
                        matrix_elements.append(matrix_element)
                        
                    # Always create an empty color basis, and the list of raw
                    # colorize objects (before simplification) associated with amplitude
                    col_basis = color_amp.ColorBasis()
                    colorize_obj = col_basis.create_color_dict_list(amplitude)

                    try:
                        # If the color configuration of the ME has already been 
                        # considered before, recycle the information
                        col_index = list_colorize.index(colorize_obj)
                        logger.info(\
                        "Reusing existing color information for %s" % \
                        amplitude.get('process').nice_string().replace('Process',
                                                                       'process'))
                    except ValueError:
                        # If not, create color basis and color matrix accordingly
                        list_colorize.append(colorize_obj)
                        col_basis.build()
                        list_color_basis.append(col_basis)
                        col_matrix = color_amp.ColorMatrix(col_basis)
                        list_color_matrices.append(col_matrix)
                        col_index = -1
                        logger.info(\
                        "Processing color information for %s" % \
                        amplitude.get('process').nice_string().replace('Process',
                                                                       'process'))

                matrix_element.set('color_basis', list_color_basis[col_index])
                matrix_element.set('color_matrix', list_color_matrices[col_index])

#===============================================================================
# HelasModel
#===============================================================================
class HelasModel(base_objects.PhysicsObject):
    """Language independent base class for writing Helas calls. The
    calls are stored in two dictionaries, wavefunctions and
    amplitudes, with entries being a mapping from a set of spin,
    incoming/outgoing states and Lorentz structure to a function which
    writes the corresponding wavefunction/amplitude call (taking a
    HelasWavefunction/HelasAmplitude as argument)."""

    def default_setup(self):

        self['name'] = ""
        self['wavefunctions'] = {}
        self['amplitudes'] = {}

    def filter(self, name, value):
        """Filter for model property values"""

        if name == 'name':
            if not isinstance(value, str):
                raise self.PhysicsObjectError, \
                    "Object of type %s is not a string" % \
                                                            type(value)

        if name == 'wavefunctions':
            # Should be a dictionary of functions returning strings, 
            # with keys (spins, flow state)
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                        "%s is not a valid dictionary for wavefunction" % \
                                                                str(value)

            for key in value.keys():
                self.add_wavefunction(key, value[key])

        if name == 'amplitudes':
            # Should be a dictionary of functions returning strings, 
            # with keys (spins, flow state)
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                        "%s is not a valid dictionary for amplitude" % \
                                                                str(value)

            for key in value.keys():
                self.add_amplitude(key, value[key])

        return True

    def get_sorted_keys(self):
        """Return process property names as a nicely sorted list."""

        return ['name', 'wavefunctions', 'amplitudes']

    def get_matrix_element_calls(self, matrix_element):
        """Return a list of strings, corresponding to the Helas calls
        for the matrix element"""

        if not isinstance(matrix_element, HelasMatrixElement):
            raise self.PhysicsObjectError, \
                  "%s not valid argument for get_matrix_element_calls" % \
                  repr(matrix_element)

        res = []
        for n, diagram in enumerate(matrix_element.get('diagrams')):
            res.extend([ self.get_wavefunction_call(wf) for \
                         wf in diagram.get('wavefunctions') ])
            res.append("# Amplitude(s) for diagram number %d" % (n + 1))
            for amplitude in diagram.get('amplitudes'):
                res.append(self.get_amplitude_call(amplitude))

        return res

    def get_wavefunction_call(self, wavefunction):
        """Return the function for writing the wavefunction
        corresponding to the key"""

        try:
            call = self["wavefunctions"][wavefunction.get_call_key()](\
                wavefunction)
            return call
        except KeyError:
            return ""

    def get_amplitude_call(self, amplitude):
        """Return the function for writing the amplitude
        corresponding to the key"""

        try:
            call = self["amplitudes"][amplitude.get_call_key()](amplitude)
            return call
        except KeyError:
            return ""

    def add_wavefunction(self, key, function):
        """Set the function for writing the wavefunction
        corresponding to the key"""


        if not isinstance(key, tuple):
            raise self.PhysicsObjectError, \
                  "%s is not a valid tuple for wavefunction key" % \
                  str(key)

        if not callable(function):
            raise self.PhysicsObjectError, \
                  "%s is not a valid function for wavefunction string" % \
                  str(function)

        self.get('wavefunctions')[key] = function
        return True

    def add_amplitude(self, key, function):
        """Set the function for writing the amplitude
        corresponding to the key"""


        if not isinstance(key, tuple):
            raise self.PhysicsObjectError, \
                  "%s is not a valid tuple for amplitude key" % \
                  str(key)

        if not callable(function):
            raise self.PhysicsObjectError, \
                  "%s is not a valid function for amplitude string" % \
                  str(function)

        self.get('amplitudes')[key] = function
        return True

    # Customized constructor
    def __init__(self, argument={}):
        """Allow generating a HelasModel from a Model
        """

        if isinstance(argument, base_objects.Model):
            super(HelasModel, self).__init__()
            self.set('name', argument.get('name'))
        else:
            super(HelasModel, self).__init__(argument)
