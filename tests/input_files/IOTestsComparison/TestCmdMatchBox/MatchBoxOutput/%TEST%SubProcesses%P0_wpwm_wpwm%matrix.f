      SUBROUTINE MG5_0_SMATRIX(P,ANS)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     MadGraph5_aMC@NLO StandAlone Version
C     
C     Returns amplitude squared summed/avg over colors
C     and helicities
C     for the point in phase space P(0:3,NEXTERNAL)
C     
C     Process: w+ w- > w+ w- WEIGHTED<=4
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER                 NCOMB
      PARAMETER (             NCOMB=81)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL),ANS
C     
C     LOCAL VARIABLES 
C     
      INTEGER NHEL(NEXTERNAL,NCOMB),NTRY
      REAL*8 T
      REAL*8 MG5_0_MATRIX
      INTEGER IHEL,IDEN, I
      INTEGER JC(NEXTERNAL)
      LOGICAL GOODHEL(NCOMB)
      DATA NTRY/0/
      DATA GOODHEL/NCOMB*.FALSE./
      DATA (NHEL(I,   1),I=1,4) / 1,-1,-1, 1/
      DATA (NHEL(I,   2),I=1,4) / 1,-1,-1, 0/
      DATA (NHEL(I,   3),I=1,4) / 1,-1,-1,-1/
      DATA (NHEL(I,   4),I=1,4) / 1,-1, 0, 1/
      DATA (NHEL(I,   5),I=1,4) / 1,-1, 0, 0/
      DATA (NHEL(I,   6),I=1,4) / 1,-1, 0,-1/
      DATA (NHEL(I,   7),I=1,4) / 1,-1, 1, 1/
      DATA (NHEL(I,   8),I=1,4) / 1,-1, 1, 0/
      DATA (NHEL(I,   9),I=1,4) / 1,-1, 1,-1/
      DATA (NHEL(I,  10),I=1,4) / 1, 0,-1, 1/
      DATA (NHEL(I,  11),I=1,4) / 1, 0,-1, 0/
      DATA (NHEL(I,  12),I=1,4) / 1, 0,-1,-1/
      DATA (NHEL(I,  13),I=1,4) / 1, 0, 0, 1/
      DATA (NHEL(I,  14),I=1,4) / 1, 0, 0, 0/
      DATA (NHEL(I,  15),I=1,4) / 1, 0, 0,-1/
      DATA (NHEL(I,  16),I=1,4) / 1, 0, 1, 1/
      DATA (NHEL(I,  17),I=1,4) / 1, 0, 1, 0/
      DATA (NHEL(I,  18),I=1,4) / 1, 0, 1,-1/
      DATA (NHEL(I,  19),I=1,4) / 1, 1,-1, 1/
      DATA (NHEL(I,  20),I=1,4) / 1, 1,-1, 0/
      DATA (NHEL(I,  21),I=1,4) / 1, 1,-1,-1/
      DATA (NHEL(I,  22),I=1,4) / 1, 1, 0, 1/
      DATA (NHEL(I,  23),I=1,4) / 1, 1, 0, 0/
      DATA (NHEL(I,  24),I=1,4) / 1, 1, 0,-1/
      DATA (NHEL(I,  25),I=1,4) / 1, 1, 1, 1/
      DATA (NHEL(I,  26),I=1,4) / 1, 1, 1, 0/
      DATA (NHEL(I,  27),I=1,4) / 1, 1, 1,-1/
      DATA (NHEL(I,  28),I=1,4) / 0,-1,-1, 1/
      DATA (NHEL(I,  29),I=1,4) / 0,-1,-1, 0/
      DATA (NHEL(I,  30),I=1,4) / 0,-1,-1,-1/
      DATA (NHEL(I,  31),I=1,4) / 0,-1, 0, 1/
      DATA (NHEL(I,  32),I=1,4) / 0,-1, 0, 0/
      DATA (NHEL(I,  33),I=1,4) / 0,-1, 0,-1/
      DATA (NHEL(I,  34),I=1,4) / 0,-1, 1, 1/
      DATA (NHEL(I,  35),I=1,4) / 0,-1, 1, 0/
      DATA (NHEL(I,  36),I=1,4) / 0,-1, 1,-1/
      DATA (NHEL(I,  37),I=1,4) / 0, 0,-1, 1/
      DATA (NHEL(I,  38),I=1,4) / 0, 0,-1, 0/
      DATA (NHEL(I,  39),I=1,4) / 0, 0,-1,-1/
      DATA (NHEL(I,  40),I=1,4) / 0, 0, 0, 1/
      DATA (NHEL(I,  41),I=1,4) / 0, 0, 0, 0/
      DATA (NHEL(I,  42),I=1,4) / 0, 0, 0,-1/
      DATA (NHEL(I,  43),I=1,4) / 0, 0, 1, 1/
      DATA (NHEL(I,  44),I=1,4) / 0, 0, 1, 0/
      DATA (NHEL(I,  45),I=1,4) / 0, 0, 1,-1/
      DATA (NHEL(I,  46),I=1,4) / 0, 1,-1, 1/
      DATA (NHEL(I,  47),I=1,4) / 0, 1,-1, 0/
      DATA (NHEL(I,  48),I=1,4) / 0, 1,-1,-1/
      DATA (NHEL(I,  49),I=1,4) / 0, 1, 0, 1/
      DATA (NHEL(I,  50),I=1,4) / 0, 1, 0, 0/
      DATA (NHEL(I,  51),I=1,4) / 0, 1, 0,-1/
      DATA (NHEL(I,  52),I=1,4) / 0, 1, 1, 1/
      DATA (NHEL(I,  53),I=1,4) / 0, 1, 1, 0/
      DATA (NHEL(I,  54),I=1,4) / 0, 1, 1,-1/
      DATA (NHEL(I,  55),I=1,4) /-1,-1,-1, 1/
      DATA (NHEL(I,  56),I=1,4) /-1,-1,-1, 0/
      DATA (NHEL(I,  57),I=1,4) /-1,-1,-1,-1/
      DATA (NHEL(I,  58),I=1,4) /-1,-1, 0, 1/
      DATA (NHEL(I,  59),I=1,4) /-1,-1, 0, 0/
      DATA (NHEL(I,  60),I=1,4) /-1,-1, 0,-1/
      DATA (NHEL(I,  61),I=1,4) /-1,-1, 1, 1/
      DATA (NHEL(I,  62),I=1,4) /-1,-1, 1, 0/
      DATA (NHEL(I,  63),I=1,4) /-1,-1, 1,-1/
      DATA (NHEL(I,  64),I=1,4) /-1, 0,-1, 1/
      DATA (NHEL(I,  65),I=1,4) /-1, 0,-1, 0/
      DATA (NHEL(I,  66),I=1,4) /-1, 0,-1,-1/
      DATA (NHEL(I,  67),I=1,4) /-1, 0, 0, 1/
      DATA (NHEL(I,  68),I=1,4) /-1, 0, 0, 0/
      DATA (NHEL(I,  69),I=1,4) /-1, 0, 0,-1/
      DATA (NHEL(I,  70),I=1,4) /-1, 0, 1, 1/
      DATA (NHEL(I,  71),I=1,4) /-1, 0, 1, 0/
      DATA (NHEL(I,  72),I=1,4) /-1, 0, 1,-1/
      DATA (NHEL(I,  73),I=1,4) /-1, 1,-1, 1/
      DATA (NHEL(I,  74),I=1,4) /-1, 1,-1, 0/
      DATA (NHEL(I,  75),I=1,4) /-1, 1,-1,-1/
      DATA (NHEL(I,  76),I=1,4) /-1, 1, 0, 1/
      DATA (NHEL(I,  77),I=1,4) /-1, 1, 0, 0/
      DATA (NHEL(I,  78),I=1,4) /-1, 1, 0,-1/
      DATA (NHEL(I,  79),I=1,4) /-1, 1, 1, 1/
      DATA (NHEL(I,  80),I=1,4) /-1, 1, 1, 0/
      DATA (NHEL(I,  81),I=1,4) /-1, 1, 1,-1/
      DATA IDEN/ 9/
