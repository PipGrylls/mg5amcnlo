################################################################################
#
# Copyright (c) 2011 The MadGraph Development team and Contributors
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
"""A File for splitting"""

import sys
import re
import os

pjoin = os.path.join

try:
    import madgraph.iolibs.misc as misc
    from madgraph import MG5DIR
    MADEVENT = False
except:
    MADEVENT = True
    MEDIR = os.path.split(os.path.dirname(os.path.realpath( __file__ )))[0]
    MEDIR = os.path.split(MEDIR)[0]



#dict
class Banner(dict):
    """ """
    
    def __init__(self, banner_path=None):
        """ """
        dict.__init__(self)
        
        #Look at the version
        if MADEVENT:
            self['MGVERSION'] = '#%s\n' % open(pjoin(MEDIR, 'MGMEVersion.txt')).read()
        else:
            info = misc.get_pkg_info()
            self['MGVERSION'] = info['version']+'\n'
            
        if banner_path:
            self.read_banner(banner_path)

    ############################################################################
    #  READ BANNER
    ############################################################################
    pat_begin=re.compile('<(?P<name>\w*)>')
    pat_end=re.compile('</(?P<name>\w*)>')

    tag_to_file={'slha':'param_card.dat',
      'MGRunCard':'run_card.dat',
      'MGPythiaCard':'pythia_card.dat',
      'MGPGSCard' : 'pgs_card.dat',
      'MGDelphesCard':'delphes_card.dat',      
      'MGDelphesTrigger':'delphes_trigger.dat',
      'MG5ProcCard':'proc_card_mg5.dat',
      'MGProcCard': 'proc_card.dat',
      }
    
    def read_banner(self, input_path):
        """read a banner"""

        text = ''
        store = False
        for line in open(input_path):
            if store:
                text += line
            if self.pat_begin.search(line):
                tag = self.pat_begin.search(line).group('name')
                if tag in self.tag_to_file:
                    store = True
                    continue
            if store and self.pat_end.search(line):
                if tag == self.pat_end.search(line).group('name'):
                    self[tag] = text
                    text = ''
                    store = False

                
    def load_basic(self, medir):
        """ Load the proc_card /param_card and run_card """
        
        self.add(pjoin(medir,'Cards', 'param_card.dat'))
        self.add(pjoin(medir,'Cards', 'run_card.dat'))
        if os.path.exists(pjoin(medir, 'SubProcesses', 'procdef_mg5.dat')):
            self.add(pjoin(medir,'SubProcesses', 'procdef_mg5.dat'))
            self.add(pjoin(medir,'Cards', 'proc_card_mg5.dat'))
        else:
            self.add(pjoin(medir,'Cards', 'proc_card.dat'))
        
    ############################################################################
    #  SPLIT BANNER
    ############################################################################
    def split(self, me_dir, proc_card=True):
        """write the banner in the Cards directory.
        proc_card argument is present to avoid the overwrite of proc_card 
        information"""

        for tag, text in self.items():
            if tag == 'MGVERSION':
                continue
            if not proc_card and tag in ['MG5ProcCard','MGProcCard']:
                continue
            ff = open(pjoin(me_dir, 'Cards', self.tag_to_file[tag]), 'w')
            ff.write(text)

    ############################################################################
    #  WRITE BANNER
    ############################################################################
    def write(self, output_path):
        """write the banner"""
        
        ff = open(output_path, 'w')
        if MADEVENT:
            
            ff.write(open(pjoin(MEDIR, 'Source', 'banner_header.txt')).read())
        else:
            ff.write(open(pjoin(MG5DIR,'Template', 'Source', 'banner_header.txt')).read())
        for tag, text in self.items():
            ff.write('<%(tag)s>\n%(text)s\n</%(tag)s>\n' % \
                     {'tag':tag, 'text':text})
        ff.write('</LesHouchesEvents>\n')
            
    ############################################################################
    # BANNER
    ############################################################################
    def add(self, path, tag=None):
        """Add the content of the file to the banner"""
        
        if not tag:
            card_name = os.path.basename(path)
            if 'param_card' in card_name:
                tag = 'slha'
            elif 'run_card' in card_name:
                tag = 'MGRunCard'
            elif 'pythia_card' in card_name:
                tag = 'MGPythiaCard'
            elif 'pgs_card' in card_name:
                tag = 'MGPGSCard'
            elif 'delphes_card' in card_name:
                tag = 'MGDelphesCard'
            elif 'delphes_trigger' in card_name:
                tag = 'MGDelphesTrigger'
            elif 'proc_card_mg5' in card_name:
                tag = 'MG5ProcCard'
            elif 'proc_card' in card_name:
                tag = 'MGProcCard'
            elif 'procdef_mg5' in card_name:
                tag = 'MGProcCard'
            else:
                raise Exception, 'Impossible to know the type of the card'

            self[tag] = open(path).read()





def split_banner(banner_path, me_dir, proc_card=True):
    """a simple way to split a banner"""
    
    banner = Banner(banner_path)
    banner.split(me_dir, proc_card)
    
def recover_banner(results_object, level):
    """as input we receive a gen_crossxhtml.AllResults object.
       This define the current banner and load it
    """
    try:  
        run = results_object.current['run_name']    
        tag = results_object.current['tag'] 
    except:
        return Banner()                                  
    path = results_object.path

    banner = Banner(pjoin(path,'Events',run,'%s_%s_banner.txt' % (run, tag)))
    
    if level == 'pythia':
        if 'MGPythiaCard' in banner:
            del banner['MGPythiaCard']
    if level in ['pythia','pgs','delphes']:
        for tag in ['MGPGSCard', 'MGDelphesCard', 'MGDelphesTrigger']:
            if tag in banner:
                del banner[tag]
    return banner
    
    

