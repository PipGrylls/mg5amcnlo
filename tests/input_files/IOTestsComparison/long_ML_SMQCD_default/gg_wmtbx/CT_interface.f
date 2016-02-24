      SUBROUTINE ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Interface between MG5 and CutTools.
C     
C     Process: g g > w- t b~ QED<=1 QCD<=2 [ virt = QCD ]
C     
C     
C     CONSTANTS 
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
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
      REAL*8 PCT(0:3,0:NLOOPLINE-1)
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
      COMMON/REDUCTIONCODEINIT/CTINIT,TIRINIT,GOLEMINIT,SAMURAIINIT
     $ ,NINJAINIT
C     
C     EXTERNAL FUNCTIONS
C     
      EXTERNAL ML5_0_LOOPNUM
      EXTERNAL ML5_0_MPLOOPNUM
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'
      INTEGER CTMODE
      REAL*8 LSCALE
      COMMON/ML5_0_CT/LSCALE,CTMODE

      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID,SYMFACT, MULTIPLIER, AMPLNUM

C     ----------
C     BEGIN CODE
C     ----------

C     INITIALIZE CUTTOOLS IF NEEDED
      IF (CTINIT) THEN
        CTINIT=.FALSE.
        CALL ML5_0_INITCT()
      ENDIF

C     YOU CAN FIND THE DETAILS ABOUT THE DIFFERENT CTMODE AT THE
C      BEGINNING OF THE FILE CTS_CUTS.F90 IN THE CUTTOOLS DISTRIBUTION

C     CONVERT THE MASSES TO BE COMPLEX
      DO I=1,NLOOPLINE
        M2LCT(I-1)=M2L(I)
      ENDDO

C     CONVERT THE MOMENTA FLOWING IN THE LOOP LINES TO CT CONVENTIONS
      DO I=0,3
        DO J=0,(NLOOPLINE-1)
          PCT(I,J)=0.D0
        ENDDO
      ENDDO
      DO I=0,3
        DO J=1,NLOOPLINE
          PCT(I,0)=PCT(I,0)+PL(I,J)
        ENDDO
      ENDDO
      IF (CHECKPCONSERVATION) THEN
        IF (PCT(0,0).GT.1.D-6) THEN
          WRITE(*,*) 'energy is not conserved ',PCT(0,0)
          STOP 'energy is not conserved'
        ELSEIF (PCT(1,0).GT.1.D-6) THEN
          WRITE(*,*) 'px is not conserved ',PCT(1,0)
          STOP 'px is not conserved'
        ELSEIF (PCT(2,0).GT.1.D-6) THEN
          WRITE(*,*) 'py is not conserved ',PCT(2,0)
          STOP 'py is not conserved'
        ELSEIF (PCT(3,0).GT.1.D-6) THEN
          WRITE(*,*) 'pz is not conserved ',PCT(3,0)
          STOP 'pz is not conserved'
        ENDIF
      ENDIF
      DO I=0,3
        DO J=1,(NLOOPLINE-1)
          DO K=1,J
            PCT(I,J)=PCT(I,J)+PL(I,K)
          ENDDO
        ENDDO
      ENDDO

      CALL CTSXCUT(CTMODE,LSCALE,MU_R,NLOOPLINE,ML5_0_LOOPNUM
     $ ,ML5_0_MPLOOPNUM,RANK,PCT,M2LCT,RES,ACC,R1,STABLE)
      RES(1)=NORMALIZATION*2.0D0*DBLE(RES(1))
      RES(2)=NORMALIZATION*2.0D0*DBLE(RES(2))
      RES(3)=NORMALIZATION*2.0D0*DBLE(RES(3))
C     WRITE(*,*) 'Loop AMPLNUM',AMPLNUM,' =',RES(1),RES(2),RES(3)
      END

      SUBROUTINE ML5_0_INITCT()
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
C     MADLOOP'S NUMERATOR IN THE DEFAULT OUTPUT IS SLOWER THAN THE
C      RECONSTRUCTED ONE IN CT. SO WE BETTER USE CT ONE IN THIS CASE.
      EXT_NUM_FOR_R1=.TRUE.
