C     ===========================================
C     ===== Beginning of CutTools Interface =====
C     ===========================================
      SUBROUTINE CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Interface between MG5 and CutTools.
C     
C     Process: u d~ > ve e+ [ all = QCD QED ] QCD^2<=0 QED^2<=6
C     Process: c s~ > ve e+ [ all = QCD QED ] QCD^2<=0 QED^2<=6
C     
C     
C     CONSTANTS 
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      LOGICAL CHECKPCONSERVATION
      PARAMETER (CHECKPCONSERVATION=.TRUE.)
      REAL*8 NORMALIZATION
      PARAMETER (NORMALIZATION = 1.D0/(16.D0*3.14159265358979323846D0*
     $ *2))
C     
C     ARGUMENTS 
C     
      INTEGER NLOOPLINE, RANK
      REAL*8 PL(0:3,NLOOPLINE)
      REAL*8 PCT(0:3,0:NLOOPLINE-1),ABSPCT(0:3)
      REAL*8 REF_P
      COMPLEX*16 M2L(NLOOPLINE)
      COMPLEX*16 M2LCT(0:NLOOPLINE-1)
      COMPLEX*16 RES(3)
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      COMPLEX*16 R1, ACC
      INTEGER I, J, K
      LOGICAL CTINIT, TIRINIT, GOLEMINIT, SAMURAIINIT, NINJAINIT
     $ ,COLLIERINIT
      COMMON/REDUCTIONCODEINIT/CTINIT,TIRINIT,GOLEMINIT,SAMURAIINIT
     $ ,NINJAINIT,COLLIERINIT
C     
C     EXTERNAL FUNCTIONS
C     
      EXTERNAL LOOPNUM
      EXTERNAL MPLOOPNUM
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'
      INTEGER CTMODE
      REAL*8 LSCALE
      COMMON/CT/LSCALE,CTMODE

      INTEGER ID,SQSOINDEX,R
      COMMON/LOOP/ID,SQSOINDEX,R

C     ----------
C     BEGIN CODE
C     ----------

C     INITIALIZE CUTTOOLS IF NEEDED
      IF (CTINIT) THEN
        CTINIT=.FALSE.
        CALL INITCT()
      ENDIF

C     YOU CAN FIND THE DETAILS ABOUT THE DIFFERENT CTMODE AT THE
C      BEGINNING OF THE FILE CTS_CUTS.F90 IN THE CUTTOOLS DISTRIBUTION

C     CONVERT THE MASSES TO BE COMPLEX
      DO I=1,NLOOPLINE
        M2LCT(I-1)=M2L(I)
      ENDDO

C     CONVERT THE MOMENTA FLOWING IN THE LOOP LINES TO CT CONVENTIONS
      DO I=0,3
        ABSPCT(I)=0.D0
        DO J=0,(NLOOPLINE-1)
          PCT(I,J)=0.D0
        ENDDO
      ENDDO
      DO I=0,3
        DO J=1,NLOOPLINE
          PCT(I,0)=PCT(I,0)+PL(I,J)
          ABSPCT(I)=ABSPCT(I)+ABS(PL(I,J))
        ENDDO
      ENDDO
      REF_P = MAX(ABSPCT(0), ABSPCT(1),ABSPCT(2),ABSPCT(3))
      DO I=0,3
        ABSPCT(I) = MAX(REF_P*1E-6, ABSPCT(I))
      ENDDO
      IF (CHECKPCONSERVATION.AND.REF_P.GT.1D-8) THEN
        IF ((PCT(0,0)/ABSPCT(0)).GT.1.D-6) THEN
          WRITE(*,*) 'energy is not conserved (flag:CT95)',PCT(0,0)
          STOP 'energy is not conserved (flag:CT95)'
        ELSEIF ((PCT(1,0)/ABSPCT(1)).GT.1.D-6) THEN
          WRITE(*,*) 'px is not conserved (flag:CT95)',PCT(1,0)
          STOP 'px is not conserved (flag:CT95)'
        ELSEIF ((PCT(2,0)/ABSPCT(2)).GT.1.D-6) THEN
          WRITE(*,*) 'py is not conserved (flag:CT95)',PCT(2,0)
          STOP 'py is not conserved (flag:CT95)'
        ELSEIF ((PCT(3,0)/ABSPCT(3)).GT.1.D-6) THEN
          WRITE(*,*) 'pz is not conserved (flag:CT95)',PCT(3,0)
          STOP 'pz is not conserved (flag:CT95)'
        ENDIF
      ENDIF
      DO I=0,3
        DO J=1,(NLOOPLINE-1)
          DO K=1,J
            PCT(I,J)=PCT(I,J)+PL(I,K)
          ENDDO
        ENDDO
      ENDDO

      CALL CTSXCUT(CTMODE,LSCALE,MU_R,NLOOPLINE,LOOPNUM,MPLOOPNUM,RANK
     $ ,PCT,M2LCT,RES,ACC,R1,STABLE)
      RES(1)=NORMALIZATION*2.0D0*DBLE(RES(1))
      RES(2)=NORMALIZATION*2.0D0*DBLE(RES(2))
      RES(3)=NORMALIZATION*2.0D0*DBLE(RES(3))
