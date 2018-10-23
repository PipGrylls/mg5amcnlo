      Program DRIVER
c**************************************************************************
c     This is the driver for the whole calculation
c**************************************************************************
      use extra_weights
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
      integer i,j,k,l,l1,l2
      character*130 buf
c
c     Global
c
cc
      include 'run.inc'
      include 'coupl.inc'
      
c     Vegas stuff
      integer         ndim
      common/tosigint/ndim

      real*8 sigint
      external sigint

      integer irestart
      logical savegrid

      logical            flat_grid
      common/to_readgrid/flat_grid                !Tells if grid read from file

      integer i_momcmp_count
      double precision xratmax
      common/ccheckcnt/i_momcmp_count,xratmax

      integer n_mp, n_disc
c For MINT:
      include "mint.inc"
      integer nhits_in_grids(maxchannels)
      real* 8 xgrid(0:nintervals,ndimmax,maxchannels),ymax(nintervals
     $     ,ndimmax,maxchannels),ymax_virt(0:maxchannels),ans(nintegrals
     $     ,0:maxchannels),unc(nintegrals,0:maxchannels),chi2(nintegrals
     $     ,0:maxchannels),x(ndimmax),itmax_fl
      integer ixi_i,iphi_i,iy_ij,vn
      integer ifold(ndimmax) 
      common /cifold/ifold
      integer ifold_energy,ifold_phi,ifold_yij
      common /cifoldnumbers/ifold_energy,ifold_phi,ifold_yij
      logical putonshell
      integer imode,dummy
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt

      logical SHsep
      logical Hevents
      common/SHevents/Hevents
      character*10 dum
c statistics for MadLoop      
      integer ntot,nsun,nsps,nups,neps,n100,nddp,nqdp,nini,n10,n1(0:9)
      common/ups_stats/ntot,nsun,nsps,nups,neps,n100,nddp,nqdp,nini,n10,n1

      double precision virtual_over_born
      common/c_vob/virtual_over_born
      double precision average_virtual(0:n_ave_virt,maxchannels)
     $     ,virtual_fraction(maxchannels)
      common/c_avg_virt/average_virtual,virtual_fraction
      include 'orders.inc'
      integer              n_ord_virt
      common /c_n_ord_virt/n_ord_virt

c timing statistics
      include "timing_variables.inc"
      real*4 tOther, tTot

c general MadFKS parameters
      include "FKSParams.inc"

c applgrid
      integer iappl
      common /for_applgrid/ iappl
c stats for granny_is_res
      double precision deravg,derstd,dermax,xi_i_fks_ev_der_max
     &     ,y_ij_fks_ev_der_max
      integer ntot_granny,derntot,ncase(0:6)
      common /c_granny_counters/ ntot_granny,ncase,derntot,deravg,derstd
     &     ,dermax,xi_i_fks_ev_der_max,y_ij_fks_ev_der_max
      logical              fixed_order,nlo_ps
      common /c_fnlo_nlops/fixed_order,nlo_ps


C-----
C  BEGIN CODE
C-----  
c
c     Setup the timing variable
c
      call cpu_time(tBefore)
      fixed_order=.true.
      nlo_ps=.false.

c     Read general MadFKS parameters
c
      call FKSParamReader(paramFileName,.TRUE.,.FALSE.)
      do kchan=1,maxchannels
         do i=0,n_ave_virt
            average_virtual(i,kchan)=0d0
         enddo
         virtual_fraction(kchan)=max(virt_fraction,min_virt_fraction)
      enddo
      n_ord_virt=amp_split_size
      
c
c     Read process number
c
      ntot_granny=0
      derntot=0
      do i=0,6
         ncase(i)=0
      enddo
      ntot=0
      nsun=0
      nsps=0
      nups=0
      neps=0
      n100=0
      nddp=0
      nqdp=0
      nini=0
      n10=0
      do i=0,9
        n1(i)=0
      enddo
      
      call setrun                !Sets up run parameters
      call setpara('param_card.dat')   !Sets up couplings and masses
      call setcuts               !Sets up cuts and particle masses
      call printout              !Prints out a summary of paramaters
      call run_printout          !Prints out a summary of the run settings
      call initcluster
      call check_amp_split 