C     ----------
C     BEGIN CODE
C     ----------
      NTRY=NTRY+1
      DO IHEL=1,NEXTERNAL
        JC(IHEL) = +1
      ENDDO
      ANS = 0D0
      DO IHEL=1,NCOMB
        IF (GOODHEL(IHEL) .OR. NTRY .LT. 20) THEN
          T=MG5_0_MATRIX(P ,NHEL(1,IHEL),JC(1))
          ANS=ANS+T
          IF (T .NE. 0D0 .AND. .NOT.    GOODHEL(IHEL)) THEN
            GOODHEL(IHEL)=.TRUE.
          ENDIF
        ENDIF
      ENDDO
      ANS=ANS/DBLE(IDEN)
      END


      REAL*8 FUNCTION MG5_0_MATRIX(P,NHEL,IC)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Returns amplitude squared summed/avg over colors
C     for the point with external lines W(0:6,NEXTERNAL)
C     
C     Process: w+ w- > w+ w- WEIGHTED<=4
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NGRAPHS
      PARAMETER (NGRAPHS=7)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NWAVEFUNCS, NCOLOR
      PARAMETER (NWAVEFUNCS=5, NCOLOR=1)
      REAL*8     ZERO
      PARAMETER (ZERO=0D0)
      COMPLEX*16 IMAG1
      PARAMETER (IMAG1=(0D0,1D0))
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL)
      INTEGER NHEL(NEXTERNAL), IC(NEXTERNAL)