C     WRITE(*,*) 'CutTools: Loop ID',ID,' =',RES(1),RES(2),RES(3)
      END

      SUBROUTINE INITCT()
C     
C     INITIALISATION OF CUTTOOLS
C     
C     LOCAL VARIABLES 
C     
      REAL*8 THRS
      LOGICAL EXT_NUM_FOR_R1
C     
C     GLOBAL VARIABLES 
C     
      INCLUDE 'MadLoopParams.inc'
C     ----------
C     BEGIN CODE
C     ----------

C     DEFAULT PARAMETERS FOR CUTTOOLS
C     -------------------------------  
C     THRS1 IS THE PRECISION LIMIT BELOW WHICH THE MP ROUTINES
C      ACTIVATES
      THRS=CTSTABTHRES
C     LOOPLIB SET WHAT LIBRARY CT USES
C     1 -> LOOPTOOLS
C     2 -> AVH
C     3 -> QCDLOOP
      LOOPLIB=CTLOOPLIBRARY
C     MADLOOP'S NUMERATOR IN THE OPEN LOOP IS MUCH FASTER THAN THE
C      RECONSTRUCTED ONE IN CT. SO WE BETTER USE MADLOOP ONE IN THIS
C      CASE.
      EXT_NUM_FOR_R1=.TRUE.
C     -------------------------------	  

C     The initialization below is for CT v1.8.+
      CALL CTSINIT(THRS,LOOPLIB,EXT_NUM_FOR_R1)
C     The initialization below is for the older stable CT v1.7, still
C      used for now in the beta release.
C     CALL CTSINIT(THRS,LOOPLIB)

      END

      SUBROUTINE BUILD_KINEMATIC_MATRIX(NLOOPLINE,P_LOOP,M2L,S_MAT)
C     
C     Helper function that compute the loop kinematic matrix with
C      proper thresholds
C     NLOOPLINE : Number of loop lines
C     P_LOOP    : List of external momenta running in the loop, i.e.
C      q_i in the denominator (l_i+q_i)**2-m_i**2
C     M2L       : List of complex-valued masses running in the loop.
C     S_MAT(N,N): Kinematic matrix output.
C     
C     ARGUMENTS
C     
      INTEGER NLOOPLINE
      REAL*8 P_LOOP(NLOOPLINE,0:3)
      COMPLEX*16 M2L(NLOOPLINE)
      COMPLEX*16 S_MAT(NLOOPLINE,NLOOPLINE)
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J,K
      COMPLEX*16 DIFFSQ
      REAL*8 REF_NORMALIZATION

C     ----------
C     BEGIN CODE
C     ----------

      DO I=1,NLOOPLINE
        DO J=1,NLOOPLINE

          IF(I.EQ.J)THEN
            S_MAT(I,J)=-(M2L(I)+M2L(J))
          ELSE
            DIFFSQ = (DCMPLX(P_LOOP(I,0),0.0D0)-DCMPLX(P_LOOP(J,0)
     $       ,0.0D0))**2
            DO K=1,3
              DIFFSQ = DIFFSQ - (DCMPLX(P_LOOP(I,K),0.0D0)
     $         -DCMPLX(P_LOOP(J,K),0.0D0))**2
            ENDDO
C           Default value of the kinematic matrix
            S_MAT(I,J)=DIFFSQ-M2L(I)-M2L(J)
