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
import logging
import re
import itertools

import madgraph.core.base_objects as base_objects
import madgraph.core.diagram_generation as diagram_generation

"""Definitions of objects used to generate Helas calls (language-independent):
HelasWavefunction, HelasAmplitude, HelasDiagram for the generation of
wavefunctions and amplitudes;
HelasParticle, HelasInteraction, HelasModel are language-independent
base classes for the language-specific classes found in the
iolibs directory"""

#===============================================================================
# 
#===============================================================================

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
        self['interaction_id'] = 0
        self['inter_color'] = []
        self['lorentz'] = []
        self['couplings'] = { (0, 0):'none'}
        # Properties relating to the leg/vertex
        self['state'] = 'initial'
        self['mothers'] = HelasWavefunctionList()
        self['number'] = 0
        self['fermionflow'] = 1
        
    # Customized constructor
    def __init__(self, *arguments):
        """Allow generating a HelasWavefunction from a Leg
        """

        if len(arguments) > 2:
            if isinstance(arguments[0], base_objects.Leg) and \
                   isinstance(arguments[1], int) and \
                   isinstance(arguments[2], base_objects.Model):
                super(HelasWavefunction, self).__init__()
                self.set('pdg_code', (arguments[0].get('id'),arguments[2]))
                self.set('number', arguments[0].get('number'))
                self.set('state', arguments[0].get('state'))
                self.set('interaction_id', (arguments[1], arguments[2]))
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
                        "%s is not a valid integer for wavefunction interaction id" % str(value)

        if name in ['inter_color', 'lorentz']:
            #Should be a list of strings
            if not isinstance(value, list):
                raise self.PhysicsObjectError, \
                        "%s is not a valid list of strings" % str(value)
            for mystr in value:
                if not isinstance(mystr, str):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid string" % str(mystr)

        if name == 'couplings':
            #Should be a dictionary of strings with (i,j) keys
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                        "%s is not a valid dictionary for couplings" % \
                                                                str(value)

            if len(value) != len(self['inter_color']) * len(self['lorentz']):
                raise self.PhysicsObjectError, \
                        "Dictionary " + str(value) + \
                        " for couplings has not the right number of entry"

            for key in value.keys():
                if not isinstance(key, tuple):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple" % str(key)
                if len(key) != 2:
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple with 2 elements" % str(key)
                if not isinstance(key[0], int) or not isinstance(key[1], int):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple of integer" % str(key)
                if key[0] < 0 or key[1] < 0 or \
                   key[0] >= len(self['inter_color']) or key[1] >= \
                                                    len(self['lorentz']):
                    raise self.PhysicsObjectError, \
                        "%s is not a tuple with valid range" % str(key)
                if not isinstance(value[key], str):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid string" % str(mystr)

        if name == 'state':
            if not isinstance(value, str):
                raise self.PhysicsObjectError, \
                        "%s is not a valid string for wavefunction state" % \
                                                                    str(value)
            if value not in ['initial', 'final', 'intermediate']:
                raise self.PhysicsObjectError, \
                        "%s is not a valid wavefunction state (initial|final|intermediate)" % \
                                                                    str(value)
        if name == 'fermionflow':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for wavefunction number" % str(value)
            if not value in [-1,0,1]:
                raise self.PhysicsObjectError, \
                        "%s is not a valid fermionflow (must be -1, 0 or 1)" % str(value)                

        if name == 'number':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for wavefunction number" % str(value)

        if name == 'mothers':
            if not isinstance(value, HelasWavefunctionList):
                raise self.PhysicsObjectError, \
                      "%s is not a valid list of mothers for wavefunction" % \
                      str(value)

        return True

    def set(self, name, value):
        """When setting interaction_id, if model is given (in tuple),
        set all other interaction properties. When setting pdg_code,
        if model is given, set all other particle properties."""

        if name == 'interaction_id' and isinstance(value, tuple):
            if len(value) < 2 or not isinstance(value[0], int) or \
               not isinstance(value[1], base_objects.Model):
                raise self.PhysicsObjectError, \
                      "%s is not a valid (interaction id, model) tuple" % \
                      str(value)
            self.set('interaction_id', value[0])
            if value[0] > 0:
                inter = value[1].get('interaction_dict')[value[0]]
                self.set('inter_color', inter.get('color'))
                self.set('lorentz', inter.get('lorentz'))
                self.set('couplings', inter.get('couplings'))
            return True
        elif name == 'pdg_code' and isinstance(value, tuple):
            if len(value) < 2 or not isinstance(value[0], int) or \
               not isinstance(value[1], base_objects.Model):
                raise self.PhysicsObjectError, \
                      "%s is not a valid (pdg code, model) tuple" % \
                      str(value)
            self.set('pdg_code', value[0])
            part = value[1].get('particle_dict')[value[0]]
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
            return super(HelasWavefunction, self).set(name, value)

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['pdg_code', 'name', 'antiname', 'spin', 'color',
                'mass', 'width', 'is_part', 'self_antipart',
                'interaction_id', 'inter_color', 'lorentz', 'couplings',
                'state', 'number', 'fermionflow', 'mothers']

    # Overloaded operators
    
    def __eq__(self, other):
        """Overloading the equality operator, to make comparison easy
        when checking if wavefunction is already written, or when
        checking for identical processes. Note that the number for
        this wavefunction, the pdg code, and the interaction id are
        irrelevant, while the numbers for the mothers are important.
        """

        if not isinstance(other,HelasWavefunction):
            return False

        # Check relevant directly defined properties
        if self['spin'] != other['spin'] or \
           self['color'] != other['color'] or \
           self['mass'] != other['mass'] or \
           self['width'] != other['width'] or \
           self['is_part'] != other['is_part'] or \
           self['self_antipart'] != other['self_antipart'] or \
           self['inter_color'] != other['inter_color'] or \
           self['lorentz'] != other['lorentz'] or \
           self['couplings'] != other['couplings'] or \
           self['fermionflow'] != other['fermionflow'] or \
           self['state'] != other['state']:
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
    """List of HelasWavefunction objects
    """

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasWavefunction for the list."""
        
        return isinstance(obj, HelasWavefunction)


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
        self['inter_color'] = []
        self['lorentz'] = []
        self['couplings'] = { (0, 0):'none'}
        # Properties relating to the vertex
        self['number'] = 0
        self['mothers'] = HelasWavefunctionList()
        
    # Customized constructor
    def __init__(self, *arguments):
        """Allow generating a HelasAmplitude from a Vertex
        """

        if len(arguments) > 1:
            if isinstance(arguments[0],base_objects.Vertex) and \
               isinstance(arguments[1],base_objects.Model):
                super(HelasAmplitude, self).__init__()
                self.set('interaction_id',
                         (arguments[0].get('id'), arguments[1]))
        elif arguments:
            super(HelasAmplitude, self).__init__(arguments[0])
        else:
            super(HelasAmplitude, self).__init__()
   
    def filter(self, name, value):
        """Filter for valid property values."""

        if name == 'interaction_id':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for wavefunction interaction id" % str(value)

        if name in ['inter_color', 'lorentz']:
            #Should be a list of strings
            if not isinstance(value, list):
                raise self.PhysicsObjectError, \
                        "%s is not a valid list of strings" % str(value)
            for mystr in value:
                if not isinstance(mystr, str):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid string" % str(mystr)

        if name == 'couplings':
            #Should be a dictionary of strings with (i,j) keys
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                        "%s is not a valid dictionary for couplings" % \
                                                                str(value)

            if len(value) != len(self['inter_color']) * len(self['lorentz']):
                raise self.PhysicsObjectError, \
                        "Dictionary " + str(value) + \
                        " for couplings has not the right number of entry"

            for key in value.keys():
                if not isinstance(key, tuple):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple" % str(key)
                if len(key) != 2:
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple with 2 elements" % str(key)
                if not isinstance(key[0], int) or not isinstance(key[1], int):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple of integer" % str(key)
                if key[0] < 0 or key[1] < 0 or \
                   key[0] >= len(self['inter_color']) or key[1] >= \
                                                    len(self['lorentz']):
                    raise self.PhysicsObjectError, \
                        "%s is not a tuple with valid range" % str(key)
                if not isinstance(value[key], str):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid string" % str(mystr)

        if name == 'number':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for amplitude number" % str(value)

        if name == 'mothers':
            if not isinstance(value, HelasWavefunctionList):
                raise self.PhysicsObjectError, \
                      "%s is not a valid list of mothers for amplitude" % \
                      str(value)

        return True

    def set(self, name, value):
        """When setting interaction_id, if model is given (in tuple),
        set all other interaction properties."""

        if name == 'interaction_id' and isinstance(value, tuple):
            if len(value) < 2 or not isinstance(value[0], int) or \
               not isinstance(value[1], base_objects.Model):
                raise self.PhysicsObjectError, \
                      "%s is not a valid (interaction id, model) tuple" % \
                      str(value)
            self.set('interaction_id', value[0])
            inter = value[1].get('interaction_dict')[value[0]]
            self.set('inter_color', inter.get('color'))
            self.set('lorentz', inter.get('lorentz'))
            self.set('couplings', inter.get('couplings'))
            return True
        else:
            return super(HelasAmplitude, self).set(name, value)

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['interaction_id', 'inter_color', 'lorentz', 'couplings',
                'number', 'mothers']

    # Comparison between different amplitudes, to allow check for
    # identical processes. Note that we are then not interested in
    # interaction id, but in all other properties.
    def __eq__(self, other):
        """Comparison between different amplitudes, to allow check for
        identical processes.
        """
        
        if not isinstance(other,HelasAmplitude):
            return False

        # Check relevant directly defined properties
        if self['inter_color'] != other['inter_color'] or \
           self['lorentz'] != other['lorentz'] or \
           self['couplings'] != other['couplings'] or \
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
    """HelasDiagram: list of vertices (ordered)
    """

    def default_setup(self):
        """Default values for all properties"""

        self['wavefunctions'] = HelasWavefunctionList()
        self['amplitude'] = HelasAmplitude()
        self['fermionfactor'] = 1

    def filter(self, name, value):
        """Filter for valid diagram property values."""

        if name == 'wavefunctions':
            if not isinstance(value, HelasWavefunctionList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasWavefunctionList object" % str(value)
        if name == 'amplitude':
            if not isinstance(value, HelasAmplitude):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasAmplitude object" % str(value)

        if name == 'fermionfactor':
            if not isinstance(value, int):
                raise self.PhysicsObjectError, \
                        "%s is not a valid integer for fermionfactor" % str(value)
            if not value in [-1,1]:
                raise self.PhysicsObjectError, \
                        "%s is not a valid fermion factor (must be -1 or 1)" % str(value)                

        return True

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['wavefunctions', 'amplitude', 'fermionfactor']
    
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
    """HelasMatrixElement: list of HelasDiagrams (ordered)
    """

    def default_setup(self):
        """Default values for all properties"""

        self['diagrams'] = HelasDiagramList()

    def filter(self, name, value):
        """Filter for valid diagram property values."""

        if name == 'diagrams':
            if not isinstance(value, HelasDiagramList):
                raise self.PhysicsObjectError, \
                        "%s is not a valid HelasDiagramList object" % str(value)
        return True

    def get_sorted_keys(self):
        """Return particle property names as a nicely sorted list."""

        return ['diagrams']
    
    # Customized constructor
    def __init__(self, *arguments):
        """Constructor for the HelasMatrixElement. In particular allows
        generating a HelasMatrixElement from a DiagramList, with
        automatic generation of the necessary wavefunctions
        """

        if arguments:
            if isinstance(arguments[0],diagram_generation.Amplitude):
                super(HelasMatrixElement, self).__init__()
                amplitude = arguments[0]
                optimization = 1
                if len(arguments) > 1 and isinstance(arguments[1],int):
                    optimization = arguments[1]

                self.generate_helas_diagrams(amplitude, optimization)
                self.calculate_fermion_factors(amplitude)
            else:
                super(HelasMatrixElement, self).__init__(arguments[0])
        else:
            super(HelasMatrixElement, self).__init__()
   
    def generate_helas_diagrams(self, amplitude, optimization = 1):
        """Starting from a list of Diagrams from the diagram
        generation, generate the corresponding HelasDiagrams, i.e.,
        the wave functions, amplitudes and fermionfactors. Choose
        between default optimization (= 1) or no optimization (= 0,
        for GPU).
        """

        if not isinstance(amplitude, diagram_generation.Amplitude) or \
               not isinstance(optimization,int):
            raise self.PhysicsObjectError,\
                  "Missing or erraneous arguments for generate_helas_diagrams"
        diagram_list = amplitude.get('diagrams')
        process = amplitude.get('process')
        model = process.get('model')
        if not diagram_list:
            return

        # wavefunctions has all the previously defined wavefunctions
        wavefunctions = []

        # Generate wavefunctions for the external particles
        external_wavefunctions = [ HelasWavefunction(leg, 0, model) for leg \
                                   in process.get('legs') ]
        
        incoming_numbers = [ leg.get('number') for leg in filter(lambda leg: \
                                  leg.get('state') == 'initial',
                                  process.get('legs')) ]

        # Sort the wavefunctions according to number, just to be sure
        external_wavefunctions.sort(lambda wf1, wf2: \
                                    wf1.get('number')-wf2.get('number'))

        wavefunctions.extend(external_wavefunctions)

        # Now go through the diagrams, looking for undefined wavefunctions

        helas_diagrams = HelasDiagramList()

        for diagram in diagram_list:

            if not optimization:
                wavefunctions = []
                wavefunctions.extend(external_wavefunctions)

            # Dictionary from leg number to wave function, keeps track
            # of the present position in the tree
            number_to_wavefunctions = {}

            # Initialize wavefunctions for this diagram
            diagram_wavefunctions = HelasWavefunctionList()
            if diagram == diagram_list[0] or not optimization:
                diagram_wavefunctions.extend(external_wavefunctions)
            elif not optimization:
                wavefunctions = copy.copy(external_wavefunctions)
            
            vertices = copy.copy(diagram.get('vertices'))

            # Single out last vertex, since this will give amplitude
            lastvx = vertices.pop()

            # Check if last vertex is indentity vertex
            if lastvx.get('id') == 0:
                # Need to "glue together" last and next-to-last
                # vertext, by replacing the (incoming) last leg of the
                # next-to-last vertex with the (outgoing) leg in the
                # last vertex
                nexttolastvertex = vertices.pop()
                legs = nexttolastvertex.get('legs')
                ntlnumber = legs[len(legs)-1].get('number')
                lastleg = filter(lambda leg: leg.get('number') != ntlnumber,
                                 lastvx.get('legs'))[0]
                # Replace the last leg of nexttolastvertex
                legs[len(legs)-1] = lastleg
                lastvx = nexttolastvertex
                # Sort the legs, to get right order of wave functions
                lastvx.get('legs').sort(lambda leg1, leg2: \
                                    leg1.get('number')-leg2.get('number'))

            # If wavefunction from incoming particles, flip pdg code
            # (both for s- and t-channel particle)
            lastleg = lastvx.get('legs')[len(lastvx.get('legs')) - 1]
            if lastleg.get('number') in incoming_numbers:
                part = model.get('particle_dict')[lastleg.get('id')]
                lastleg.set('id', part.get_anti_pdg_code())

            # Go through all vertices except the last and create
            # wavefunctions
            for vertex in vertices:
                legs = copy.copy(vertex.get('legs'))
                last_leg = legs.pop()
                # Generate list of mothers from legs
                mothers = self.getmothers(legs, number_to_wavefunctions,
                                          external_wavefunctions)
                # If wavefunction from incoming particles, flip pdg code
                # (both for s- and t-channel particle)
                if last_leg.get('number') in incoming_numbers:
                    part = model.get('particle_dict')[last_leg.get('id')]
                    last_leg.set('id', part.get_anti_pdg_code())
                # Now generate new wavefunction for the last leg
                wf = HelasWavefunction(last_leg, vertex.get('id'), model)
                wf.set('mothers', mothers)
                wf.set('number', len(wavefunctions) + 1)
                wf.set('state','intermediate')
                if wf in wavefunctions and optimization:
                    wf = wavefunctions[wavefunctions.index(wf)]
                else:
                    wavefunctions.append(wf)
                    diagram_wavefunctions.append(wf)
                number_to_wavefunctions[last_leg.get('number')] = wf

            # Find mothers for the amplitude
            legs = lastvx.get('legs')
            mothers = self.getmothers(legs, number_to_wavefunctions,
                                      external_wavefunctions)
                
            # Now generate a HelasAmplitude from the last vertex.
            amp = HelasAmplitude(lastvx, model)
            amp.set('mothers', mothers)
            amp.set('number', diagram_list.index(diagram) + 1)

            # Sort the wavefunctions according to number
            diagram_wavefunctions.sort(lambda wf1, wf2: \
                                       wf1.get('number')-wf2.get('number'))

            # Generate HelasDiagram
            helas_diagrams.append(HelasDiagram({ \
                'wavefunctions': diagram_wavefunctions,
                'amplitude': amp
                }))

        self.set('diagrams',helas_diagrams)

    def calculate_fermion_factors(self, amplitude):
        """Starting from a list of Diagrams from the
        diagram generation, generate the corresponding HelasDiagrams,
        i.e., the wave functions, amplitudes and fermionfactors
        """


    # Helper methods

    def getmothers(self, legs, number_to_wavefunctions,
                   external_wavefunctions):
        """Generate list of mothers from number_to_wavefunctions and
        external_wavefunctions"""
        
        mothers = HelasWavefunctionList()

        for leg in legs:
            if not leg.get('number') in number_to_wavefunctions:
                # This is an external leg, pick from external_wavefunctions
                wf = external_wavefunctions[leg.get('number')-1]
                number_to_wavefunctions[leg.get('number')] = wf
            else:
                # The mother is an existing wavefunction
                wf = number_to_wavefunctions[leg.get('number')]
            mothers.append(wf)

        return mothers

#===============================================================================
# HelasParticle
#===============================================================================
class HelasParticle(base_objects.Particle):
    """HelasParticle: The necessary information for writing a
    wavefunction. Language-independent base class for
    language-dependent writing of calls to Helas routines.
    """

    # Static dictionnary, from particle properties to
    # language-specific HELAS calls
    wavefunctions = {}

    def default_setup(self):
        """Default values for all properties"""

        super(HelasParticle, self).default_setup()

    def filter(self, name, value):
        """Filter for valid particle property values."""

        super(HelasParticle, self).filter(name, value)

        if name == 'wavefunctions':
            # Should be a dictionary of functions returning strings, 
            # with keys (spin, initial/final)
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                        "%s is not a valid dictionary for wavefunction" % \
                                                                str(value)

            for key in value.keys():
                if not isinstance(key, tuple):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple" % str(key)
                if len(key) != 2:
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple with 2 elements" % str(key)
                if not isinstance(key[0], int) or not isinstance(key[1], string):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple of (integer, string)" % str(key)
                if key[0] < 1 or key[0] > 5 or \
                       key[1] not in ['initial', 'final']:
                    raise self.PhysicsObjectError, \
                          "%s is not a valid tuple of (spin, initial/final)" % str(key)
                if not callable(value[key]):
                    raise self.PhysicsObjectError, \
                        "%s is not a callable function" % str(value[key])

        return True

    def get(self, name):
        """Get the value of the property name."""

        if name == 'wavefunctions':
            return HelasParticle.wavefunctions

        return super(HelasParticle, self).get(name)

    def set(self, name, value):
        """Set the value of the property name. First check if value
        is a valid value for the considered property. Return True if the
        value has been correctly set, False otherwise."""

        if name == 'wavefunctions':
            try:
                self.filter(name, value)
                HelasParticle.wavefunctions = value
                return True
            except self.PhysicsObjectError, why:
                logging.warning("Property " + name + " cannot be changed:" + \
                                str(why))
                return False

        return super(HelasParticle, self).set(name, value)
        
#===============================================================================
# HelasParticleList
#===============================================================================
class HelasParticleList(base_objects.ParticleList):
    """A class to store lists of helas particles."""

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasParticle for the list."""
        return isinstance(obj, HelasParticle)

    # Customized constructor
    def __init__(self, argument = {}):
        """Allow generating a HelasParticleList from a ParticleList
        """

        if isinstance(argument,base_objects.ParticleList):
            super(HelasParticleList, self).__init__()
            for part in argument:
                self.append(HelasParticle(part))

        else:
            super(HelasParticleList, self).__init__(argument)