C     -------------------------------	  

C     The initialization below is for CT v1.8.+
      CALL CTSINIT(THRS,LOOPLIB,EXT_NUM_FOR_R1)
C     The initialization below is for the older stable CT v1.7, still
C      used for now in the beta release.
C     CALL CTSINIT(THRS,LOOPLIB)

      END

      SUBROUTINE ML5_0_LOOP_3_3( LID, W1, W2, W3, M1,MP_M1, M2,MP_M2
     $ , M3,MP_M3, C1,MP_C1, C2,MP_C2, C3,MP_C3,  RANK, LSYMFACT
     $ , LMULTIPLIER, AMPLN, RES, STABLE)

      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    MAXLCOUPLINGS
      PARAMETER (MAXLCOUPLINGS=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=3)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3
      COMPLEX*16 M1, M2, M3
      COMPLEX*32 MP_M1, MP_M2, MP_M3
      COMPLEX*16 C1, C2, C3
      COMPLEX*32 MP_C1, MP_C2, MP_C3

      COMPLEX*16 RES(3)
      INTEGER LID, RANK, LSYMFACT, LMULTIPLIER
      INTEGER AMPLN
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE)
      INTEGER I, J, K, TEMP
C     
C     GLOBAL VARIABLES
C     
      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID, SYMFACT, MULTIPLIER,AMPLNUM

      COMPLEX*16 LC(MAXLCOUPLINGS)
      COMPLEX*16 ML(NEXTERNAL+2)
      COMMON/ML5_0_DP_LOOP/LC,ML

      COMPLEX*32 MP_LC(MAXLCOUPLINGS)
      COMPLEX*32 MP_ML(NEXTERNAL+2)
      COMMON/ML5_0_MP_LOOP/MP_LC,MP_ML

      COMPLEX*16 W(20,NWAVEFUNCS,NCOMB)
      INTEGER VALIDH
      COMMON/ML5_0_WFCTS/W
      COMMON/ML5_0_VALIDH/VALIDH

C     ----------
C     BEGIN CODE
C     ----------

      WE(1)=W1
      WE(2)=W2
      WE(3)=W3
      M2L(1)=M3**2
      M2L(2)=M1**2
      M2L(3)=M2**2
      ML(1)=M3
      ML(2)=M3
      MP_ML(1)=MP_M3
      MP_ML(2)=MP_M3
      ML(3)=M1
      MP_ML(3)=MP_M1
      ML(4)=M2
      MP_ML(4)=MP_M2
      ML(5)=M3
      MP_ML(5)=MP_M3
      DO I=1,NLOOPLINE
        PAIRING(I)=1
      ENDDO

      LC(1)=C1
      MP_LC(1)=MP_C1
      LC(2)=C2
      MP_LC(2)=MP_C2
      LC(3)=C3
      MP_LC(3)=MP_C3
      AMPLNUM=AMPLN
      ID=LID
      SYMFACT=LSYMFACT
      MULTIPLIER=LMULTIPLIER
      DO I=0,3
        TEMP=1
        DO J=1,NLOOPLINE
          PL(I,J)=0.D0
          DO K=TEMP,(TEMP+PAIRING(J)-1)
            PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K),VALIDH))
          ENDDO
          TEMP=TEMP+PAIRING(J)
        ENDDO
      ENDDO
      CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)

      END

      SUBROUTINE ML5_0_LOOP_2_2( LID, W1, W2, M1,MP_M1, M2,MP_M2, C1
     $ ,MP_C1, C2,MP_C2,  RANK, LSYMFACT, LMULTIPLIER, AMPLN, RES
     $ , STABLE)

      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    MAXLCOUPLINGS
      PARAMETER (MAXLCOUPLINGS=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=2)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2
      COMPLEX*16 M1, M2
      COMPLEX*32 MP_M1, MP_M2
      COMPLEX*16 C1, C2
      COMPLEX*32 MP_C1, MP_C2

      COMPLEX*16 RES(3)
      INTEGER LID, RANK, LSYMFACT, LMULTIPLIER
      INTEGER AMPLN
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE)
      INTEGER I, J, K, TEMP
