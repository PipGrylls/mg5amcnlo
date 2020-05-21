      SUBROUTINE HELAS_CALLS_AMPB_1(P,NHEL,H,IC)
C     
C     Modules
C     
      USE POLYNOMIAL_CONSTANTS
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)
      INTEGER NBORNAMPS
      PARAMETER (NBORNAMPS=1)
      INTEGER    NLOOPS, NLOOPGROUPS, NCTAMPS
      PARAMETER (NLOOPS=35, NLOOPGROUPS=25, NCTAMPS=15)
      INTEGER    NLOOPAMPS
      PARAMETER (NLOOPAMPS=50)
      INTEGER    NWAVEFUNCS,NLOOPWAVEFUNCS
      PARAMETER (NWAVEFUNCS=6,NLOOPWAVEFUNCS=73)
      REAL*8     ZERO
      PARAMETER (ZERO=0D0)
      REAL*16     MP__ZERO
      PARAMETER (MP__ZERO=0.0E0_16)
C     These are constants related to the split orders
      INTEGER    NSO, NSQUAREDSO, NAMPSO
      PARAMETER (NSO=2, NSQUAREDSO=1, NAMPSO=2)
C     
C     ARGUMENTS
C     
      REAL*8 P(0:3,NEXTERNAL)
      INTEGER NHEL(NEXTERNAL), IC(NEXTERNAL)
      INTEGER H
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J,K
      COMPLEX*16 COEFS(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)

      LOGICAL DUMMYFALSE
      DATA DUMMYFALSE/.FALSE./
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'
      INCLUDE 'mp_coupl.inc'

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NSQUAREDSO,NLOOPGROUPS)
      COMMON/FILTERS/GOODAMP,GOODHEL,HELOFFSET

      LOGICAL CHECKPHASE
      LOGICAL HELDOUBLECHECKED
      COMMON/INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER SQSO_TARGET
      COMMON/SOCHOICE/SQSO_TARGET

      LOGICAL UVCT_REQ_SO_DONE,MP_UVCT_REQ_SO_DONE,CT_REQ_SO_DONE
     $ ,MP_CT_REQ_SO_DONE,LOOP_REQ_SO_DONE,MP_LOOP_REQ_SO_DONE
     $ ,CTCALL_REQ_SO_DONE,FILTER_SO
      COMMON/SO_REQS/UVCT_REQ_SO_DONE,MP_UVCT_REQ_SO_DONE
     $ ,CT_REQ_SO_DONE,MP_CT_REQ_SO_DONE,LOOP_REQ_SO_DONE
     $ ,MP_LOOP_REQ_SO_DONE,CTCALL_REQ_SO_DONE,FILTER_SO

      INTEGER I_SO
      COMMON/I_SO/I_SO
      INTEGER I_LIB
      COMMON/I_LIB/I_LIB

      COMPLEX*16 AMP(NBORNAMPS)
      COMMON/AMPS/AMP
      COMPLEX*16 W(20,NWAVEFUNCS)
      COMMON/W/W

      COMPLEX*16 WL(MAXLWFSIZE,0:LOOPMAXCOEFS-1,MAXLWFSIZE,
     $ -1:NLOOPWAVEFUNCS)
      COMPLEX*16 PL(0:3,-1:NLOOPWAVEFUNCS)
      COMMON/WL/WL,PL

      COMPLEX*16 AMPL(3,NCTAMPS)
      COMMON/AMPL/AMPL

C     
C     ----------
C     BEGIN CODE
C     ----------

C     The target squared split order contribution is already reached
C      if true.
      IF (FILTER_SO.AND.CT_REQ_SO_DONE) THEN
        GOTO 1001
      ENDIF

      CALL IXXXXX(P(0,1),ZERO,NHEL(1),+1*IC(1),W(1,1))
      CALL OXXXXX(P(0,2),ZERO,NHEL(2),-1*IC(2),W(1,2))
      CALL OXXXXX(P(0,3),ZERO,NHEL(3),+1*IC(3),W(1,3))
      CALL IXXXXX(P(0,4),ZERO,NHEL(4),-1*IC(4),W(1,4))
      CALL FFV2P0_3(W(1,1),W(1,2),GC_67,DCMPLX(CMASS_MDL_MW),W(1,5))
C     Amplitude(s) for born diagram with ID 1
      CALL FFV2_0(W(1,4),W(1,3),W(1,5),GC_67,AMP(1))
      CALL FFV2P0_3(W(1,4),W(1,3),GC_67,DCMPLX(CMASS_MDL_MW),W(1,6))
C     Counter-term amplitude(s) for loop diagram number 2
      CALL L_WMWPMASS2_L_WMWPMASS4_0(W(1,6),W(1,5),C_UVWMWPMASS2EW_1EPS
     $ ,C_UVWMWPMASS1EW_1EPS,AMPL(2,1))
      CALL L_WMWPMASS2_L_WMWPMASS4_0(W(1,6),W(1,5),C_UVWMWPMASS2EW
     $ ,C_UVWMWPMASS1EW,AMPL(1,2))
C     Counter-term amplitude(s) for loop diagram number 4
      CALL L_VEXVEA21_0(W(1,4),W(1,3),W(1,5),C_UVEPVEWM1EW_1EPS,AMPL(2
     $ ,3))
      CALL L_VEXVEA21_0(W(1,4),W(1,3),W(1,5),C_UVTTPVTWM1EW,AMPL(1,4))
C     Counter-term amplitude(s) for loop diagram number 5
      CALL L_VEXVEA21_0(W(1,1),W(1,2),W(1,6),C_UVDXUWM1EW_1EPS,AMPL(2
     $ ,5))
      CALL L_VEXVEA21_0(W(1,1),W(1,2),W(1,6),C_UVUXDWP1EW,AMPL(1,6))
C     Counter-term amplitude(s) for loop diagram number 14
      CALL FFV2_0(W(1,4),W(1,3),W(1,5),R2_VLW,AMPL(1,7))
C     Counter-term amplitude(s) for loop diagram number 16
      CALL FFV2_0(W(1,1),W(1,2),W(1,6),R2_TXBW2CP,AMPL(1,8))
C     Counter-term amplitude(s) for loop diagram number 23
      CALL R2_GG_1_R2_GG_2_R2_GG_3_0(W(1,5),W(1,6),R2_WWBOSON1
     $ ,R2_WWBOSON2,R2_WWBOSON3,AMPL(1,9))
C     Counter-term amplitude(s) for loop diagram number 34
      CALL R2_GG_1_0(W(1,5),W(1,6),R2_WWUD1,AMPL(1,10))
      CALL R2_GG_1_0(W(1,5),W(1,6),R2_WWUD1,AMPL(1,11))
C     Counter-term amplitude(s) for loop diagram number 35
      CALL R2_GG_1_R2_GG_3_0(W(1,5),W(1,6),R2_WWUD1,R2_WWTB3,AMPL(1,12)
     $ )
C     Counter-term amplitude(s) for loop diagram number 36
      CALL R2_GG_1_0(W(1,5),W(1,6),R2_WWL,AMPL(1,13))
      CALL R2_GG_1_0(W(1,5),W(1,6),R2_WWL,AMPL(1,14))
      CALL R2_GG_1_0(W(1,5),W(1,6),R2_WWL,AMPL(1,15))
C     At this point, all CT amps needed for (QCD=0 QED=6), i.e. of
C      split order ID=1, are computed.
      IF(FILTER_SO.AND.SQSO_TARGET.EQ.1) GOTO 2000

      GOTO 1001
 2000 CONTINUE
      CT_REQ_SO_DONE=.TRUE.
 1001 CONTINUE
      END