#===============================================================================
# HelasInteraction
#===============================================================================
class HelasInteraction(base_objects.Interaction):
    """HelasInteraction: The necessary information for writing a
    wavefunction or amplitude from an
    interaction. Language-independent base class for
    language-dependent writing of calls to Helas routines.
    """
    
    # Static dictionnaries, from particle properties to
    # language-specific HELAS calls
    wavefunctions = {}
    amplitudes = {}

    def default_setup(self):
        """Default values for all properties"""

        super(HelasInteraction, self).default_setup()

    def filter(self, name, value):
        """Filter for valid particle property values."""

        super(HelasInteraction, self).filter(name, value)

        if name == 'wavefunctions':
            # Should be a dictionary of functions returning strings, 
            # with keys (spin, initial/final)
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                        "%s is not a valid dictionary for wavefunction" % \
                                                                str(value)

            for key in value.keys():
                if not isinstance(key, tuple):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple" % str(key)
                if not callable(value[key]):
                    raise self.PhysicsObjectError, \
                        "%s is not a callable function" % str(value[key])

        if name == 'amplitudes':
            # Should be a dictionary of functions returning strings, 
            # with keys (spin, initial/final)
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                        "%s is not a valid dictionary for amplitude" % \
                                                                str(value)

            for key in value.keys():
                if not isinstance(key, tuple):
                    raise self.PhysicsObjectError, \
                        "%s is not a valid tuple" % str(key)
                if not callable(value[key]):
                    raise self.PhysicsObjectError, \
                        "%s is not a callable function" % str(value[key])

        return True

    def get(self, name):
        """Get the value of the property name."""

        if name == 'wavefunctions':
            return HelasInteraction.wavefunctions

        if name == 'amplitudes':
            return HelasInteraction.amplitudes

        return super(HelasInteraction, self).get(name)

    def set(self, name, value):
        """Set the value of the property name. First check if value
        is a valid value for the considered property. Return True if the
        value has been correctly set, False otherwise."""

        if name == 'wavefunctions':
            try:
                self.filter(name, value)
                HelasInteraction.wavefunctions = value
                return True
            except self.PhysicsObjectError, why:
                logging.warning("Property " + name + " cannot be changed:" + \
                                str(why))
                return False

        if name == 'amplitudes':
            try:
                self.filter(name, value)
                HelasInteraction.amplitudes = value
                return True
            except self.PhysicsObjectError, why:
                logging.warning("Property " + name + " cannot be changed:" + \
                                str(why))
                return False

        return super(HelasInteraction, self).set(name, value)