c     
c     Get user input
c
      write(*,*) "getting user params"
      call get_user_params(ncall,itmax,imode)
      if(imode.eq.0)then
        flat_grid=.true.
      else
        flat_grid=.false.
      endif
      ndim = 3*(nexternal-nincoming)-4
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
      write(*,*) "about to integrate ", ndim,ncall,itmax
c APPLgrid
      if (imode.eq.0) iappl=0 ! overwrite when starting completely fresh
      if(iappl.ne.0) then
         write(6,*) "Initializing aMCfast ..."
c     Set flavor map, starting from all possible
c     parton lumi configurations defined in initial_states_map.dat
         call setup_flavourmap
c     Fill the number of combined matrix elements for given initial state luminosity
         call find_iproc_map
         write(6,*) "   ... done."
      endif
      i_momcmp_count=0
      xratmax=0.d0
      unwgt=.false.
      call addfil(dum)
      if (imode.eq.-1.or.imode.eq.0) then
         if(imode.eq.0)then
c Don't safe the reweight information when just setting up the grids.
            doreweight=.false.
            do_rwgt_scale=.false.
            do_rwgt_pdf=.false.
            do kchan=1,nchans
               do i=1,ndimmax
                  do j=0,nintervals
                     xgrid(j,i,kchan)=0.d0
                  enddo
               enddo
            enddo
         else
            doreweight=do_rwgt_scale.or.do_rwgt_pdf
c to restore grids:
            open (unit=12, file='mint_grids',status='old')
            ans(1,0)=0d0
            unc(1,0)=0d0
            do kchan=1,nchans
               do j=0,nintervals
                  read (12,*) (xgrid(j,i,kchan),i=1,ndim)
               enddo
               do j=1,nintervals_virt
                  do k=0,n_ord_virt
                     read (12,*) (ave_virt(j,i,k,kchan),i=1,ndim)
                  enddo
               enddo
               read(12,*) ans(1,kchan),unc(1,kchan),dummy,dummy
     $              ,nhits_in_grids(kchan)
               read(12,*) virtual_fraction(kchan),average_virtual(0
     $              ,kchan)
               ans(1,0)=ans(1,0)+ans(1,kchan)
               unc(1,0)=unc(1,0)+unc(1,kchan)**2
            enddo
            unc(1,0)=sqrt(unc(1,0))
            close (12)
            write (*,*) "Update iterations and points to",itmax,ncall
         endif
c
         write (*,*) 'imode is ',imode

         if (ickkw.eq.-1) then
            min_virt_fraction=1d0
            do kchan=1,nchans
               virtual_fraction(kchan)=1d0
            enddo
         endif
C check for zero cross-section
C if restoring grids corresponding to sigma=0, just terminate the run
         if (imode.ne.0.and.ans(1,0).eq.0d0.and.unc(1,0).eq.0d0) then
            call initplot()
            call close_run_zero_res(ncall, itmax, ndim)
            stop
         endif
         call mint(sigint,ndim,ncall,itmax,imode,xgrid,ymax
     $        ,ymax_virt,ans,unc,chi2,nhits_in_grids)
         call topout
         call deallocate_weight_lines
         write(*,*)'Final result [ABS]:',ans(1,0),' +/-',unc(1,0)
         write(*,*)'Final result:',ans(2,0),' +/-',unc(2,0)
         write(*,*)'chi**2 per D.o.F.:',chi2(1,0)
         open(unit=58,file='results.dat',status='unknown')
         do kchan=0,nchans
            write(58,*) ans(1,kchan),unc(2,kchan),0d0,0,0,0,0,0d0,0d0
     $           ,ans(2,kchan)
         enddo
         close(58)