C     
C     GLOBAL VARIABLES
C     
      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID, SYMFACT, MULTIPLIER,AMPLNUM

      COMPLEX*16 LC(MAXLCOUPLINGS)
      COMPLEX*16 ML(NEXTERNAL+2)
      COMMON/ML5_0_DP_LOOP/LC,ML

      COMPLEX*32 MP_LC(MAXLCOUPLINGS)
      COMPLEX*32 MP_ML(NEXTERNAL+2)
      COMMON/ML5_0_MP_LOOP/MP_LC,MP_ML

      COMPLEX*16 W(20,NWAVEFUNCS,NCOMB)
      INTEGER VALIDH
      COMMON/ML5_0_WFCTS/W
      COMMON/ML5_0_VALIDH/VALIDH

C     ----------
C     BEGIN CODE
C     ----------

      WE(1)=W1
      WE(2)=W2
      M2L(1)=M2**2
      M2L(2)=M1**2
      ML(1)=M2
      ML(2)=M2
      MP_ML(1)=MP_M2
      MP_ML(2)=MP_M2
      ML(3)=M1
      MP_ML(3)=MP_M1
      ML(4)=M2
      MP_ML(4)=MP_M2
      DO I=1,NLOOPLINE
        PAIRING(I)=1
      ENDDO

      LC(1)=C1
      MP_LC(1)=MP_C1
      LC(2)=C2
      MP_LC(2)=MP_C2
      AMPLNUM=AMPLN
      ID=LID
      SYMFACT=LSYMFACT
      MULTIPLIER=LMULTIPLIER
      DO I=0,3
        TEMP=1
        DO J=1,NLOOPLINE
          PL(I,J)=0.D0
          DO K=TEMP,(TEMP+PAIRING(J)-1)
            PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K),VALIDH))
          ENDDO
          TEMP=TEMP+PAIRING(J)
        ENDDO
      ENDDO
      CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)

      END

      SUBROUTINE ML5_0_LOOP_3_4_3( LID, P1, P2, P3, W1, W2, W3, W4, M1
     $ ,MP_M1, M2,MP_M2, M3,MP_M3, C1,MP_C1, C2,MP_C2, C3,MP_C3,  RANK
     $ , LSYMFACT, LMULTIPLIER, AMPLN, RES, STABLE)

      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    MAXLCOUPLINGS
      PARAMETER (MAXLCOUPLINGS=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=3)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4
      COMPLEX*16 M1, M2, M3
      COMPLEX*32 MP_M1, MP_M2, MP_M3
      COMPLEX*16 C1, C2, C3
      COMPLEX*32 MP_C1, MP_C2, MP_C3
      INTEGER P1, P2, P3
      COMPLEX*16 RES(3)
      INTEGER LID, RANK, LSYMFACT, LMULTIPLIER
      INTEGER AMPLN
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE)
      INTEGER I, J, K, TEMP
C     
C     GLOBAL VARIABLES
C     
      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID, SYMFACT, MULTIPLIER,AMPLNUM

      COMPLEX*16 LC(MAXLCOUPLINGS)
      COMPLEX*16 ML(NEXTERNAL+2)
      COMMON/ML5_0_DP_LOOP/LC,ML

      COMPLEX*32 MP_LC(MAXLCOUPLINGS)
      COMPLEX*32 MP_ML(NEXTERNAL+2)
      COMMON/ML5_0_MP_LOOP/MP_LC,MP_ML

      COMPLEX*16 W(20,NWAVEFUNCS,NCOMB)
      INTEGER VALIDH
      COMMON/ML5_0_WFCTS/W
      COMMON/ML5_0_VALIDH/VALIDH

