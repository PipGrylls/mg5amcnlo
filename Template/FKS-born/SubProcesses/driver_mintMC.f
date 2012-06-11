      Program DRIVER
c**************************************************************************
c     This is the driver for the whole calculation
c**************************************************************************
      implicit none
C
C     CONSTANTS
C
      double precision zero
      parameter       (ZERO = 0d0)
      include 'nexternal.inc'
      include 'genps.inc'
      INTEGER    ITMAX,   NCALL

      common/citmax/itmax,ncall
C
C     LOCAL
C
      integer i,nconfigs,j,l,l1,l2,ndim,nevts
      double precision tot,mean,sigma,res_abs
      integer npoints
      double precision y,jac,s1,s2,xmin
      character*130 buf,string

      integer lunlhe
      parameter (lunlhe=98)
c
c     Global
c
      integer                                      nsteps
      character*40          result_file,where_file
      common /sample_status/result_file,where_file,nsteps
      integer           Minvar(maxdim,lmaxconfigs)
      common /to_invar/ Minvar
      real*8          dsigtot(10)
      common/to_dsig/ dsigtot
      integer ngroup
      common/to_group/ngroup
      data ngroup/0/
cc
      include 'run.inc'
      include 'coupl.inc'
      
      integer           iconfig
      common/to_configs/iconfig


      double precision twgt, maxwgt,swgt(maxevents)
      integer                             lun, nw
      common/to_unwgt/twgt, maxwgt, swgt, lun, nw

c Vegas stuff
      integer ipole
      common/tosigint/ndim,ipole

      real*8 sigintH,sigintS,sigintF,resA,errA,resS,errS,chi2a
      external sigintH,sigintS,sigintF

      integer irestart
      character * 70 idstring
      logical savegrid

      external initplot
c Set plotKin=.true. to plot H and S event kinematics (integration steps)
c Set plotEv=.true. to use events for plotting (unweighting phase)
      logical plotEv,plotKin
      common/cEvKinplot/plotEv,plotKin

c For tests
      real*8 fksmaxwgt,xisave,ysave
      common/cfksmaxwgt/fksmaxwgt,xisave,ysave

      integer itotalpoints
      common/ctotalpoints/itotalpoints

      integer ivirtpoints,ivirtpointsExcept
      double precision  virtmax,virtmin,virtsum
      common/cvirt3test/virtmax,virtmin,virtsum,ivirtpoints,
     &     ivirtpointsExcept
      double precision total_wgt_sum,total_wgt_sum_max,
     &                 total_wgt_sum_min
      common/csum_of_wgts/total_wgt_sum,total_wgt_sum_max,
     &                 total_wgt_sum_min

      logical            flat_grid
      common/to_readgrid/flat_grid                !Tells if grid read from file

      double precision weight
c For MINT:
      include "mint.inc"
      real * 8 xgrid(0:nintervals,ndimmax),xint,ymax(nintervals,ndimmax)
      real * 8 x(ndimmax)
      integer ixi_i,iphi_i,iy_ij
      integer ifold(ndimmax) 
      common /cifold/ifold
      integer ifold_energy,ifold_phi,ifold_yij
      common /cifoldnumbers/ifold_energy,ifold_phi,ifold_yij
      logical putonshell
      integer imode
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt

      logical SHsep
      logical Hevents
      common/SHevents/Hevents
      character*10 dum

C-----
C  BEGIN CODE
C-----  
c
c     Read process number
c
      open (unit=lun+1,file='../dname.mg',status='unknown',err=11)
      read (lun+1,'(a130)',err=11,end=11) buf
      l1=index(buf,'P')
      l2=index(buf,'_')
      if(l1.ne.0.and.l2.ne.0.and.l1.lt.l2-1)
     $     read(buf(l1+1:l2-1),*,err=11) ngroup
 11   print *,'Process in group number ',ngroup

      lun = 27
      twgt = -2d0            !determine wgt after first iteration
      open(unit=lun,status='scratch')
      nsteps=2
      call setrun                !Sets up run parameters
      call setpara('param_card.dat')   !Sets up couplings and masses
      call setcuts               !Sets up cuts & particle masses
      call printout              !Prints out a summary of paramaters
      call run_printout          !Prints out a summary of the run settings
      nconfigs = 1
c     
c     Get user input
c
      write(*,*) "getting user params"
      call get_user_params(ncall,itmax,iconfig,imode,
     &     ixi_i,iphi_i,iy_ij,SHsep)
      if(imode.eq.0)then
        flat_grid=.true.
      else
        flat_grid=.false.
      endif
c$$$      call setfksfactor(iconfig)
      ndim = 3*(nexternal-2)-4
      if (abs(lpp(1)) .ge. 1) ndim=ndim+1
      if (abs(lpp(2)) .ge. 1) ndim=ndim+1