C           And we now test various thresholds. Normaly, at most one
C            applies.
            IF(ABS(M2L(I)).NE.0.0D0)THEN
              IF(ABS((DIFFSQ-M2L(I))/M2L(I)).LT.OSTHRES)THEN
                S_MAT(I,J)=-M2L(J)
              ENDIF
            ENDIF
            IF(ABS(M2L(J)).NE.0.0D0)THEN
              IF(ABS((DIFFSQ-M2L(J))/M2L(J)).LT.OSTHRES)THEN
                S_MAT(I,J)=-M2L(I)
              ENDIF
            ENDIF
C           Choose what seems the most appropriate way to compare
C           massless onshellness.
            REF_NORMALIZATION=0.0D0
C           Here, we chose to base the threshold only on the energy
C            component
            DO K=0,0
              REF_NORMALIZATION = REF_NORMALIZATION + ABS(P_LOOP(I,K))
     $          + ABS(P_LOOP(J,K))
            ENDDO
            REF_NORMALIZATION = (REF_NORMALIZATION/2.0D0)**2
            IF(REF_NORMALIZATION.NE.0.0D0)THEN
              IF(ABS(DIFFSQ/REF_NORMALIZATION).LT.OSTHRES)THEN
                S_MAT(I,J)=-(M2L(I)+M2L(J))
              ENDIF
            ENDIF
          ENDIF

        ENDDO
      ENDDO

      END

      SUBROUTINE MP_BUILD_KINEMATIC_MATRIX(NLOOPLINE,P_LOOP,M2L,S_MAT)
C     
C     Helper function that compute the loop kinematic matrix with
C      proper thresholds
C     NLOOPLINE : Number of loop lines
C     P_LOOP    : List of external momenta running in the loop, i.e.
C      q_i in the denominator (l_i+q_i)**2-m_i**2
C     M2L       : List of complex-valued masses running in the loop.
C     S_MAT(N,N): Kinematic matrix output.
C     
C     ARGUMENTS
C     
      INTEGER NLOOPLINE
      REAL*16 P_LOOP(NLOOPLINE,0:3)
      COMPLEX*32 M2L(NLOOPLINE)
      COMPLEX*32 S_MAT(NLOOPLINE,NLOOPLINE)
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J,K
      COMPLEX*32 DIFFSQ
      REAL*16 REF_NORMALIZATION

C     ----------
C     BEGIN CODE
C     ----------

      DO I=1,NLOOPLINE
        DO J=1,NLOOPLINE

          IF(I.EQ.J)THEN
            S_MAT(I,J)=-(M2L(I)+M2L(J))
          ELSE
            DIFFSQ = (CMPLX(P_LOOP(I,0),0.0E0_16,KIND=16)
     $       -CMPLX(P_LOOP(J,0),0.0E0_16,KIND=16))**2
            DO K=1,3
              DIFFSQ = DIFFSQ - (CMPLX(P_LOOP(I,K),0.0E0_16,KIND=16)
     $         -CMPLX(P_LOOP(J,K),0.0E0_16,KIND=16))**2
            ENDDO
C           Default value of the kinematic matrix
            S_MAT(I,J)=DIFFSQ-M2L(I)-M2L(J)
C           And we now test various thresholds. Normaly, at most one
C            applies.
            IF(ABS(M2L(I)).NE.0.0E0_16)THEN
              IF(ABS((DIFFSQ-M2L(I))/M2L(I)).LT.OSTHRES)THEN
                S_MAT(I,J)=-M2L(J)
              ENDIF
            ENDIF
            IF(ABS(M2L(J)).NE.0.0E0_16)THEN
              IF(ABS((DIFFSQ-M2L(J))/M2L(J)).LT.OSTHRES)THEN
                S_MAT(I,J)=-M2L(I)
              ENDIF
            ENDIF
C           Choose what seems the most appropriate way to compare
C           massless onshellness.
            REF_NORMALIZATION=0.0E0_16
C           Here, we chose to base the threshold only on the energy
C            component
            DO K=0,0
              REF_NORMALIZATION = REF_NORMALIZATION + ABS(P_LOOP(I,K))
     $          + ABS(P_LOOP(J,K))
            ENDDO
            REF_NORMALIZATION = (REF_NORMALIZATION/2.0E0_16)**2
            IF(REF_NORMALIZATION.NE.0.0E0_16)THEN
              IF(ABS(DIFFSQ/REF_NORMALIZATION).LT.OSTHRES)THEN
                S_MAT(I,J)=-(M2L(I)+M2L(J))
              ENDIF
            ENDIF
          ENDIF

        ENDDO
      ENDDO

      END