c
c to save grids:
         open (unit=12, file='mint_grids',status='unknown')
         do kchan=1,nchans
            do j=0,nintervals
               write (12,*) (xgrid(j,i,kchan),i=1,ndim)
            enddo
            do j=1,nintervals_virt
               do k=0,n_ord_virt
                  write (12,*) (ave_virt(j,i,k,kchan),i=1,ndim)
               enddo
            enddo
            write (12,*) ans(1,kchan),unc(1,kchan),ncall,itmax
     $           ,nhits_in_grids(kchan)
            write (12,*) virtual_fraction(kchan),average_virtual(0
     $           ,kchan)
         enddo
         close (12)
      else
         write (*,*) 'Unknown imode',imode
         stop
      endif

      if (ntot.ne.0) then
         write(*,*) "Satistics from MadLoop:"
         write(*,*)
     &        "  Total points tried:                              ",ntot
         write(*,*)
     &        "  Stability unknown:                               ",nsun
         write(*,*)
     &        "  Stable PS point:                                 ",nsps
         write(*,*)
     &        "  Unstable PS point (and rescued):                 ",nups
         write(*,*)
     &        "  Exceptional PS point (unstable and not rescued): ",neps
         write(*,*)
     &        "  Double precision used:                           ",nddp
         write(*,*)
     &        "  Quadruple precision used:                        ",nqdp
         write(*,*)
     &        "  Initialization phase-space points:               ",nini
         write(*,*)
     &        "  Unknown return code (100):                       ",n100
         write(*,*)
     &        "  Unknown return code (10):                        ",n10
         write(*,*)
     &        "  Unit return code distribution (1):               "
         do j=0,9
           if (n1(j).ne.0) then
              write(*,*) "#Unit ",j," = ",n1(j)
           endif
         enddo
      endif

      write (*,*) 'counters for the granny resonances'
      write (*,*) 'ntot     ',ntot_granny
      if (ntot_granny.gt.0) then
         do i=0,6
            write (*,*) '% icase ',i,' : ',ncase(i)/dble(ntot_granny)
         enddo
         write (*,*) 'average,std dev. and max of derivative:',deravg
     &        ,sqrt(abs(derstd-deravg**2)),dermax
         write (*,*)
     &        'and xi_i_fks and y_ij_fks corresponding to max of der.',
     &        xi_i_fks_ev_der_max,y_ij_fks_ev_der_max
      endif
      call cpu_time(tAfter)
      tTot = tAfter-tBefore
      tOther = tTot - (tBorn+tGenPS+tReal+tCount+tIS+tFxFx+tf_nb+tf_all
     &     +t_as+tr_s+tr_pdf+t_plot+t_cuts+t_MC_subt+t_isum+t_p_unw
     $     +t_write)
      write(*,*) 'Time spent in Born : ',tBorn
      write(*,*) 'Time spent in PS_Generation : ',tGenPS
      write(*,*) 'Time spent in Reals_evaluation: ',tReal
      write(*,*) 'Time spent in MCsubtraction : ',t_MC_subt
      write(*,*) 'Time spent in Counter_terms : ',tCount
      write(*,*) 'Time spent in Integrated_CT : ',tIS-tOLP
      write(*,*) 'Time spent in Virtuals : ',tOLP      
      write(*,*) 'Time spent in FxFx_cluster : ',tFxFx
      write(*,*) 'Time spent in Nbody_prefactor : ',tf_nb
      write(*,*) 'Time spent in N1body_prefactor : ',tf_all
      write(*,*) 'Time spent in Adding_alphas_pdf : ',t_as
      write(*,*) 'Time spent in Reweight_scale : ',tr_s
      write(*,*) 'Time spent in Reweight_pdf : ',tr_pdf
      write(*,*) 'Time spent in Filling_plots : ',t_plot
      write(*,*) 'Time spent in Applying_cuts : ',t_cuts
      write(*,*) 'Time spent in Sum_ident_contr : ',t_isum
      write(*,*) 'Time spent in Pick_unwgt : ',t_p_unw
      write(*,*) 'Time spent in Write_events : ',t_write
      write(*,*) 'Time spent in Other_tasks : ',tOther
      write(*,*) 'Time spent in Total : ',tTot

      open (unit=12, file='res.dat',status='unknown')
      do kchan=0,nchans
         write (12,*)ans(1,kchan),unc(1,kchan),ans(2,kchan),unc(2,kchan)
     $        ,itmax,ncall,tTot
      enddo
      close(12)


      if(i_momcmp_count.ne.0)then
        write(*,*)'     '
        write(*,*)'WARNING: genps_fks code 555555'
        write(*,*)i_momcmp_count,xratmax
      endif

      end


      block data timing