C     ----------
C     BEGIN CODE
C     ----------

      WE(1)=W1
      WE(2)=W2
      WE(3)=W3
      WE(4)=W4
      M2L(1)=M3**2
      M2L(2)=M1**2
      M2L(3)=M2**2
      ML(1)=M3
      ML(2)=M3
      MP_ML(1)=MP_M3
      MP_ML(2)=MP_M3
      ML(3)=M1
      MP_ML(3)=MP_M1
      ML(4)=M2
      MP_ML(4)=MP_M2
      ML(5)=M3
      MP_ML(5)=MP_M3
      PAIRING(1)=P1
      PAIRING(2)=P2
      PAIRING(3)=P3
      LC(1)=C1
      MP_LC(1)=MP_C1
      LC(2)=C2
      MP_LC(2)=MP_C2
      LC(3)=C3
      MP_LC(3)=MP_C3
      AMPLNUM=AMPLN
      ID=LID
      SYMFACT=LSYMFACT
      MULTIPLIER=LMULTIPLIER
      DO I=0,3
        TEMP=1
        DO J=1,NLOOPLINE
          PL(I,J)=0.D0
          DO K=TEMP,(TEMP+PAIRING(J)-1)
            PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K),VALIDH))
          ENDDO
          TEMP=TEMP+PAIRING(J)
        ENDDO
      ENDDO
      CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)

      END

      SUBROUTINE ML5_0_LOOP_2_3_2( LID, P1, P2, W1, W2, W3, M1,MP_M1
     $ , M2,MP_M2, C1,MP_C1, C2,MP_C2,  RANK, LSYMFACT, LMULTIPLIER
     $ , AMPLN, RES, STABLE)

      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    MAXLCOUPLINGS
      PARAMETER (MAXLCOUPLINGS=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=2)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3
      COMPLEX*16 M1, M2
      COMPLEX*32 MP_M1, MP_M2
      COMPLEX*16 C1, C2
      COMPLEX*32 MP_C1, MP_C2
      INTEGER P1, P2
      COMPLEX*16 RES(3)
      INTEGER LID, RANK, LSYMFACT, LMULTIPLIER
      INTEGER AMPLN
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE)
      INTEGER I, J, K, TEMP
C     
C     GLOBAL VARIABLES
C     
      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID, SYMFACT, MULTIPLIER,AMPLNUM

      COMPLEX*16 LC(MAXLCOUPLINGS)
      COMPLEX*16 ML(NEXTERNAL+2)
      COMMON/ML5_0_DP_LOOP/LC,ML

      COMPLEX*32 MP_LC(MAXLCOUPLINGS)
      COMPLEX*32 MP_ML(NEXTERNAL+2)
      COMMON/ML5_0_MP_LOOP/MP_LC,MP_ML

      COMPLEX*16 W(20,NWAVEFUNCS,NCOMB)
      INTEGER VALIDH
      COMMON/ML5_0_WFCTS/W
      COMMON/ML5_0_VALIDH/VALIDH

