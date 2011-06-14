# This file was automatically created by FeynRules $Revision: 535 $
# Mathematica version: 7.0 for Mac OS X x86 (64-bit) (November 11, 2008)
# Date: Fri 18 Mar 2011 18:40:51


from object_library import all_vertices, Vertex
import particles as P
import couplings as C
import lorentz as L

# Implementation of the R2 vertices

# ggg d-quark internal line
V_101 = Vertex(name = 'V_101',
              particles = [ P.G, P.G, P.G ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_101},
              type = ['R2',(1,1,1)])

# ggg u-quark internal line              
V_102 = Vertex(name = 'V_102',
              particles = [ P.G, P.G, P.G ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_101},
              type = ['R2',(2,2,2)])

# ggg gluon internal line
V_103 = Vertex(name = 'V_103',
              particles = [ P.G, P.G, P.G ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_102},
              type = ['R2',(21,21,21)])

# gggg
V_104 = Vertex(name = 'V_104',
              particles = [ P.G, P.G, P.G, P.G ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVV1, L.VVVV3, L.VVVV4 ],
              couplings = {(1,1):C.GC_103,(0,0):C.GC_103,(2,2):C.GC_103},
              type = ['UV',()])

# gdd~
V_105 = Vertex(name = 'V_105',
              particles = [ P.d__tilde__, P.d, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_104},
              type = ['R2',()])

# guu~              
V_106 = Vertex(name = 'V_106',
               particles = [ P.u__tilde__, P.u, P.G ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_104},
               type = ['R2',()])  

# gg             
V_107 = Vertex(name = 'V_107',
               particles = [ P.G, P.G ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.R2_GG_1],
               couplings = {(0,0):C.GC_105},
               type = ['R2',(1,1,1)])  

# gg             
V_117 = Vertex(name = 'V_117',
               particles = [ P.G, P.G ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.R2_GG_1],
               couplings = {(0,0):C.GC_105},
               type = ['R2',(2,2,2)])  

# gg             
V_127 = Vertex(name = 'V_127',
               particles = [ P.G, P.G ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.R2_GG_1 , L.R2_GG_2 ],
               couplings = {(0,0):C.GC_115, (0,1):C.GC_125},
               type = ['R2',(21,21,21)])  

# d~d            
V_108 = Vertex(name = 'V_108',
               particles = [ P.d__tilde__, P.d ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.R2_QQ ],
               couplings = {(0,0):C.GC_106},
               type = ['R2',()]) 

# u~u             
V_109 = Vertex(name = 'V_109',
               particles = [ P.u__tilde__, P.u ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.R2_QQ ],
               couplings = {(0,0):C.GC_106},
               type = ['R2',()]) 

# UV counter-terms

# ggg
V_201 = Vertex(name = 'V_201',
              particles = [ P.G, P.G, P.G ],
              color = [ 'f(1,2,3)' ],
              lorentz = [ L.VVV1 ],
              couplings = {(0,0):C.GC_201},
              type = ['UV',()])

# gggg
V_202 = Vertex(name = 'V_202',
              particles = [ P.G, P.G, P.G, P.G ],
              color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
              lorentz = [ L.VVVV1, L.VVVV3, L.VVVV4 ],
              couplings = {(1,1):C.GC_202,(0,0):C.GC_202,(2,2):C.GC_202},
              type = ['UV',()])

# gdd~
V_203 = Vertex(name = 'V_203',
              particles = [ P.d__tilde__, P.d, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_203},
              type = ['UV',()])

# guu~              
V_204 = Vertex(name = 'V_204',
               particles = [ P.u__tilde__, P.u, P.G ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_203},
               type = ['UV',()])