      program select_events
c Keeps selected events out of those originally stored in the event file.
c Compile with
c gfortran -ffixed-line-length-132 -fno-automatic -I../SubProcesses/P0_<anydir> -o
c select_events select_events.f handling_lhe_events.f fill_MC_mshell.f
      implicit none
      integer maxevt,ifile,ofile,i,npart,nevmin,nevmax,nevmin0,nevmax0
      integer IDBMUP(2),PDFGUP(2),PDFSUP(2),IDWTUP,NPRUP,LPRUP
      double precision EBMUP(2),XSECUP,XERRUP,XMAXUP
      INTEGER MAXNUP
      PARAMETER (MAXNUP=500)
      INTEGER NUP,IDPRUP,IDUP(MAXNUP),ISTUP(MAXNUP),
     # MOTHUP(2,MAXNUP),ICOLUP(2,MAXNUP)
      DOUBLE PRECISION XWGTUP,SCALUP,AQEDUP,AQCDUP,
     # PUP(5,MAXNUP),VTIMUP(MAXNUP),SPINUP(MAXNUP)
      double precision sum_wgt
      integer isorh_lhe,ifks_lhe,jfks_lhe,fksfather_lhe,ipartner_lhe
      double precision scale1_lhe,scale2_lhe,percentage
      integer jwgtinfo,mexternal,iwgtnumpartn
      double precision wgtcentral,wgtmumin,wgtmumax,wgtpdfmin,wgtpdfmax
      character*80 event_file,fname2
      character*140 buff
      character*10 MonteCarlo,string
      character*1 ch1
      logical extra
      integer numev,number,ioffset,jj,loc

      include "nexternal.inc"
      include "genps.inc"
      integer j,k,itype,istep,ievts_ok,i_mult(30),imin,imax
      real*8 ecm,xmass(3*nexternal),xmom(0:3,3*nexternal)
c
      write(*,*)'Enter event file name'
      read(*,*)event_file
      write(*,*)'Type 1 to keep S events'
      write(*,*)'     2 to keep H events'
      write(*,*)'     3 to keep a subset of events'
      read(*,*)itype

      loc=index(event_file,' ')
      if(itype.eq.1)then
         fname2=event_file(1:loc-1)//'.S'
      elseif(itype.eq.2)then
         fname2=event_file(1:loc-1)//'.H'
      elseif(itype.eq.3)then
         fname2=event_file(1:loc-1)//'.RED'
         write(*,*)'Enter first and last event to keep'
         read(*,*)nevmin0,nevmax0
         if(nevmin0.lt.0.or.nevmax0.lt.0)then
            write(*,*)'Only positive values allowed'
            write(*,*)nevmin0,nevmax0
            stop
         endif
         nevmin=min(nevmin0,nevmax0)
         nevmax=max(nevmin0,nevmax0)
      else
         write(*,*)'Invalid itype',itype
         stop
      endif