C     ----------
C     BEGIN CODE
C     ----------

      WE(1)=W1
      WE(2)=W2
      WE(3)=W3
      M2L(1)=M2**2
      M2L(2)=M1**2
      ML(1)=M2
      ML(2)=M2
      MP_ML(1)=MP_M2
      MP_ML(2)=MP_M2
      ML(3)=M1
      MP_ML(3)=MP_M1
      ML(4)=M2
      MP_ML(4)=MP_M2
      PAIRING(1)=P1
      PAIRING(2)=P2
      LC(1)=C1
      MP_LC(1)=MP_C1
      LC(2)=C2
      MP_LC(2)=MP_C2
      AMPLNUM=AMPLN
      ID=LID
      SYMFACT=LSYMFACT
      MULTIPLIER=LMULTIPLIER
      DO I=0,3
        TEMP=1
        DO J=1,NLOOPLINE
          PL(I,J)=0.D0
          DO K=TEMP,(TEMP+PAIRING(J)-1)
            PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K),VALIDH))
          ENDDO
          TEMP=TEMP+PAIRING(J)
        ENDDO
      ENDDO
      CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)

      END

      SUBROUTINE ML5_0_LOOP_4_5_4( LID, P1, P2, P3, P4, W1, W2, W3, W4
     $ , W5, M1,MP_M1, M2,MP_M2, M3,MP_M3, M4,MP_M4, C1,MP_C1, C2
     $ ,MP_C2, C3,MP_C3, C4,MP_C4,  RANK, LSYMFACT, LMULTIPLIER, AMPLN
     $ , RES, STABLE)

      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    MAXLCOUPLINGS
      PARAMETER (MAXLCOUPLINGS=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=4)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4, W5
      COMPLEX*16 M1, M2, M3, M4
      COMPLEX*32 MP_M1, MP_M2, MP_M3, MP_M4
      COMPLEX*16 C1, C2, C3, C4
      COMPLEX*32 MP_C1, MP_C2, MP_C3, MP_C4
      INTEGER P1, P2, P3, P4
      COMPLEX*16 RES(3)
      INTEGER LID, RANK, LSYMFACT, LMULTIPLIER
      INTEGER AMPLN
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE)
      INTEGER I, J, K, TEMP
C     
C     GLOBAL VARIABLES
C     
      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID, SYMFACT, MULTIPLIER,AMPLNUM

      COMPLEX*16 LC(MAXLCOUPLINGS)
      COMPLEX*16 ML(NEXTERNAL+2)
      COMMON/ML5_0_DP_LOOP/LC,ML

      COMPLEX*32 MP_LC(MAXLCOUPLINGS)
      COMPLEX*32 MP_ML(NEXTERNAL+2)
      COMMON/ML5_0_MP_LOOP/MP_LC,MP_ML

      COMPLEX*16 W(20,NWAVEFUNCS,NCOMB)
      INTEGER VALIDH
      COMMON/ML5_0_WFCTS/W
      COMMON/ML5_0_VALIDH/VALIDH

C     ----------
C     BEGIN CODE
C     ----------

      WE(1)=W1
      WE(2)=W2
      WE(3)=W3
      WE(4)=W4
      WE(5)=W5
      M2L(1)=M4**2
      M2L(2)=M1**2
      M2L(3)=M2**2
      M2L(4)=M3**2
      ML(1)=M4
      ML(2)=M4
      MP_ML(1)=MP_M4
      MP_ML(2)=MP_M4
      ML(3)=M1
      MP_ML(3)=MP_M1
      ML(4)=M2
      MP_ML(4)=MP_M2
      ML(5)=M3
      MP_ML(5)=MP_M3
      ML(6)=M4
      MP_ML(6)=MP_M4
      PAIRING(1)=P1
      PAIRING(2)=P2
      PAIRING(3)=P3
      PAIRING(4)=P4
      LC(1)=C1
      MP_LC(1)=MP_C1
      LC(2)=C2
      MP_LC(2)=MP_C2
      LC(3)=C3
      MP_LC(3)=MP_C3
      LC(4)=C4
      MP_LC(4)=MP_C4
      AMPLNUM=AMPLN
      ID=LID
      SYMFACT=LSYMFACT
      MULTIPLIER=LMULTIPLIER
      DO I=0,3
        TEMP=1
        DO J=1,NLOOPLINE
          PL(I,J)=0.D0
          DO K=TEMP,(TEMP+PAIRING(J)-1)
            PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K),VALIDH))
          ENDDO
          TEMP=TEMP+PAIRING(J)
        ENDDO
      ENDDO
      CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)

      END

      SUBROUTINE ML5_0_LOOP_4_4( LID, W1, W2, W3, W4, M1,MP_M1, M2
     $ ,MP_M2, M3,MP_M3, M4,MP_M4, C1,MP_C1, C2,MP_C2, C3,MP_C3, C4
     $ ,MP_C4,  RANK, LSYMFACT, LMULTIPLIER, AMPLN, RES, STABLE)

      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    MAXLCOUPLINGS
      PARAMETER (MAXLCOUPLINGS=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=4)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4
      COMPLEX*16 M1, M2, M3, M4
      COMPLEX*32 MP_M1, MP_M2, MP_M3, MP_M4
      COMPLEX*16 C1, C2, C3, C4
      COMPLEX*32 MP_C1, MP_C2, MP_C3, MP_C4

      COMPLEX*16 RES(3)
      INTEGER LID, RANK, LSYMFACT, LMULTIPLIER
      INTEGER AMPLN
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE)
      INTEGER I, J, K, TEMP