C     ===========================================
C     ===== Beginning of Ninja interface  =====
C     ===========================================

      SUBROUTINE NINJA_LOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)
C     
C     Module used
C     
      USE MNINJA
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Interface between MG5 and Ninja.
C     
C     Process: u d~ > ve e+ [ all = QCD QED ] QCD^2<=0 QED^2<=6
C     Process: c s~ > ve e+ [ all = QCD QED ] QCD^2<=0 QED^2<=6
C     
C     
C     CONSTANTS 
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      LOGICAL CHECKPCONSERVATION
      PARAMETER (CHECKPCONSERVATION=.TRUE.)
      REAL*8 NORMALIZATION
      PARAMETER (NORMALIZATION = 1.D0/(16.D0*3.14159265358979323846D0*
     $ *2))
      INTEGER NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=25)
C     These are constants related to the split orders
      INTEGER NSQUAREDSO
      PARAMETER (NSQUAREDSO=1)
      INCLUDE 'loop_max_coefs.inc'
C     
C     ARGUMENTS 
C     
      INTEGER NLOOPLINE, RANK
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      COMPLEX*16 RES(3)
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 P_TMP(0:3,0:NLOOPLINE-1),ABSP_TMP(0:3)
      REAL*8 REF_P
      REAL*8 P_NINJA(0:3,NLOOPLINE)
      REAL*8 P_S_MAT(NLOOPLINE,0:3)
      COMPLEX*16 M2L_NINJA(NLOOPLINE)
      COMPLEX*16 NINJA_RES(0:2)
      COMPLEX*16 R1
      INTEGER NINJA_STATUS
      INTEGER I, J, K
      REAL*8 PDEN_DUMMY(0:3,NLOOPLINE-1)

      COMPLEX*16 S_MAT(NLOOPLINE,NLOOPLINE)
      REAL*8 REAL_S_MAT(NLOOPLINE,NLOOPLINE)

      INTEGER CURR_MAXCOEF
      COMPLEX*16, ALLOCATABLE :: TENSORCOEFS(:)

C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'

      LOGICAL CTINIT, TIRINIT, GOLEMINIT, SAMURAIINIT, NINJAINIT
     $ ,COLLIERINIT
      COMMON/REDUCTIONCODEINIT/CTINIT,TIRINIT,GOLEMINIT,SAMURAIINIT
     $ ,NINJAINIT,COLLIERINIT

      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/CT/LSCALE,CTMODE

      INTEGER ID,SQSOINDEX,R
      COMMON/LOOP/ID,SQSOINDEX,R
      COMPLEX*16 LOOPCOEFS(0:LOOPMAXCOEFS-1,NSQUAREDSO,NLOOPGROUPS)
      COMMON/LCOEFS/LOOPCOEFS

      LOGICAL FPE_IN_DP_REDUCTION, FPE_IN_QP_REDUCTION
      COMMON/FPE_IN_REDUCTION/FPE_IN_DP_REDUCTION, FPE_IN_QP_REDUCTION

C     ----------
C     BEGIN CODE
C     ----------

C     For the direction test, we must switch the direction in which
C      the loop is read for CTMode equal to 2 or 4.
      CALL SWITCH_ORDER(CTMODE,NLOOPLINE,PL,PDEN_DUMMY,M2L)

C     The CT initialization is also performed here if not done already
C      because it calls MPINIT of OneLOop which is necessary on some
C      system
      IF (CTINIT) THEN
        CTINIT=.FALSE.
        CALL INITCT()
      ENDIF

C     INITIALIZE NINJA IF NEEDED
      IF (NINJAINIT) THEN
        NINJAINIT=.FALSE.
        CALL INITNINJA()
      ENDIF

C     CONVERT THE MASSES TO BE COMPLEX
      DO I=1,NLOOPLINE
        M2L_NINJA(I)=M2L(I)
      ENDDO