c timing statistics
      include "timing_variables.inc"
      data tOLP/0.0/
      data tGenPS/0.0/
      data tBorn/0.0/
      data tIS/0.0/
      data tReal/0.0/
      data tCount/0.0/
      data tFxFx/0.0/
      data tf_nb/0.0/
      data tf_all/0.0/
      data t_as/0.0/
      data tr_s/0.0/
      data tr_pdf/0.0/
      data t_plot/0.0/
      data t_cuts/0.0/
      data t_MC_subt/0.0/
      data t_isum/0.0/
      data t_p_unw/0.0/
      data t_write/0.0/
      end


      double precision function sigint(xx,vegas_wgt,ifl,f)
      use weight_lines
      use extra_weights
      implicit none
      include 'nexternal.inc'
      include 'mint.inc'
      include 'nFKSconfigs.inc'
      include 'run.inc'
      include 'orders.inc'
      include 'fks_info.inc'
      double precision xx(ndimmax),vegas_wgt,f(nintegrals),jac,p(0:3
     $     ,nexternal),rwgt,vol,sig,x(99),MC_int_wgt
      integer ifl,nFKS_born,nFKS_picked,iFKS,nFKS_min,iamp
     $     ,nFKS_max,izero,ione,itwo,mohdr,i,iran_picked
      parameter (izero=0,ione=1,itwo=2,mohdr=-100)
      logical passcuts,passcuts_nbody,passcuts_n1body,sum,firsttime
      data firsttime/.true./
      external passcuts
      integer             ini_fin_fks(maxchannels)
      common/fks_channels/ini_fin_fks
      data sum /.false./
      integer         ndim
      common/tosigint/ndim
      logical       nbody
      common/cnbody/nbody
      double precision p1_cnt(0:3,nexternal,-2:2),wgt_cnt(-2:2)
     $     ,pswgt_cnt(-2:2),jac_cnt(-2:2)
      common/counterevnts/p1_cnt,wgt_cnt,pswgt_cnt,jac_cnt
      double precision p_born(0:3,nexternal-1)
      common /pborn/   p_born
      double precision           virt_wgt_mint(0:n_ave_virt),
     &                           born_wgt_mint(0:n_ave_virt)
      common /virt_born_wgt_mint/virt_wgt_mint,born_wgt_mint
      double precision virtual_over_born
      common/c_vob/virtual_over_born
      logical                calculatedBorn
      common/ccalculatedBorn/calculatedBorn
      character*4      abrv
      common /to_abrv/ abrv
      integer iappl
      common /for_applgrid/ iappl
      double precision       wgt_ME_born,wgt_ME_real
      common /c_wgt_ME_tree/ wgt_ME_born,wgt_ME_real
C dressed initial lepton stuff
      double precision vol_ee_MCintN
      integer n_ee, i_ee_bw
      logical bw_exists
      common /to_dressed_leptons/n_ee
      common /to_dressed_leptons_MCint/vol_ee_MCintN
      common /to_dressed_leptons_bw/i_ee_bw, bw_exists
C
      integer ini_fin_fks_map(0:2,0:fks_configs)
      save ini_fin_fks_map
      if (firsttime) then
         firsttime=.false.
         call setup_ini_fin_fks_map(ini_fin_fks_map)
         write (*,*) 'initial-final FKS maps:'
         write (*,*) 0 ,':',ini_fin_fks_map(0,:)
         write (*,*) 1 ,':',ini_fin_fks_map(1,:)
         write (*,*) 2 ,':',ini_fin_fks_map(2,:)
      endif
      if (ifl.ne.0) then
         write (*,*) 'ERROR ifl not equal to zero in sigint',ifl
         stop 1
      endif
      if (iappl.ne.0 .and. sum) then
         write (*,*) 'WARNING: applgrid only possible '/
     &        /'with MC over FKS directories',iappl,sum
         write (*,*) 'Switching to MC over FKS directories'
         sum=.false.
      endif
      sigint=0d0
      icontr=0
      do iamp=0,amp_split_size
         virt_wgt_mint(iamp)=0d0
         born_wgt_mint(iamp)=0d0
      enddo
      virtual_over_born=0d0
      wgt_me_born=0d0
      wgt_me_real=0d0
      if (ickkw.eq.-1) H1_factor_virt=0d0
      if (ickkw.eq.3) call set_FxFx_scale(0,p)
      call update_vegas_x(xx,x)
      call get_MC_integer(max(ini_fin_fks(ichan),1)
     $     ,ini_fin_fks_map(ini_fin_fks(ichan),0),iran_picked,vol)
      nFKS_picked=ini_fin_fks_map(ini_fin_fks(ichan),iran_picked)
      