C     
C     LOCAL VARIABLES 
C     
      INTEGER I,J
      COMPLEX*16 ZTEMP
      REAL*8  CF(NCOLOR,NCOLOR)
      COMPLEX*16 AMP(NGRAPHS), JAMP(NCOLOR), LNJAMP(NCOLOR)
      COMPLEX*16 W(18,NWAVEFUNCS)
      COMPLEX*16 DUM0,DUM1
      DATA DUM0, DUM1/(0D0, 0D0), (1D0, 0D0)/
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'

C     
C     COLOR DATA
C     
      DATA (CF(I,  1),I=  1,  1) /1.000000000000000D+00/
C     1 ColorOne()
C     ----------
C     BEGIN CODE
C     ----------
      CALL VXXXXX(P(0,1),MDL_MW,NHEL(1),-1*IC(1),W(1,1))
      CALL VXXXXX(P(0,2),MDL_MW,NHEL(2),-1*IC(2),W(1,2))
      CALL VXXXXX(P(0,3),MDL_MW,NHEL(3),+1*IC(3),W(1,3))
      CALL VXXXXX(P(0,4),MDL_MW,NHEL(4),+1*IC(4),W(1,4))
C     Amplitude(s) for diagram number 1
      CALL VVVV2_0(W(1,1),W(1,4),W(1,2),W(1,3),GC_35,AMP(1))
      CALL VVV1P0_1(W(1,1),W(1,2),-GC_3,ZERO,ZERO,W(1,5))
C     Amplitude(s) for diagram number 2
      CALL VVV1_0(W(1,5),W(1,4),W(1,3),-GC_3,AMP(2))
      CALL VVS1_3(W(1,1),W(1,2),GC_72,MDL_MH,MDL_WH,W(1,5))
C     Amplitude(s) for diagram number 3
      CALL VVS1_0(W(1,4),W(1,3),W(1,5),GC_72,AMP(3))
      CALL VVV1_3(W(1,1),W(1,2),GC_53,MDL_MZ,MDL_WZ,W(1,5))
C     Amplitude(s) for diagram number 4
      CALL VVV1_0(W(1,4),W(1,3),W(1,5),GC_53,AMP(4))
      CALL VVV1P0_1(W(1,1),W(1,3),-GC_3,ZERO,ZERO,W(1,5))
C     Amplitude(s) for diagram number 5
      CALL VVV1_0(W(1,5),W(1,4),W(1,2),-GC_3,AMP(5))
      CALL VVS1_3(W(1,1),W(1,3),GC_72,MDL_MH,MDL_WH,W(1,5))
C     Amplitude(s) for diagram number 6
      CALL VVS1_0(W(1,4),W(1,2),W(1,5),GC_72,AMP(6))
      CALL VVV1_3(W(1,1),W(1,3),GC_53,MDL_MZ,MDL_WZ,W(1,5))
C     Amplitude(s) for diagram number 7
      CALL VVV1_0(W(1,4),W(1,2),W(1,5),GC_53,AMP(7))
      JAMP(1) = AMP(1)+AMP(2)+AMP(3)+AMP(4)+AMP(5)+AMP(6)+AMP(7)
      LNJAMP(1) = AMP(1)+AMP(2)+AMP(3)+AMP(4)+AMP(5)+AMP(6)+AMP(7)

      MG5_0_MATRIX = 0.D0
      DO I = 1, NCOLOR
        ZTEMP = (0.D0,0.D0)
        DO J = 1, NCOLOR
          ZTEMP = ZTEMP + CF(J,I)*JAMP(J)
        ENDDO
        MG5_0_MATRIX = MG5_0_MATRIX+ZTEMP*DCONJG(JAMP(I))
      ENDDO

      END










      SUBROUTINE MG5_0_BORN(P,NHEL)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Returns amplitude squared summed/avg over colors
C     for the point with external lines W(0:6,NEXTERNAL)
C     
C     Process: w+ w- > w+ w- WEIGHTED<=4
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NGRAPHS
      PARAMETER (NGRAPHS=7)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=4)
      INTEGER    NWAVEFUNCS, NCOLOR
      PARAMETER (NWAVEFUNCS=5, NCOLOR=1)
      REAL*8     ZERO
      PARAMETER (ZERO=0D0)
      COMPLEX*16 IMAG1
      PARAMETER (IMAG1=(0D0,1D0))
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL)
      INTEGER NHEL(NEXTERNAL), IC(NEXTERNAL)