C     CONVERT THE MOMENTA FLOWING IN THE LOOP LINES TO NINJA
C      CONVENTIONS
      DO I=0,3
        ABSP_TMP = 0.D0
        DO J=0,(NLOOPLINE-1)
          P_TMP(I,J)=0.D0
        ENDDO
      ENDDO
      DO I=0,3
        DO J=1,NLOOPLINE
          P_TMP(I,0)=P_TMP(I,0)+PL(I,J)
          ABSP_TMP(I) = ABSP_TMP(I)+ABS(PL(I,J))
        ENDDO
      ENDDO
      REF_P = MAX(ABSP_TMP(0), ABSP_TMP(1),ABSP_TMP(2),ABSP_TMP(3))
      DO I=0,3
        ABSP_TMP(I) = MAX(REF_P*1E-6, ABSP_TMP(I))
      ENDDO

      IF (CHECKPCONSERVATION.AND.REF_P.GT.1D-8) THEN
        IF ((P_TMP(0,0)/ABSP_TMP(0)).GT.1.D-6) THEN
          WRITE(*,*) 'energy is not conserved (flag:CT692)',P_TMP(0,0)
          STOP 'energy is not conserved (flag:CT692)'
        ELSEIF ((P_TMP(1,0)/ABSP_TMP(1)).GT.1.D-6) THEN
          WRITE(*,*) 'px is not conserved (flag:CT692)',P_TMP(1,0)
          STOP 'px is not conserved (flag:CT692)'
        ELSEIF ((P_TMP(2,0)/ABSP_TMP(2)).GT.1.D-6) THEN
          WRITE(*,*) 'py is not conserved (flag:CT692)',P_TMP(2,0)
          STOP 'py is not conserved (flag:CT692)'
        ELSEIF ((P_TMP(3,0)/ABSP_TMP(3)).GT.1.D-6) THEN
          WRITE(*,*) 'pz is not conserved (flag:CT692)',P_TMP(3,0)
          STOP 'pz is not conserved (flag:CT692)'
        ENDIF
      ENDIF
      DO I=0,3
        DO J=1,(NLOOPLINE-1)
          DO K=1,J
            P_TMP(I,J)=P_TMP(I,J)+PL(I,K)
          ENDDO
        ENDDO
      ENDDO
C     In Ninja, the loop line index starts at 1
      DO I=0,NLOOPLINE-1
        P_NINJA(0,I+1) = P_TMP(0,I)
        P_NINJA(1,I+1) = P_TMP(1,I)
        P_NINJA(2,I+1) = P_TMP(2,I)
        P_NINJA(3,I+1) = P_TMP(3,I)
      ENDDO

C     Number of coefficients for the current rank
      CURR_MAXCOEF = 0
      DO I=0,RANK
        CURR_MAXCOEF=CURR_MAXCOEF+(3+I)*(2+I)*(1+I)/6
      ENDDO
C     Now write the tensor coefficients for Ninja
C     It should never be allocated at this stage
      IF (.NOT. ALLOCATED(TENSORCOEFS)) THEN
        ALLOCATE(TENSORCOEFS(0:CURR_MAXCOEF-1))
      ENDIF
      DO I=0,CURR_MAXCOEF-1
        TENSORCOEFS(I) = LOOPCOEFS(I,SQSOINDEX,ID)
      ENDDO
C     The loop momentum is in fact q_loop -> -q_loop, so that the
C     coefficients must be changed accordingly
      CALL INVERT_MOMENTA_IN_POLYNOMIAL(CURR_MAXCOEF,TENSORCOEFS)

C     Compute the kinematic matrix
      DO J=1,NLOOPLINE
        DO I=0,3
          P_S_MAT(J,I)=P_NINJA(I,J)
        ENDDO
      ENDDO
      CALL BUILD_KINEMATIC_MATRIX(NLOOPLINE,P_S_MAT,M2L,S_MAT)

      DO I=1,NLOOPLINE
        DO J=1,NLOOPLINE
          REAL_S_MAT(I,J) = DBLE(S_MAT(I,J)+M2L(I)+M2L(J))
        ENDDO
      ENDDO

C     Below is the call specifying the kinematic matrix
      CALL NINJA_TENSOR_EVALUATE(TENSORCOEFS,NLOOPLINE,RANK,REAL_S_MAT
     $ ,P_NINJA,M2L,MU_R**2,NINJA_RES,R1,NINJA_STATUS)