C     
C     GLOBAL VARIABLES
C     
      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID, SYMFACT, MULTIPLIER,AMPLNUM

      COMPLEX*16 LC(MAXLCOUPLINGS)
      COMPLEX*16 ML(NEXTERNAL+2)
      COMMON/ML5_0_DP_LOOP/LC,ML

      COMPLEX*32 MP_LC(MAXLCOUPLINGS)
      COMPLEX*32 MP_ML(NEXTERNAL+2)
      COMMON/ML5_0_MP_LOOP/MP_LC,MP_ML

      COMPLEX*16 W(20,NWAVEFUNCS,NCOMB)
      INTEGER VALIDH
      COMMON/ML5_0_WFCTS/W
      COMMON/ML5_0_VALIDH/VALIDH

C     ----------
C     BEGIN CODE
C     ----------

      WE(1)=W1
      WE(2)=W2
      WE(3)=W3
      WE(4)=W4
      M2L(1)=M4**2
      M2L(2)=M1**2
      M2L(3)=M2**2
      M2L(4)=M3**2
      ML(1)=M4
      ML(2)=M4
      MP_ML(1)=MP_M4
      MP_ML(2)=MP_M4
      ML(3)=M1
      MP_ML(3)=MP_M1
      ML(4)=M2
      MP_ML(4)=MP_M2
      ML(5)=M3
      MP_ML(5)=MP_M3
      ML(6)=M4
      MP_ML(6)=MP_M4
      DO I=1,NLOOPLINE
        PAIRING(I)=1
      ENDDO

      LC(1)=C1
      MP_LC(1)=MP_C1
      LC(2)=C2
      MP_LC(2)=MP_C2
      LC(3)=C3
      MP_LC(3)=MP_C3
      LC(4)=C4
      MP_LC(4)=MP_C4
      AMPLNUM=AMPLN
      ID=LID
      SYMFACT=LSYMFACT
      MULTIPLIER=LMULTIPLIER
      DO I=0,3
        TEMP=1
        DO J=1,NLOOPLINE
          PL(I,J)=0.D0
          DO K=TEMP,(TEMP+PAIRING(J)-1)
            PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K),VALIDH))
          ENDDO
          TEMP=TEMP+PAIRING(J)
        ENDDO
      ENDDO
      CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)

      END

      SUBROUTINE ML5_0_LOOP_5_5( LID, W1, W2, W3, W4, W5, M1,MP_M1, M2
     $ ,MP_M2, M3,MP_M3, M4,MP_M4, M5,MP_M5, C1,MP_C1, C2,MP_C2, C3
     $ ,MP_C3, C4,MP_C4, C5,MP_C5,  RANK, LSYMFACT, LMULTIPLIER, AMPLN
     $ , RES, STABLE)

      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER    MAXLCOUPLINGS
      PARAMETER (MAXLCOUPLINGS=5)
      INTEGER    NLOOPLINE
      PARAMETER (NLOOPLINE=5)
      INTEGER    NWAVEFUNCS
      PARAMETER (NWAVEFUNCS=28)
      INTEGER    NCOMB
      PARAMETER (NCOMB=48)