c The nbody contributions
      if (abrv.eq.'real') goto 11
      nbody=.true.
      calculatedBorn=.false.
      call get_born_nFKSprocess(nFKS_picked,nFKS_born)
      call update_fks_dir(nFKS_born)
      if (ini_fin_fks(ichan).eq.0) then
         jac=1d0
      else
         jac=0.5d0
      endif
      call generate_momenta(ndim,iconfig,jac,x,p)
      if (p_born(0,1).lt.0d0.or.p(0,1).lt.0d0.or.jac.lt.0d0) goto 12
      call compute_prefactors_nbody(vegas_wgt)
      call set_cms_stuff(izero)
      passcuts_nbody=passcuts(p1_cnt(0,1,0),rwgt)
      if (passcuts_nbody) then
         if (ickkw.eq.3) call set_FxFx_scale(1,p1_cnt(0,1,0))
         call set_alphaS(p1_cnt(0,1,0))
         if (abrv(1:2).ne.'vi') then
            call compute_born
         endif
         if (abrv.ne.'born') then
            call compute_nbody_noborn
         endif
      endif

 11   continue
c The n+1-body contributions (including counter terms)
      if ( abrv(1:4).eq.'born' .or.
     $     abrv(1:4).eq.'bovi' .or.
     $     abrv(1:2).eq.'vi' ) goto 12
      nbody=.false.
      if (sum) then
         nFKS_min=1
         nFKS_max=ini_fin_fks_map(ini_fin_fks(ichan),0)
         MC_int_wgt=1d0
      else
         nFKS_min=iran_picked
         nFKS_max=iran_picked
         MC_int_wgt=1d0/vol
      endif
      do i=nFKS_min,nFKS_max
         iFKS=ini_fin_fks_map(ini_fin_fks(ichan),i)
         calculatedBorn=.false. 
         ! MZ this is a temporary fix for processes without
         ! soft singularities associated to the initial state
         ! DO NOT extend this fix to event generation
         wgt_me_born=0d0
         wgt_me_real=0d0
         jac=MC_int_wgt
         call update_fks_dir(iFKS)
         call generate_momenta(ndim,iconfig,jac,x,p)
         if (p_born(0,1).lt.0d0.or.p(0,1).lt.0d0.or.jac.lt.0d0) cycle
         call compute_prefactors_n1body(vegas_wgt,jac)
         call set_cms_stuff(izero)
         passcuts_nbody =passcuts(p1_cnt(0,1,0),rwgt)
         call set_cms_stuff(mohdr)
         passcuts_n1body=passcuts(p,rwgt)
         if (passcuts_nbody .and. abrv.ne.'real') then
            call set_cms_stuff(izero)
            if (ickkw.eq.3) call set_FxFx_scale(2,p1_cnt(0,1,0))
            call set_alphaS(p1_cnt(0,1,0))
            call compute_soft_counter_term(0d0)
            call set_cms_stuff(ione)
            call compute_collinear_counter_term(0d0)
            call set_cms_stuff(itwo)
            call compute_soft_collinear_counter_term(0d0)
         endif
         if (passcuts_n1body) then
            call set_cms_stuff(mohdr)
            if (ickkw.eq.3) call set_FxFx_scale(3,p)
            call set_alphaS(p)
            call compute_real_emission(p,1d0)
         endif
      enddo
      
 12   continue
c Include PDFs and alpha_S and reweight to include the uncertainties
      if (ickkw.eq.-1) call include_veto_multiplier
      call include_PDF_and_alphas
      if (doreweight) then
         if (do_rwgt_scale .and. ickkw.ne.-1) call reweight_scale
         if (do_rwgt_scale .and. ickkw.eq.-1) call reweight_scale_NNLL
         if (do_rwgt_pdf) call reweight_pdf
      endif
      
      if (iappl.ne.0) then
         if (sum) then
            write (*,*) 'ERROR: applgrid only possible '/
     &           /'with MC over FKS directories',iappl,sum
            stop 1
         endif
         call fill_applgrid_weights(vegas_wgt)
      endif

c Importance sampling for FKS configurations
      if (sum) then
         call get_wgt_nbody(sig)
         call fill_MC_integer(max(ini_fin_fks(ichan),1),iran_picked
     $        ,abs(sig))
      else
         call get_wgt_no_nbody(sig)
         call fill_MC_integer(max(ini_fin_fks(ichan),1),iran_picked
     $        ,abs(sig)*vol)
      endif

      if (abs(lpp(1)).eq.4.and.abs(lpp(2)).eq.4) then
         ! this is for the MC over the dressed-electron
         ! components
         call get_wgt_nbody(sig)
         call fill_MC_integer(6,n_ee,abs(sig)*vol_ee_MCintN)
      endif