c first round to establish ievts_ok, and to check whether
c information iSorH_lhe is available
      ifile=34
      do i=1,30
         i_mult(i)=0
      enddo
      imin=31
      imax=1
      extra=.false.
      open(unit=ifile,file=event_file,status='unknown')
      call read_lhef_header(ifile,maxevt,MonteCarlo)
      if(itype.eq.3.and.nevmin.gt.maxevt)then
         write(*,*)'Invalid inputs',nevmin,nevmax,maxevt
         stop
      endif
      call read_lhef_init(ifile,
     &     IDBMUP,EBMUP,PDFGUP,PDFSUP,IDWTUP,NPRUP,
     &     XSECUP,XERRUP,XMAXUP,LPRUP)
      i=1
      ievts_ok=0
      if(itype.le.2)then
         do while(i.le.maxevt)
            call read_lhef_event(ifile,
     &           NUP,IDPRUP,XWGTUP,SCALUP,AQEDUP,AQCDUP,
     &           IDUP,ISTUP,MOTHUP,ICOLUP,PUP,VTIMUP,SPINUP,buff)
            if(buff(1:1).eq.'#')then
               extra=.true.
               read(buff,200)ch1,iSorH_lhe,ifks_lhe,jfks_lhe,
     &           fksfather_lhe,ipartner_lhe,
     &           scale1_lhe,scale2_lhe,
     &           jwgtinfo,mexternal,iwgtnumpartn,
     &           wgtcentral,wgtmumin,wgtmumax,wgtpdfmin,wgtpdfmax
               if(itype.eq.iSorH_lhe)ievts_ok=ievts_ok+1
            else
               i_mult(nup)=i_mult(nup)+1
            endif
            i=i+1
         enddo
         if(.not.extra)then
            do i=1,30
               j=30-i
               if(i.le.2.and.i_mult(i).ne.0)then
                  write(*,*)'Error in i_mult',i_mult
                  stop
               endif
               if(i_mult(i).ne.0.and.i.lt.imin)imin=i
               if(i_mult(j).ne.0.and.j.gt.imax)imax=j
            enddo
            if(imax-imin.eq.1)then
               if(itype.eq.1)ievts_ok=i_mult(imin)
               if(itype.eq.2)ievts_ok=i_mult(imax)
            else
               write(*,*)'Unable to understand files with more than'
               write(*,*)'two multiplicities. Set imin and imax by'
               write(*,*)'hand here'
               stop
            endif
         endif
      elseif(itype.eq.3)then
         ievts_ok=min(maxevt,nevmax)-nevmin
      endif
      close(34)
      if(ievts_ok.eq.0)then
         write(*,*)' '
         write(*,*)'No events of desired type found in file !'
         write(*,*)' '
         stop
      endif

c second round to write file
      ifile=34
      ofile=35
      open(unit=ifile,file=event_file,status='old')
      open(unit=ofile,file=fname2,status='unknown')

      call copy_header(ifile,ofile,ievts_ok)
      call read_lhef_init(ifile,
     &     IDBMUP,EBMUP,PDFGUP,PDFSUP,IDWTUP,NPRUP,
     &     XSECUP,XERRUP,XMAXUP,LPRUP)
      call write_lhef_init(ofile,
     &     IDBMUP,EBMUP,PDFGUP,PDFSUP,IDWTUP,NPRUP,
     &     XSECUP,XERRUP,XMAXUP,LPRUP)
      i=1
      ievts_ok=0
      sum_wgt=0d0
      if(itype.le.2)numev=maxevt
      if(itype.eq.3)numev=min(maxevt,nevmax)
      do while(i.le.numev)
         call read_lhef_event(ifile,
     &        NUP,IDPRUP,XWGTUP,SCALUP,AQEDUP,AQCDUP,
     &        IDUP,ISTUP,MOTHUP,ICOLUP,PUP,VTIMUP,SPINUP,buff)
         sum_wgt=sum_wgt+XWGTUP
         if(extra)then
            if(buff(1:1).ne.'#')then
               write(*,*)'Inconsistency in event file',i,' ',buff
               stop
            endif
            read(buff,200)ch1,iSorH_lhe,ifks_lhe,jfks_lhe,
     &         fksfather_lhe,ipartner_lhe,
     &         scale1_lhe,scale2_lhe,
     &         jwgtinfo,mexternal,iwgtnumpartn,
     &         wgtcentral,wgtmumin,wgtmumax,wgtpdfmin,wgtpdfmax
         endif
         npart=0
         do k=1,nup
            if(abs(ISTUP(k)).eq.1)then
               npart=npart+1
               xmass(npart)=pup(5,k)
               do j=1,4
                  xmom(mod(j,4),npart)=pup(j,k)
               enddo
            endif
         enddo
         call phspncheck_nocms2(i,npart,xmass,xmom)
         if( (itype.le.2.and.extra.and.itype.eq.iSorH_lhe).or.
     &       (itype.eq.1.and..not.extra.and.nup.eq.imin).or.
     &       (itype.eq.2.and..not.extra.and.nup.eq.imax).or.
     &       (itype.eq.3.and.i.ge.nevmin) )then
            call write_lhef_event(ofile,
     &           NUP,IDPRUP,XWGTUP,SCALUP,AQEDUP,AQCDUP,
     &           IDUP,ISTUP,MOTHUP,ICOLUP,PUP,VTIMUP,SPINUP,buff)
         endif
         if(itype.le.2)then
            ioffset=0
            number=maxevt
         elseif(itype.eq.3)then
            ioffset=nevmin
            number=abs(min(nevmax,maxevt)-ioffset)
         endif
         istep=number/10
         if(istep.eq.0)istep=1
         jj=i-ioffset
         percentage=jj*100.d0/number
         if(jj.gt.0.and.mod(jj,istep).eq.0.or.jj.eq.number)
     &        write(*,*)'Read',int(percentage),'% of event file'
         i=i+1
      enddo
      write(ofile,*)'</LesHouchesEvents>'
      if(itype.eq.3)write(*,*)'The sum of the weights is:',sum_wgt
 200  format(1a,1x,i1,4(1x,i2),2(1x,d14.8),1x,i1,2(1x,i2),5(1x,d14.8))

      close(34)
      close(35)

      end



      subroutine phspncheck_nocms2(nev,npart,xmass,xmom)