C     Below is the call without specification of the kinematic matrix
C     call ninja_tensor_evaluate(TENSORCOEFS,NLOOPLINE,RANK,P_NINJA,M2L
C     ,MU_R**2,NINJA_RES,R1,NINJA_STATUS)

C     If a floating point exception was found in Ninja (e.g. exactly
C      zero gram. det.)
C     Then warn loop_matrix.f so that it will flag this kinematic
C      point as unstable no matter what.
      IF (NINJA_STATUS.EQ.NINJA_UNSTABLE_KINEMATICS) THEN
        FPE_IN_DP_REDUCTION = .TRUE.
      ENDIF

C     Make sure to deallocate the tensor of coefficients
      IF (ALLOCATED(TENSORCOEFS)) THEN
        DEALLOCATE(TENSORCOEFS)
      ENDIF

      RES(1)=NORMALIZATION*2.0D0*DBLE(NINJA_RES(0))
      RES(2)=NORMALIZATION*2.0D0*DBLE(NINJA_RES(1))
      RES(3)=NORMALIZATION*2.0D0*DBLE(NINJA_RES(2))
C     WRITE(*,*) 'Ninja:  Loop ID',ID,' =',RES(1),RES(2),RES(3)
      END

C     
C     The Ninja version installed does not support quadruple precision
C     so that the corresponding subroutines are not output.
C     

      SUBROUTINE INITNINJA()
C     
C     Module used
C     
      USE MNINJA
C     
C     Initialization of Ninja 
C     
C     LOCAL VARIABLES 
C     
      INTEGER LOOPLIB
C     
C     GLOBAL VARIABLES 
C     
      INCLUDE 'MadLoopParams.inc'
C     ----------
C     BEGIN CODE
C     ----------

C     LOOPLIB SET WHAT LIBRARY NINJA USES
C     1 -> LOOPTOOLS
C     2 -> AVH
C     3 -> QCDLOOP
      IF (CTLOOPLIBRARY.EQ.1) THEN
        WRITE(*,*) 'Warning in Ninja initialization. LoopTools is not'
     $   //' supported by the Ninja interface. It will use OneLOop'
     $   //' instead.'
        LOOPLIB = 1
      ELSEIF (CTLOOPLIBRARY.EQ.3) THEN
        WRITE(*,*) 'Warning in Ninja initialization. LoopTools is not'
     $   //' supported by the Ninja interface. It will use OneLOop'
     $   //' instead.'
        LOOPLIB = 1
      ELSEIF (CTLOOPLIBRARY.EQ.2) THEN
        LOOPLIB = 1
      ELSE
        WRITE(*,*) 'Error in Ninja initialization. Loop library ID='
     $   ,CTLOOPLIBRARY,' is not supported. Change variable'
     $   //' CTLoopLibrary in MadLoopParams.dat.'
        STOP 1
      ENDIF
      CALL NINJA_SET_INTEGRAL_LIBRARY(LOOPLIB)

      END

      SUBROUTINE LOOP_2(W1, W2, M1, M2,  RANK, SQUAREDSOINDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=2)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=6)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=25)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=1)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2
      COMPLEX*16 M1, M2

      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      REAL*16 MP_PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(2)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/W/W
      COMPLEX*32 MP_W(20,NWAVEFUNCS)
      COMMON/MP_W/MP_W

      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

C     Determine it uses qp or not
      DOING_QP = (CTMODE.GE.4)

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED)
     $ .OR.GOODAMP(SQUAREDSOINDEX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        M2L(1)=M2**2
        M2L(2)=M1**2
        DO I=1,NLOOPLINE
          PAIRING(I)=1
        ENDDO

        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            IF (DOING_QP) THEN
              MP_PL(I,J)=0.0E+0_16
            ENDIF
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
              IF (DOING_QP) THEN
                MP_PL(I,J)=MP_PL(I,J)-REAL(MP_W(1+I,WE(K)),KIND=16)
              ENDIF
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Choose the correct loop library
        CALL CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS,ID
     $   ,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX
     $     ,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSEIF (MLREDUCTIONLIB(I_LIB).EQ.6) THEN
C         Ninja is used
          IF (.NOT.DOING_QP) THEN
            CALL NINJA_LOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1
     $       ,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
          ELSE
            WRITE(*,*) 'ERROR: Ninja should not be called in quadruple'
     $       //' precision since the installed version considered does'
     $       //' not support it.'
            STOP 9
          ENDIF
        ELSE
C         Tensor Integral Reduction is used 
          CALL TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL,M2L
     $     ,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE LOOP_3(W1, W2, W3, M1, M2, M3,  RANK, SQUAREDSOINDEX,
     $  LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=3)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=6)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=25)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=1)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3
      COMPLEX*16 M1, M2, M3

      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      REAL*16 MP_PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(3)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/W/W
      COMPLEX*32 MP_W(20,NWAVEFUNCS)
      COMMON/MP_W/MP_W

      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

