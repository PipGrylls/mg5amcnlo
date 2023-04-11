import model sm-no_b_mass
define p = g u c d s u~ c~ d~ s~ b b~
define j = g u c d s u~ c~ d~ s~ b b~
define l+ = e+ mu+ ta+
define l- = e- mu- ta-
define vl = ve vm vt
define vl~ = ve~ vm~ vt~

generate p p > w+ w+ j j QCD=2, w+ > l+ vl @1
add process p p > w- w- j j QCD=2, w- > l- vl~ @1

output PROC_ssWWjj_QCD
launch PROC_ssWWjj_QCD
reweight=ON
#set nb_workers = 46
done
Cards/param_card.dat
set gridpack = .true.
set ebeam1 = 13000
set ebeam2 = 13000
set ptj = 10.0 
set ptl = 10.0
set etaj = -1
set etal = -1
set mmjj = 300
set mmll = 0
set lhe_version = 3.0
#set pdlabel = 'lhapdf'
#set lhaid = 305200
set bwcutoff = 15
set maxjetflavor = 5
#set systematics_program = systematics
#set systematics_arguments = ['--mur=0.5,1,2', '--muf=0.5,1,2', '--dyn=-1,1,2,3,4', '--weight_info=MUR%(mur).1f_MUF%(muf).1f_PDF%(pdf)i_DYNSCALE%(dyn)i', '--pdf=errorset, NNPDF31_nnlo_hessian_pdfas, MSHT20nlo_as118, MSHT20nnlo_as118']
#set use_syst = .true.
set asrwgtflavor = 5
set auto_ptj_mjj = .false.
set cut_decays = .false.
done