c Finalize PS point
      call fill_plots
      call fill_mint_function(f)
      return
      end

      subroutine update_fks_dir(nFKS)
      implicit none
      include 'run.inc'
      integer nFKS
      integer              nFKSprocess
      common/c_nFKSprocess/nFKSprocess
      nFKSprocess=nFKS
      call fks_inc_chooser()
      call leshouche_inc_chooser()
      call setcuts
      call setfksfactor(.false.)
      if (ickkw.eq.3) call configs_and_props_inc_chooser()
      return
      end
      
      subroutine setup_ini_fin_FKS_map(ini_fin_FKS_map)
      implicit none
      include 'nexternal.inc'
      include 'nFKSconfigs.inc'
      include 'fks_info.inc'
      integer ini_fin_FKS_map(0:2,0:fks_configs),iFKS
      ini_fin_FKS_map(0,0)=0
      ini_fin_FKS_map(1,0)=0
      ini_fin_FKS_map(2,0)=0
      do iFKS=1,fks_configs
         ini_fin_FKS_map(0,0)=ini_fin_FKS_map(0,0)+1
         ini_fin_FKS_map(0,ini_fin_FKS_map(0,0))=iFKS
         if (fks_j_d(iFKS).le.nincoming .and.
     $       fks_j_d(iFKS).gt.0) then
            ini_fin_FKS_map(2,0)=ini_fin_FKS_map(2,0)+1
            ini_fin_FKS_map(2,ini_fin_FKS_map(2,0))=iFKS
         elseif (fks_j_d(iFKS).gt.nincoming .and.
     $           fks_j_d(iFKS).le.nexternal) then
            ini_fin_FKS_map(1,0)=ini_fin_FKS_map(1,0)+1
            ini_fin_FKS_map(1,ini_fin_FKS_map(1,0))=iFKS
         else
            write (*,*) 'ERROR in setup_ini_fin_FKS_map',fks_j_d(iFKS)
     $           ,nincoming,iFKS
            stop 1
         endif
      enddo
      return
      end

      subroutine get_born_nFKSprocess(nFKS_in,nFKS_out)
      implicit none
      include 'nexternal.inc'
      include 'nFKSconfigs.inc'
      include 'fks_info.inc'
      integer nFKS_in,nFKS_out,iFKS,iiFKS,nFKSprocessBorn(fks_configs)
      logical firsttime
      data firsttime /.true./
      save nFKSprocessBorn
c
      if (firsttime) then
         firsttime=.false.
         do iFKS=1,fks_configs
            nFKSprocessBorn(iFKS)=0
            if ( need_color_links_D(iFKS) .or. 
     &           need_charge_links_D(iFKS) )then
               nFKSprocessBorn(iFKS)=iFKS
            endif
            if (nFKSprocessBorn(iFKS).eq.0) then
c     try to find the process that has the same j_fks but with i_fks a
c     gluon
               do iiFKS=1,fks_configs
                  if ( (need_color_links_D(iiFKS) .or.
     &                  need_charge_links_D(iiFKS)) .and.
     &                 fks_j_D(iFKS).eq.fks_j_D(iiFKS) ) then
                     nFKSprocessBorn(iFKS)=iiFKS
                     exit
                  endif
               enddo
            endif
c     try to find the process that has the j_fks initial state if
c     current j_fks is initial state (and similar for final state j_fks)
            if (nFKSprocessBorn(iFKS).eq.0) then
               do iiFKS=1,fks_configs
                  if ( need_color_links_D(iiFKS) .or.
     &                 need_charge_links_D(iiFKS) ) then
                     if ( fks_j_D(iiFKS).le.nincoming .and.
     &                    fks_j_D(iFKS).le.nincoming ) then
                        nFKSprocessBorn(iFKS)=iiFKS
                        exit
                     elseif ( fks_j_D(iiFKS).gt.nincoming .and.
     &                        fks_j_D(iFKS).gt.nincoming ) then
                        nFKSprocessBorn(iFKS)=iiFKS
                        exit
                     endif
                  endif
               enddo
            endif
c     If still not found, just pick any one that has a soft singularity
            if (nFKSprocessBorn(iFKS).eq.0) then
               do iiFKS=1,fks_configs
                  if ( need_color_links_D(iiFKS) .or.
     &                 need_charge_links_D(iiFKS) ) then
                     nFKSprocessBorn(iFKS)=iiFKS
                  endif
               enddo
            endif