C     Determine it uses qp or not
      DOING_QP = (CTMODE.GE.4)

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED)
     $ .OR.GOODAMP(SQUAREDSOINDEX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        M2L(1)=M3**2
        M2L(2)=M1**2
        M2L(3)=M2**2
        DO I=1,NLOOPLINE
          PAIRING(I)=1
        ENDDO

        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            IF (DOING_QP) THEN
              MP_PL(I,J)=0.0E+0_16
            ENDIF
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
              IF (DOING_QP) THEN
                MP_PL(I,J)=MP_PL(I,J)-REAL(MP_W(1+I,WE(K)),KIND=16)
              ENDIF
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Choose the correct loop library
        CALL CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS,ID
     $   ,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX
     $     ,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSEIF (MLREDUCTIONLIB(I_LIB).EQ.6) THEN
C         Ninja is used
          IF (.NOT.DOING_QP) THEN
            CALL NINJA_LOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1
     $       ,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
          ELSE
            WRITE(*,*) 'ERROR: Ninja should not be called in quadruple'
     $       //' precision since the installed version considered does'
     $       //' not support it.'
            STOP 9
          ENDIF
        ELSE
C         Tensor Integral Reduction is used 
          CALL TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL,M2L
     $     ,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE LOOP_4(W1, W2, W3, W4, M1, M2, M3, M4,  RANK,
     $  SQUAREDSOINDEX, LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=4)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=6)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=25)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=1)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4
      COMPLEX*16 M1, M2, M3, M4

      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      REAL*16 MP_PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(4)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/W/W
      COMPLEX*32 MP_W(20,NWAVEFUNCS)
      COMMON/MP_W/MP_W

      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

C     Determine it uses qp or not
      DOING_QP = (CTMODE.GE.4)

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED)
     $ .OR.GOODAMP(SQUAREDSOINDEX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        WE(3)=W3
        WE(4)=W4
        M2L(1)=M4**2
        M2L(2)=M1**2
        M2L(3)=M2**2
        M2L(4)=M3**2
        DO I=1,NLOOPLINE
          PAIRING(I)=1
        ENDDO

        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            IF (DOING_QP) THEN
              MP_PL(I,J)=0.0E+0_16
            ENDIF
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
              IF (DOING_QP) THEN
                MP_PL(I,J)=MP_PL(I,J)-REAL(MP_W(1+I,WE(K)),KIND=16)
              ENDIF
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Choose the correct loop library
        CALL CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS,ID
     $   ,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX
     $     ,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSEIF (MLREDUCTIONLIB(I_LIB).EQ.6) THEN
C         Ninja is used
          IF (.NOT.DOING_QP) THEN
            CALL NINJA_LOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1
     $       ,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
          ELSE
            WRITE(*,*) 'ERROR: Ninja should not be called in quadruple'
     $       //' precision since the installed version considered does'
     $       //' not support it.'
            STOP 9
          ENDIF
        ELSE
C         Tensor Integral Reduction is used 
          CALL TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL,M2L
     $     ,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

      SUBROUTINE LOOP_1_2(P1, W1, W2, M1,  RANK, SQUAREDSOINDEX,
     $  LOOPNUM)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=1)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=6)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=25)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)
