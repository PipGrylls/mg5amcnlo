################################################################################
#
# Copyright (c) 2009 The MadGraph5_aMC@NLO Development team and Contributors
#
# This file is a part of the MadGraph5_aMC@NLO project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph5_aMC@NLO license which should accompany this 
# distribution.
#
# For more information, visit madgraph.phys.ucl.ac.be and amcatnlo.web.cern.ch
#
################################################################################

"""Unit test library for the export Pythia8 format routines"""

import StringIO
import copy
import fractions
import os
import re

import tests.unit_tests as unittest

import aloha.aloha_writers as aloha_writers
import aloha.create_aloha as create_aloha

import madgraph.iolibs.export_cpp as export_cpp
import madgraph.iolibs.file_writers as writers
import madgraph.iolibs.helas_call_writers as helas_call_writer
import models.import_ufo as import_ufo
import madgraph.iolibs.save_load_object as save_load_object
import madgraph.iolibs.group_subprocs as group_subprocs

import madgraph.core.base_objects as base_objects
import madgraph.core.color_algebra as color
import madgraph.core.helas_objects as helas_objects
import madgraph.core.diagram_generation as diagram_generation

import madgraph.various.misc as misc

from madgraph import MG5DIR

import tests.unit_tests.core.test_helas_objects as test_helas_objects
import tests.unit_tests.iolibs.test_file_writers as test_file_writers