#===============================================================================
# HelasInteractionList
#===============================================================================
class HelasInteractionList(base_objects.InteractionList):
    """A class to store lists of helas interactionss."""

    def is_valid_element(self, obj):
        """Test if object obj is a valid HelasInteraction for the list."""

        return isinstance(obj, HelasInteraction)

    # Customized constructor
    def __init__(self, argument = {}):
        """Allow generating a HelasInteractionList from a InteractionList
        """

        if isinstance(argument,base_objects.InteractionList):
            super(HelasInteractionList, self).__init__()
            for part in argument:
                self.append(HelasInteraction(part))

        else:
            super(HelasInteractionList, self).__init__(argument)

#===============================================================================
# HelasModel
#===============================================================================
class HelasModel(base_objects.PhysicsObject):
    """A class to store all the model information."""

    def default_setup(self):

        self['name'] = ""
        self['particles'] = HelasParticleList()
        self['parameters'] = None
        self['interactions'] = HelasInteractionList()
        self['couplings'] = None
        self['lorentz'] = None
        self['particle_dict'] = {}
        self['interaction_dict'] = {}

    def filter(self, name, value):
        """Filter for model property values"""

        if name == 'name':
            if not isinstance(value, str):
                raise self.PhysicsObjectError, \
                    "Object of type %s is not a string" % \
                                                            type(value)
        if name == 'particles':
            if not isinstance(value, HelasParticleList):
                raise self.PhysicsObjectError, \
                    "Object of type %s is not a HelasParticleList object" % \
                                                            type(value)
        if name == 'interactions':
            if not isinstance(value, HelasInteractionList):
                raise self.PhysicsObjectError, \
                    "Object of type %s is not a HelasInteractionList object" % \
                                                            type(value)
        if name == 'particle_dict':
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                    "Object of type %s is not a dictionary" % \
                                                        type(value)
        if name == 'interaction_dict':
            if not isinstance(value, dict):
                raise self.PhysicsObjectError, \
                    "Object of type %s is not a dictionary" % \
                                                        type(value)

        return True

    def get(self, name):
        """Get the value of the property name."""

        if (name == 'particle_dict') and not self[name]:
            if self['particles']:
                self['particle_dict'] = self['particles'].generate_dict()

        if (name == 'interaction_dict') and not self[name]:
            if self['interactions']:
                self['interaction_dict'] = self['interactions'].generate_dict()

        return super(HelasModel, self).get(name)

    def get_sorted_keys(self):
        """Return process property names as a nicely sorted list."""

        return ['name', 'particles', 'parameters', 'interactions', 'couplings',
                'lorentz']

    def get_particle(self, id):
        """Return the particle corresponding to the id"""

        if id in self.get("particle_dict").keys():
            return self["particle_dict"][id]
        else:
            return None

    def get_interaction(self, id):
        """Return the interaction corresponding to the id"""

        if id in self.get("interaction_dict").keys():
            return self["interaction_dict"][id]
        else:
            return None

    # Customized constructor
    def __init__(self, argument = {}):
        """Allow generating a HelasModel from a Model
        """

        if isinstance(argument,base_objects.Model):
            super(HelasModel, self).__init__()
            self.set('name',argument.get('name'))
            self.set('particles',
                     HelasParticleList(argument.get('particles')))
            self.set('parameters',argument.get('parameters'))
            self.set('interactions',
                     HelasInteractionList(argument.get('interactions')))
            self.set('couplings',argument.get('couplings'))
            self.set('lorentz',argument.get('lorentz'))
        else:
            super(HelasModel, self).__init__(argument)