C     These are constants related to the split orders
      INTEGER    NSQUAREDSO
      PARAMETER (NSQUAREDSO=1)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2
      COMPLEX*16 M1
      INTEGER P1
      INTEGER RANK, LSYMFACT
      INTEGER LOOPNUM, SQUAREDSOINDEX
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      REAL*16 MP_PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE),WE(2)
      INTEGER I, J, K, TEMP,I_LIB
      LOGICAL COMPLEX_MASS,DOING_QP
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'MadLoopParams.inc'
      INTEGER ID,SQSOINDEX,R
      COMMON/LOOP/ID,SQSOINDEX,R

      LOGICAL CHECKPHASE, HELDOUBLECHECKED
      COMMON/INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/FILTERS/GOODAMP,GOODHEL,HELOFFSET

      COMPLEX*16 LOOPRES(3,NSQUAREDSO,NLOOPGROUPS)
      LOGICAL S(NSQUAREDSO,NLOOPGROUPS)
      COMMON/LOOPRES/LOOPRES,S


      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/W/W
      COMPLEX*32 MP_W(20,NWAVEFUNCS)
      COMMON/MP_W/MP_W

      REAL*8 LSCALE
      INTEGER CTMODE
      COMMON/CT/LSCALE,CTMODE
      INTEGER LIBINDEX
      COMMON/I_LIB/LIBINDEX

C     ----------
C     BEGIN CODE
C     ----------

C     Determine it uses qp or not
      DOING_QP = (CTMODE.GE.4)

      IF (CHECKPHASE.OR.(.NOT.HELDOUBLECHECKED)
     $ .OR.GOODAMP(SQUAREDSOINDEX,LOOPNUM)) THEN
        WE(1)=W1
        WE(2)=W2
        M2L(1)=M1**2
        PAIRING(1)=P1
        R=RANK
        ID=LOOPNUM
        SQSOINDEX=SQUAREDSOINDEX
        DO I=0,3
          TEMP=1
          DO J=1,NLOOPLINE
            PL(I,J)=0.D0
            IF (DOING_QP) THEN
              MP_PL(I,J)=0.0E+0_16
            ENDIF
            DO K=TEMP,(TEMP+PAIRING(J)-1)
              PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K)))
              IF (DOING_QP) THEN
                MP_PL(I,J)=MP_PL(I,J)-REAL(MP_W(1+I,WE(K)),KIND=16)
              ENDIF
            ENDDO
            TEMP=TEMP+PAIRING(J)
          ENDDO
        ENDDO
C       Determine whether the integral is with complex masses or not
C       since some reduction libraries, e.g.PJFry++ and IREGI, are
C        still
C       not able to deal with complex masses
        COMPLEX_MASS=.FALSE.
        DO I=1,NLOOPLINE
          IF(DIMAG(M2L(I)).EQ.0D0)CYCLE
          IF(ABS(DIMAG(M2L(I)))/MAX(ABS(M2L(I)),1D-2).GT.1D-15)THEN
            COMPLEX_MASS=.TRUE.
            EXIT
          ENDIF
        ENDDO
C       Choose the correct loop library
        CALL CHOOSE_LOOPLIB(LIBINDEX,NLOOPLINE,RANK,COMPLEX_MASS,ID
     $   ,DOING_QP,I_LIB)
        IF(MLREDUCTIONLIB(I_LIB).EQ.1)THEN
C         CutTools is used
          CALL CTLOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1,SQUAREDSOINDEX
     $     ,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
        ELSEIF (MLREDUCTIONLIB(I_LIB).EQ.6) THEN
C         Ninja is used
          IF (.NOT.DOING_QP) THEN
            CALL NINJA_LOOP(NLOOPLINE,PL,M2L,RANK,LOOPRES(1
     $       ,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX,LOOPNUM))
          ELSE
            WRITE(*,*) 'ERROR: Ninja should not be called in quadruple'
     $       //' precision since the installed version considered does'
     $       //' not support it.'
            STOP 9
          ENDIF
        ELSE
C         Tensor Integral Reduction is used 
          CALL TIRLOOP(SQUAREDSOINDEX,LOOPNUM,I_LIB,NLOOPLINE,PL,M2L
     $     ,RANK,LOOPRES(1,SQUAREDSOINDEX,LOOPNUM),S(SQUAREDSOINDEX
     $     ,LOOPNUM))
        ENDIF
      ELSE
        LOOPRES(1,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(2,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        LOOPRES(3,SQUAREDSOINDEX,LOOPNUM)=(0.0D0,0.0D0)
        S(SQUAREDSOINDEX,LOOPNUM)=.TRUE.
      ENDIF
      END