C     
C     ARGUMENTS 
C     
      INTEGER W1, W2, W3, W4, W5
      COMPLEX*16 M1, M2, M3, M4, M5
      COMPLEX*32 MP_M1, MP_M2, MP_M3, MP_M4, MP_M5
      COMPLEX*16 C1, C2, C3, C4, C5
      COMPLEX*32 MP_C1, MP_C2, MP_C3, MP_C4, MP_C5

      COMPLEX*16 RES(3)
      INTEGER LID, RANK, LSYMFACT, LMULTIPLIER
      INTEGER AMPLN
      LOGICAL STABLE
C     
C     LOCAL VARIABLES 
C     
      REAL*8 PL(0:3,NLOOPLINE)
      COMPLEX*16 M2L(NLOOPLINE)
      INTEGER PAIRING(NLOOPLINE)
      INTEGER I, J, K, TEMP
C     
C     GLOBAL VARIABLES
C     
      INTEGER WE(NEXTERNAL)
      INTEGER ID, SYMFACT, MULTIPLIER, AMPLNUM
      COMMON/ML5_0_LOOP/WE,ID, SYMFACT, MULTIPLIER,AMPLNUM

      COMPLEX*16 LC(MAXLCOUPLINGS)
      COMPLEX*16 ML(NEXTERNAL+2)
      COMMON/ML5_0_DP_LOOP/LC,ML

      COMPLEX*32 MP_LC(MAXLCOUPLINGS)
      COMPLEX*32 MP_ML(NEXTERNAL+2)
      COMMON/ML5_0_MP_LOOP/MP_LC,MP_ML

      COMPLEX*16 W(20,NWAVEFUNCS,NCOMB)
      INTEGER VALIDH
      COMMON/ML5_0_WFCTS/W
      COMMON/ML5_0_VALIDH/VALIDH

C     ----------
C     BEGIN CODE
C     ----------

      WE(1)=W1
      WE(2)=W2
      WE(3)=W3
      WE(4)=W4
      WE(5)=W5
      M2L(1)=M5**2
      M2L(2)=M1**2
      M2L(3)=M2**2
      M2L(4)=M3**2
      M2L(5)=M4**2
      ML(1)=M5
      ML(2)=M5
      MP_ML(1)=MP_M5
      MP_ML(2)=MP_M5
      ML(3)=M1
      MP_ML(3)=MP_M1
      ML(4)=M2
      MP_ML(4)=MP_M2
      ML(5)=M3
      MP_ML(5)=MP_M3
      ML(6)=M4
      MP_ML(6)=MP_M4
      ML(7)=M5
      MP_ML(7)=MP_M5
      DO I=1,NLOOPLINE
        PAIRING(I)=1
      ENDDO

      LC(1)=C1
      MP_LC(1)=MP_C1
      LC(2)=C2
      MP_LC(2)=MP_C2
      LC(3)=C3
      MP_LC(3)=MP_C3
      LC(4)=C4
      MP_LC(4)=MP_C4
      LC(5)=C5
      MP_LC(5)=MP_C5
      AMPLNUM=AMPLN
      ID=LID
      SYMFACT=LSYMFACT
      MULTIPLIER=LMULTIPLIER
      DO I=0,3
        TEMP=1
        DO J=1,NLOOPLINE
          PL(I,J)=0.D0
          DO K=TEMP,(TEMP+PAIRING(J)-1)
            PL(I,J)=PL(I,J)-DBLE(W(1+I,WE(K),VALIDH))
          ENDDO
          TEMP=TEMP+PAIRING(J)
        ENDDO
      ENDDO
      CALL ML5_0_CTLOOP(NLOOPLINE,PL,M2L,RANK,RES,STABLE)

      END