#===============================================================================
# IOExportPythia8Test
#===============================================================================
class IOExportPythia8Test(unittest.TestCase,
                         test_file_writers.CheckFileCreate):
    """Test class for the export v4 module"""

    mymodel = base_objects.Model()
    mymatrixelement = helas_objects.HelasMatrixElement()
    created_files = ['test.h', 'test.cc'
                    ]

    def setUp(self):

        test_file_writers.CheckFileCreate.clean_files

        # Set up model
        mypartlist = base_objects.ParticleList()
        myinterlist = base_objects.InteractionList()

        # u and c quarkd and their antiparticles
        mypartlist.append(base_objects.Particle({'name':'u',
                      'antiname':'u~',
                      'spin':2,
                      'color':3,
                      'mass':'ZERO',
                      'width':'ZERO',
                      'texname':'u',
                      'antitexname':'\bar u',
                      'line':'straight',
                      'charge':2. / 3.,
                      'pdg_code':2,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        u = mypartlist[len(mypartlist) - 1]
        antiu = copy.copy(u)
        antiu.set('is_part', False)

        mypartlist.append(base_objects.Particle({'name':'c',
                      'antiname':'c~',
                      'spin':2,
                      'color':3,
                      'mass':'MC',
                      'width':'ZERO',
                      'texname':'c',
                      'antitexname':'\bar c',
                      'line':'straight',
                      'charge':2. / 3.,
                      'pdg_code':4,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        c = mypartlist[len(mypartlist) - 1]
        antic = copy.copy(c)
        antic.set('is_part', False)

        # A gluon
        mypartlist.append(base_objects.Particle({'name':'g',
                      'antiname':'g',
                      'spin':3,
                      'color':8,
                      'mass':'ZERO',
                      'width':'ZERO',
                      'texname':'g',
                      'antitexname':'g',
                      'line':'curly',
                      'charge':0.,
                      'pdg_code':21,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))

        g = mypartlist[len(mypartlist) - 1]

        # A photon
        mypartlist.append(base_objects.Particle({'name':'Z',
                      'antiname':'Z',
                      'spin':3,
                      'color':1,
                      'mass':'MZ',
                      'width':'WZ',
                      'texname':'Z',
                      'antitexname':'Z',
                      'line':'wavy',
                      'charge':0.,
                      'pdg_code':23,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))
        z = mypartlist[len(mypartlist) - 1]

        # A gluino
        mypartlist.append(base_objects.Particle({'name':'go',
                      'antiname':'go',
                      'spin':2,
                      'color':8,
                      'mass':'MGO',
                      'width':'WGO',
                      'texname':'go',
                      'antitexname':'go',
                      'line':'straight',
                      'charge':0.,
                      'pdg_code':1000021,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))

        go = mypartlist[len(mypartlist) - 1]

        # A sextet diquark
        mypartlist.append(base_objects.Particle({'name':'six',
                      'antiname':'six~',
                      'spin':1,
                      'color':6,
                      'mass':'MSIX',
                      'width':'WSIX',
                      'texname':'six',
                      'antitexname':'sixbar',
                      'line':'straight',
                      'charge':4./3.,
                      'pdg_code':6000001,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))

        six = mypartlist[len(mypartlist) - 1]
        antisix = copy.copy(six)
        antisix.set('is_part', False)
        

        # Gluon couplings to quarks
        myinterlist.append(base_objects.Interaction({
                      'id': 1,
                      'particles': base_objects.ParticleList(\
                                            [antiu, \
                                             u, \
                                             g]),
                      'color': [color.ColorString([color.T(2, 1, 0)])],
                      'lorentz':['FFV1'],
                      'couplings':{(0, 0):'GC_10'},
                      'orders':{'QCD':1}}))

        # Gamma couplings to quarks
        myinterlist.append(base_objects.Interaction({
                      'id': 2,
                      'particles': base_objects.ParticleList(\
                                            [antiu, \
                                             u, \
                                             z]),
                      'color': [color.ColorString([color.T(1, 0)])],
                      'lorentz':['FFV2', 'FFV5'],
                      'couplings':{(0,0): 'GC_35', (0,1): 'GC_47'},
                      'orders':{'QED':1}}))

        # Gluon couplings to gluinos
        myinterlist.append(base_objects.Interaction({
                      'id': 3,
                      'particles': base_objects.ParticleList(\
                                            [go, \
                                             go, \
                                             g]),
                      'color': [color.ColorString([color.f(0,1,2)])],
                      'lorentz':['FFV1'],
                      'couplings':{(0, 0):'GC_8'},
                      'orders':{'QCD':1}}))

        # Sextet couplings to quarks
        myinterlist.append(base_objects.Interaction({
                      'id': 4,
                      'particles': base_objects.ParticleList(\
                                            [u, \
                                             u, \
                                             antisix]),
                      'color': [color.ColorString([color.K6Bar(2, 0, 1)])],
                      'lorentz':['FFS1'],
                      'couplings':{(0,0): 'GC_24'},
                      'orders':{'QSIX':1}}))

        myinterlist.append(base_objects.Interaction({
                      'id': 5,
                      'particles': base_objects.ParticleList(\
                                            [antiu, \
                                             antiu, \
                                             six]),
                      'color': [color.ColorString([color.K6(2, 0, 1)])],
                      'lorentz':['FFS1'],
                      'couplings':{(0,0): 'GC_24'},
                      'orders':{'QSIX':1}}))

        self.mymodel.set('particles', mypartlist)
        self.mymodel.set('interactions', myinterlist)
        self.mymodel.set('name', 'sm')

        myleglist = base_objects.LegList()

        myleglist.append(base_objects.Leg({'id':2,
                                         'state':False}))
        myleglist.append(base_objects.Leg({'id':-2,
                                         'state':False}))
        myleglist.append(base_objects.Leg({'id':2,
                                         'state':True}))
        myleglist.append(base_objects.Leg({'id':-2,
                                         'state':True}))

        myproc = base_objects.Process({'legs':myleglist,
                                       'model':self.mymodel,
                                       'orders':{'QSIX':0}})
        
        myamplitude = diagram_generation.Amplitude({'process': myproc})

        self.mymatrixelement = helas_objects.HelasMultiProcess(myamplitude)

        myleglist = base_objects.LegList()

        myleglist.append(base_objects.Leg({'id':4,
                                           'state':False,
                                           'number' : 1}))
        myleglist.append(base_objects.Leg({'id':-4,
                                         'state':False,
                                           'number' : 2}))
        myleglist.append(base_objects.Leg({'id':4,
                                         'state':True,
                                           'number' : 3}))
        myleglist.append(base_objects.Leg({'id':-4,
                                         'state':True,
                                           'number' : 4}))

        myproc = base_objects.Process({'legs':myleglist,
                                       'model':self.mymodel,
                                       'orders':{'QSIX':0}})

        self.mymatrixelement.get('matrix_elements')[0].\
                                               get('processes').append(myproc)

        self.mycppwriter = helas_call_writer.CPPUFOHelasCallWriter(self.mymodel)
    
        self.pythia8_exporter = export_cpp.ProcessExporterPythia8(\
            self.mymatrixelement, self.mycppwriter,
            process_string = "q q~ > q q~")
        
        self.cpp_exporter = export_cpp.ProcessExporterCPP(\
            self.mymatrixelement, self.mycppwriter,
            process_string = "q q~ > q q~")

    tearDown = test_file_writers.CheckFileCreate.clean_files

    def test_pythia8_export_functions(self):
        """Test functions used by the Pythia export"""

        # Test the exporter setup
        self.assertEqual(self.pythia8_exporter.model, self.mymodel)
        self.assertEqual(self.pythia8_exporter.matrix_elements, self.mymatrixelement.get('matrix_elements'))
        self.assertEqual(self.pythia8_exporter.process_string, "q q~ > q q~")
        self.assertEqual(self.pythia8_exporter.process_name, "Sigma_sm_qqx_qqx")
        self.assertEqual(self.pythia8_exporter.nexternal, 4)
        self.assertEqual(self.pythia8_exporter.ninitial, 2)
        self.assertEqual(self.pythia8_exporter.nfinal, 2)
        self.assertTrue(self.pythia8_exporter.single_helicities)
        self.assertEqual(self.pythia8_exporter.wavefunctions, self.mymatrixelement.get('matrix_elements')[0].get_all_wavefunctions())

        # Test get_process_influx
        processes = self.mymatrixelement.get('matrix_elements')[0].get('processes')
        self.assertEqual(self.pythia8_exporter.get_process_influx(), "qqbarSame")
        self.assertEqual(self.pythia8_exporter.get_id_masses(processes[0]), "")
        self.assertEqual(self.pythia8_exporter.get_id_masses(processes[1]), \
                        """int id3Mass() const {return 4;}
int id4Mass() const {return 4;}""")
        self.assertEqual(self.pythia8_exporter.get_resonance_lines(), \
                        "virtual int resonanceA() const {return 23;}")

    def test_write_process_h_file(self):
        """Test writing the .h Pythia file for a matrix element"""

        goal_string = \
"""//==========================================================================
// This file has been automatically generated for Pythia 8
// MadGraph5_aMC@NLO v. %(version)s, %(date)s
// By the MadGraph5_aMC@NLO Development Team
// Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#ifndef Pythia8_Sigma_sm_qqx_qqx_H
#define Pythia8_Sigma_sm_qqx_qqx_H

#include <complex> 

#include "SigmaProcess.h"
#include "Parameters_sm.h"

using namespace std; 

namespace Pythia8 
{
//==========================================================================
// A class for calculating the matrix elements for
// Process: u u~ > u u~ QSIX=0
// Process: c c~ > c c~ QSIX=0
//--------------------------------------------------------------------------

class Sigma_sm_qqx_qqx : public Sigma2Process 
{
  public:

    // Constructor.
    Sigma_sm_qqx_qqx() {}

    // Initialize process.
    virtual void initProc(); 

    // Calculate flavour-independent parts of cross section.
    virtual void sigmaKin(); 

    // Evaluate sigmaHat(sHat).
    virtual double sigmaHat(); 

    // Select flavour, colour and anticolour.
    virtual void setIdColAcol(); 

    // Evaluate weight for decay angles.
    virtual double weightDecay(Event& process, int iResBeg, int iResEnd); 

    // Info on the subprocess.
    virtual string name() const {return "q q~ > q q~ (sm)";}

    virtual int code() const {return 10000;}

    virtual string inFlux() const {return "qqbarSame";}

    virtual int resonanceA() const {return 23;}
    // Tell Pythia that sigmaHat returns the ME^2
    virtual bool convertM2() const {return true;}

  private:

    // Private functions to calculate the matrix element for all subprocesses
    // Calculate wavefunctions
    void calculate_wavefunctions(const int perm[], const int hel[]); 
    static const int nwavefuncs = 8; 
    std::complex<double> w[nwavefuncs][18]; 
    static const int namplitudes = 4; 
    std::complex<double> amp[namplitudes]; 
    double matrix_uux_uux(); 

    // Constants for array limits
    static const int nexternal = 4; 
    static const int nprocesses = 1; 

    // Store the matrix element value from sigmaKin
    double matrix_element[nprocesses]; 

    // Color flows, used when selecting color
    double * jamp2[nprocesses]; 

    // Pointer to the model parameters
    Parameters_sm * pars; 

}; 

}  // end namespace Pythia

#endif  // Pythia8_Sigma_sm_qqx_qqx_H
""" % misc.get_pkg_info()

        self.pythia8_exporter.write_process_h_file(\
            writers.CPPWriter(self.give_pos('test.h')))

        #print open(self.give_pos('test.h')).read()
        self.assertFileContains('test.h', goal_string)

    def test_write_process_cc_file(self):
        """Test writing the .cc Pythia file for a matrix element"""

        goal_string = \
"""//==========================================================================
// This file has been automatically generated for Pythia 8 by
// MadGraph5_aMC@NLO v. %(version)s, %(date)s
// By the MadGraph5_aMC@NLO Development Team
// Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#include "Sigma_sm_qqx_qqx.h"
#include "HelAmps_sm.h"

using namespace Pythia8_sm; 

namespace Pythia8 
{

//==========================================================================
// Class member functions for calculating the matrix elements for
// Process: u u~ > u u~ QSIX=0
// Process: c c~ > c c~ QSIX=0

//--------------------------------------------------------------------------
// Initialize process.

void Sigma_sm_qqx_qqx::initProc() 
{
  // Instantiate the model class and set parameters that stay fixed during run
  pars = Parameters_sm::getInstance(); 
  pars->setIndependentParameters(particleDataPtr, couplingsPtr, slhaPtr); 
  pars->setIndependentCouplings(); 
  // Set massive/massless matrix elements for c/b/mu/tau
  mcME = particleDataPtr->m0(4); 
  mbME = 0.; 
  mmuME = 0.; 
  mtauME = 0.; 
  jamp2[0] = new double[2]; 
}

//--------------------------------------------------------------------------
// Evaluate |M|^2, part independent of incoming flavour.

void Sigma_sm_qqx_qqx::sigmaKin() 
{
  // Set the parameters which change event by event
  pars->setDependentParameters(particleDataPtr, couplingsPtr, slhaPtr, alpS); 
  pars->setDependentCouplings(); 
  // Reset color flows
  for(int i = 0; i < 2; i++ )
    jamp2[0][i] = 0.; 

  // Local variables and constants
  const int ncomb = 16; 
  static bool goodhel[ncomb] = {ncomb * false}; 
  static int ntry = 0, sum_hel = 0, ngood = 0; 
  static int igood[ncomb]; 
  static int jhel; 
  double t[nprocesses]; 
  // Helicities for the process
  static const int helicities[ncomb][nexternal] = {{-1, -1, -1, -1}, {-1, -1,
      -1, 1}, {-1, -1, 1, -1}, {-1, -1, 1, 1}, {-1, 1, -1, -1}, {-1, 1, -1, 1},
      {-1, 1, 1, -1}, {-1, 1, 1, 1}, {1, -1, -1, -1}, {1, -1, -1, 1}, {1, -1,
      1, -1}, {1, -1, 1, 1}, {1, 1, -1, -1}, {1, 1, -1, 1}, {1, 1, 1, -1}, {1,
      1, 1, 1}};
  // Denominators: spins, colors and identical particles
  const int denominators[nprocesses] = {36}; 

  ntry = ntry + 1; 

  // Reset the matrix elements
  for(int i = 0; i < nprocesses; i++ )
  {
    matrix_element[i] = 0.; 
    t[i] = 0.; 
  }

  // Define permutation
  int perm[nexternal]; 
  for(int i = 0; i < nexternal; i++ )
  {
    perm[i] = i; 
  }

  // For now, call setupForME() here
  id1 = 2; 
  id2 = -2; 
  if( !setupForME())
  {
    return; 
  }

  if (sum_hel == 0 || ntry < 10)
  {
    // Calculate the matrix element for all helicities
    for(int ihel = 0; ihel < ncomb; ihel++ )
    {
      if (goodhel[ihel] || ntry < 2)
      {
        calculate_wavefunctions(perm, helicities[ihel]); 
        t[0] = matrix_uux_uux(); 

        double tsum = 0; 
        for(int iproc = 0; iproc < nprocesses; iproc++ )
        {
          matrix_element[iproc] += t[iproc]; 
          tsum += t[iproc]; 
        }
        // Store which helicities give non-zero result
        if (tsum != 0. && !goodhel[ihel])
        {
          goodhel[ihel] = true; 
          ngood++; 
          igood[ngood] = ihel; 
        }
      }
    }
    jhel = 0; 
    sum_hel = min(sum_hel, ngood); 
  }
  else
  {
    // Only use the "good" helicities
    for(int j = 0; j < sum_hel; j++ )
    {
      jhel++; 
      if (jhel >= ngood)
        jhel = 0; 
      double hwgt = double(ngood)/double(sum_hel); 
      int ihel = igood[jhel]; 
      calculate_wavefunctions(perm, helicities[ihel]); 
      t[0] = matrix_uux_uux(); 

      for(int iproc = 0; iproc < nprocesses; iproc++ )
      {
        matrix_element[iproc] += t[iproc] * hwgt; 
      }
    }
  }

  for (int i = 0; i < nprocesses; i++ )
    matrix_element[i] /= denominators[i]; 



}

//--------------------------------------------------------------------------
// Evaluate |M|^2, including incoming flavour dependence.

double Sigma_sm_qqx_qqx::sigmaHat() 
{
  // Select between the different processes
  if(id1 == 4 && id2 == -4)
  {
    // Add matrix elements for processes with beams (4, -4)
    return matrix_element[0]; 
  }
  else if(id1 == 2 && id2 == -2)
  {
    // Add matrix elements for processes with beams (2, -2)
    return matrix_element[0]; 
  }
  else
  {
    // Return 0 if not correct initial state assignment
    return 0.; 
  }
}

//--------------------------------------------------------------------------
// Select identity, colour and anticolour.

void Sigma_sm_qqx_qqx::setIdColAcol() 
{
  if(id1 == 4 && id2 == -4)
  {
    // Pick one of the flavor combinations (4, -4)
    int flavors[1][2] = {{4, -4}}; 
    vector<double> probs; 
    double sum = matrix_element[0]; 
    probs.push_back(matrix_element[0]/sum); 
    int choice = rndmPtr->pick(probs); 
    id3 = flavors[choice][0]; 
    id4 = flavors[choice][1]; 
  }
  else if(id1 == 2 && id2 == -2)
  {
    // Pick one of the flavor combinations (2, -2)
    int flavors[1][2] = {{2, -2}}; 
    vector<double> probs; 
    double sum = matrix_element[0]; 
    probs.push_back(matrix_element[0]/sum); 
    int choice = rndmPtr->pick(probs); 
    id3 = flavors[choice][0]; 
    id4 = flavors[choice][1]; 
  }
  setId(id1, id2, id3, id4); 
  // Pick color flow
  int ncolor[1] = {2}; 
  if(id1 == 2 && id2 == -2 && id3 == 2 && id4 == -2 || id1 == 4 && id2 == -4 &&
      id3 == 4 && id4 == -4)
  {
    vector<double> probs; 
    double sum = jamp2[0][0] + jamp2[0][1]; 
    for(int i = 0; i < ncolor[0]; i++ )
      probs.push_back(jamp2[0][i]/sum); 
    int ic = rndmPtr->pick(probs); 
    static int colors[2][8] = {{1, 0, 0, 1, 2, 0, 0, 2}, {2, 0, 0, 1, 2, 0, 0,
        1}};
    setColAcol(colors[ic][0], colors[ic][1], colors[ic][2], colors[ic][3],
        colors[ic][4], colors[ic][5], colors[ic][6], colors[ic][7]);
  }
}

//--------------------------------------------------------------------------
// Evaluate weight for angles of decay products in process

double Sigma_sm_qqx_qqx::weightDecay(Event& process, int iResBeg, int iResEnd) 
{
  // Just use isotropic decay (default)
  return 1.; 
}

//==========================================================================
// Private class member functions

//--------------------------------------------------------------------------
// Evaluate |M|^2 for each subprocess

void Sigma_sm_qqx_qqx::calculate_wavefunctions(const int perm[], const int
    hel[])
{
  // Calculate wavefunctions for all processes
  double p[nexternal][4]; 
  int i; 

  // Convert Pythia 4-vectors to double[]
  for(i = 0; i < nexternal; i++ )
  {
    p[i][0] = pME[i].e(); 
    p[i][1] = pME[i].px(); 
    p[i][2] = pME[i].py(); 
    p[i][3] = pME[i].pz(); 
  }

  // Calculate all wavefunctions
  ixxxxx(p[perm[0]], mME[0], hel[0], +1, w[0]); 
  oxxxxx(p[perm[1]], mME[1], hel[1], -1, w[1]); 
  oxxxxx(p[perm[2]], mME[2], hel[2], +1, w[2]); 
  ixxxxx(p[perm[3]], mME[3], hel[3], -1, w[3]); 
  FFV1_3(w[0], w[1], pars->GC_10, pars->ZERO, pars->ZERO, w[4]); 
  FFV2_5_3(w[0], w[1], pars->GC_35, pars->GC_47, pars->MZ, pars->WZ, w[5]); 
  FFV1_3(w[0], w[2], pars->GC_10, pars->ZERO, pars->ZERO, w[6]); 
  FFV2_5_3(w[0], w[2], pars->GC_35, pars->GC_47, pars->MZ, pars->WZ, w[7]); 

  // Calculate all amplitudes
  // Amplitude(s) for diagram number 0
  FFV1_0(w[3], w[2], w[4], pars->GC_10, amp[0]); 
  FFV2_5_0(w[3], w[2], w[5], pars->GC_35, pars->GC_47, amp[1]); 
  FFV1_0(w[3], w[1], w[6], pars->GC_10, amp[2]); 
  FFV2_5_0(w[3], w[1], w[7], pars->GC_35, pars->GC_47, amp[3]); 


}
double Sigma_sm_qqx_qqx::matrix_uux_uux() 
{
  int i, j; 
  // Local variables
  const int ngraphs = 4; 
  const int ncolor = 2; 
  std::complex<double> ztemp; 
  std::complex<double> jamp[ncolor]; 
  // The color matrix;
  static const double denom[ncolor] = {1, 1}; 
  static const double cf[ncolor][ncolor] = {{9, 3}, {3, 9}}; 

  // Calculate color flows
  jamp[0] = +1./6. * amp[0] - amp[1] + 1./2. * amp[2]; 
  jamp[1] = -1./2. * amp[0] - 1./6. * amp[2] + amp[3]; 

  // Sum and square the color flows to get the matrix element
  double matrix = 0; 
  for(i = 0; i < ncolor; i++ )
  {
    ztemp = 0.; 
    for(j = 0; j < ncolor; j++ )
      ztemp = ztemp + cf[i][j] * jamp[j]; 
    matrix = matrix + real(ztemp * conj(jamp[i]))/denom[i]; 
  }

  // Store the leading color flows for choice of color
  for(i = 0; i < ncolor; i++ )
    jamp2[0][i] += real(jamp[i] * conj(jamp[i])); 

  return matrix; 
}


}  // end namespace Pythia
""" % misc.get_pkg_info()

        exporter = export_cpp.ProcessExporterPythia8(self.mymatrixelement,
        self.mycppwriter, process_string = "q q~ > q q~")

        exporter.write_process_cc_file(\
        writers.CPPWriter(self.give_pos('test.cc')))

        #print open(self.give_pos('test.cc')).read()
        self.assertFileContains('test.cc', goal_string)

    def test_write_process_cc_file_uu_six(self):
        """Test writing the .cc Pythia file for u u > six"""

        myleglist = base_objects.LegList()

        myleglist.append(base_objects.Leg({'id':2,
                                           'state':False,
                                           'number' : 1}))
        myleglist.append(base_objects.Leg({'id':2,
                                           'state':False,
                                           'number' : 2}))
        myleglist.append(base_objects.Leg({'id':6000001,
                                           'number' : 3}))

        myproc = base_objects.Process({'legs':myleglist,
                                       'model':self.mymodel})

        myamplitude = diagram_generation.Amplitude({'process': myproc})

        mymatrixelement = helas_objects.HelasMultiProcess(myamplitude)

        exporter = export_cpp.ProcessExporterPythia8(\
            mymatrixelement, self.mycppwriter,
            process_string = "q q > six")

        goal_string = \
"""//==========================================================================
// This file has been automatically generated for Pythia 8 by
// MadGraph5_aMC@NLO v. %(version)s, %(date)s
// By the MadGraph5_aMC@NLO Development Team
// Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#include "Sigma_sm_qq_six.h"
#include "HelAmps_sm.h"

using namespace Pythia8_sm; 

namespace Pythia8 
{

//==========================================================================
// Class member functions for calculating the matrix elements for
// Process: u u > six

//--------------------------------------------------------------------------
// Initialize process.

void Sigma_sm_qq_six::initProc() 
{
  // Instantiate the model class and set parameters that stay fixed during run
  pars = Parameters_sm::getInstance(); 
  pars->setIndependentParameters(particleDataPtr, couplingsPtr, slhaPtr); 
  pars->setIndependentCouplings(); 
  // Set massive/massless matrix elements for c/b/mu/tau
  mcME = particleDataPtr->m0(4); 
  mbME = 0.; 
  mmuME = 0.; 
  mtauME = 0.; 
  jamp2[0] = new double[1]; 
}

//--------------------------------------------------------------------------
// Evaluate |M|^2, part independent of incoming flavour.

void Sigma_sm_qq_six::sigmaKin() 
{
  // Set the parameters which change event by event
  pars->setDependentParameters(particleDataPtr, couplingsPtr, slhaPtr, alpS); 
  pars->setDependentCouplings(); 
  // Reset color flows
  for(int i = 0; i < 1; i++ )
    jamp2[0][i] = 0.; 

  // Local variables and constants
  const int ncomb = 4; 
  static bool goodhel[ncomb] = {ncomb * false}; 
  static int ntry = 0, sum_hel = 0, ngood = 0; 
  static int igood[ncomb]; 
  static int jhel; 
  double t[nprocesses]; 
  // Helicities for the process
  static const int helicities[ncomb][nexternal] = {{-1, -1, 0}, {-1, 1, 0}, {1,
      -1, 0}, {1, 1, 0}};
  // Denominators: spins, colors and identical particles
  const int denominators[nprocesses] = {36}; 

  ntry = ntry + 1; 

  // Reset the matrix elements
  for(int i = 0; i < nprocesses; i++ )
  {
    matrix_element[i] = 0.; 
    t[i] = 0.; 
  }

  // Define permutation
  int perm[nexternal]; 
  for(int i = 0; i < nexternal; i++ )
  {
    perm[i] = i; 
  }

  // For now, call setupForME() here
  id1 = 2; 
  id2 = 2; 
  if( !setupForME())
  {
    return; 
  }

  if (sum_hel == 0 || ntry < 10)
  {
    // Calculate the matrix element for all helicities
    for(int ihel = 0; ihel < ncomb; ihel++ )
    {
      if (goodhel[ihel] || ntry < 2)
      {
        calculate_wavefunctions(perm, helicities[ihel]); 
        t[0] = matrix_uu_six(); 

        double tsum = 0; 
        for(int iproc = 0; iproc < nprocesses; iproc++ )
        {
          matrix_element[iproc] += t[iproc]; 
          tsum += t[iproc]; 
        }
        // Store which helicities give non-zero result
        if (tsum != 0. && !goodhel[ihel])
        {
          goodhel[ihel] = true; 
          ngood++; 
          igood[ngood] = ihel; 
        }
      }
    }
    jhel = 0; 
    sum_hel = min(sum_hel, ngood); 
  }
  else
  {
    // Only use the "good" helicities
    for(int j = 0; j < sum_hel; j++ )
    {
      jhel++; 
      if (jhel >= ngood)
        jhel = 0; 
      double hwgt = double(ngood)/double(sum_hel); 
      int ihel = igood[jhel]; 
      calculate_wavefunctions(perm, helicities[ihel]); 
      t[0] = matrix_uu_six(); 

      for(int iproc = 0; iproc < nprocesses; iproc++ )
      {
        matrix_element[iproc] += t[iproc] * hwgt; 
      }
    }
  }

  for (int i = 0; i < nprocesses; i++ )
    matrix_element[i] /= denominators[i]; 



}

//--------------------------------------------------------------------------
// Evaluate |M|^2, including incoming flavour dependence.

double Sigma_sm_qq_six::sigmaHat() 
{
  // Select between the different processes
  if(id1 == 2 && id2 == 2)
  {
    // Add matrix elements for processes with beams (2, 2)
    return matrix_element[0]; 
  }
  else
  {
    // Return 0 if not correct initial state assignment
    return 0.; 
  }
}

//--------------------------------------------------------------------------
// Select identity, colour and anticolour.

void Sigma_sm_qq_six::setIdColAcol() 
{
  if(id1 == 2 && id2 == 2)
  {
    // Pick one of the flavor combinations (6000001,)
    int flavors[1][1] = {{6000001}}; 
    vector<double> probs; 
    double sum = matrix_element[0]; 
    probs.push_back(matrix_element[0]/sum); 
    int choice = rndmPtr->pick(probs); 
    id3 = flavors[choice][0]; 
  }
  setId(id1, id2, id3); 
  // Pick color flow
  int ncolor[1] = {1}; 
  if(id1 == 2 && id2 == 2 && id3 == 6000001)
  {
    vector<double> probs; 
    double sum = jamp2[0][0]; 
    for(int i = 0; i < ncolor[0]; i++ )
      probs.push_back(jamp2[0][i]/sum); 
    int ic = rndmPtr->pick(probs); 
    static int colors[1][6] = {{1, 0, 2, 0, 1, -2}}; 
    setColAcol(colors[ic][0], colors[ic][1], colors[ic][2], colors[ic][3],
        colors[ic][4], colors[ic][5]);
  }
}

//--------------------------------------------------------------------------
// Evaluate weight for angles of decay products in process

double Sigma_sm_qq_six::weightDecay(Event& process, int iResBeg, int iResEnd) 
{
  // Just use isotropic decay (default)
  return 1.; 
}

//==========================================================================
// Private class member functions

//--------------------------------------------------------------------------
// Evaluate |M|^2 for each subprocess

void Sigma_sm_qq_six::calculate_wavefunctions(const int perm[], const int hel[])
{
  // Calculate wavefunctions for all processes
  double p[nexternal][4]; 
  int i; 

  // Convert Pythia 4-vectors to double[]
  for(i = 0; i < nexternal; i++ )
  {
    p[i][0] = pME[i].e(); 
    p[i][1] = pME[i].px(); 
    p[i][2] = pME[i].py(); 
    p[i][3] = pME[i].pz(); 
  }

  // Calculate all wavefunctions
  oxxxxx(p[perm[0]], mME[0], hel[0], -1, w[0]); 
  ixxxxx(p[perm[1]], mME[1], hel[1], +1, w[1]); 
  sxxxxx(p[perm[2]], +1, w[2]); 

  // Calculate all amplitudes
  // Amplitude(s) for diagram number 0
  FFS1C1_0(w[1], w[0], w[2], pars->GC_24, amp[0]); 


}
double Sigma_sm_qq_six::matrix_uu_six() 
{
  int i, j; 
  // Local variables
  const int ngraphs = 1; 
  const int ncolor = 1; 
  std::complex<double> ztemp; 
  std::complex<double> jamp[ncolor]; 
  // The color matrix;
  static const double denom[ncolor] = {1}; 
  static const double cf[ncolor][ncolor] = {{6}}; 

  // Calculate color flows
  jamp[0] = -amp[0]; 

  // Sum and square the color flows to get the matrix element
  double matrix = 0; 
  for(i = 0; i < ncolor; i++ )
  {
    ztemp = 0.; 
    for(j = 0; j < ncolor; j++ )
      ztemp = ztemp + cf[i][j] * jamp[j]; 
    matrix = matrix + real(ztemp * conj(jamp[i]))/denom[i]; 
  }

  // Store the leading color flows for choice of color
  for(i = 0; i < ncolor; i++ )
    jamp2[0][i] += real(jamp[i] * conj(jamp[i])); 

  return matrix; 
}


}  // end namespace Pythia
""" % misc.get_pkg_info()

        exporter.write_process_cc_file(\
                 writers.CPPWriter(self.give_pos('test.cc')))

        #print open(self.give_pos('test.cc')).read()
        self.assertFileContains('test.cc', goal_string)

    def test_write_dec_multiprocess_files(self):
        """Test writing the .cc C++ standalone file for p p > z j, z > j j"""

        # Setup a model

        mypartlist = base_objects.ParticleList()
        myinterlist = base_objects.InteractionList()

        # A gluon
        mypartlist.append(base_objects.Particle({'name':'g',
                      'antiname':'g',
                      'spin':3,
                      'color':8,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'g',
                      'antitexname':'g',
                      'line':'curly',
                      'charge':0.,
                      'pdg_code':21,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))

        g = mypartlist[-1]

        # A quark U and its antiparticle
        mypartlist.append(base_objects.Particle({'name':'u',
                      'antiname':'u~',
                      'spin':2,
                      'color':3,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'u',
                      'antitexname':'\bar u',
                      'line':'straight',
                      'charge':2. / 3.,
                      'pdg_code':2,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        u = mypartlist[-1]
        antiu = copy.copy(u)
        antiu.set('is_part', False)

        # A quark S and its antiparticle
        mypartlist.append(base_objects.Particle({'name':'s',
                      'antiname':'s~',
                      'spin':2,
                      'color':3,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'d',
                      'antitexname':'\bar d',
                      'line':'straight',
                      'charge':-1. / 3.,
                      'pdg_code':3,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        s = mypartlist[-1]
        antis = copy.copy(s)
        antis.set('is_part', False)

        # A quark D and its antiparticle
        mypartlist.append(base_objects.Particle({'name':'d',
                      'antiname':'d~',
                      'spin':2,
                      'color':3,
                      'mass':'zero',
                      'width':'zero',
                      'texname':'d',
                      'antitexname':'\bar d',
                      'line':'straight',
                      'charge':-1. / 3.,
                      'pdg_code':1,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':False}))
        d = mypartlist[-1]
        antid = copy.copy(d)
        antid.set('is_part', False)

        # A Z
        mypartlist.append(base_objects.Particle({'name':'z',
                      'antiname':'z',
                      'spin':3,
                      'color':1,
                      'mass':'MZ',
                      'width':'WZ',
                      'texname':'Z',
                      'antitexname':'Z',
                      'line':'wavy',
                      'charge':0.,
                      'pdg_code':23,
                      'propagating':True,
                      'is_part':True,
                      'self_antipart':True}))
        z = mypartlist[-1]

        # Gluon and photon couplings to quarks
        myinterlist.append(base_objects.Interaction({
                      'id': 1,
                      'particles': base_objects.ParticleList(\
                                            [antiu, \
                                             u, \
                                             g]),
                      'color': [color.ColorString([color.T(2,1,0)])],
                      'lorentz':['FFV1'],
                      'couplings':{(0, 0):'GQQ'},
                      'orders':{'QCD':1}}))

        myinterlist.append(base_objects.Interaction({
                      'id': 2,
                      'particles': base_objects.ParticleList(\
                                            [antid, \
                                             d, \
                                             g]),
                      'color': [color.ColorString([color.T(2,1,0)])],
                      'lorentz':['FFV1'],
                      'couplings':{(0, 0):'GQQ'},
                      'orders':{'QCD':1}}))

        myinterlist.append(base_objects.Interaction({
                      'id': 3,
                      'particles': base_objects.ParticleList(\
                                            [antis, \
                                             s, \
                                             g]),
                      'color': [color.ColorString([color.T(2,1,0)])],
                      'lorentz':['FFV1'],
                      'couplings':{(0, 0):'GQQ'},
                      'orders':{'QCD':1}}))

        # Coupling of Z to quarks
        
        myinterlist.append(base_objects.Interaction({
                      'id': 6,
                      'particles': base_objects.ParticleList(\
                                            [antiu, \
                                             u, \
                                             z]),
                      'color': [color.ColorString([color.T(1,0)])],
                      'lorentz':['FFV1', 'FFV2'],
                      'couplings':{(0, 0):'GUZ1', (0, 1):'GUZ2'},
                      'orders':{'QED':1}}))

        myinterlist.append(base_objects.Interaction({
                      'id': 7,
                      'particles': base_objects.ParticleList(\
                                            [antid, \
                                             d, \
                                             z]),
                      'color': [color.ColorString([color.T(1,0)])],
                      'lorentz':['FFV1', 'FFV2'],
                      'couplings':{(0, 0):'GDZ1', (0, 0):'GDZ2'},
                      'orders':{'QED':1}}))

        myinterlist.append(base_objects.Interaction({
                      'id': 8,
                      'particles': base_objects.ParticleList(\
                                            [antis, \
                                             s, \
                                             z]),
                      'color': [color.ColorString([color.T(1,0)])],
                      'lorentz':['FFV1', 'FFV2'],
                      'couplings':{(0, 0):'GDZ1', (0, 0):'GDZ2'},
                      'orders':{'QED':1}}))

        mymodel = base_objects.Model()
        mymodel.set('particles', mypartlist)
        mymodel.set('interactions', myinterlist)        
        mymodel.set('name', 'sm')

        # Set parameters
        external_parameters = [\
            base_objects.ParamCardVariable('zero', 0.,'DUM', 1),
            base_objects.ParamCardVariable('MZ', 91.,'MASS', 23),
            base_objects.ParamCardVariable('WZ', 2.,'DECAY', 23)]
        couplings = [\
            base_objects.ModelVariable('GQQ', '1.', 'complex'),
            base_objects.ModelVariable('GQED', '0.1', 'complex'),
            base_objects.ModelVariable('G', '1.', 'complex'),
            base_objects.ModelVariable('GUZ1', '0.1', 'complex'),
            base_objects.ModelVariable('GUZ2', '0.1', 'complex'),
            base_objects.ModelVariable('GDZ1', '0.05', 'complex'),
            base_objects.ModelVariable('GDZ2', '0.05', 'complex'),
            base_objects.ModelVariable('ZZQQ', '0.01', 'complex')]
        mymodel.set('parameters', {('external',): external_parameters})
        mymodel.set('couplings', {(): couplings})
        mymodel.set('functions', [])
        p = [21,1,2,3,-1,-2,-3]
        q = [1,2,-1,-2]
        procs = [[p,p,[23],p]]
        decays = [[[23],p,p]]
        my_processes = base_objects.ProcessDefinitionList()
        decayprocs = base_objects.ProcessDefinitionList()

        for proc in procs:
            # Define the multiprocess
            my_leglist = base_objects.MultiLegList([\
                base_objects.MultiLeg({'ids': id, 'state': True}) for id in proc])

            my_leglist[0].set('state', False)
            my_leglist[1].set('state', False)

            my_process = base_objects.ProcessDefinition({'legs':my_leglist,
                                                         'model':mymodel})
            my_processes.append(my_process)

        for proc in decays:
            # Define the decays
            my_leglist = base_objects.MultiLegList([\
                base_objects.MultiLeg({'ids': id, 'state': True}) for id in proc])

            my_leglist[0].set('state', False)

            my_process = base_objects.ProcessDefinition({'legs':my_leglist,
                                                         'model':mymodel,
                                                         'is_decay_chain': True})
            decayprocs.append(my_process)

        for proc in my_processes:
            proc.set('decay_chains', decayprocs)
            
        decay_chains = diagram_generation.MultiProcess(my_processes,
                                                       collect_mirror_procs = True)

        dc_subproc_group = group_subprocs.DecayChainSubProcessGroup.\
              group_amplitudes(diagram_generation.DecayChainAmplitudeList(\
                               decay_chains.get('amplitudes')))

        subproc_groups = \
                       dc_subproc_group.generate_helas_decay_chain_subproc_groups()

        # Check number of groups
        self.assertEqual(len(subproc_groups), 2)
        self.assertEqual([g.get('name') for g in subproc_groups],
                         ['gq_zq_z_qq','qq_zg_z_qq'])

        subprocess_group = subproc_groups[0]
        matrix_elements = subprocess_group.get('matrix_elements')

        exporter = export_cpp.ProcessExporterPythia8(matrix_elements,
                                                 self.mycppwriter)

        # Test .h file output
        exporter.write_process_h_file(\
            writers.CPPWriter(self.give_pos('test.h')))

        goal_string = """//==========================================================================
// This file has been automatically generated for Pythia 8
// MadGraph5_aMC@NLO v. %(version)s, %(date)s
// By the MadGraph5_aMC@NLO Development Team
// Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#ifndef Pythia8_Sigma_sm_gd_ddxd_H
#define Pythia8_Sigma_sm_gd_ddxd_H

#include <complex> 

#include "SigmaProcess.h"
#include "Parameters_sm.h"

using namespace std; 

namespace Pythia8 
{
//==========================================================================
// A class for calculating the matrix elements for
// Process: g d > z d WEIGHTED=3
// *   Decay: z > d d~ WEIGHTED=2
// Process: g s > z s WEIGHTED=3
// *   Decay: z > d d~ WEIGHTED=2
// Process: g d > z d WEIGHTED=3
// *   Decay: z > u u~ WEIGHTED=2
// Process: g s > z s WEIGHTED=3
// *   Decay: z > u u~ WEIGHTED=2
// Process: g d > z d WEIGHTED=3
// *   Decay: z > s s~ WEIGHTED=2
// Process: g s > z s WEIGHTED=3
// *   Decay: z > s s~ WEIGHTED=2
// Process: g u > z u WEIGHTED=3
// *   Decay: z > d d~ WEIGHTED=2
// Process: g u > z u WEIGHTED=3
// *   Decay: z > s s~ WEIGHTED=2
// Process: g u > z u WEIGHTED=3
// *   Decay: z > u u~ WEIGHTED=2
// Process: g d~ > z d~ WEIGHTED=3
// *   Decay: z > d d~ WEIGHTED=2
// Process: g s~ > z s~ WEIGHTED=3
// *   Decay: z > d d~ WEIGHTED=2
// Process: g d~ > z d~ WEIGHTED=3
// *   Decay: z > u u~ WEIGHTED=2
// Process: g s~ > z s~ WEIGHTED=3
// *   Decay: z > u u~ WEIGHTED=2
// Process: g d~ > z d~ WEIGHTED=3
// *   Decay: z > s s~ WEIGHTED=2
// Process: g s~ > z s~ WEIGHTED=3
// *   Decay: z > s s~ WEIGHTED=2
// Process: g u~ > z u~ WEIGHTED=3
// *   Decay: z > d d~ WEIGHTED=2
// Process: g u~ > z u~ WEIGHTED=3
// *   Decay: z > s s~ WEIGHTED=2
// Process: g u~ > z u~ WEIGHTED=3
// *   Decay: z > u u~ WEIGHTED=2
//--------------------------------------------------------------------------

class Sigma_sm_gd_ddxd : public Sigma3Process 
{
  public:

    // Constructor.
    Sigma_sm_gd_ddxd() {}

    // Initialize process.
    virtual void initProc(); 

    // Calculate flavour-independent parts of cross section.
    virtual void sigmaKin(); 

    // Evaluate sigmaHat(sHat).
    virtual double sigmaHat(); 

    // Select flavour, colour and anticolour.
    virtual void setIdColAcol(); 

    // Evaluate weight for decay angles.
    virtual double weightDecay(Event& process, int iResBeg, int iResEnd); 

    // Info on the subprocess.
    virtual string name() const {return "g d > d d~ d (sm)";}

    virtual int code() const {return 10000;}

    virtual string inFlux() const {return "qg";}

    virtual int resonanceA() const {return 23;}
    // Tell Pythia that sigmaHat returns the ME^2
    virtual bool convertM2() const {return true;}

  private:

    // Private functions to calculate the matrix element for all subprocesses
    // Calculate wavefunctions
    void calculate_wavefunctions(const int perm[], const int hel[]); 
    static const int nwavefuncs = 13; 
    std::complex<double> w[nwavefuncs][18]; 
    static const int namplitudes = 18; 
    std::complex<double> amp[namplitudes]; 
    double matrix_gd_zd_z_ddx(); 
    double matrix_gd_zd_z_uux(); 
    double matrix_gd_zd_z_ssx(); 
    double matrix_gu_zu_z_ddx(); 
    double matrix_gu_zu_z_uux(); 
    double matrix_gdx_zdx_z_ddx(); 
    double matrix_gdx_zdx_z_uux(); 
    double matrix_gdx_zdx_z_ssx(); 
    double matrix_gux_zux_z_ddx(); 
    double matrix_gux_zux_z_uux(); 

    // Constants for array limits
    static const int nexternal = 5; 
    static const int nprocesses = 20; 

    // Store the matrix element value from sigmaKin
    double matrix_element[nprocesses]; 

    // Color flows, used when selecting color
    double * jamp2[nprocesses]; 

    // Pointer to the model parameters
    Parameters_sm * pars; 

}; 

}  // end namespace Pythia

#endif  // Pythia8_Sigma_sm_gd_ddxd_H
""" % misc.get_pkg_info()
        #print open(self.give_pos('test.h')).read()
        self.assertFileContains('test.h', goal_string)

        # Test .cc file output

        text = exporter.get_process_function_definitions()

        goal_string = """//==========================================================================
// Class member functions for calculating the matrix elements for
# Process: g d > z d WEIGHTED=3
# *   Decay: z > d d~ WEIGHTED=2
# Process: g s > z s WEIGHTED=3
# *   Decay: z > d d~ WEIGHTED=2
# Process: g d > z d WEIGHTED=3
# *   Decay: z > u u~ WEIGHTED=2
# Process: g s > z s WEIGHTED=3
# *   Decay: z > u u~ WEIGHTED=2
# Process: g d > z d WEIGHTED=3
# *   Decay: z > s s~ WEIGHTED=2
# Process: g s > z s WEIGHTED=3
# *   Decay: z > s s~ WEIGHTED=2
# Process: g u > z u WEIGHTED=3
# *   Decay: z > d d~ WEIGHTED=2
# Process: g u > z u WEIGHTED=3
# *   Decay: z > s s~ WEIGHTED=2
# Process: g u > z u WEIGHTED=3
# *   Decay: z > u u~ WEIGHTED=2
# Process: g d~ > z d~ WEIGHTED=3
# *   Decay: z > d d~ WEIGHTED=2
# Process: g s~ > z s~ WEIGHTED=3
# *   Decay: z > d d~ WEIGHTED=2
# Process: g d~ > z d~ WEIGHTED=3
# *   Decay: z > u u~ WEIGHTED=2
# Process: g s~ > z s~ WEIGHTED=3
# *   Decay: z > u u~ WEIGHTED=2
# Process: g d~ > z d~ WEIGHTED=3
# *   Decay: z > s s~ WEIGHTED=2
# Process: g s~ > z s~ WEIGHTED=3
# *   Decay: z > s s~ WEIGHTED=2
# Process: g u~ > z u~ WEIGHTED=3
# *   Decay: z > d d~ WEIGHTED=2
# Process: g u~ > z u~ WEIGHTED=3
# *   Decay: z > s s~ WEIGHTED=2
# Process: g u~ > z u~ WEIGHTED=3
# *   Decay: z > u u~ WEIGHTED=2

//--------------------------------------------------------------------------
// Initialize process. 
  
void Sigma_sm_gd_ddxd::initProc() {
// Instantiate the model class and set parameters that stay fixed during run
    pars = Parameters_sm::getInstance();
    pars->setIndependentParameters(particleDataPtr, couplingsPtr, slhaPtr);
    pars->setIndependentCouplings();
    // Set massive/massless matrix elements for c/b/mu/tau
mcME = 0.;
mbME = 0.;
mmuME = 0.;
mtauME = 0.;
jamp2[0] = new double[1];
jamp2[1] = new double[1];
jamp2[2] = new double[1];
jamp2[3] = new double[1];
jamp2[4] = new double[1];
jamp2[5] = new double[1];
jamp2[6] = new double[1];
jamp2[7] = new double[1];
jamp2[8] = new double[1];
jamp2[9] = new double[1];
} 

//--------------------------------------------------------------------------
// Evaluate |M|^2, part independent of incoming flavour. 

void Sigma_sm_gd_ddxd::sigmaKin() { 
    // Set the parameters which change event by event
    pars->setDependentParameters(particleDataPtr, couplingsPtr, slhaPtr, alpS);
    pars->setDependentCouplings();
    // Reset color flows
    for(int i=0;i < 1; i++)
            jamp2[0][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[1][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[2][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[3][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[4][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[5][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[6][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[7][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[8][i]=0.;
for(int i=0;i < 1; i++)
            jamp2[9][i]=0.;

    // Local variables and constants
const int ncomb = 32;
static bool goodhel[ncomb] = {ncomb * false};
static int ntry = 0, sum_hel = 0, ngood = 0;
static int igood[ncomb];
static int jhel;
double t[nprocesses];
// Helicities for the process
static const int helicities[ncomb][nexternal] = {{-1,-1,-1,-1,-1},{-1,-1,-1,-1,1},{-1,-1,-1,1,-1},{-1,-1,-1,1,1},{-1,-1,1,-1,-1},{-1,-1,1,-1,1},{-1,-1,1,1,-1},{-1,-1,1,1,1},{-1,1,-1,-1,-1},{-1,1,-1,-1,1},{-1,1,-1,1,-1},{-1,1,-1,1,1},{-1,1,1,-1,-1},{-1,1,1,-1,1},{-1,1,1,1,-1},{-1,1,1,1,1},{1,-1,-1,-1,-1},{1,-1,-1,-1,1},{1,-1,-1,1,-1},{1,-1,-1,1,1},{1,-1,1,-1,-1},{1,-1,1,-1,1},{1,-1,1,1,-1},{1,-1,1,1,1},{1,1,-1,-1,-1},{1,1,-1,-1,1},{1,1,-1,1,-1},{1,1,-1,1,1},{1,1,1,-1,-1},{1,1,1,-1,1},{1,1,1,1,-1},{1,1,1,1,1}};
// Denominators: spins, colors and identical particles
const int denominators[nprocesses] = {96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96,96};

ntry=ntry+1;

// Reset the matrix elements
for(int i = 0; i < nprocesses; i++){
    matrix_element[i] = 0.;
    t[i] = 0.;
}

// Define permutation
int perm[nexternal];
for(int i = 0; i < nexternal; i++){
  perm[i]=i;
}

// For now, call setupForME() here
id1 = 21;
id2 = 1;
if(!setupForME()){
    return;
}

if (sum_hel == 0 || ntry < 10){
// Calculate the matrix element for all helicities
  for(int ihel = 0; ihel < ncomb; ihel ++){
    if (goodhel[ihel] || ntry < 2){
      calculate_wavefunctions(perm, helicities[ihel]);
      t[0]=matrix_gd_zd_z_ddx();
t[1]=matrix_gd_zd_z_uux();
t[2]=matrix_gd_zd_z_ssx();
t[3]=matrix_gu_zu_z_ddx();
t[4]=matrix_gu_zu_z_uux();
t[5]=matrix_gdx_zdx_z_ddx();
t[6]=matrix_gdx_zdx_z_uux();
t[7]=matrix_gdx_zdx_z_ssx();
t[8]=matrix_gux_zux_z_ddx();
t[9]=matrix_gux_zux_z_uux();
             // Mirror initial state momenta for mirror process
                perm[0]=1;
                perm[1]=0;
                // Calculate wavefunctions
                calculate_wavefunctions(perm, helicities[ihel]);
                // Mirror back
                perm[0]=0;
                perm[1]=1;
                // Calculate matrix elements
                t[10]=matrix_gd_zd_z_ddx();
t[11]=matrix_gd_zd_z_uux();
t[12]=matrix_gd_zd_z_ssx();
t[13]=matrix_gu_zu_z_ddx();
t[14]=matrix_gu_zu_z_uux();
t[15]=matrix_gdx_zdx_z_ddx();
t[16]=matrix_gdx_zdx_z_uux();
t[17]=matrix_gdx_zdx_z_ssx();
t[18]=matrix_gux_zux_z_ddx();
t[19]=matrix_gux_zux_z_uux();
      double tsum = 0;
      for(int iproc = 0;iproc < nprocesses; iproc++){
         matrix_element[iproc]+=t[iproc];
         tsum += t[iproc];
      }
      // Store which helicities give non-zero result
      if (tsum != 0. && !goodhel[ihel]){
	goodhel[ihel]=true;
	ngood ++;
	igood[ngood] = ihel;
      }
    }
  }
  jhel = 0;
  sum_hel=min(sum_hel, ngood);
}
else              
{
// Only use the "good" helicities
  for(int j=0; j < sum_hel; j++){
    jhel++;
    if (jhel >= ngood) jhel=0;
    double hwgt = double(ngood)/double(sum_hel);
    int ihel = igood[jhel];
    calculate_wavefunctions(perm, helicities[ihel]);
    t[0]=matrix_gd_zd_z_ddx();
t[1]=matrix_gd_zd_z_uux();
t[2]=matrix_gd_zd_z_ssx();
t[3]=matrix_gu_zu_z_ddx();
t[4]=matrix_gu_zu_z_uux();
t[5]=matrix_gdx_zdx_z_ddx();
t[6]=matrix_gdx_zdx_z_uux();
t[7]=matrix_gdx_zdx_z_ssx();
t[8]=matrix_gux_zux_z_ddx();
t[9]=matrix_gux_zux_z_uux();
             // Mirror initial state momenta for mirror process
                perm[0]=1;
                perm[1]=0;
                // Calculate wavefunctions
                calculate_wavefunctions(perm, helicities[ihel]);
                // Mirror back
                perm[0]=0;
                perm[1]=1;
                // Calculate matrix elements
                t[10]=matrix_gd_zd_z_ddx();
t[11]=matrix_gd_zd_z_uux();
t[12]=matrix_gd_zd_z_ssx();
t[13]=matrix_gu_zu_z_ddx();
t[14]=matrix_gu_zu_z_uux();
t[15]=matrix_gdx_zdx_z_ddx();
t[16]=matrix_gdx_zdx_z_uux();
t[17]=matrix_gdx_zdx_z_ssx();
t[18]=matrix_gux_zux_z_ddx();
t[19]=matrix_gux_zux_z_uux();
    for(int iproc = 0;iproc < nprocesses; iproc++){
      matrix_element[iproc]+=t[iproc]*hwgt;
    }
  }
}

for (int i=0;i < nprocesses; i++)
    matrix_element[i] /= denominators[i];



}

//--------------------------------------------------------------------------
// Evaluate |M|^2, including incoming flavour dependence. 

double Sigma_sm_gd_ddxd::sigmaHat() {  
    // Select between the different processes
if(id1 == 21 && id2 == -2){
// Add matrix elements for processes with beams (21, -2)
return matrix_element[8]*2+matrix_element[9];
}
else if(id1 == -2 && id2 == 21){
// Add matrix elements for processes with beams (-2, 21)
return matrix_element[18]*2+matrix_element[19];
}
else if(id1 == -1 && id2 == 21){
// Add matrix elements for processes with beams (-1, 21)
return matrix_element[15]+matrix_element[16]+matrix_element[17];
}
else if(id1 == 1 && id2 == 21){
// Add matrix elements for processes with beams (1, 21)
return matrix_element[10]+matrix_element[11]+matrix_element[12];
}
else if(id1 == 21 && id2 == 1){
// Add matrix elements for processes with beams (21, 1)
return matrix_element[0]+matrix_element[1]+matrix_element[2];
}
else if(id1 == 2 && id2 == 21){
// Add matrix elements for processes with beams (2, 21)
return matrix_element[13]*2+matrix_element[14];
}
else if(id1 == 21 && id2 == 2){
// Add matrix elements for processes with beams (21, 2)
return matrix_element[3]*2+matrix_element[4];
}
else if(id1 == 21 && id2 == -3){
// Add matrix elements for processes with beams (21, -3)
return matrix_element[5]+matrix_element[6]+matrix_element[7];
}
else if(id1 == 21 && id2 == 3){
// Add matrix elements for processes with beams (21, 3)
return matrix_element[0]+matrix_element[1]+matrix_element[2];
}
else if(id1 == 21 && id2 == -1){
// Add matrix elements for processes with beams (21, -1)
return matrix_element[5]+matrix_element[6]+matrix_element[7];
}
else if(id1 == -3 && id2 == 21){
// Add matrix elements for processes with beams (-3, 21)
return matrix_element[15]+matrix_element[16]+matrix_element[17];
}
else if(id1 == 3 && id2 == 21){
// Add matrix elements for processes with beams (3, 21)
return matrix_element[10]+matrix_element[11]+matrix_element[12];
}
else {
// Return 0 if not correct initial state assignment
 return 0.;}
}

//--------------------------------------------------------------------------
// Select identity, colour and anticolour.

void Sigma_sm_gd_ddxd::setIdColAcol() {
    if(id1 == 21 && id2 == -2){
// Pick one of the flavor combinations (1, -1, -2), (2, -2, -2), (3, -3, -2)
int flavors[3][3] = {{1,-1,-2},{2,-2,-2},{3,-3,-2}};
vector<double> probs;
double sum = matrix_element[8]+matrix_element[9]+matrix_element[8];
probs.push_back(matrix_element[8]/sum);
probs.push_back(matrix_element[9]/sum);
probs.push_back(matrix_element[8]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == -2 && id2 == 21){
// Pick one of the flavor combinations 
int flavors[3][3] = {{1,-1,-2},{2,-2,-2},{3,-3,-2}};
vector<double> probs;
double sum = matrix_element[18]+matrix_element[19]+matrix_element[18];
probs.push_back(matrix_element[18]/sum);
probs.push_back(matrix_element[19]/sum);
probs.push_back(matrix_element[18]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == -1 && id2 == 21){
// Pick one of the flavor combinations 
int flavors[3][3] = {{1,-1,-1},{2,-2,-1},{3,-3,-1}};
vector<double> probs;
double sum = matrix_element[15]+matrix_element[16]+matrix_element[17];
probs.push_back(matrix_element[15]/sum);
probs.push_back(matrix_element[16]/sum);
probs.push_back(matrix_element[17]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 1 && id2 == 21){
// Pick one of the flavor combinations 
int flavors[3][3] = {{3,-3,1},{2,-2,1},{1,-1,1}};
vector<double> probs;
double sum = matrix_element[12]+matrix_element[11]+matrix_element[10];
probs.push_back(matrix_element[12]/sum);
probs.push_back(matrix_element[11]/sum);
probs.push_back(matrix_element[10]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 21 && id2 == 1){
// Pick one of the flavor combinations (3, -3, 1), (2, -2, 1), (1, -1, 1)
int flavors[3][3] = {{3,-3,1},{2,-2,1},{1,-1,1}};
vector<double> probs;
double sum = matrix_element[2]+matrix_element[1]+matrix_element[0];
probs.push_back(matrix_element[2]/sum);
probs.push_back(matrix_element[1]/sum);
probs.push_back(matrix_element[0]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 2 && id2 == 21){
// Pick one of the flavor combinations 
int flavors[3][3] = {{3,-3,2},{1,-1,2},{2,-2,2}};
vector<double> probs;
double sum = matrix_element[13]+matrix_element[13]+matrix_element[14];
probs.push_back(matrix_element[13]/sum);
probs.push_back(matrix_element[13]/sum);
probs.push_back(matrix_element[14]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 21 && id2 == 2){
// Pick one of the flavor combinations (3, -3, 2), (1, -1, 2), (2, -2, 2)
int flavors[3][3] = {{3,-3,2},{1,-1,2},{2,-2,2}};
vector<double> probs;
double sum = matrix_element[3]+matrix_element[3]+matrix_element[4];
probs.push_back(matrix_element[3]/sum);
probs.push_back(matrix_element[3]/sum);
probs.push_back(matrix_element[4]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 21 && id2 == -3){
// Pick one of the flavor combinations (2, -2, -3), (1, -1, -3), (3, -3, -3)
int flavors[3][3] = {{2,-2,-3},{1,-1,-3},{3,-3,-3}};
vector<double> probs;
double sum = matrix_element[6]+matrix_element[5]+matrix_element[7];
probs.push_back(matrix_element[6]/sum);
probs.push_back(matrix_element[5]/sum);
probs.push_back(matrix_element[7]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 21 && id2 == 3){
// Pick one of the flavor combinations (3, -3, 3), (1, -1, 3), (2, -2, 3)
int flavors[3][3] = {{3,-3,3},{1,-1,3},{2,-2,3}};
vector<double> probs;
double sum = matrix_element[2]+matrix_element[0]+matrix_element[1];
probs.push_back(matrix_element[2]/sum);
probs.push_back(matrix_element[0]/sum);
probs.push_back(matrix_element[1]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 21 && id2 == -1){
// Pick one of the flavor combinations (1, -1, -1), (2, -2, -1), (3, -3, -1)
int flavors[3][3] = {{1,-1,-1},{2,-2,-1},{3,-3,-1}};
vector<double> probs;
double sum = matrix_element[5]+matrix_element[6]+matrix_element[7];
probs.push_back(matrix_element[5]/sum);
probs.push_back(matrix_element[6]/sum);
probs.push_back(matrix_element[7]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == -3 && id2 == 21){
// Pick one of the flavor combinations 
int flavors[3][3] = {{2,-2,-3},{1,-1,-3},{3,-3,-3}};
vector<double> probs;
double sum = matrix_element[16]+matrix_element[15]+matrix_element[17];
probs.push_back(matrix_element[16]/sum);
probs.push_back(matrix_element[15]/sum);
probs.push_back(matrix_element[17]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
else if(id1 == 3 && id2 == 21){
// Pick one of the flavor combinations 
int flavors[3][3] = {{3,-3,3},{1,-1,3},{2,-2,3}};
vector<double> probs;
double sum = matrix_element[12]+matrix_element[10]+matrix_element[11];
probs.push_back(matrix_element[12]/sum);
probs.push_back(matrix_element[10]/sum);
probs.push_back(matrix_element[11]/sum);
int choice = rndmPtr->pick(probs);
id3 = flavors[choice][0];
id4 = flavors[choice][1];
id5 = flavors[choice][2];
}
setId(id1,id2,id3,id4,id5);
// Pick color flow
int ncolor[10] = {1,1,1,1,1,1,1,1,1,1};
if(id1 == 21&&id2 == 1&&id3 == 1&&id4 == -1&&id5 == 1||id1 == 21&&id2 == 3&&id3 == 1&&id4 == -1&&id5 == 3){
vector<double> probs;
                  double sum = jamp2[0][0];
                  for(int i=0;i<ncolor[0];i++)
                  probs.push_back(jamp2[0][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{2,3,3,0,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == 1&&id3 == 2&&id4 == -2&&id5 == 1||id1 == 21&&id2 == 3&&id3 == 2&&id4 == -2&&id5 == 3){
vector<double> probs;
                  double sum = jamp2[1][0];
                  for(int i=0;i<ncolor[1];i++)
                  probs.push_back(jamp2[1][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{2,3,3,0,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == 1&&id3 == 3&&id4 == -3&&id5 == 1||id1 == 21&&id2 == 3&&id3 == 3&&id4 == -3&&id5 == 3){
vector<double> probs;
                  double sum = jamp2[2][0];
                  for(int i=0;i<ncolor[2];i++)
                  probs.push_back(jamp2[2][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{2,3,3,0,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == 2&&id3 == 1&&id4 == -1&&id5 == 2||id1 == 21&&id2 == 2&&id3 == 3&&id4 == -3&&id5 == 2){
vector<double> probs;
                  double sum = jamp2[3][0];
                  for(int i=0;i<ncolor[3];i++)
                  probs.push_back(jamp2[3][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{2,3,3,0,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == 2&&id3 == 2&&id4 == -2&&id5 == 2){
vector<double> probs;
                  double sum = jamp2[4][0];
                  for(int i=0;i<ncolor[4];i++)
                  probs.push_back(jamp2[4][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{2,3,3,0,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == -1&&id3 == 1&&id4 == -1&&id5 == -1||id1 == 21&&id2 == -3&&id3 == 1&&id4 == -1&&id5 == -3){
vector<double> probs;
                  double sum = jamp2[5][0];
                  for(int i=0;i<ncolor[5];i++)
                  probs.push_back(jamp2[5][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{1,3,0,1,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == -1&&id3 == 2&&id4 == -2&&id5 == -1||id1 == 21&&id2 == -3&&id3 == 2&&id4 == -2&&id5 == -3){
vector<double> probs;
                  double sum = jamp2[6][0];
                  for(int i=0;i<ncolor[6];i++)
                  probs.push_back(jamp2[6][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{1,3,0,1,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == -1&&id3 == 3&&id4 == -3&&id5 == -1||id1 == 21&&id2 == -3&&id3 == 3&&id4 == -3&&id5 == -3){
vector<double> probs;
                  double sum = jamp2[7][0];
                  for(int i=0;i<ncolor[7];i++)
                  probs.push_back(jamp2[7][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{1,3,0,1,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == -2&&id3 == 1&&id4 == -1&&id5 == -2||id1 == 21&&id2 == -2&&id3 == 3&&id4 == -3&&id5 == -2){
vector<double> probs;
                  double sum = jamp2[8][0];
                  for(int i=0;i<ncolor[8];i++)
                  probs.push_back(jamp2[8][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{1,3,0,1,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 21&&id2 == -2&&id3 == 2&&id4 == -2&&id5 == -2){
vector<double> probs;
                  double sum = jamp2[9][0];
                  for(int i=0;i<ncolor[9];i++)
                  probs.push_back(jamp2[9][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{1,3,0,1,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 1&&id2 == 21&&id3 == 1&&id4 == -1&&id5 == 1||id1 == 3&&id2 == 21&&id3 == 1&&id4 == -1&&id5 == 3){
vector<double> probs;
                  double sum = jamp2[0][0];
                  for(int i=0;i<ncolor[0];i++)
                  probs.push_back(jamp2[0][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{3,0,2,3,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 1&&id2 == 21&&id3 == 2&&id4 == -2&&id5 == 1||id1 == 3&&id2 == 21&&id3 == 2&&id4 == -2&&id5 == 3){
vector<double> probs;
                  double sum = jamp2[1][0];
                  for(int i=0;i<ncolor[1];i++)
                  probs.push_back(jamp2[1][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{3,0,2,3,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 1&&id2 == 21&&id3 == 3&&id4 == -3&&id5 == 1||id1 == 3&&id2 == 21&&id3 == 3&&id4 == -3&&id5 == 3){
vector<double> probs;
                  double sum = jamp2[2][0];
                  for(int i=0;i<ncolor[2];i++)
                  probs.push_back(jamp2[2][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{3,0,2,3,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 2&&id2 == 21&&id3 == 1&&id4 == -1&&id5 == 2||id1 == 2&&id2 == 21&&id3 == 3&&id4 == -3&&id5 == 2){
vector<double> probs;
                  double sum = jamp2[3][0];
                  for(int i=0;i<ncolor[3];i++)
                  probs.push_back(jamp2[3][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{3,0,2,3,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == 2&&id2 == 21&&id3 == 2&&id4 == -2&&id5 == 2){
vector<double> probs;
                  double sum = jamp2[4][0];
                  for(int i=0;i<ncolor[4];i++)
                  probs.push_back(jamp2[4][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{3,0,2,3,1,0,0,1,2,0}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == -1&&id2 == 21&&id3 == 1&&id4 == -1&&id5 == -1||id1 == -3&&id2 == 21&&id3 == 1&&id4 == -1&&id5 == -3){
vector<double> probs;
                  double sum = jamp2[5][0];
                  for(int i=0;i<ncolor[5];i++)
                  probs.push_back(jamp2[5][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{0,1,1,3,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == -1&&id2 == 21&&id3 == 2&&id4 == -2&&id5 == -1||id1 == -3&&id2 == 21&&id3 == 2&&id4 == -2&&id5 == -3){
vector<double> probs;
                  double sum = jamp2[6][0];
                  for(int i=0;i<ncolor[6];i++)
                  probs.push_back(jamp2[6][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{0,1,1,3,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == -1&&id2 == 21&&id3 == 3&&id4 == -3&&id5 == -1||id1 == -3&&id2 == 21&&id3 == 3&&id4 == -3&&id5 == -3){
vector<double> probs;
                  double sum = jamp2[7][0];
                  for(int i=0;i<ncolor[7];i++)
                  probs.push_back(jamp2[7][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{0,1,1,3,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == -2&&id2 == 21&&id3 == 1&&id4 == -1&&id5 == -2||id1 == -2&&id2 == 21&&id3 == 3&&id4 == -3&&id5 == -2){
vector<double> probs;
                  double sum = jamp2[8][0];
                  for(int i=0;i<ncolor[8];i++)
                  probs.push_back(jamp2[8][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{0,1,1,3,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
else if(id1 == -2&&id2 == 21&&id3 == 2&&id4 == -2&&id5 == -2){
vector<double> probs;
                  double sum = jamp2[9][0];
                  for(int i=0;i<ncolor[9];i++)
                  probs.push_back(jamp2[9][i]/sum);
                  int ic = rndmPtr->pick(probs);
static int colors[1][10] = {{0,1,1,3,2,0,0,2,0,3}};
setColAcol(colors[ic][0],colors[ic][1],colors[ic][2],colors[ic][3],colors[ic][4],colors[ic][5],colors[ic][6],colors[ic][7],colors[ic][8],colors[ic][9]);
}
}

//--------------------------------------------------------------------------
// Evaluate weight for angles of decay products in process 

double Sigma_sm_gd_ddxd::weightDecay(Event& process, int iResBeg, int iResEnd) {
    // Just use isotropic decay (default)
return 1.;
}

//==========================================================================
// Private class member functions

//--------------------------------------------------------------------------
// Evaluate |M|^2 for each subprocess

void Sigma_sm_gd_ddxd::calculate_wavefunctions(const int perm[], const int hel[]){
// Calculate wavefunctions for all processes
double p[nexternal][4];
int i;
 
// Convert Pythia 4-vectors to double[]
for(i=0;i < nexternal;i++){
    p[i][0] = pME[i].e();
    p[i][1] = pME[i].px();
    p[i][2] = pME[i].py();
    p[i][3] = pME[i].pz();
}

// Calculate all wavefunctions
vxxxxx(p[perm[0]],mME[0],hel[0],-1,w[0]);
ixxxxx(p[perm[1]],mME[1],hel[1],+1,w[1]);
oxxxxx(p[perm[2]],mME[2],hel[2],+1,w[2]);
ixxxxx(p[perm[3]],mME[3],hel[3],-1,w[3]);
FFV1_3(w[3],w[2],pars->GDZ2,pars->MZ,pars->WZ,w[4]);
oxxxxx(p[perm[4]],mME[4],hel[4],+1,w[5]);
FFV1_2(w[1],w[0],pars->GQQ,pars->zero,pars->zero,w[6]);
FFV1_1(w[5],w[0],pars->GQQ,pars->zero,pars->zero,w[7]);
FFV1_2_3(w[3],w[2],pars->GUZ1,pars->GUZ2,pars->MZ,pars->WZ,w[8]);
oxxxxx(p[perm[1]],mME[1],hel[1],-1,w[9]);
ixxxxx(p[perm[4]],mME[4],hel[4],-1,w[10]);
FFV1_2(w[10],w[0],pars->GQQ,pars->zero,pars->zero,w[11]);
FFV1_1(w[9],w[0],pars->GQQ,pars->zero,pars->zero,w[12]);

// Calculate all amplitudes
# Amplitude(s) for diagram number 0
FFV1_0(w[6],w[5],w[4],pars->GDZ2,amp[0]);
FFV1_0(w[1],w[7],w[4],pars->GDZ2,amp[1]);
FFV1_0(w[6],w[5],w[8],pars->GDZ2,amp[2]);
FFV1_0(w[1],w[7],w[8],pars->GDZ2,amp[3]);
FFV1_2_0(w[6],w[5],w[4],pars->GUZ1,pars->GUZ2,amp[4]);
FFV1_2_0(w[1],w[7],w[4],pars->GUZ1,pars->GUZ2,amp[5]);
FFV1_2_0(w[6],w[5],w[8],pars->GUZ1,pars->GUZ2,amp[6]);
FFV1_2_0(w[1],w[7],w[8],pars->GUZ1,pars->GUZ2,amp[7]);
FFV1_0(w[11],w[9],w[4],pars->GDZ2,amp[8]);
FFV1_0(w[10],w[12],w[4],pars->GDZ2,amp[9]);
FFV1_0(w[11],w[9],w[8],pars->GDZ2,amp[10]);
FFV1_0(w[10],w[12],w[8],pars->GDZ2,amp[11]);
FFV1_0(w[11],w[9],w[4],pars->GDZ2,amp[12]);
FFV1_0(w[10],w[12],w[4],pars->GDZ2,amp[13]);
FFV1_2_0(w[11],w[9],w[4],pars->GUZ1,pars->GUZ2,amp[14]);
FFV1_2_0(w[10],w[12],w[4],pars->GUZ1,pars->GUZ2,amp[15]);
FFV1_2_0(w[11],w[9],w[8],pars->GUZ1,pars->GUZ2,amp[16]);
FFV1_2_0(w[10],w[12],w[8],pars->GUZ1,pars->GUZ2,amp[17]);


}
double Sigma_sm_gd_ddxd::matrix_gd_zd_z_ddx() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=-amp[0]-amp[1];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[0][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gd_zd_z_uux() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=-amp[2]-amp[3];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[1][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gd_zd_z_ssx() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=-amp[0]-amp[1];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[2][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gu_zu_z_ddx() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=-amp[4]-amp[5];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[3][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gu_zu_z_uux() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=-amp[6]-amp[7];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[4][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gdx_zdx_z_ddx() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=+amp[8]+amp[9];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[5][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gdx_zdx_z_uux() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=+amp[10]+amp[11];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[6][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gdx_zdx_z_ssx() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=+amp[12]+amp[13];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[7][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gux_zux_z_ddx() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=+amp[14]+amp[15];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[8][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

double Sigma_sm_gd_ddxd::matrix_gux_zux_z_uux() { 
int i, j;
// Local variables
const int ngraphs = 2;
const int ncolor = 1;
std::complex<double> ztemp;
std::complex<double> jamp[ncolor];
// The color matrix;
static const double denom[ncolor] = {1};
static const double cf[ncolor][ncolor] = {{12}};

// Calculate color flows
jamp[0]=+amp[16]+amp[17];

// Sum and square the color flows to get the matrix element
double matrix = 0;
for(i=0;i < ncolor; i++){
  ztemp = 0.;
  for(j = 0; j < ncolor; j++)
    ztemp = ztemp + cf[i][j]*jamp[j];
  matrix = matrix+real(ztemp*conj(jamp[i]))/denom[i];
}

// Store the leading color flows for choice of color
for(i=0;i < ncolor; i++)
    jamp2[9][i] += real(jamp[i]*conj(jamp[i]));
    
return matrix;
}

"""

        self.assertEqual(text.replace('\t', '    ').split('\n'), 
                         goal_string.replace('\t', '    ').split('\n'))        
        



    def test_write_cpp_go_process_cc_file(self):
        """Test writing the .cc C++ standalone file for u u~ > go go"""

        myleglist = base_objects.LegList()

        myleglist.append(base_objects.Leg({'id':2,
                                         'state':False}))
        myleglist.append(base_objects.Leg({'id':-2,
                                         'state':False}))
        myleglist.append(base_objects.Leg({'id':1000021,
                                         'state':True}))
        myleglist.append(base_objects.Leg({'id':1000021,
                                         'state':True}))

        myproc = base_objects.Process({'legs':myleglist,
                                       'model':self.mymodel})
        
        myamplitude = diagram_generation.Amplitude({'process': myproc})

        matrix_element = helas_objects.HelasMultiProcess(myamplitude)
        matrix_element.get('matrix_elements')[0].set('has_mirror_process',
                                                     True)

        goal_string = \
"""//==========================================================================
// This file has been automatically generated for C++ Standalone by
// MadGraph5_aMC@NLO v. %(version)s, %(date)s
// By the MadGraph5_aMC@NLO Development Team
// Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#include "CPPProcess.h"
#include "HelAmps_sm.h"

using namespace MG5_sm; 

//==========================================================================
// Class member functions for calculating the matrix elements for
// Process: u u~ > go go

//--------------------------------------------------------------------------
// Initialize process.

void CPPProcess::initProc(string param_card_name) 
{
  // Instantiate the model class and set parameters that stay fixed during run
  pars = Parameters_sm::getInstance(); 
  SLHAReader slha(param_card_name); 
  pars->setIndependentParameters(slha); 
  pars->setIndependentCouplings(); 
  pars->printIndependentParameters(); 
  pars->printIndependentCouplings(); 
  // Set external particle masses for this matrix element
  mME.push_back(pars->ZERO); 
  mME.push_back(pars->ZERO); 
  mME.push_back(pars->MGO); 
  mME.push_back(pars->MGO); 
  jamp2[0] = new double[2]; 
}

//--------------------------------------------------------------------------
// Evaluate |M|^2, part independent of incoming flavour.

void CPPProcess::sigmaKin() 
{
  // Set the parameters which change event by event
  pars->setDependentParameters(); 
  pars->setDependentCouplings(); 
  static bool firsttime = true; 
  if (firsttime)
  {
    pars->printDependentParameters(); 
    pars->printDependentCouplings(); 
    firsttime = false; 
  }

  // Reset color flows
  for(int i = 0; i < 2; i++ )
    jamp2[0][i] = 0.; 

  // Local variables and constants
  const int ncomb = 16; 
  static bool goodhel[ncomb] = {ncomb * false}; 
  static int ntry = 0, sum_hel = 0, ngood = 0; 
  static int igood[ncomb]; 
  static int jhel; 
  std::complex<double> * * wfs; 
  double t[nprocesses]; 
  // Helicities for the process
  static const int helicities[ncomb][nexternal] = {{-1, -1, -1, -1}, {-1, -1,
      -1, 1}, {-1, -1, 1, -1}, {-1, -1, 1, 1}, {-1, 1, -1, -1}, {-1, 1, -1, 1},
      {-1, 1, 1, -1}, {-1, 1, 1, 1}, {1, -1, -1, -1}, {1, -1, -1, 1}, {1, -1,
      1, -1}, {1, -1, 1, 1}, {1, 1, -1, -1}, {1, 1, -1, 1}, {1, 1, 1, -1}, {1,
      1, 1, 1}};
  // Denominators: spins, colors and identical particles
  const int denominators[nprocesses] = {72, 72}; 

  ntry = ntry + 1; 

  // Reset the matrix elements
  for(int i = 0; i < nprocesses; i++ )
  {
    matrix_element[i] = 0.; 
  }
  // Define permutation
  int perm[nexternal]; 
  for(int i = 0; i < nexternal; i++ )
  {
    perm[i] = i; 
  }

  if (sum_hel == 0 || ntry < 10)
  {
    // Calculate the matrix element for all helicities
    for(int ihel = 0; ihel < ncomb; ihel++ )
    {
      if (goodhel[ihel] || ntry < 2)
      {
        calculate_wavefunctions(perm, helicities[ihel]); 
        t[0] = matrix_uux_gogo(); 
        // Mirror initial state momenta for mirror process
        perm[0] = 1; 
        perm[1] = 0; 
        // Calculate wavefunctions
        calculate_wavefunctions(perm, helicities[ihel]); 
        // Mirror back
        perm[0] = 0; 
        perm[1] = 1; 
        // Calculate matrix elements
        t[1] = matrix_uux_gogo(); 
        double tsum = 0; 
        for(int iproc = 0; iproc < nprocesses; iproc++ )
        {
          matrix_element[iproc] += t[iproc]; 
          tsum += t[iproc]; 
        }
        // Store which helicities give non-zero result
        if (tsum != 0. && !goodhel[ihel])
        {
          goodhel[ihel] = true; 
          ngood++; 
          igood[ngood] = ihel; 
        }
      }
    }
    jhel = 0; 
    sum_hel = min(sum_hel, ngood); 
  }
  else
  {
    // Only use the "good" helicities
    for(int j = 0; j < sum_hel; j++ )
    {
      jhel++; 
      if (jhel >= ngood)
        jhel = 0; 
      double hwgt = double(ngood)/double(sum_hel); 
      int ihel = igood[jhel]; 
      calculate_wavefunctions(perm, helicities[ihel]); 
      t[0] = matrix_uux_gogo(); 
      // Mirror initial state momenta for mirror process
      perm[0] = 1; 
      perm[1] = 0; 
      // Calculate wavefunctions
      calculate_wavefunctions(perm, helicities[ihel]); 
      // Mirror back
      perm[0] = 0; 
      perm[1] = 1; 
      // Calculate matrix elements
      t[1] = matrix_uux_gogo(); 
      for(int iproc = 0; iproc < nprocesses; iproc++ )
      {
        matrix_element[iproc] += t[iproc] * hwgt; 
      }
    }
  }

  for (int i = 0; i < nprocesses; i++ )
    matrix_element[i] /= denominators[i]; 



}

//--------------------------------------------------------------------------
// Evaluate |M|^2, including incoming flavour dependence.

double CPPProcess::sigmaHat() 
{
  // Select between the different processes
  if(id1 == 2 && id2 == -2)
  {
    // Add matrix elements for processes with beams (2, -2)
    return matrix_element[0]; 
  }
  else if(id1 == -2 && id2 == 2)
  {
    // Add matrix elements for processes with beams (-2, 2)
    return matrix_element[1]; 
  }
  else
  {
    // Return 0 if not correct initial state assignment
    return 0.; 
  }
}

//==========================================================================
// Private class member functions

//--------------------------------------------------------------------------
// Evaluate |M|^2 for each subprocess

void CPPProcess::calculate_wavefunctions(const int perm[], const int hel[])
{
  // Calculate wavefunctions for all processes
  int i, j; 

  // Calculate all wavefunctions
  ixxxxx(p[perm[0]], mME[0], hel[0], +1, w[0]); 
  oxxxxx(p[perm[1]], mME[1], hel[1], -1, w[1]); 
  ixxxxx(p[perm[2]], mME[2], hel[2], -1, w[2]); 
  oxxxxx(p[perm[3]], mME[3], hel[3], +1, w[3]); 
  FFV1_3(w[0], w[1], pars->GC_10, pars->ZERO, pars->ZERO, w[4]); 

  // Calculate all amplitudes
  // Amplitude(s) for diagram number 0
  FFV1_0(w[2], w[3], w[4], pars->GC_8, amp[0]); 

}
double CPPProcess::matrix_uux_gogo() 
{
  int i, j; 
  // Local variables
  const int ngraphs = 1; 
  const int ncolor = 2; 
  std::complex<double> ztemp; 
  std::complex<double> jamp[ncolor]; 
  // The color matrix;
  static const double denom[ncolor] = {3, 3}; 
  static const double cf[ncolor][ncolor] = {{16, -2}, {-2, 16}}; 

  // Calculate color flows
  jamp[0] = -std::complex<double> (0, 1) * amp[0]; 
  jamp[1] = +std::complex<double> (0, 1) * amp[0]; 

  // Sum and square the color flows to get the matrix element
  double matrix = 0; 
  for(i = 0; i < ncolor; i++ )
  {
    ztemp = 0.; 
    for(j = 0; j < ncolor; j++ )
      ztemp = ztemp + cf[i][j] * jamp[j]; 
    matrix = matrix + real(ztemp * conj(jamp[i]))/denom[i]; 
  }

  // Store the leading color flows for choice of color
  for(i = 0; i < ncolor; i++ )
    jamp2[0][i] += real(jamp[i] * conj(jamp[i])); 

  return matrix; 
}



""" % misc.get_pkg_info()

        exporter = export_cpp.ProcessExporterCPP(matrix_element,
                                                 self.mycppwriter)

        exporter.write_process_cc_file(\
                  writers.CPPWriter(self.give_pos('test.cc')))

        #print open(self.give_pos('test.cc')).read()
        self.assertFileContains('test.cc', goal_string)

    def disabled_test_write_process_files(self):
        """Test writing the .h  and .cc Pythia file for a matrix element"""

        export_cpp.generate_process_files_pythia8(self.mymatrixelement,
                                                      self.mycppwriter,
                                                      process_string = "q q~ > q q~",
                                                      path = "/tmp")
        
        print "Please try compiling the file /tmp/Sigma_sm_qqx_qqx.cc:"
        print "cd /tmp; g++ -c -I $PATH_TO_PYTHIA8/include Sigma_sm_qqx_qqx.cc.cc"


#===============================================================================
# ExportUFOModelPythia8Test
#===============================================================================
class ExportUFOModelPythia8Test(unittest.TestCase,
                                test_file_writers.CheckFileCreate):

    created_files = [
                    ]

    def setUp(self):

        model_pkl = os.path.join(MG5DIR, 'models','sm','model.pkl')
        if os.path.isfile(model_pkl):
            self.model = save_load_object.load_from_file(model_pkl)
        else:
            sm_path = import_ufo.find_ufo_path('sm')
            self.model = import_ufo.import_model(sm_path)
        self.model_builder = export_cpp.UFOModelConverterPythia8(\
                                             self.model, "/tmp")
        
        test_file_writers.CheckFileCreate.clean_files

    tearDown = test_file_writers.CheckFileCreate.clean_files

    def test_write_pythia8_parameter_files(self):
        """Test writing the Pythia model parameter files"""

        goal_file_h = \
"""//==========================================================================
// This file has been automatically generated for Pythia 8
#  MadGraph5_aMC@NLO v. %(version)s, %(date)s
#  By the MadGraph5_aMC@NLO Development Team
#  Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#ifndef Pythia8_parameters_sm_H
#define Pythia8_parameters_sm_H

#include <complex>

#include "ParticleData.h"
#include "StandardModel.h"
#include "SusyLesHouches.h"

using namespace std;

namespace Pythia8 {

class Parameters_sm
{
public:

static Parameters_sm* getInstance();

// Model parameters independent of aS
double WTau,WH,WT,WW,WZ,MTA,MM,Me,MH,MB,MT,MC,MZ,ymtau,ymm,yme,ymt,ymb,ymc,etaWS,rhoWS,AWS,lamWS,Gf,aEWM1,ZERO,lamWS__exp__2,lamWS__exp__3,MZ__exp__2,MZ__exp__4,sqrt__2,MH__exp__2,aEW,MW,sqrt__aEW,ee,MW__exp__2,sw2,cw,sqrt__sw2,sw,g1,gw,vev,vev__exp__2,lam,yb,yc,ye,ym,yt,ytau,muH,ee__exp__2,sw__exp__2,cw__exp__2;
std::complex<double> CKM1x1,CKM1x2,complexi,CKM1x3,CKM2x1,CKM2x2,CKM2x3,CKM3x1,CKM3x2,CKM3x3,conjg__CKM1x3,conjg__CKM2x3,conjg__CKM3x3,conjg__CKM2x1,conjg__CKM3x1,conjg__CKM2x2,conjg__CKM3x2,conjg__CKM1x1,conjg__CKM1x2,I1x31,I1x32,I1x33,I2x12,I2x13,I2x22,I2x23,I2x32,I2x33,I3x21,I3x22,I3x23,I3x31,I3x32,I3x33,I4x13,I4x23,I4x33;
// Model parameters dependent on aS
double aS,sqrt__aS,G,G__exp__2;
// Model couplings independent of aS
std::complex<double> GC_1,GC_2,GC_3,GC_4,GC_5,GC_6,GC_7,GC_8,GC_9,GC_13,GC_14,GC_15,GC_16,GC_17,GC_18,GC_19,GC_20,GC_21,GC_22,GC_23,GC_24,GC_25,GC_26,GC_27,GC_28,GC_29,GC_30,GC_31,GC_32,GC_33,GC_34,GC_35,GC_36,GC_37,GC_38,GC_39,GC_40,GC_41,GC_42,GC_43,GC_44,GC_45,GC_46,GC_47,GC_48,GC_49,GC_50,GC_51,GC_52,GC_53,GC_54,GC_55,GC_56,GC_57,GC_58,GC_59,GC_60,GC_61,GC_62,GC_63,GC_64,GC_65,GC_66,GC_67,GC_68,GC_69,GC_70,GC_71,GC_72,GC_73,GC_74,GC_75,GC_76,GC_77,GC_78,GC_79,GC_80,GC_81,GC_82,GC_83,GC_84,GC_85,GC_86,GC_87,GC_88,GC_89,GC_90,GC_91,GC_92,GC_93,GC_94,GC_95,GC_96,GC_97,GC_98,GC_99,GC_100,GC_101,GC_102,GC_103,GC_104,GC_105,GC_106,GC_107,GC_108;
// Model couplings dependent on aS
std::complex<double> GC_12,GC_11,GC_10;

// Set parameters that are unchanged during the run
void setIndependentParameters(ParticleData*& pd, Couplings*& csm, SusyLesHouches*& slhaPtr);
// Set couplings that are unchanged during the run
void setIndependentCouplings();
// Set parameters that are changed event by event
void setDependentParameters(ParticleData*& pd, Couplings*& csm, SusyLesHouches*& slhaPtr, double alpS);
// Set couplings that are changed event by event
void setDependentCouplings();

// Print parameters that are unchanged during the run
void printIndependentParameters();
// Print couplings that are unchanged during the run
void printIndependentCouplings();
// Print parameters that are changed event by event
void printDependentParameters();
// Print couplings that are changed event by event
void printDependentCouplings();


  private:
static Parameters_sm* instance;
};

} // end namespace Pythia8
#endif // Pythia8_parameters_sm_H
"""% misc.get_pkg_info()


        goal_file_cc = \
"""//==========================================================================
// This file has been automatically generated for Pythia 8 by
#  MadGraph5_aMC@NLO v. %(version)s, %(date)s
#  By the MadGraph5_aMC@NLO Development Team
#  Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#include <iostream>
#include "Parameters_sm.h"
#include "PythiaStdlib.h"

namespace Pythia8 {

    // Initialize static instance
    Parameters_sm* Parameters_sm::instance = 0;

    // Function to get static instance - only one instance per program
    Parameters_sm* Parameters_sm::getInstance(){
    if (instance == 0)
        instance = new Parameters_sm();

    return instance;
    }

    void Parameters_sm::setIndependentParameters(ParticleData*& pd, Couplings*& csm, SusyLesHouches*& slhaPtr){
    WTau=pd->mWidth(15);
WH=pd->mWidth(25);
WT=pd->mWidth(6);
WW=pd->mWidth(24);
WZ=pd->mWidth(23);
MTA=pd->m0(15);
MM=pd->m0(13);
Me=pd->m0(11);
MH=pd->m0(25);
MB=pd->m0(5);
MT=pd->m0(6);
MC=pd->m0(4);
MZ=pd->m0(23);
ymtau=pd->mRun(15, pd->m0(24));
ymm=pd->mRun(13, pd->m0(24));
yme=pd->mRun(11, pd->m0(24));
ymt=pd->mRun(6, pd->m0(24));
ymb=pd->mRun(5, pd->m0(24));
ymc=pd->mRun(4, pd->m0(24));
if(!slhaPtr->getEntry<double>("wolfenstein", 4, etaWS)){
cout << "Warning, setting etaWS to 3.410000e-01" << endl;
etaWS = 3.410000e-01;}
if(!slhaPtr->getEntry<double>("wolfenstein", 3, rhoWS)){
cout << "Warning, setting rhoWS to 1.320000e-01" << endl;
rhoWS = 1.320000e-01;}
if(!slhaPtr->getEntry<double>("wolfenstein", 2, AWS)){
cout << "Warning, setting AWS to 8.080000e-01" << endl;
AWS = 8.080000e-01;}
if(!slhaPtr->getEntry<double>("wolfenstein", 1, lamWS)){
cout << "Warning, setting lamWS to 2.253000e-01" << endl;
lamWS = 2.253000e-01;}
Gf = M_PI*csm->alphaEM(pow(pd->m0(23),2))*pow(pd->m0(23),2)/(sqrt(2.)*pow(pd->m0(24),2)*(pow(pd->m0(23),2)-pow(pd->m0(24),2)));
aEWM1 = 1./csm->alphaEM(pow(pd->m0(23),2));
ZERO = 0.;
lamWS__exp__2 = pow(lamWS,2.);
CKM1x1 = 1.-lamWS__exp__2/2.;
CKM1x2 = lamWS;
complexi = std::complex<double>(0.,1.);
lamWS__exp__3 = pow(lamWS,3.);
CKM1x3 = AWS*lamWS__exp__3*(-(etaWS*complexi)+rhoWS);
CKM2x1 = -lamWS;
CKM2x2 = 1.-lamWS__exp__2/2.;
CKM2x3 = AWS*lamWS__exp__2;
CKM3x1 = AWS*lamWS__exp__3*(1.-etaWS*complexi-rhoWS);
CKM3x2 = -(AWS*lamWS__exp__2);
CKM3x3 = 1.;
MZ__exp__2 = pow(MZ,2.);
MZ__exp__4 = pow(MZ,4.);
sqrt__2 = sqrt(2.);
MH__exp__2 = pow(MH,2.);
conjg__CKM1x3 = conj(CKM1x3);
conjg__CKM2x3 = conj(CKM2x3);
conjg__CKM3x3 = conj(CKM3x3);
conjg__CKM2x1 = conj(CKM2x1);
conjg__CKM3x1 = conj(CKM3x1);
conjg__CKM2x2 = conj(CKM2x2);
conjg__CKM3x2 = conj(CKM3x2);
conjg__CKM1x1 = conj(CKM1x1);
conjg__CKM1x2 = conj(CKM1x2);
aEW = 1./aEWM1;
MW = sqrt(MZ__exp__2/2.+sqrt(MZ__exp__4/4.-(aEW*M_PI*MZ__exp__2)/(Gf*sqrt__2)));
sqrt__aEW = sqrt(aEW);
ee = 2.*sqrt__aEW*sqrt(M_PI);
MW__exp__2 = pow(MW,2.);
sw2 = 1.-MW__exp__2/MZ__exp__2;
cw = sqrt(1.-sw2);
sqrt__sw2 = sqrt(sw2);
sw = sqrt__sw2;
g1 = ee/cw;
gw = ee/sw;
vev = (2.*MW*sw)/ee;
vev__exp__2 = pow(vev,2.);
lam = MH__exp__2/(2.*vev__exp__2);
yb = (ymb*sqrt__2)/vev;
yc = (ymc*sqrt__2)/vev;
ye = (yme*sqrt__2)/vev;
ym = (ymm*sqrt__2)/vev;
yt = (ymt*sqrt__2)/vev;
ytau = (ymtau*sqrt__2)/vev;
muH = sqrt(lam*vev__exp__2);
I1x31 = yb*conjg__CKM1x3;
I1x32 = yb*conjg__CKM2x3;
I1x33 = yb*conjg__CKM3x3;
I2x12 = yc*conjg__CKM2x1;
I2x13 = yt*conjg__CKM3x1;
I2x22 = yc*conjg__CKM2x2;
I2x23 = yt*conjg__CKM3x2;
I2x32 = yc*conjg__CKM2x3;
I2x33 = yt*conjg__CKM3x3;
I3x21 = CKM2x1*yc;
I3x22 = CKM2x2*yc;
I3x23 = CKM2x3*yc;
I3x31 = CKM3x1*yt;
I3x32 = CKM3x2*yt;
I3x33 = CKM3x3*yt;
I4x13 = CKM1x3*yb;
I4x23 = CKM2x3*yb;
I4x33 = CKM3x3*yb;
ee__exp__2 = pow(ee,2.);
sw__exp__2 = pow(sw,2.);
cw__exp__2 = pow(cw,2.);
    }
    void Parameters_sm::setIndependentCouplings(){
    GC_1 = -(ee*complexi)/3.;
GC_2 = (2.*ee*complexi)/3.;
GC_3 = -(ee*complexi);
GC_4 = ee*complexi;
GC_5 = ee__exp__2*complexi;
GC_6 = 2.*ee__exp__2*complexi;
GC_7 = -ee__exp__2/(2.*cw);
GC_8 = (ee__exp__2*complexi)/(2.*cw);
GC_9 = ee__exp__2/(2.*cw);
GC_13 = I1x31;
GC_14 = I1x32;
GC_15 = I1x33;
GC_16 = -I2x12;
GC_17 = -I2x13;
GC_18 = -I2x22;
GC_19 = -I2x23;
GC_20 = -I2x32;
GC_21 = -I2x33;
GC_22 = I3x21;
GC_23 = I3x22;
GC_24 = I3x23;
GC_25 = I3x31;
GC_26 = I3x32;
GC_27 = I3x33;
GC_28 = -I4x13;
GC_29 = -I4x23;
GC_30 = -I4x33;
GC_31 = -2.*complexi*lam;
GC_32 = -4.*complexi*lam;
GC_33 = -6.*complexi*lam;
GC_34 = (ee__exp__2*complexi)/(2.*sw__exp__2);
GC_35 = -((ee__exp__2*complexi)/sw__exp__2);
GC_36 = (cw__exp__2*ee__exp__2*complexi)/sw__exp__2;
GC_37 = -ee/(2.*sw);
GC_38 = -(ee*complexi)/(2.*sw);
GC_39 = (ee*complexi)/(2.*sw);
GC_40 = (ee*complexi)/(sw*sqrt__2);
GC_41 = (CKM1x1*ee*complexi)/(sw*sqrt__2);
GC_42 = (CKM1x2*ee*complexi)/(sw*sqrt__2);
GC_43 = (CKM1x3*ee*complexi)/(sw*sqrt__2);
GC_44 = (CKM2x1*ee*complexi)/(sw*sqrt__2);
GC_45 = (CKM2x2*ee*complexi)/(sw*sqrt__2);
GC_46 = (CKM2x3*ee*complexi)/(sw*sqrt__2);
GC_47 = (CKM3x1*ee*complexi)/(sw*sqrt__2);
GC_48 = (CKM3x2*ee*complexi)/(sw*sqrt__2);
GC_49 = (CKM3x3*ee*complexi)/(sw*sqrt__2);
GC_50 = -(cw*ee*complexi)/(2.*sw);
GC_51 = (cw*ee*complexi)/(2.*sw);
GC_52 = -((cw*ee*complexi)/sw);
GC_53 = (cw*ee*complexi)/sw;
GC_54 = -ee__exp__2/(2.*sw);
GC_55 = -(ee__exp__2*complexi)/(2.*sw);
GC_56 = ee__exp__2/(2.*sw);
GC_57 = (-2.*cw*ee__exp__2*complexi)/sw;
GC_58 = -(ee*complexi*sw)/(6.*cw);
GC_59 = (ee*complexi*sw)/(2.*cw);
GC_60 = -(cw*ee)/(2.*sw)-(ee*sw)/(2.*cw);
GC_61 = -(cw*ee*complexi)/(2.*sw)+(ee*complexi*sw)/(2.*cw);
GC_62 = (cw*ee*complexi)/(2.*sw)+(ee*complexi*sw)/(2.*cw);
GC_63 = (cw*ee__exp__2*complexi)/sw-(ee__exp__2*complexi*sw)/cw;
GC_64 = -(ee__exp__2*complexi)+(cw__exp__2*ee__exp__2*complexi)/(2.*sw__exp__2)+(ee__exp__2*complexi*sw__exp__2)/(2.*cw__exp__2);
GC_65 = ee__exp__2*complexi+(cw__exp__2*ee__exp__2*complexi)/(2.*sw__exp__2)+(ee__exp__2*complexi*sw__exp__2)/(2.*cw__exp__2);
GC_66 = -(ee__exp__2*vev)/(2.*cw);
GC_67 = (ee__exp__2*vev)/(2.*cw);
GC_68 = -2.*complexi*lam*vev;
GC_69 = -6.*complexi*lam*vev;
GC_70 = -(ee__exp__2*vev)/(4.*sw__exp__2);
GC_71 = -(ee__exp__2*complexi*vev)/(4.*sw__exp__2);
GC_72 = (ee__exp__2*complexi*vev)/(2.*sw__exp__2);
GC_73 = (ee__exp__2*vev)/(4.*sw__exp__2);
GC_74 = -(ee__exp__2*vev)/(2.*sw);
GC_75 = (ee__exp__2*vev)/(2.*sw);
GC_76 = -(ee__exp__2*vev)/(4.*cw)-(cw*ee__exp__2*vev)/(4.*sw__exp__2);
GC_77 = (ee__exp__2*vev)/(4.*cw)-(cw*ee__exp__2*vev)/(4.*sw__exp__2);
GC_78 = -(ee__exp__2*vev)/(4.*cw)+(cw*ee__exp__2*vev)/(4.*sw__exp__2);
GC_79 = (ee__exp__2*vev)/(4.*cw)+(cw*ee__exp__2*vev)/(4.*sw__exp__2);
GC_80 = -(ee__exp__2*complexi*vev)/2.-(cw__exp__2*ee__exp__2*complexi*vev)/(4.*sw__exp__2)-(ee__exp__2*complexi*sw__exp__2*vev)/(4.*cw__exp__2);
GC_81 = ee__exp__2*complexi*vev+(cw__exp__2*ee__exp__2*complexi*vev)/(2.*sw__exp__2)+(ee__exp__2*complexi*sw__exp__2*vev)/(2.*cw__exp__2);
GC_82 = -(yb/sqrt__2);
GC_83 = -((complexi*yb)/sqrt__2);
GC_84 = -((complexi*yc)/sqrt__2);
GC_85 = yc/sqrt__2;
GC_86 = -ye;
GC_87 = ye;
GC_88 = -(ye/sqrt__2);
GC_89 = -((complexi*ye)/sqrt__2);
GC_90 = -ym;
GC_91 = ym;
GC_92 = -(ym/sqrt__2);
GC_93 = -((complexi*ym)/sqrt__2);
GC_94 = -((complexi*yt)/sqrt__2);
GC_95 = yt/sqrt__2;
GC_96 = -ytau;
GC_97 = ytau;
GC_98 = -(ytau/sqrt__2);
GC_99 = -((complexi*ytau)/sqrt__2);
GC_100 = (ee*complexi*conjg__CKM1x1)/(sw*sqrt__2);
GC_101 = (ee*complexi*conjg__CKM1x2)/(sw*sqrt__2);
GC_102 = (ee*complexi*conjg__CKM1x3)/(sw*sqrt__2);
GC_103 = (ee*complexi*conjg__CKM2x1)/(sw*sqrt__2);
GC_104 = (ee*complexi*conjg__CKM2x2)/(sw*sqrt__2);
GC_105 = (ee*complexi*conjg__CKM2x3)/(sw*sqrt__2);
GC_106 = (ee*complexi*conjg__CKM3x1)/(sw*sqrt__2);
GC_107 = (ee*complexi*conjg__CKM3x2)/(sw*sqrt__2);
GC_108 = (ee*complexi*conjg__CKM3x3)/(sw*sqrt__2);
    }
    void Parameters_sm::setDependentParameters(ParticleData*& pd, Couplings*& csm, SusyLesHouches*& slhaPtr, double alpS){
    aS = alpS;
sqrt__aS = sqrt(aS);
G = 2.*sqrt__aS*sqrt(M_PI);
G__exp__2 = pow(G,2.);
    }
    void Parameters_sm::setDependentCouplings(){
    GC_12 = complexi*G__exp__2;
GC_11 = complexi*G;
GC_10 = -G;
    }

    // Routines for printing out parameters
    void Parameters_sm::printIndependentParameters(){
    cout << "sm model parameters independent of event kinematics:" << endl;
    cout << setw(20) << "WTau " << "= " << setiosflags(ios::scientific) << setw(10) << WTau << endl;
cout << setw(20) << "WH " << "= " << setiosflags(ios::scientific) << setw(10) << WH << endl;
cout << setw(20) << "WT " << "= " << setiosflags(ios::scientific) << setw(10) << WT << endl;
cout << setw(20) << "WW " << "= " << setiosflags(ios::scientific) << setw(10) << WW << endl;
cout << setw(20) << "WZ " << "= " << setiosflags(ios::scientific) << setw(10) << WZ << endl;
cout << setw(20) << "MTA " << "= " << setiosflags(ios::scientific) << setw(10) << MTA << endl;
cout << setw(20) << "MM " << "= " << setiosflags(ios::scientific) << setw(10) << MM << endl;
cout << setw(20) << "Me " << "= " << setiosflags(ios::scientific) << setw(10) << Me << endl;
cout << setw(20) << "MH " << "= " << setiosflags(ios::scientific) << setw(10) << MH << endl;
cout << setw(20) << "MB " << "= " << setiosflags(ios::scientific) << setw(10) << MB << endl;
cout << setw(20) << "MT " << "= " << setiosflags(ios::scientific) << setw(10) << MT << endl;
cout << setw(20) << "MC " << "= " << setiosflags(ios::scientific) << setw(10) << MC << endl;
cout << setw(20) << "MZ " << "= " << setiosflags(ios::scientific) << setw(10) << MZ << endl;
cout << setw(20) << "ymtau " << "= " << setiosflags(ios::scientific) << setw(10) << ymtau << endl;
cout << setw(20) << "ymm " << "= " << setiosflags(ios::scientific) << setw(10) << ymm << endl;
cout << setw(20) << "yme " << "= " << setiosflags(ios::scientific) << setw(10) << yme << endl;
cout << setw(20) << "ymt " << "= " << setiosflags(ios::scientific) << setw(10) << ymt << endl;
cout << setw(20) << "ymb " << "= " << setiosflags(ios::scientific) << setw(10) << ymb << endl;
cout << setw(20) << "ymc " << "= " << setiosflags(ios::scientific) << setw(10) << ymc << endl;
cout << setw(20) << "etaWS " << "= " << setiosflags(ios::scientific) << setw(10) << etaWS << endl;
cout << setw(20) << "rhoWS " << "= " << setiosflags(ios::scientific) << setw(10) << rhoWS << endl;
cout << setw(20) << "AWS " << "= " << setiosflags(ios::scientific) << setw(10) << AWS << endl;
cout << setw(20) << "lamWS " << "= " << setiosflags(ios::scientific) << setw(10) << lamWS << endl;
cout << setw(20) << "Gf " << "= " << setiosflags(ios::scientific) << setw(10) << Gf << endl;
cout << setw(20) << "aEWM1 " << "= " << setiosflags(ios::scientific) << setw(10) << aEWM1 << endl;
cout << setw(20) << "ZERO " << "= " << setiosflags(ios::scientific) << setw(10) << ZERO << endl;
cout << setw(20) << "lamWS__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << lamWS__exp__2 << endl;
cout << setw(20) << "CKM1x1 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM1x1 << endl;
cout << setw(20) << "CKM1x2 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM1x2 << endl;
cout << setw(20) << "complexi " << "= " << setiosflags(ios::scientific) << setw(10) << complexi << endl;
cout << setw(20) << "lamWS__exp__3 " << "= " << setiosflags(ios::scientific) << setw(10) << lamWS__exp__3 << endl;
cout << setw(20) << "CKM1x3 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM1x3 << endl;
cout << setw(20) << "CKM2x1 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM2x1 << endl;
cout << setw(20) << "CKM2x2 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM2x2 << endl;
cout << setw(20) << "CKM2x3 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM2x3 << endl;
cout << setw(20) << "CKM3x1 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM3x1 << endl;
cout << setw(20) << "CKM3x2 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM3x2 << endl;
cout << setw(20) << "CKM3x3 " << "= " << setiosflags(ios::scientific) << setw(10) << CKM3x3 << endl;
cout << setw(20) << "MZ__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << MZ__exp__2 << endl;
cout << setw(20) << "MZ__exp__4 " << "= " << setiosflags(ios::scientific) << setw(10) << MZ__exp__4 << endl;
cout << setw(20) << "sqrt__2 " << "= " << setiosflags(ios::scientific) << setw(10) << sqrt__2 << endl;
cout << setw(20) << "MH__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << MH__exp__2 << endl;
cout << setw(20) << "conjg__CKM1x3 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM1x3 << endl;
cout << setw(20) << "conjg__CKM2x3 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM2x3 << endl;
cout << setw(20) << "conjg__CKM3x3 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM3x3 << endl;
cout << setw(20) << "conjg__CKM2x1 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM2x1 << endl;
cout << setw(20) << "conjg__CKM3x1 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM3x1 << endl;
cout << setw(20) << "conjg__CKM2x2 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM2x2 << endl;
cout << setw(20) << "conjg__CKM3x2 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM3x2 << endl;
cout << setw(20) << "conjg__CKM1x1 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM1x1 << endl;
cout << setw(20) << "conjg__CKM1x2 " << "= " << setiosflags(ios::scientific) << setw(10) << conjg__CKM1x2 << endl;
cout << setw(20) << "aEW " << "= " << setiosflags(ios::scientific) << setw(10) << aEW << endl;
cout << setw(20) << "MW " << "= " << setiosflags(ios::scientific) << setw(10) << MW << endl;
cout << setw(20) << "sqrt__aEW " << "= " << setiosflags(ios::scientific) << setw(10) << sqrt__aEW << endl;
cout << setw(20) << "ee " << "= " << setiosflags(ios::scientific) << setw(10) << ee << endl;
cout << setw(20) << "MW__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << MW__exp__2 << endl;
cout << setw(20) << "sw2 " << "= " << setiosflags(ios::scientific) << setw(10) << sw2 << endl;
cout << setw(20) << "cw " << "= " << setiosflags(ios::scientific) << setw(10) << cw << endl;
cout << setw(20) << "sqrt__sw2 " << "= " << setiosflags(ios::scientific) << setw(10) << sqrt__sw2 << endl;
cout << setw(20) << "sw " << "= " << setiosflags(ios::scientific) << setw(10) << sw << endl;
cout << setw(20) << "g1 " << "= " << setiosflags(ios::scientific) << setw(10) << g1 << endl;
cout << setw(20) << "gw " << "= " << setiosflags(ios::scientific) << setw(10) << gw << endl;
cout << setw(20) << "vev " << "= " << setiosflags(ios::scientific) << setw(10) << vev << endl;
cout << setw(20) << "vev__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << vev__exp__2 << endl;
cout << setw(20) << "lam " << "= " << setiosflags(ios::scientific) << setw(10) << lam << endl;
cout << setw(20) << "yb " << "= " << setiosflags(ios::scientific) << setw(10) << yb << endl;
cout << setw(20) << "yc " << "= " << setiosflags(ios::scientific) << setw(10) << yc << endl;
cout << setw(20) << "ye " << "= " << setiosflags(ios::scientific) << setw(10) << ye << endl;
cout << setw(20) << "ym " << "= " << setiosflags(ios::scientific) << setw(10) << ym << endl;
cout << setw(20) << "yt " << "= " << setiosflags(ios::scientific) << setw(10) << yt << endl;
cout << setw(20) << "ytau " << "= " << setiosflags(ios::scientific) << setw(10) << ytau << endl;
cout << setw(20) << "muH " << "= " << setiosflags(ios::scientific) << setw(10) << muH << endl;
cout << setw(20) << "I1x31 " << "= " << setiosflags(ios::scientific) << setw(10) << I1x31 << endl;
cout << setw(20) << "I1x32 " << "= " << setiosflags(ios::scientific) << setw(10) << I1x32 << endl;
cout << setw(20) << "I1x33 " << "= " << setiosflags(ios::scientific) << setw(10) << I1x33 << endl;
cout << setw(20) << "I2x12 " << "= " << setiosflags(ios::scientific) << setw(10) << I2x12 << endl;
cout << setw(20) << "I2x13 " << "= " << setiosflags(ios::scientific) << setw(10) << I2x13 << endl;
cout << setw(20) << "I2x22 " << "= " << setiosflags(ios::scientific) << setw(10) << I2x22 << endl;
cout << setw(20) << "I2x23 " << "= " << setiosflags(ios::scientific) << setw(10) << I2x23 << endl;
cout << setw(20) << "I2x32 " << "= " << setiosflags(ios::scientific) << setw(10) << I2x32 << endl;
cout << setw(20) << "I2x33 " << "= " << setiosflags(ios::scientific) << setw(10) << I2x33 << endl;
cout << setw(20) << "I3x21 " << "= " << setiosflags(ios::scientific) << setw(10) << I3x21 << endl;
cout << setw(20) << "I3x22 " << "= " << setiosflags(ios::scientific) << setw(10) << I3x22 << endl;
cout << setw(20) << "I3x23 " << "= " << setiosflags(ios::scientific) << setw(10) << I3x23 << endl;
cout << setw(20) << "I3x31 " << "= " << setiosflags(ios::scientific) << setw(10) << I3x31 << endl;
cout << setw(20) << "I3x32 " << "= " << setiosflags(ios::scientific) << setw(10) << I3x32 << endl;
cout << setw(20) << "I3x33 " << "= " << setiosflags(ios::scientific) << setw(10) << I3x33 << endl;
cout << setw(20) << "I4x13 " << "= " << setiosflags(ios::scientific) << setw(10) << I4x13 << endl;
cout << setw(20) << "I4x23 " << "= " << setiosflags(ios::scientific) << setw(10) << I4x23 << endl;
cout << setw(20) << "I4x33 " << "= " << setiosflags(ios::scientific) << setw(10) << I4x33 << endl;
cout << setw(20) << "ee__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << ee__exp__2 << endl;
cout << setw(20) << "sw__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << sw__exp__2 << endl;
cout << setw(20) << "cw__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << cw__exp__2 << endl;
    }
    void Parameters_sm::printIndependentCouplings(){
    cout << "sm model couplings independent of event kinematics:" << endl;
    cout << setw(20) << "GC_1 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_1 << endl;
cout << setw(20) << "GC_2 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_2 << endl;
cout << setw(20) << "GC_3 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_3 << endl;
cout << setw(20) << "GC_4 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_4 << endl;
cout << setw(20) << "GC_5 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_5 << endl;
cout << setw(20) << "GC_6 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_6 << endl;
cout << setw(20) << "GC_7 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_7 << endl;
cout << setw(20) << "GC_8 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_8 << endl;
cout << setw(20) << "GC_9 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_9 << endl;
cout << setw(20) << "GC_13 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_13 << endl;
cout << setw(20) << "GC_14 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_14 << endl;
cout << setw(20) << "GC_15 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_15 << endl;
cout << setw(20) << "GC_16 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_16 << endl;
cout << setw(20) << "GC_17 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_17 << endl;
cout << setw(20) << "GC_18 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_18 << endl;
cout << setw(20) << "GC_19 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_19 << endl;
cout << setw(20) << "GC_20 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_20 << endl;
cout << setw(20) << "GC_21 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_21 << endl;
cout << setw(20) << "GC_22 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_22 << endl;
cout << setw(20) << "GC_23 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_23 << endl;
cout << setw(20) << "GC_24 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_24 << endl;
cout << setw(20) << "GC_25 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_25 << endl;
cout << setw(20) << "GC_26 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_26 << endl;
cout << setw(20) << "GC_27 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_27 << endl;
cout << setw(20) << "GC_28 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_28 << endl;
cout << setw(20) << "GC_29 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_29 << endl;
cout << setw(20) << "GC_30 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_30 << endl;
cout << setw(20) << "GC_31 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_31 << endl;
cout << setw(20) << "GC_32 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_32 << endl;
cout << setw(20) << "GC_33 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_33 << endl;
cout << setw(20) << "GC_34 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_34 << endl;
cout << setw(20) << "GC_35 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_35 << endl;
cout << setw(20) << "GC_36 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_36 << endl;
cout << setw(20) << "GC_37 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_37 << endl;
cout << setw(20) << "GC_38 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_38 << endl;
cout << setw(20) << "GC_39 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_39 << endl;
cout << setw(20) << "GC_40 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_40 << endl;
cout << setw(20) << "GC_41 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_41 << endl;
cout << setw(20) << "GC_42 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_42 << endl;
cout << setw(20) << "GC_43 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_43 << endl;
cout << setw(20) << "GC_44 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_44 << endl;
cout << setw(20) << "GC_45 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_45 << endl;
cout << setw(20) << "GC_46 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_46 << endl;
cout << setw(20) << "GC_47 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_47 << endl;
cout << setw(20) << "GC_48 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_48 << endl;
cout << setw(20) << "GC_49 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_49 << endl;
cout << setw(20) << "GC_50 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_50 << endl;
cout << setw(20) << "GC_51 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_51 << endl;
cout << setw(20) << "GC_52 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_52 << endl;
cout << setw(20) << "GC_53 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_53 << endl;
cout << setw(20) << "GC_54 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_54 << endl;
cout << setw(20) << "GC_55 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_55 << endl;
cout << setw(20) << "GC_56 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_56 << endl;
cout << setw(20) << "GC_57 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_57 << endl;
cout << setw(20) << "GC_58 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_58 << endl;
cout << setw(20) << "GC_59 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_59 << endl;
cout << setw(20) << "GC_60 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_60 << endl;
cout << setw(20) << "GC_61 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_61 << endl;
cout << setw(20) << "GC_62 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_62 << endl;
cout << setw(20) << "GC_63 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_63 << endl;
cout << setw(20) << "GC_64 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_64 << endl;
cout << setw(20) << "GC_65 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_65 << endl;
cout << setw(20) << "GC_66 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_66 << endl;
cout << setw(20) << "GC_67 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_67 << endl;
cout << setw(20) << "GC_68 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_68 << endl;
cout << setw(20) << "GC_69 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_69 << endl;
cout << setw(20) << "GC_70 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_70 << endl;
cout << setw(20) << "GC_71 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_71 << endl;
cout << setw(20) << "GC_72 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_72 << endl;
cout << setw(20) << "GC_73 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_73 << endl;
cout << setw(20) << "GC_74 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_74 << endl;
cout << setw(20) << "GC_75 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_75 << endl;
cout << setw(20) << "GC_76 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_76 << endl;
cout << setw(20) << "GC_77 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_77 << endl;
cout << setw(20) << "GC_78 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_78 << endl;
cout << setw(20) << "GC_79 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_79 << endl;
cout << setw(20) << "GC_80 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_80 << endl;
cout << setw(20) << "GC_81 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_81 << endl;
cout << setw(20) << "GC_82 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_82 << endl;
cout << setw(20) << "GC_83 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_83 << endl;
cout << setw(20) << "GC_84 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_84 << endl;
cout << setw(20) << "GC_85 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_85 << endl;
cout << setw(20) << "GC_86 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_86 << endl;
cout << setw(20) << "GC_87 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_87 << endl;
cout << setw(20) << "GC_88 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_88 << endl;
cout << setw(20) << "GC_89 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_89 << endl;
cout << setw(20) << "GC_90 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_90 << endl;
cout << setw(20) << "GC_91 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_91 << endl;
cout << setw(20) << "GC_92 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_92 << endl;
cout << setw(20) << "GC_93 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_93 << endl;
cout << setw(20) << "GC_94 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_94 << endl;
cout << setw(20) << "GC_95 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_95 << endl;
cout << setw(20) << "GC_96 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_96 << endl;
cout << setw(20) << "GC_97 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_97 << endl;
cout << setw(20) << "GC_98 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_98 << endl;
cout << setw(20) << "GC_99 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_99 << endl;
cout << setw(20) << "GC_100 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_100 << endl;
cout << setw(20) << "GC_101 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_101 << endl;
cout << setw(20) << "GC_102 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_102 << endl;
cout << setw(20) << "GC_103 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_103 << endl;
cout << setw(20) << "GC_104 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_104 << endl;
cout << setw(20) << "GC_105 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_105 << endl;
cout << setw(20) << "GC_106 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_106 << endl;
cout << setw(20) << "GC_107 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_107 << endl;
cout << setw(20) << "GC_108 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_108 << endl;
    }
    void Parameters_sm::printDependentParameters(){
    cout << "sm model parameters dependent on event kinematics:" << endl;
    cout << setw(20) << "aS " << "= " << setiosflags(ios::scientific) << setw(10) << aS << endl;
cout << setw(20) << "sqrt__aS " << "= " << setiosflags(ios::scientific) << setw(10) << sqrt__aS << endl;
cout << setw(20) << "G " << "= " << setiosflags(ios::scientific) << setw(10) << G << endl;
cout << setw(20) << "G__exp__2 " << "= " << setiosflags(ios::scientific) << setw(10) << G__exp__2 << endl;
    }
    void Parameters_sm::printDependentCouplings(){
    cout << "sm model couplings dependent on event kinematics:" << endl;
    cout << setw(20) << "GC_12 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_12 << endl;
cout << setw(20) << "GC_11 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_11 << endl;
cout << setw(20) << "GC_10 " << "= " << setiosflags(ios::scientific) << setw(10) << GC_10 << endl;
    }

} // end namespace Pythia8
""" % misc.get_pkg_info()

        file_h, file_cc = self.model_builder.generate_parameters_class_files()
        self.assertEqual(file_h.split('\n'), goal_file_h.split('\n'))
        self.assertEqual(file_cc.replace('\t', '    ').split('\n'), goal_file_cc.replace('\t', '    ').split('\n'))