c Don't proceed if muF1#muF2 (we need to work out the relevant formulae
c at the NLO)
      if( ( fixed_fac_scale .and.
     #       (muF1_over_ref*muF1_ref_fixed) .ne.
     #       (muF2_over_ref*muF2_ref_fixed) ) .or.
     #    ( (.not.fixed_fac_scale) .and.
     #      muF1_over_ref.ne.muF2_over_ref ) )then
        write(*,*)'NLO computations require muF1=muF2'
        stop
      endif

      write(*,*) "about to integrate ", ndim,ncall,itmax,nconfigs

      itotalpoints=0
      ivirtpoints=0
      ivirtpointsExcept=0
      total_wgt_sum=0d0
      total_wgt_sum_max=0d0
      total_wgt_sum_min=0d0

      unwgt=.false.

c Plots
      plotEv=.false.
      plotKin=.false.

      call addfil(dum)
      if (imode.eq.-1.or.imode.eq.0) then
         if(imode.eq.0)then
            do j=0,nintervals
               do i=1,ndimmax
                  xgrid(j,i)=0.d0
               enddo
            enddo
         else
c to restore grids:
            open (unit=12, file='preset_mint_grids',status='old')
            do j=0,nintervals
               read (12,*) (xgrid(j,i),i=1,ndim)
            enddo
            read (12,*) xint
            read (12,*) ifold_energy,ifold_phi,ifold_yij
            close (12)
         endif
c
         if(plotKin)then
            open(unit=99,file='WARMUP.top',status='unknown')
            call initplot
         endif
c
         write (*,*) 'imode is ',imode
         if (Hevents.and.SHsep) then
            call mint(sigintH,ndim,ncall,itmax,imode,
     &           xgrid,xint,ymax,resA,errA,resS,errS)
         elseif(.not.SHsep) then
            call mint(sigintF,ndim,ncall,itmax,imode,
     &           xgrid,xint,ymax,resA,errA,resS,errS)
         else
            call mint(sigintS,ndim,ncall,itmax,imode,
     &           xgrid,xint,ymax,resA,errA,resS,errS)
         endif
         open(unit=58,file='res_0',status='unknown')
         write(58,*)'Final result [ABS]:',resA,' +/-',errA
         write(58,*)'Final result:',resS,' +/-',errS
         close(58)
         write(*,*)'Final result [ABS]:',resA,' +/-',errA
         write(*,*)'Final result:',resS,' +/-',errS
      
c to save grids:
         open (unit=12, file='mint_grids',status='unknown')
         do j=0,nintervals
            write (12,*) (xgrid(j,i),i=1,ndim)
         enddo
         write (12,*) xint
         write (12,*) ifold_energy,ifold_phi,ifold_yij
         close (12)

      elseif(imode.eq.1) then
         open (unit=99,file='nevts',status='old',err=999)
         read (99,*) nevts
         close(99)
         if(nevts.eq.0) then
            write (*,*)
     &           'No events needed for this channel...skipping it'
            stop
         endif
c
         if(plotKin)then
            open(unit=99,file='MADatNLO.top',status='unknown')
            call initplot
         endif

c to restore grids:
         open (unit=12, file='mint_grids',status='old')
         do j=0,nintervals
            read (12,*) (xgrid(j,i),i=1,ndim)
         enddo
         read (12,*) xint
         read (12,*) ifold_energy,ifold_phi,ifold_yij
         close (12)

c Prepare the MINT folding
         do j=1,ndimmax
            if (j.le.ndim) then
               ifold(j)=1
            else
               ifold(j)=0
            endif
         enddo
         ifold(ifold_energy)=ixi_i
         ifold(ifold_phi)=iphi_i
         ifold(ifold_yij)=iy_ij
         
         write (*,*) 'imode is ',imode
         if (Hevents.and.SHsep) then
            call mint(sigintH,ndim,ncall,itmax,imode,
     &           xgrid,xint,ymax,resA,errA,resS,errS)
         elseif (.not.SHsep) then
            call mint(sigintF,ndim,ncall,itmax,imode,
     &           xgrid,xint,ymax,resA,errA,resS,errS)
         else
            call mint(sigintS,ndim,ncall,itmax,imode,
     &           xgrid,xint,ymax,resA,errA,resS,errS)
         endif
         open(unit=58,file='res_1',status='unknown')
         write(58,*)'Final result [ABS]:',resA,' +/-',errA
         write(58,*)'Final result:',resS,' +/-',errS
         close(58)

         write(*,*)'Final result [ABS]:',resA,' +/-',errA
         write(*,*)'Final result:',resS,' +/-',errS

c to save grids:
         open (unit=12, file='mint_grids_NLO',status='unknown')
         write (12,*) (xgrid(0,i),i=1,ndim)
         do j=1,nintervals
            write (12,*) (xgrid(j,i),i=1,ndim)
            write (12,*) (ymax(j,i),i=1,ndim)
         enddo
         write (12,*) (ifold(i),i=1,ndim)
         write (12,*) resS,errS
         close (12)


c Event generation
      elseif(imode.eq.2) then

c Mass-shell stuff. This is MC-dependent
         call fill_MC_mshell()
         putonshell=.true.
c$$$         putonshell=.false.

         unwgt=.true.
         open (unit=99,file='nevts',status='old',err=999)
         read (99,*) nevts
         close(99)
         if(nevts.eq.0) then
            write (*,*)
     &           'No events needed for this channel...skipping it'
            stop
         endif
         ncall=nevts ! Update ncall with the number found in 'nevts'
         
c to restore grids:
         open (unit=12, file='mint_grids_NLO',status='unknown')
         read (12,*) (xgrid(0,i),i=1,ndim)
         do j=1,nintervals
            read (12,*) (xgrid(j,i),i=1,ndim)
            read (12,*) (ymax(j,i),i=1,ndim)
         enddo
         read (12,*) (ifold(i),i=1,ndim)
         read (12,*) resS,errS
         close (12)

         open(unit=58,file='res_1',status='old')
         read(58,'(a)')string
         read(string(index(string,':')+1:index(string,'+/-')-1),*) res_abs
         close(58)
   
         if(plotEv)open(unit=99,file='hard-events.top',status='unknown')
         open(unit=lunlhe,file='events.lhe',status='unknown')

         call write_header_init(lunlhe,ncall,resS,res_abs,errS)
         if(plotEv)call initplot
         open(unit=58,file='res_1',status='old')
         read(58,'(a)')string
         read(string(index(string,'[ABS]:')+6:index(string,'+/-')-1),*)
     &        res_abs
         close(58)

         weight=res_abs/(itmax*ncall)

         write (*,*) 'imode is ',imode
         if (Hevents.and.SHsep) then
            imode=0 
            call gen(sigintH,ndim,xgrid,ymax,imode,x) 
            imode=1 
            do j=1,ncall
               call gen(sigintH,ndim,xgrid,ymax,imode,x) 
               call finalize_event(x,weight,lunlhe,plotEv,putonshell)
            enddo 
            imode=3 
            call gen(sigintH,ndim,xgrid,ymax,imode,x) 
         elseif (.not.SHsep) then
            imode=0 
            call gen(sigintF,ndim,xgrid,ymax,imode,x) 
            imode=1 
            do j=1,ncall
               call gen(sigintF,ndim,xgrid,ymax,imode,x) 
               call finalize_event(x,weight,lunlhe,plotEv,putonshell)
            enddo 
            imode=3 
            call gen(sigintF,ndim,xgrid,ymax,imode,x) 
         else
            imode=0 
            call gen(sigintS,ndim,xgrid,ymax,imode,x) 
            imode=1 
            do j=1,ncall
               call gen(sigintS,ndim,xgrid,ymax,imode,x) 
               call finalize_event(x,weight,lunlhe,plotEv,putonshell)
            enddo 
            imode=3 
            call gen(sigintS,ndim,xgrid,ymax,imode,x) 
         endif
         write (*,*) 'Generation efficiency:',x(1)

         write (lunlhe,'(a)') "</LesHouchesEvents>"
         close(lunlhe)
      endif

      write(*,*)'Maximum weight found:',fksmaxwgt
      write(*,*)'Found for:',xisave,ysave



      write (*,*) ''
      write (*,*) '----------------------------------------------------'
      write (*,*) 'Total points tried:                   ',
     &     ncall*itmax
      write (*,*) 'Total points passing generation cuts: ',
     &     itotalpoints
      write (*,*) 'Efficiency of events passing cuts:    ',
     &     dble(itotalpoints)/dble(ncall*itmax)
      write (*,*) '----------------------------------------------------'
      write (*,*) ''
      write (*,*) ''
      write (*,*) '----------------------------------------------------'
      write (*,*) 'number of except PS points:',ivirtpointsExcept,
     &     'out of',ivirtpoints,'points'
      write (*,*) '   treatment of exceptional PS points:'
      write (*,*) '      maximum approximation:',
     &     total_wgt_sum + dsqrt(total_wgt_sum_max)/dble(ncall*itmax)
      write (*,*) '      minimum approximation:',
     &     total_wgt_sum - dsqrt(total_wgt_sum_min)/dble(ncall*itmax)
      write (*,*) '      taking the max/min average:',
     &     total_wgt_sum/dble(ncall*itmax)
      write (*,*) '----------------------------------------------------'
      write (*,*) ''



      if(plotEv.or.plotKin)then
        call mclear
        call topout
        close(99)
      endif

      return
 999  write (*,*) 'nevts file not found'
      stop
      end

      subroutine get_user_params(ncall,itmax,iconfig,
     &     imode,ixi_i,iphi_i,iy_ij,SHsep)
c**********************************************************************
c     Routine to get user specified parameters for run
c**********************************************************************
      implicit none
c
c     Constants
c
      include 'nexternal.inc'
      include 'genps.inc'
c
c     Arguments
c
      integer ncall,itmax,iconfig, jconfig
c
c     Local
c
      integer i, j
      double precision dconfig
c
c     Global
c
      integer           isum_hel
      logical                   multi_channel
      common/to_matrix/isum_hel, multi_channel
      double precision    accur
      common /to_accuracy/accur
      integer           use_cut
      common /to_weight/use_cut

      integer        lbw(0:nexternal)  !Use of B.W.
      common /to_BW/ lbw

      character*5 abrvinput
      character*4 abrv
      common /to_abrv/ abrv

      logical nbody
      common/cnbody/nbody
c
c To convert diagram number to configuration
c
      integer iforest(2,-max_branch:-1,lmaxconfigs)
      integer sprop(-max_branch:-1,lmaxconfigs)
      integer tprid(-max_branch:-1,lmaxconfigs)
      integer mapconfig(0:lmaxconfigs)
      include 'born_conf.inc'
c
c MC counterterm stuff
c
c alsf and besf are the parameters that control gfunsoft
      double precision alsf,besf
      common/cgfunsfp/alsf,besf
c alazi and beazi are the parameters that control gfunazi
      double precision alazi,beazi
      common/cgfunazi/alazi,beazi
      
      logical SHsep
      logical Hevents
      common/SHevents/Hevents
c
c MINT stuff
c
      integer imode,ixi_i,iphi_i,iy_ij

      logical usexinteg,mint
      common/cusexinteg/usexinteg,mint

      character*10 MonteCarlo
      common/cMonteCarloType/MonteCarlo
c-----
c  Begin Code
c-----
      mint=.true.
      usexinteg=.false.
      write(*,'(a)') 'Enter number of events and iterations: '
      read(*,*) ncall,itmax
      write(*,*) 'Number of events and iterations ',ncall,itmax

      write(*,*)'Enter alpha, beta for G_soft'
      write(*,*)'  Enter alpha<0 to set G_soft=1 (no ME soft)'
      read(*,*)alsf,besf
      write (*,*) 'for G_soft: alpha=',alsf,', beta=',besf 

      write(*,*)'Enter alpha, beta for G_azi'
      write(*,*)'  Enter alpha>0 to set G_azi=0 (no azi corr)'
      read(*,*)alazi,beazi
      write (*,*) 'for G_azi: alpha=',alazi,', beta=',beazi

      write (*,*) "H-events (0), or S-events (1)"
      read (*,*) i
      if (i.eq.0) then
         Hevents=.true.
         write (*,*) 'Doing the H-events'
         SHsep=.true.
      elseif (i.eq.1) then
         Hevents=.false.
         write (*,*) 'Doing the S-events'
         SHsep=.true.
      elseif (i.eq.2) then
         Hevents=.true.
         write (*,*) 'Doing the S and H events together'
         SHsep=.false.
      endif

c These should be ignored (but kept for 'historical reasons')      
      accur=0
      use_cut=2


      write(*,10) 'Suppress amplitude (0 no, 1 yes)? '
      read(*,*) i
      if (i .eq. 1) then
         multi_channel = .true.
         write(*,*) 'Using suppressed amplitude.'
      else
         multi_channel = .false.
         write(*,*) 'Using full amplitude.'
      endif

      write(*,10) 'Exact helicity sum (0 yes, n = number/event)? '
      read(*,*) i
      if (i .eq. 0) then
         isum_hel = 0
         write(*,*) 'Explicitly summing over helicities'
      else
         isum_hel= i
         write(*,*) 'Summing over',i,' helicities/event'
      endif

      write(*,10) 'Enter Configuration Number: '
      read(*,*) dconfig
      iconfig = int(dconfig)
      do i=1,mapconfig(0)
         if (iconfig.eq.mapconfig(i)) then
            iconfig=i
            exit
         endif
      enddo
      write(*,12) 'Running Configuration Number: ',iconfig

      write (*,'(a)') 'Enter running mode for MINT:'
      write (*,'(a)') '0 to set-up grids, 1 to integrate,'//
     &     ' 2 to generate events'
      read (*,*) imode
      write (*,*) 'MINT running mode:',imode
      if (imode.eq.2)then
         write (*,*) 'Generating events, doing only one iteration'
         itmax=1
      endif

      write (*,'(a)') 'Set the three folding parameters for MINT'
      write (*,'(a)') 'xi_i, phi_i, y_ij'
      read (*,*) ixi_i,iphi_i,iy_ij
      write (*,*)ixi_i,iphi_i,iy_ij


      write (*,'(a)') 'Monte Carlo for showering. Possible options are'
      write (*,'(a)') 'HERWIG6, HERWIGPP, PYTHIA6Q, PYTHIA6PT, PYTHIA8'
      read (*,*) MonteCarlo
      write (*,*) MonteCarlo

      if(MonteCarlo.ne.'HERWIG6' .and.MonteCarlo.ne.'HERWIGPP' .and.
     #   MonteCarlo.ne.'PYTHIA6Q'.and.MonteCarlo.ne.'PYTHIA6PT'.and.
     #   MonteCarlo.ne.'PYTHIA8')then
        write(*,*)'Take it easy. This MC is not implemented'
        stop
      endif

      abrvinput='     '
      write (*,*) "'all ', 'born', 'real', 'virt', 'novi' or 'grid'?"
      write (*,*) "Enter 'born0' or 'virt0' to perform"
      write (*,*) " a pure n-body integration (no S functions)"
      read(*,*) abrvinput
      if(abrvinput(5:5).eq.'0')then
         write (*,*) 'This option is no longer supported:',abrvinput
         stop
        nbody=.true.
      else
        nbody=.false.
      endif
      abrv=abrvinput(1:4)
      if(nbody.and.abrv.ne.'born'.and.abrv(1:2).ne.'vi'
     &     .and. abrv.ne.'grid')then
        write(*,*)'Error in driver: inconsistent input',abrvinput
        stop
      endif

      write (*,*) "doing the ",abrv," of this channel"
      if(nbody)then
        write (*,*) "integration Born/virtual with Sfunction=1"
      else
        write (*,*) "Normal integration (Sfunction != 1)"
      endif
c
c
c     Here I want to set up with B.W. we map and which we don't
c
      dconfig = dconfig-iconfig
      if (dconfig .eq. 0) then
         write(*,*) 'Not subdividing B.W.'
         lbw(0)=0
      else
         lbw(0)=1
         jconfig=dconfig*1000.1
         write(*,*) 'Using dconfig=',jconfig
         call DeCode(jconfig,lbw(1),3,nexternal)
         write(*,*) 'BW Setting ', (lbw(j),j=1,nexternal-2)
      endif
 10   format( a)
 12   format( a,i4)
      end
c     $E$ get_user_params $E$ ! tag for MadWeight
c     change this routine to read the input in a file
c






      function sigintF(xx,w,ifl,f_abs)
c From dsample_fks
      implicit none
      include 'mint.inc'
      include 'nexternal.inc'
      include 'genps.inc'
      include 'nFKSconfigs.inc'
      include 'reweight_all.inc'
      include 'run.inc'
      integer ndim,ipole
      common/tosigint/ndim,ipole
      integer           iconfig
      common/to_configs/iconfig
      integer i,j,k
      integer ifl
      integer fold
      common /cfl/fold
      real*8 sigintF,xx(ndimmax),w
      integer ione
      parameter (ione=1)
      double precision wgt,dsigS,dsigH,f_abs,lum,dlum
      external dlum
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt
      logical Hevents
      common/SHevents/Hevents
      double precision result1,result2,ran2,rnd
      external ran2
      double precision p(0:3,nexternal)
      double precision f_check
      double precision x(99),sigintF_without_w,f_abs_without_w
      common /c_sigint/ x,sigintF_without_w,f_abs_without_w
      double precision f(2),result(0:fks_configs,2)
      save f,result
      INTEGER NFKSPROCESS
      COMMON/C_NFKSPROCESS/NFKSPROCESS
      character*4 abrv
      common /to_abrv/ abrv
      logical nbody
      common/cnbody/nbody
      integer fks_j_from_i(nexternal,0:nexternal)
     &     ,particle_type(nexternal),pdg_type(nexternal)
      common /c_fks_inc/fks_j_from_i,particle_type,pdg_type
      integer i_fks,j_fks
      common/fks_indices/i_fks,j_fks
      logical firsttime
      integer sum
      parameter (sum=0)
      data firsttime /.true./
      logical foundB(2),j_fks_initial(fks_configs),found_ini1,found_ini2
     $     ,found_fnl
      integer nFKSprocessBorn(2)
      save nFKSprocessBorn,foundB
      double precision vol,sigintR,res,f_tot,rfract
      integer proc_map(0:fks_configs,0:fks_configs)
     $     ,i_fks_proc(fks_configs),j_fks_proc(fks_configs)
     $     ,nFKSprocess_all,i_fks_pdg_proc(fks_configs)
     $     ,j_fks_pdg_proc(fks_configs)
      integer itotalpoints
      common/ctotalpoints/itotalpoints
      INTEGER              IPROC
      DOUBLE PRECISION PD(0:MAXPROC)
      COMMON /SUBPROC/ PD, IPROC
      double precision unwgt_table(0:fks_configs,2,maxproc)
      common/c_uwgt_table/unwgt_table
      integer maxproc_save
      save maxproc_save
      double precision rfrac
c
c Find the nFKSprocess for which we compute the Born-like contributions
      if (firsttime) then
         firsttime=.false.
         foundB(1)=.false.
         foundB(2)=.false.
         maxproc_save=0
         do nFKSprocess=1,fks_configs
            call fks_inc_chooser()
            if (PDG_type(i_fks).eq.21) then
               if (j_fks.le.nincoming) then
                  foundB(1)=.true.
                  nFKSprocessBorn(1)=nFKSprocess
               else
                  foundB(2)=.true.
                  nFKSprocessBorn(2)=nFKSprocess
               endif
            endif
            if (doreweight) then
               call reweight_settozero()
               call reweight_settozero_all(nFKSprocess*2,.true.)
               call reweight_settozero_all(nFKSprocess*2-1,.true.)
            endif
c Set Bjorken x's to some random value before calling the dlum() function
            xbk(1)=0.5d0
            xbk(2)=0.5d0
            lum=dlum()
            maxproc_save=max(maxproc_save,IPROC)
         enddo
         write (*,*) 'Total number of FKS directories is', fks_configs
         write (*,*) 'For the Born we use nFKSprocesses  #',
     &        nFKSprocessBorn
c For sum over identical FKS pairs, need to find the identical structures
         if (sum.eq.0) then
            proc_map(0,0)=fks_configs
            do i=1,fks_configs
               proc_map(i,0)=1
               proc_map(i,1)=i
            enddo
         elseif (sum.eq.1) then
            proc_map(0,0)=1
            proc_map(1,0)=fks_configs
            do i=1,fks_configs
               proc_map(1,i)=i
            enddo
         elseif (sum.eq.2) then
            proc_map(0,0)=0
            do i=1,fks_configs
               proc_map(i,0)=0
               i_fks_proc(i)=0
               j_fks_proc(i)=0
            enddo
            do nFKSprocess=1,fks_configs
               call fks_inc_chooser()
               i=1
               do while ( i.le.proc_map(0,0) )
                  if (i_fks.eq.i_fks_proc(i)
     &              .and. j_fks.eq.j_fks_proc(i) ) then
                     exit
                  endif
                  i=i+1
               enddo
               proc_map(i,0)=proc_map(i,0)+1
               proc_map(i,proc_map(i,0))=nFKSprocess
               if (i.gt.proc_map(0,0)) then
                  proc_map(0,0)=proc_map(0,0)+1
                  i_fks_proc(proc_map(0,0))=i_fks
                  j_fks_proc(proc_map(0,0))=j_fks
               endif
            enddo
            write (*,*) 'FKS process map:'
            do i=1,proc_map(0,0)
               write (*,*) i,'-->',proc_map(i,0),':',
     &              (proc_map(i,j),j=1,proc_map(i,0))
            enddo
         elseif (sum.eq.3) then
            proc_map(0,0)=0
            do i=1,fks_configs
               proc_map(i,0)=0
               i_fks_pdg_proc(i)=0
               j_fks_pdg_proc(i)=0
               j_fks_proc(i)=0
            enddo
c First find all the nFKSprocesses that have a soft singularity and put
c them in the process map
            do nFKSprocess=1,fks_configs
               call fks_inc_chooser()
               if (PDG_type(i_fks).eq.21) then
                  proc_map(0,0)=proc_map(0,0)+1
                  proc_map(proc_map(0,0),0)=proc_map(proc_map(0,0),0)+1
                  proc_map(proc_map(0,0),proc_map(proc_map(0,0),0))
     $                 =nFKSprocess
                  i_fks_pdg_proc(proc_map(0,0))=PDG_type(i_fks)
                  j_fks_pdg_proc(proc_map(0,0))=PDG_type(j_fks)
                  j_fks_proc(proc_map(0,0))=j_fks
               endif
            enddo
c Check to make sure that there is at most two initial and one final
c state all gluon
            found_ini1=.false.
            found_ini2=.false.
            found_fnl=.false.
            do i=1,proc_map(0,0)
               if (i_fks_pdg_proc(i).eq.21 .and. j_fks_proc(i).eq.1
     $              .and. .not.found_ini1) then
                  found_ini1=.true.
               elseif (i_fks_pdg_proc(i).eq.21 .and. j_fks_proc(i).eq.1
     $                 .and. found_ini1) then
                  write (*,*)'Initial state 1 g->gg already'/
     $                 /' found in driver_mintMC'
                  write (*,*) i_fks_pdg_proc
                  write (*,*) j_fks_pdg_proc
                  write (*,*) j_fks_proc
                  stop
               elseif (i_fks_pdg_proc(i).eq.21 .and. j_fks_proc(i).eq.2
     $                 .and. .not.found_ini2) then
                  found_ini2=.true.
               elseif (i_fks_pdg_proc(i).eq.21 .and. j_fks_proc(i).eq.2
     $                 .and. found_ini2) then
                  write (*,*)'Initial state 2 g->gg already'/
     $                 /' found in driver_mintMC'
                  write (*,*) i_fks_pdg_proc
                  write (*,*) j_fks_pdg_proc
                  write (*,*) j_fks_proc
                  stop
               elseif (i_fks_pdg_proc(i).eq.21 .and.
     $                 j_fks_pdg_proc(i).eq.21 .and.
     $                 j_fks_proc(i).gt.nincoming .and. .not.found_fnl)
     $                 then
                  found_fnl=.true.
               elseif (i_fks_pdg_proc(i).eq.21 .and.
     $                 j_fks_pdg_proc(i).eq.21 .and.
     $                 j_fks_proc(i).gt.nincoming .and. found_fnl) then
                  write (*,*)
     &              'Final state g->gg already found in driver_mintMC'
                  write (*,*) i_fks_pdg_proc
                  write (*,*) j_fks_pdg_proc
                  write (*,*) j_fks_proc
                  stop
               endif
            enddo
c Loop again, and identify the nFKSprocesses that do not have a soft
c singularity and put them together with the corresponding gluon to
c gluons splitting
            do nFKSprocess=1,fks_configs
               call fks_inc_chooser()
               if (PDG_type(i_fks).ne.21) then
                  if (j_fks.eq.1 .and. found_ini1) then
                     do i=1,proc_map(0,0)
                        if (i_fks_pdg_proc(i).eq.21 .and.
     $                       j_fks_proc(i).eq.1) then
                           proc_map(i,0)=proc_map(i,0)+1
                           proc_map(i,proc_map(i,0))=nFKSprocess
                           exit
                        endif
                     enddo
                  elseif (j_fks.eq.2 .and. found_ini2) then
                     do i=1,proc_map(0,0)
                        if (i_fks_pdg_proc(i).eq.21 .and.
     $                       j_fks_proc(i).eq.2) then
                           proc_map(i,0)=proc_map(i,0)+1
                           proc_map(i,proc_map(i,0))=nFKSprocess
                           exit
                        endif
                     enddo
                  elseif (j_fks.gt.nincoming .and. found_fnl) then
                     do i=1,proc_map(0,0)
                        if (i_fks_pdg_proc(i).eq.21 .and.
     $                       j_fks_pdg_proc(i).eq.21.and.
     $                       j_fks_proc(i).gt.nincoming) then
                           proc_map(i,0)=proc_map(i,0)+1
                           proc_map(i,proc_map(i,0))=nFKSprocess
                           exit
                        endif
                     enddo
                  else
                     write (*,*) 'Driver_mintMC: inconsistent process'
                     write (*,*) 'This process has nFKSprocesses'/
     $                    /' without soft singularities, but not a'/
     $                    /' corresponding g->gg splitting that has a'/
     $                    /' soft singularity.',found_ini1,found_ini2
     $                    ,found_fnl
                     do i=1,proc_map(0,0)
                        write (*,*) i,'-->',proc_map(i,0),':',
     &                       (proc_map(i,j),j=1,proc_map(i,0))
                     enddo
                     stop
                  endif
               endif
            enddo
            write (*,*) 'FKS process map:'
            do i=1,proc_map(0,0)
               write (*,*) i,'-->',proc_map(i,0),':',
     &              (proc_map(i,j),j=1,proc_map(i,0))
            enddo
         endif
      endif

      fold=ifl
      if (ifl.eq.0) then
         do k=1,maxproc_save
            do j=1,2
               do i=0,fks_configs
                  unwgt_table(i,j,k)=0d0
               enddo
            enddo
         enddo
         f(1)=0d0
         f(2)=0d0
         do i=0,fks_configs
            result(i,1)=0d0
            result(i,2)=0d0
         enddo
         dsigS=0d0
         dsigH=0d0
      endif

      if (ifl.eq.0)then
         do i=1,99
            if (abrv.eq.'grid'.or.abrv.eq.'born'.or.abrv(1:2).eq.'vi')
     &           then
               if(i.le.ndim-3)then
                  x(i)=xx(i)
               elseif(i.le.ndim) then
                  x(i)=ran2()   ! Choose them flat when not including real-emision
               else
                  x(i)=0.d0
               endif
            else
               if(i.le.ndim)then
                  x(i)=xx(i)
               else
                  x(i)=0.d0
               endif
            endif
         enddo
c
c Compute the Born-like contributions with nbody=.true.
c     
         call get_MC_integer(proc_map(0,0),proc_map(0,1),vol)
         nFKSprocess=proc_map(proc_map(0,1),1) ! just pick the first
                                               ! because it only matters
                                               ! which parton is j_fks
         nFKSprocess_all=nFKSprocess
         call fks_inc_chooser()
         if (j_fks.le.nincoming) then
            if (.not.foundB(1)) then
               write(*,*) 'Trying to generate Born momenta with '/
     &              /'initial state j_fks, but there is no '/
     &              /'configuration with i_fks a gluon and j_fks '/
     &              /'initial state'
               stop
            endif
            nFKSprocess=nFKSprocessBorn(1)
         else
            if (.not.foundB(2)) then
               write(*,*) 'Trying to generate Born momenta with '/
     &              /'final state j_fks, but there is no configuration'/
     &              /' with i_fks a gluon and j_fks final state'
               stop
            endif
            nFKSprocess=nFKSprocessBorn(2)
         endif
         nbody=.true.
         nFKSprocess_used=nFKSprocess
         nFKSprocess_used_Born=nFKSprocess
         call fks_inc_chooser()
         call leshouche_inc_chooser()
c THIS CAN BE OPTIMIZED
         call setcuts
         call setfksfactor(iconfig)
         wgt=1d0
         call generate_momenta(ndim,iconfig,wgt,x,p)
         call dsigF(p,wgt,w,dsigS,dsigH)
         result(0,1)= w*dsigS
         result(0,2)= w*dsigH
         f(1) = f(1)+result(0,1)
         f(2) = f(2)+result(0,2)
c
c Compute the subtracted real-emission corrections either as an explicit
c sum or a Monte Carlo sum or a combination
c      
         if (.not.( abrv.eq.'born' .or. abrv.eq.'grid' .or.
     &        abrv(1:2).eq.'vi') ) then
            nbody=.false.
            if (sum.eq.1 .or. sum.eq.2) then
               write (*,*) 'This option # 1322 has not been implemented'
     $              ,sum
               stop
            endif
            sigintR=0d0
            do i=1,proc_map(proc_map(0,1),0)
               nFKSprocess=proc_map(proc_map(0,1),i)
               nFKSprocess_used=nFKSprocess
               call fks_inc_chooser()
               call leshouche_inc_chooser()
c THIS CAN BE OPTIMIZED
               call setcuts
               call setfksfactor(iconfig)
               wgt=1d0/vol
c When sum=3, we can compute the nFKSprocesses without soft
c singularities fewer number of PS points, because their contribution is
c small. This should save some time, without degrading the uncertainty
c much. Do this by overwrite the 'wgt' variable
               if (sum.eq.3 .and. PDG_type(i_fks).ne.21) then
                  rnd=ran2()
                  rfrac=0.25d0  ! fraction of PS points to include
                                ! them. This could be determined
                                ! dynamically, based on the relative
                                ! importance of this contribution.
                  if (rnd.gt.rfract) then
                     wgt=0d0    ! fks_singular will not compute anything
                  else
                     wgt=wgt/rfract
                  endif
               endif
               call generate_momenta(ndim,iconfig,wgt,x,p)
               call dsigF(p,wgt,w,dsigS,dsigH)
               sigintR = sigintR+(abs(dsigS)+abs(dsigH))*vol*w
               result(nFKSprocess,1)= w*dsigS
               result(nFKSprocess,2)= w*dsigH
               f(1) = f(1)+result(nFKSprocess,1)
               f(2) = f(2)+result(nFKSprocess,2)
            enddo
            call fill_MC_integer(proc_map(0,1),sigintR)
         endif
         sigintF=f(1)+f(2)
         unwgt=.false.
         call update_unwgt_table(unwgt_table,proc_map,unwgt,f_check
     $        ,f_abs)
         if (f_check.ne.0d0.or.sigintF.ne.0d0) then
            if (abs(sigintF-f_check)/max(abs(f_check),abs(sigintF))
     $           .gt.1d-4) then
               write (*,*) 'Error inaccuracy in unweight table 1'
     $              ,sigintF,f_check
               stop
            elseif (abs(sigintF-f_check)/max(abs(f_check),abs(sigintF))
     $           .gt.1d-6) then
               write (*,*) 'Warning inaccuracy in unweight table 1'
     $              ,sigintF,f_check
            endif
         endif
         if (f_abs.ne.0d0) itotalpoints=itotalpoints+1
      elseif(ifl.eq.1) then
         write (*,*) 'Folding not implemented'
         stop
      elseif(ifl.eq.2) then
         unwgt=.true.
         call update_unwgt_table(unwgt_table,proc_map,unwgt,f_check
     $        ,f_abs)
c The following two are needed when writing events to do NLO/Born
c reweighting
         sigintF=f_check
         sigintF_without_w=sigintF/w
         f_abs_without_w=f_abs/w
      endif
      return
      end

     
      function sigintS(xx,w,ifl,f_abs)
c From dsample_fks
      implicit none
      integer ndim,ipole
      common/tosigint/ndim,ipole
      integer           iconfig
      common/to_configs/iconfig
      integer i
      integer ifl
      integer fold
      common /cfl/fold
      include 'mint.inc'
      real*8 sigintS,xx(ndimmax),w
      integer ione
      parameter (ione=1)
      double precision wgt,dsigS,f_abs
      include 'nexternal.inc'
      double precision x(99),p(0:3,nexternal)
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt
      double precision result
      save result
c
      write (*,*) 'Generation of S-events no longer supported'
      stop
c
      do i=1,99
        if(i.le.ndim)then
          x(i)=xx(i)
        else
          x(i)=-9d99
        endif
      enddo
      wgt=1.d0
      fold=ifl
      if (ifl.eq.0)then
         call generate_momenta(ndim,iconfig,wgt,x,p)
         result = w*dsigS(p,wgt,w)
         sigintS = result
         f_abs=abs(sigintS)
      elseif(ifl.eq.1) then
         call generate_momenta(ndim,iconfig,wgt,x,p)
         result = result+w*dsigS(p,wgt,w)
         sigintS = result
         f_abs=abs(sigintS)
      elseif(ifl.eq.2) then
         sigintS = result
         f_abs=abs(sigintS)
         evtsgn=sign(1d0,result)
      endif
      return
      end

     
      function sigintH(xx,w,ifl,f_abs)
c From dsample_fks
      implicit none
      integer ndim,ipole
      common/tosigint/ndim,ipole
      integer           iconfig
      common/to_configs/iconfig
      integer i
      integer ifl
      integer fold
      common /cfl/fold
      include 'mint.inc'
      real*8 sigintH,xx(ndimmax),w
      integer ione
      parameter (ione=1)
      double precision wgt,dsigH,f_abs
      include 'nexternal.inc'
      double precision x(99),p(0:3,nexternal)
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt
      double precision result
      save result
c
      write (*,*) 'Generation of H-events no longer supported'
      stop
c
      do i=1,99
        if(i.le.ndim)then
          x(i)=xx(i)
        else
          x(i)=-9d99
        endif
      enddo
      wgt=1.d0
      fold=ifl
      if (ifl.eq.0)then
         call generate_momenta(ndim,iconfig,wgt,x,p)
         result = w*dsigH(p,wgt,w)
         sigintH = result
         f_abs=abs(sigintH)
      elseif(ifl.eq.1) then
         call generate_momenta(ndim,iconfig,wgt,x,p)
         result = result+w*dsigH(p,wgt,w)
         sigintH = result
         f_abs=abs(sigintH)
      elseif(ifl.eq.2) then
         sigintH = result
         f_abs=abs(sigintH)
         evtsgn=sign(1d0,result)
      endif
      return
      end




      subroutine update_unwgt_table(unwgt_table,proc_map,unweight,f
     $     ,f_abs)
      implicit none
      include 'nexternal.inc'
      include 'genps.inc'
      include 'nFKSconfigs.inc'
      include 'reweight.inc'
      double precision unwgt_table(0:fks_configs,2,maxproc),f,f_abs
     $     ,dummy,dlum,f_abs_H,f_abs_S,rnd,ran2,current,f_abs_S_un
     $     ,f_unwgt(fks_configs,maxproc)
      external ran2
      external dlum
      integer maxproc_found,maxproc_found_first,iproc_save(fks_configs)
     $     ,i,j,ii,jj,k,kk,proc_map(0:fks_configs,0:fks_configs)
      save maxproc_found
      logical unweight,firsttime
      data firsttime /.true./
      integer nFKSprocess_save,ifound
      integer id_current(maxproc,nexternal),id_first(maxproc,nexternal)
     &     ,nequal,equal_to(maxproc,fks_configs),eto(maxproc
     &     ,fks_configs),equal_to_inverse(maxproc,fks_configs)
     &     ,etoi(maxproc,fks_configs)
      save equal_to,equal_to_inverse,eto,etoi
      character*100 buff
      INTEGER              IPROC
      DOUBLE PRECISION PD(0:MAXPROC)
      COMMON /SUBPROC/ PD, IPROC
      INTEGER NFKSPROCESS
      COMMON/C_NFKSPROCESS/NFKSPROCESS
      integer i_fks,j_fks
      common/fks_indices/i_fks,j_fks
      integer maxflow
      parameter (maxflow=999)
      integer idup(nexternal,maxproc),mothup(2,nexternal,maxproc),
     &     icolup(2,nexternal,maxflow)
      common /c_leshouche_inc/idup,mothup,icolup
      integer fks_j_from_i(nexternal,0:nexternal)
     &     ,particle_type(nexternal),pdg_type(nexternal)
      common /c_fks_inc/fks_j_from_i,particle_type,pdg_type
      logical Hevents
      common/SHevents/Hevents
      integer i_process
      common/c_addwrite/i_process
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt
      character*4 abrv
      common /to_abrv/ abrv

c For the S-events, we can combine processes when they give identical
c processes at the Born. Make sure we check that we get indeed identical
c IRPOC's
      if (firsttime) then
         nFKSprocess_save=nFKSprocess
         do nFKSprocess=1,fks_configs
            call fks_inc_chooser()
            call leshouche_inc_chooser()
            dummy=dlum()
c 1. First map the IPROC's for this nFKSprocess to the underlying Born
c to get the unique IPROC's
            iproc_save(nFKSprocess)=iproc
            do j=1,iproc
               do i=1,nexternal-1
                  if (i.eq.min(j_fks,i_fks)) then
                     if (abs(idup(i_fks,j)).eq.abs(idup(j_fks,j))) then
                        id_current(i,j)=21
                     elseif(abs(particle_type(j_fks)).eq.3) then
                        id_current(i,j)=idup(j_fks,j)
                     elseif (abs(particle_type(i_fks)).eq.3) then
                        id_current(i,j)=-idup(i_fks,j)
                     else
                        write (*,*) 'Error #1 in unwgt_table'
                        stop
                     endif
                  elseif (i.lt.max(j_fks,i_fks)) then
                     id_current(i,j)=idup(i,j)
                  else
                     id_current(i,j)=idup(i+1,j)
                  endif
               enddo
c 1a. if IPROC not yet found, save it for checking. Also fill an array
c equal_to() that maps the IPROC to the set of unique IPROCs
               if (j.eq.1) then
                  maxproc_found=1
                  equal_to(j,nFKSprocess)=1
                  equal_to_inverse(1,nFKSprocess)=j
               elseif (j.gt.1) then
                  do jj=1,maxproc_found
                     nequal=0
                     do ii=1,nexternal-1
                        if (id_current(ii,j).eq.id_current(ii
     &                       ,equal_to_inverse(jj,nFKSprocess))) then
                           nequal=nequal+1
                        endif
                     enddo
                     if (nequal.eq.nexternal-1) then
                        equal_to(j,nFKSprocess)=jj
                        exit
                     endif
                  enddo
                  if (nequal.ne.nexternal-1) then
                     maxproc_found=maxproc_found+1
                     equal_to(j,nFKSprocess)=maxproc_found
                     equal_to_inverse(maxproc_found,nFKSprocess)=j
                  endif
               endif
            enddo
c 2. Now that we have the unique IPROCs for a given nFKSprocess, we need
c to check that they are equal among all nFKSprocesses.
            if (nFKSprocess.eq.1) then
               maxproc_found_first=maxproc_found
               do j=1,iproc
                  if (j.le.maxproc_found) then
                     do i=1,nexternal-1
                        id_first(i,j)=id_current(i,equal_to_inverse(j
     &                       ,nFKSprocess))
                     enddo
                     eto(j,nFKSprocess)=equal_to(j,nFKSprocess)
                     etoi(j,nFKSprocess)=equal_to_inverse(j,nFKSprocess)
                  else
                     eto(j,nFKSprocess)=equal_to(j,nFKSprocess)
                  endif
               enddo
            else
               if (maxproc_found.ne.maxproc_found_first) then
                  write (*,*) 'Number of unique IPROCs not identical'/
     $                 /' among nFKSprocesses',nFKSprocess,maxproc_found
     $                 ,maxproc_found_first
                  stop
               endif
c If order not equal: re-order them. This will fill the eto() and etoi()
c arrays which map the processes for a given FKS dir to the 1st FKS dir
               do j=1,iproc
                  do jj=1,maxproc_found
                     nequal=0
                     do ii=1,nexternal-1
                        if (id_current(ii,j) .eq. id_first(ii,jj)) then
                           nequal=nequal+1
                        endif
                     enddo
                     if (nequal.eq.nexternal-1) then
                        eto(j,nFKSprocess)=jj
                        etoi(jj,nFKSprocess)=j
                     endif
                  enddo
               enddo
c Should have the correct mapping now. Check that this is indeed the
c case.
               do j=1,maxproc_found
                  do i=1,nexternal-1
                     if (id_current(i,etoi(j,nFKSprocess)) .ne.
     &                    id_first(i,j)) then
                        write (*,*)'Particle IDs not equal (inverse)',j
     &                       ,nFKSprocess,maxproc_found,iproc
                        do jj=1,maxproc_found
                           write (*,*) jj,etoi(jj,nFKSprocess)
     &                          ,' current:', (id_current(ii,etoi(jj
     &                          ,nFKSprocess)),ii=1,nexternal-1)
                           write (*,*) jj,jj
     &                          ,' saved  :', (id_first(ii
     &                          ,jj),ii=1,nexternal-1)
                        enddo
                        stop
                     endif
                  enddo
               enddo
               do j=1,iproc
                  do i=1,nexternal-1
                     if (id_current(i,j) .ne. id_first(i,eto(j
     &                    ,nFKSprocess))) then
                        write (*,*)'Particle IDs not equal',j
     &                       ,nFKSprocess,maxproc_found,iproc
                        do jj=1,iproc
                           write (*,*) jj,jj ,' current:',
     &                          (id_current(ii,jj),ii=1 ,nexternal-1)
                           write (*,*) jj,jj,' saved  :', (id_first(ii
     &                          ,eto(jj,nFKSprocess)),ii=1,nexternal-1)
                        enddo
                        stop
                     endif
                  enddo
               enddo
            endif
c Print the map to the screen
            if (nFKSprocess.eq.1) 
     &       write (*,*) '================================'
            if (nFKSprocess.eq.1) write (*,*) 'process combination map '
     &           //'(specified per FKS dir):'
            write (buff(1:3),'(i3)') nFKSprocess
            write (buff(4:13),'(a)') ' map     '
            do j=1,iproc
               write (buff(10+4*j:13+4*j),'(i4)') eto(j,nFKSprocess)
            enddo
            write (*,'(a)') buff(1:13+4*iproc)
            write (buff(1:3),'(i3)') nFKSprocess
            write (buff(4:13),'(a)') ' inv. map'
            do j=1,maxproc_found
               write (buff(10+4*j:13+4*j),'(i4)') etoi(j,nFKSprocess)
            enddo
            write (*,'(a)') buff(1:13+4*maxproc_found)
            if (nFKSprocess.eq.fks_configs) 
     &       write (*,*) '================================'
         enddo
         if (maxproc_found.ne.iproc_save(nFKSprocess_used_born)) then
            write (*,*) 'ERROR #5 in unweight_table',maxproc_found
     $           ,nFKSprocess_used_born
     $           ,iproc_save(nFKSprocess_used_born)
            stop
         endif
c Restore nFKSprocess
         nFKSprocess=nFKSprocess_save
         call fks_inc_chooser()
         call leshouche_inc_chooser()
         firsttime=.false.
      endif
c Trivial check on the Born contribution
      do i=1,iproc_save(nFKSprocess_used_born)
         if (unwgt_table(0,2,i).ne.0d0) then
            write (*,*)
     &           'H-event contribution to the n-body should be zero',i
            stop
         endif
      enddo
c
c Compute the total rate. This is simply the sum of all
c
      if (.not.( abrv.eq.'born' .or. abrv.eq.'grid' .or.
     &     abrv(1:2).eq.'vi') ) then
         f=0d0
c all the (n+1)-body contributions
         do i=1,proc_map(proc_map(0,1),0)
            nFKSprocess=proc_map(proc_map(0,1),i)
            do j=1,iproc_save(nFKSprocess)
               f = f + unwgt_table(nFKSprocess,1,j)+
     &              unwgt_table(nFKSprocess,2,j)
            enddo
         enddo
c and the n-body contributions
         do j=1,iproc_save(nFKSprocess_used_born)
            f=f+unwgt_table(0,1,j)+unwgt_table(0,2,j)
         enddo
c
c Compute the abs of the total rate. Need to take ABS of all
c contributions separately, except when they give equal events
c (i.e. equal momenta, particle IDs, color info and shower starting
c scale, this might happen for S-events)
c     
         f_abs_H=0d0
         f_abs_S=0d0
c Nothing to combine for H-events, so need to sum them independently
         do i=1,proc_map(proc_map(0,1),0)
            nFKSprocess=proc_map(proc_map(0,1),i)
            do j=1,iproc_save(nFKSprocess)
               f_abs_H=f_abs_H+abs(unwgt_table(nFKSprocess,2,j))
            enddo
         enddo
         do i=1,fks_configs
            do j=1,maxproc_found
               f_unwgt(i,j)=0d0
            enddo
         enddo
c Add the Born and the S-events
         do k=1,proc_map(proc_map(0,1),0)
            nFKSprocess=proc_map(proc_map(0,1),k)
            do i=1,maxproc_found
               if (proc_map(proc_map(0,1),0).gt.1) then
c if there are more than one nFKSprocesses compute (i.e. sum.eq.3) we
c should add the Born only the one with the soft singularity
                  call fks_inc_chooser()
                  if (PDG_type(i_fks).eq.21) then
                     f_unwgt(nFKSprocess,i)=
     &                    unwgt_table(0,1,i)+unwgt_table(0,2,i)
                  endif
                  do j=1,iproc_save(nFKSprocess)
                     if (eto(j,nFKSprocess).eq.i) then
                        f_unwgt(nFKSprocess,i)=f_unwgt(nFKSprocess,i)
     $                       +unwgt_table(nFKSprocess,1,j)
                     endif
                  enddo
               else
                  f_unwgt(nFKSprocess,i)=
     &                 unwgt_table(0,1,i)+unwgt_table(0,2,i)
                  do j=1,iproc_save(nFKSprocess)
                     if (eto(j,nFKSprocess).eq.i) then
                        f_unwgt(nFKSprocess,i)=f_unwgt(nFKSprocess,i)
     $                       +unwgt_table(nFKSprocess,1,j)
                     endif
                  enddo
               endif
               f_abs_S=f_abs_S+abs(f_unwgt(nFKSprocess,i))
            enddo
         enddo
         if (.not.unweight)then
c just return the (correct) absolute value
            f_abs=f_abs_H+f_abs_S
         else
c pick one at random and update reweight info and all that
            f_abs=f_abs_H+f_abs_S
            if (f_abs.ne.0d0) then
               rnd=ran2()
               if (rnd.le.f_abs_H/f_abs) then
                  Hevents=.true.
c Pick one of the nFKSprocesses and one of the IPROC's 
                  i_process=1
                  nFKSprocess=1
                  current=abs(unwgt_table(1,2,1))
                  rnd=ran2()
                  do while (current.lt.rnd*f_abs_H .and.
     $                 (i_process.le.iproc_save(nFKSprocess) .or.
     $                 nFKSprocess.le.fks_configs))
                     i_process=i_process+1
                     if (i_process.gt.iproc_save(nFKSprocess)) then
                        i_process=1
                        nFKSprocess=nFKSprocess+1
                     endif
                     current=current+abs(unwgt_table(nFKSprocess,2
     $                    ,i_process))
                  enddo
                  if (i_process.gt.iproc_save(nFKSprocess) .or.
     $                 nFKSprocess.gt.fks_configs) then
                     write (*,*) 'ERROR #4 in unweight table',i_process
     $                    ,nFKSprocess
                     stop
                  endif
                  evtsgn=sign(1d0,unwgt_table(nFKSprocess,2,i_process))
               else
                  Hevents=.false.
c Pick one of the nFKSprocesses and IPROC's of the Born
                  i_process=1
                  nFKSprocess=1
                  current=abs(f_unwgt(1,1))
                  rnd=ran2()
                  do while (current.lt.rnd*f_abs_S .and.
     $                 (i_process.le.maxproc_found .or.
     $                 nFKSprocess.le.fks_configs))
                     i_process=i_process+1
                     if (i_process.gt.maxproc_found) then
                        i_process=1
                        nFKSprocess=nFKSprocess+1
                     endif
                     current=current+abs(f_unwgt(nFKSprocess,i_process))
                  enddo
                  if (i_process.gt.maxproc_found .or.
     $                 nFKSprocess.gt.fks_configs) then
                     write (*,*) 'ERROR #4 in unweight table',i_process
     $                    ,maxproc_found,nFKSprocess
                     stop
                  endif
                  evtsgn=sign(1d0,f_unwgt(nFKSprocess,i_process))
c Set the i_process to one of the (n+1)-body configurations that leads
c to this Born configuration. Needed for add_write_info to work properly
                  i_process=etoi(i_process,nFKSprocess)
               endif
            endif
c Now update the reweight information
            if(doreweight) then
               call fks_inc_chooser()
               call leshouche_inc_chooser()
               if (Hevents) then
                  call fill_reweight0inc(nFKSprocess*2)
               else
                  call fill_reweight0inc(nFKSprocess*2-1)
               endif
c Set the n-body contributions to zero for H-events, or for S-events
c with more than one nFKSprocess contribution and not nFKSprocess with
c soft singularity
               if (Hevents.or.(PDG_type(i_fks).ne.21.and.
     &              proc_map(proc_map(0,1),0).gt.1)) then
                  wgtwborn(2)=0d0
                  wgtwns(2)=0d0
                  wgtwnsmuf(2)=0d0
                  wgtwnsmur(2)=0d0
               endif
               call reweight_fill_extra()
            endif
         endif
      else  ! abrv='born' or 'grid' or 'vi*' (ie. doing only the nbody)
         f=0d0
c and the n-body contributions
         do j=1,iproc_save(nFKSprocess_used_born)
            if (unwgt_table(0,2,j).ne.0d0) then
               write (*,*) 'Error #4 in unwgt_table',unwgt_table(0,2,j)
               stop
            endif
            f=f+unwgt_table(0,1,j)
         enddo
         f_abs_H=0d0
         f_abs_S=0d0
         do i=1,maxproc_found
            do j=1,iproc_save(nFKSprocess_used_born)
               if (eto(j,nFKSprocess_used_born).eq.i) then
                  f_unwgt(nFKSprocess_used_born,i)=unwgt_table(0,1,i)
               endif
            enddo
            f_abs_S=f_abs_S+abs(f_unwgt(nFKSprocess_used_born,i))
         enddo
         if (.not.unweight)then
c just return the (correct) absolute value
            f_abs=f_abs_H+f_abs_S
         else
c pick one at random and update reweight info and all that
            f_abs=f_abs_H+f_abs_S
            Hevents=.false.
            if (f_abs.ne.0d0) then
               rnd=ran2()
c Pick one of the IPROC's of the Born
               i_process=1
               current=abs(f_unwgt(nFKSprocess_used_born,1))
               do while (current.lt.rnd*f_abs_S .and.
     $              i_process.le.maxproc_found)
                  i_process=i_process+1
                  current=current+abs(f_unwgt(nFKSprocess_used_born
     &                 ,i_process))
               enddo
               if (i_process.gt.maxproc_found) then
                  write (*,*) 'ERROR #4 in unweight table',i_process 
                  stop
               endif
               evtsgn=sign(1d0,f_unwgt(nFKSprocess_used_born,i_process))
c Set the i_process to one of the (n+1)-body configurations that leads
c to this Born configuration. Needed for add_write_info to work properly
               i_process=etoi(i_process
     &              ,nFKSprocess_used_born)
            endif
c Now update the reweight information
            if(doreweight) then
               nFKSprocess=nFKSprocess_used_born
               call fks_inc_chooser()
               call leshouche_inc_chooser()
               call fill_reweight0inc(nFKSprocess_used_born*2-1)
               call reweight_fill_extra()
            endif
         endif
      endif
      return
      end