c     if there are no soft singularities at all, just do something trivial
            if (nFKSprocessBorn(iFKS).eq.0) then
               nFKSprocessBorn(iFKS)=iFKS
            endif
         enddo
         write (*,*) 'Total number of FKS directories is', fks_configs
         write (*,*) 'For the Born we use nFKSprocesses:'
         write (*,*)  nFKSprocessBorn
      endif
      if (nFKSprocessBorn(nFKS_in).eq.0) then
         write(*,*) 'Could not find the correct map to Born '/
     &        /'FKS configuration for the NLO FKS '/
     &        /'configuration', nFKS_in
         stop 1
      else
         nFKS_out=nFKSprocessBorn(nFKS_in)
      endif
      return
      end

      subroutine update_vegas_x(xx,x)
      implicit none
      include 'mint.inc'
      integer i
      double precision xx(ndimmax),x(99),ran2
      external ran2
      integer ndim
      common/tosigint/ndim
      character*4 abrv
      common /to_abrv/ abrv
      do i=1,99
         if (abrv.eq.'born'.or.abrv(1:2).eq.'vi') then
            if(i.le.ndim-3)then
               x(i)=xx(i)
            elseif(i.le.ndim) then
               x(i)=ran2()      ! Choose them flat when not including real-emision
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
      return
      end

c
      subroutine get_user_params(ncall,itmax,irestart)
c**********************************************************************
c     Routine to get user specified parameters for run
c**********************************************************************
      implicit none
c
c     Constants
c
      include 'genps.inc'
      include 'nexternal.inc'
      include 'nFKSconfigs.inc'
      include 'fks_info.inc'
      include 'run.inc'
      include 'mint.inc'
      include 'orders.inc'
c
c     Arguments
c
      integer ncall,itmax
c
c     Local
c
      integer i, j
      double precision dconfig(maxchannels)
c
c     Global
c
      integer ini_fin_fks(maxchannels)
      common /fks_channels/ini_fin_fks
      integer           isum_hel
      logical                   multi_channel
      common/to_matrix/isum_hel, multi_channel
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
      include 'born_conf.inc'
c
c Vegas stuff
c
      integer irestart,itmp
      character * 70 idstring
      logical savegrid

      logical usexinteg,mint
      common/cusexinteg/usexinteg,mint
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt
      logical fillh
      integer mc_hel,ihel
      double precision volh
      common/mc_int2/volh,mc_hel,ihel,fillh
      integer random_offset_split
      common /c_random_offset_split/ random_offset_split
      logical done
      character*140 buffer