C     
C     LOCAL VARIABLES 
C     
      INTEGER I,J
      COMPLEX*16 ZTEMP
      REAL*8 CF(NCOLOR,NCOLOR)
      COMPLEX*16 AMP(NGRAPHS), JAMP(NCOLOR), LNJAMP(NCOLOR)
      COMMON/MG5_0_JAMP/JAMP,LNJAMP

      COMPLEX*16 W(18,NWAVEFUNCS)
      COMPLEX*16 DUM0,DUM1
      DATA DUM0, DUM1/(0D0, 0D0), (1D0, 0D0)/
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'

C     
C     COLOR DATA
C     
      DATA (CF(I,  1),I=  1,  1) /1.000000000000000D+00/
C     1 ColorOne()
C     ----------
C     BEGIN CODE
C     ----------
      DO I=1,NEXTERNAL
        IC(I) = 1
      ENDDO

      CALL VXXXXX(P(0,1),MDL_MW,NHEL(1),-1*IC(1),W(1,1))
      CALL VXXXXX(P(0,2),MDL_MW,NHEL(2),-1*IC(2),W(1,2))
      CALL VXXXXX(P(0,3),MDL_MW,NHEL(3),+1*IC(3),W(1,3))
      CALL VXXXXX(P(0,4),MDL_MW,NHEL(4),+1*IC(4),W(1,4))
C     Amplitude(s) for diagram number 1
      CALL VVVV2_0(W(1,1),W(1,4),W(1,2),W(1,3),GC_35,AMP(1))
      CALL VVV1P0_1(W(1,1),W(1,2),-GC_3,ZERO,ZERO,W(1,5))
C     Amplitude(s) for diagram number 2
      CALL VVV1_0(W(1,5),W(1,4),W(1,3),-GC_3,AMP(2))
      CALL VVS1_3(W(1,1),W(1,2),GC_72,MDL_MH,MDL_WH,W(1,5))
C     Amplitude(s) for diagram number 3
      CALL VVS1_0(W(1,4),W(1,3),W(1,5),GC_72,AMP(3))
      CALL VVV1_3(W(1,1),W(1,2),GC_53,MDL_MZ,MDL_WZ,W(1,5))
C     Amplitude(s) for diagram number 4
      CALL VVV1_0(W(1,4),W(1,3),W(1,5),GC_53,AMP(4))
      CALL VVV1P0_1(W(1,1),W(1,3),-GC_3,ZERO,ZERO,W(1,5))
C     Amplitude(s) for diagram number 5
      CALL VVV1_0(W(1,5),W(1,4),W(1,2),-GC_3,AMP(5))
      CALL VVS1_3(W(1,1),W(1,3),GC_72,MDL_MH,MDL_WH,W(1,5))
C     Amplitude(s) for diagram number 6
      CALL VVS1_0(W(1,4),W(1,2),W(1,5),GC_72,AMP(6))
      CALL VVV1_3(W(1,1),W(1,3),GC_53,MDL_MZ,MDL_WZ,W(1,5))
C     Amplitude(s) for diagram number 7
      CALL VVV1_0(W(1,4),W(1,2),W(1,5),GC_53,AMP(7))
      JAMP(1) = AMP(1)+AMP(2)+AMP(3)+AMP(4)+AMP(5)+AMP(6)+AMP(7)
      LNJAMP(1) = AMP(1)+AMP(2)+AMP(3)+AMP(4)+AMP(5)+AMP(6)+AMP(7)

      END

      SUBROUTINE MG5_0_GET_JAMP(NJAMP, ONEJAMP)

      INTEGER     NCOLOR, NJAMP
      PARAMETER (NCOLOR=1)
      COMPLEX*16  JAMP(NCOLOR), ONEJAMP
      COMMON/MG5_0_JAMP/JAMP,LNJAMP

      ONEJAMP = JAMP(NJAMP+1)  ! +1 since njamp start at zero (c convention)
      END

      SUBROUTINE MG5_0_GET_LNJAMP(NJAMP, ONEJAMP)

      INTEGER     NCOLOR, NJAMP
      PARAMETER (NCOLOR=1)
      COMPLEX*16  JAMP(NCOLOR), LNJAMP(NCOLOR), ONEJAMP
      COMMON/MG5_0_JAMP/JAMP,LNJAMP

      ONEJAMP = LNJAMP(NJAMP+1)  ! +1 since njamp start at zero (c convention)
      END




      SUBROUTINE MG5_0_GET_NCOLOR(IN1, IN2, OUT)

      INTEGER IN1, IN2, OUT

      OUT = - 1

      END

      SUBROUTINE MG5_0_GET_NCOL(NCOL)
      INTEGER NCOL
      NCOL = 1
      RETURN
      END