c Checks four-momentum conservation. Derived from phspncheck;
c works in any frame
      implicit none
      integer nev,npart,maxmom
      include "nexternal.inc"
      include "genps.inc"
      real*8 xmass(3*nexternal),xmom(0:3,3*nexternal)
      real*8 tiny,vtiny,xm,xlen4,den,xsum(0:3),xsuma(0:3),
     # xrat(0:3),ptmp(0:3)
      parameter (tiny=5.d-3)
      parameter (vtiny=1.d-6)
      integer jflag,i,j,jj
      double precision dot
      external dot
c
      jflag=0
      do i=0,3
        xsum(i)=-xmom(i,1)-xmom(i,2)
        xsuma(i)=abs(xmom(i,1))+abs(xmom(i,2))
        do j=3,npart
          xsum(i)=xsum(i)+xmom(i,j)
          xsuma(i)=xsuma(i)+abs(xmom(i,j))
        enddo
        if(xsuma(i).lt.1.d0)then
          xrat(i)=abs(xsum(i))
        else
          xrat(i)=abs(xsum(i))/xsuma(i)
        endif
        if(xrat(i).gt.tiny.and.jflag.eq.0)then
          write(*,*)'Momentum is not conserved [nocms]'
          write(*,*)'i=',i
          do j=1,npart
            write(*,'(4(d14.8,1x))') (xmom(jj,j),jj=0,3)
          enddo
          jflag=1
        endif
      enddo
      if(jflag.eq.1)then
        write(*,'(4(d14.8,1x))') (xsum(jj),jj=0,3)
        write(*,'(4(d14.8,1x))') (xrat(jj),jj=0,3)
        write(*,*)'event #',nev
      endif
c
      do j=1,npart
        do i=0,3
          ptmp(i)=xmom(i,j)
        enddo
        xm=xlen4(ptmp)
        if(ptmp(0).ge.1.d0)then
          den=ptmp(0)
        else
          den=1.d0
        endif
        if(abs(xm-xmass(j))/den.gt.tiny .and.
     &       abs(xm-xmass(j)).gt.tiny)then
          write(*,*)'Mass shell violation [nocms]'
          write(*,*)'j=',j
          write(*,*)'mass=',xmass(j)
          write(*,*)'mass computed=',xm
          write(*,'(4(d14.8,1x))') (xmom(jj,j),jj=0,3)
          write(*,*)'event #',nev
        endif
      enddo

      return
      end


      double precision function dot(p1,p2)
C****************************************************************************
C     4-Vector Dot product
C****************************************************************************
      implicit none
      double precision p1(0:3),p2(0:3)
      dot=p1(0)*p2(0)-p1(1)*p2(1)-p1(2)*p2(2)-p1(3)*p2(3)

      if(dabs(dot).lt.1d-6)then ! solve numerical problem 
         dot=0d0
      endif

      end


      function xlen4(v)
      implicit none
      real*8 xlen4,tmp,v(0:3)
c
      tmp=v(0)**2-v(1)**2-v(2)**2-v(3)**2
      xlen4=sign(1.d0,tmp)*sqrt(abs(tmp))
      return
      end