c-----
c  Begin Code
c-----
      mint=.true.
      unwgt=.false.
      open (unit=83,file='input_app.txt',status='old')
      done=.false.
      nchans=0
      do while (.not. done)
         read(83,'(a)',err=222,end=222) buffer
         if (buffer(1:7).eq.'NPOINTS') then
            buffer=buffer(10:100)
            read(buffer,*) ncall
            write (*,*) 'Number of phase-space points per iteration:',ncall
         elseif(buffer(1:11).eq.'NITERATIONS') then
            read(buffer(14:),*) itmax
            write (*,*) 'Maximum number of iterations is:',itmax
         elseif(buffer(1:8).eq.'ACCURACY') then
            read(buffer(11:),*) accuracy
            write (*,*) 'Desired accuracy is:',accuracy
         elseif(buffer(1:10).eq.'ADAPT_GRID') then
            read(buffer(13:),*) use_cut
            write (*,*) 'Using adaptive grids:',use_cut
         elseif(buffer(1:12).eq.'MULTICHANNEL') then
            read(buffer(15:),*) i
            if (i.eq.1) then
               multi_channel=.true.
               write (*,*) 'Using Multi-channel integration'
            else
               multi_channel=.false.
               write (*,*) 'Not using Multi-channel integration'
            endif
         elseif(buffer(1:12).eq.'SUM_HELICITY') then
            read(buffer(15:),*) i
            if (nincoming.eq.1) then
               write (*,*) 'Sum over helicities in the virtuals'/
     $              /' for decay process'
               mc_hel=0
            elseif (i.eq.0) then
               mc_hel=0
               write (*,*) 'Explicitly summing over helicities'/
     $              /' for the virtuals'
            else
               mc_hel=1
               write(*,*) 'Do MC over helicities for the virtuals'
            endif
            isum_hel=0
         elseif(buffer(1:6).eq.'NCHANS') then
            read(buffer(9:),*) nchans
            write (*,*) 'Number of channels to integrate together:'
     $           ,nchans
            if (nchans.gt.maxchannels) then
               write (*,*) 'Too many integration channels to be '/
     $              /'integrated together. Increase maxchannels',nchans
     $              ,maxchannels
               stop 1
            endif
         elseif(buffer(1:7).eq.'CHANNEL') then
            if (nchans.le.0) then
               write (*,*) '"NCHANS" missing in input files'/
     $              /' (still zero)',nchans
               stop
            endif
            read(buffer(10:),*) (dconfig(kchan),kchan=1,nchans)
            do kchan=1,nchans
               iconfigs(kchan) = int(dconfig(kchan))
               if ( nint(dconfig(kchan)*10)-iconfigs(kchan)*10.eq.0 )
     $              then
                  ini_fin_fks(kchan)=0
               elseif ( nint(dconfig(kchan)*10)-iconfigs(kchan)*10.eq.1
     $                 ) then
                  ini_fin_fks(kchan)=1
               elseif ( nint(dconfig(kchan)*10)-iconfigs(kchan)*10.eq.2
     $                 ) then
                  ini_fin_fks(kchan)=2
               else
                  write (*,*) 'ERROR: invalid configuration number',dconfig
                  stop 1
               endif
               do i=1,mapconfig(0)
                  if (iconfigs(kchan).eq.mapconfig(i)) then
                     iconfigs(kchan)=i
                     exit
                  endif
               enddo
            enddo
            write(*,*) 'Running Configuration Number(s): '
     $           ,(iconfigs(kchan),kchan=1,nchans)
            write(*,*) 'initial-or-final',(ini_fin_fks(kchan),kchan=1,nchans)
         elseif(buffer(1:5).eq.'SPLIT') then
            read(buffer(8:),*) random_offset_split
            write (*,*) 'Splitting channel:',random_offset_split
         elseif(buffer(1:8).eq.'WGT_MULT') then
            read(buffer(11:),*) wgt_mult
            write (*,*) 'Weight multiplier:',wgt_mult
         elseif(buffer(1:8).eq.'RUN_MODE') then
            read(buffer(11:),*) abrvinput
            if(abrvinput(5:5).eq.'0')then
               nbody=.true.
            else
               nbody=.false.
            endif
            abrv=abrvinput(1:4)
            write (*,*) "doing the ",abrv," of this channel"
            if(nbody)then
               write (*,*) "integration Born/virtual with Sfunction=1"
            else
               write (*,*) "Normal integration (Sfunction != 1)"
            endif
         elseif(buffer(1:7).eq.'RESTART') then
            read(buffer(10:),*) irestart
            if (irestart.eq.0) then
               write (*,*) 'RESTART: Fresh run'
            elseif(irestart.eq.-1) then
               write (*,*) 'RESTART: Use old grids, but refil plots'
            elseif(irestart.eq.1) then
               write (*,*) 'RESTART: continue with existing run'
            else
               write (*,*) 'RESTART:',irestart
            endif
         endif
         cycle
 222     done=.true.
      enddo
      close(83)

      if (fks_configs.eq.1) then
         if (pdg_type_d(1,fks_i_d(1)).eq.-21.and.abrv.ne.'born') then
C Two cases can occur
C   1) the process has been generated with the LOonly flav
C   2) the process has only virtual corrections, e.g. z > v v [QED]
C the two cases can be distinguished by looking at the values
C  of AMP_SPLIT_SIZE, AMP_SPLIT_SIZE_BORN (if they are ==, it is 1))
           if (amp_split_size.eq.amp_split_size_born) then
             write (*,*) 'Process generated with [LOonly=QCD]. '/
     $           /'Setting abrv to "born".'
             abrv='born'
             if (ickkw.eq.3) then
               write (*,*) 'FxFx merging not possible with'/
     $              /' [LOonly=QCD] processes'
               stop 1
             endif
           else
             write (*,*) 'Process only with virtual corrections'/
     $           /'Setting abrv to "bovi".'
             abrv='bovi'
           endif
         endif
      endif
c
c     Here I want to set up with B.W. we map and which we don't
c
      lbw(0)=0
      end
c
