      SUBROUTINE SMATRIX(P,ANS_SUMMED)
C     
C     Simple routine wrapper to provide the same interface for
C     backward compatibility for usage without split orders.
C     
C     
C     CONSTANTS
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=6)
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL), ANS_SUMMED
C     
C     VARIABLES
C     
      INTEGER I
      REAL*8 ANS(0:NSQAMPSO)
C     
C     BEGIN CODE
C     
      CALL SMATRIX_SPLITORDERS(P,ANS)
      ANS_SUMMED=ANS(0)

      END

      SUBROUTINE SMATRIXHEL(P,HEL,ANS)
      IMPLICIT NONE
C     
C     CONSTANT
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=6)
      INTEGER                 NCOMB
      PARAMETER (             NCOMB=64)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL),ANS
      INTEGER HEL
C     
C     GLOBAL VARIABLES
C     
      INTEGER USERHEL
      COMMON/HELUSERCHOICE/USERHEL
C     ----------
C     BEGIN CODE
C     ----------
      USERHEL=HEL
      CALL SMATRIX(P,ANS)
      USERHEL=-1

      END

      SUBROUTINE SMATRIX_SPLITORDERS(P,ANS)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     MadGraph StandAlone Version
C     
C     Returns amplitude squared summed/avg over colors
C     and helicities
C     for the point in phase space P(0:3,NEXTERNAL)
C     
C     Process: u u~ > u u~ u u~ QED^2<=6
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=6)
      INTEGER    NINITIAL
      PARAMETER (NINITIAL=2)
      INTEGER NPOLENTRIES
      PARAMETER (NPOLENTRIES=(NEXTERNAL+1)*6)
      INTEGER                 NCOMB
      PARAMETER (             NCOMB=64)
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
      INTEGER HELAVGFACTOR
      PARAMETER (HELAVGFACTOR=4)
      LOGICAL CHOSEN_SO_CONFIGS(NSQAMPSO)
      DATA CHOSEN_SO_CONFIGS/.TRUE./
      COMMON/CHOSEN_BORN_SQSO/CHOSEN_SO_CONFIGS
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL),ANS(0:NSQAMPSO)
C     
C     LOCAL VARIABLES 
C     
      INTEGER NTRY
      REAL*8 T(NSQAMPSO), BUFF
      INTEGER IHEL,IDEN, I, J
C     For a 1>N process, them BEAMTWO_HELAVGFACTOR would be set to 1.
      INTEGER BEAMS_HELAVGFACTOR(2)
      DATA (BEAMS_HELAVGFACTOR(I),I=1,2)/2,2/
      INTEGER JC(NEXTERNAL)
      LOGICAL GOODHEL(NCOMB)
      DATA NTRY/0/
      DATA GOODHEL/NCOMB*.FALSE./
      DATA IDEN/144/
C     
C     GLOBAL VARIABLES
C     
      INTEGER NHEL(NEXTERNAL,NCOMB)
      DATA (NHEL(I,   1),I=1,6) / 1,-1,-1, 1,-1, 1/
      DATA (NHEL(I,   2),I=1,6) / 1,-1,-1, 1,-1,-1/
      DATA (NHEL(I,   3),I=1,6) / 1,-1,-1, 1, 1, 1/
      DATA (NHEL(I,   4),I=1,6) / 1,-1,-1, 1, 1,-1/
      DATA (NHEL(I,   5),I=1,6) / 1,-1,-1,-1,-1, 1/
      DATA (NHEL(I,   6),I=1,6) / 1,-1,-1,-1,-1,-1/
      DATA (NHEL(I,   7),I=1,6) / 1,-1,-1,-1, 1, 1/
      DATA (NHEL(I,   8),I=1,6) / 1,-1,-1,-1, 1,-1/
      DATA (NHEL(I,   9),I=1,6) / 1,-1, 1, 1,-1, 1/
      DATA (NHEL(I,  10),I=1,6) / 1,-1, 1, 1,-1,-1/
      DATA (NHEL(I,  11),I=1,6) / 1,-1, 1, 1, 1, 1/
      DATA (NHEL(I,  12),I=1,6) / 1,-1, 1, 1, 1,-1/
      DATA (NHEL(I,  13),I=1,6) / 1,-1, 1,-1,-1, 1/
      DATA (NHEL(I,  14),I=1,6) / 1,-1, 1,-1,-1,-1/
      DATA (NHEL(I,  15),I=1,6) / 1,-1, 1,-1, 1, 1/
      DATA (NHEL(I,  16),I=1,6) / 1,-1, 1,-1, 1,-1/
      DATA (NHEL(I,  17),I=1,6) / 1, 1,-1, 1,-1, 1/
      DATA (NHEL(I,  18),I=1,6) / 1, 1,-1, 1,-1,-1/
      DATA (NHEL(I,  19),I=1,6) / 1, 1,-1, 1, 1, 1/
      DATA (NHEL(I,  20),I=1,6) / 1, 1,-1, 1, 1,-1/
      DATA (NHEL(I,  21),I=1,6) / 1, 1,-1,-1,-1, 1/
      DATA (NHEL(I,  22),I=1,6) / 1, 1,-1,-1,-1,-1/
      DATA (NHEL(I,  23),I=1,6) / 1, 1,-1,-1, 1, 1/
      DATA (NHEL(I,  24),I=1,6) / 1, 1,-1,-1, 1,-1/
      DATA (NHEL(I,  25),I=1,6) / 1, 1, 1, 1,-1, 1/
      DATA (NHEL(I,  26),I=1,6) / 1, 1, 1, 1,-1,-1/
      DATA (NHEL(I,  27),I=1,6) / 1, 1, 1, 1, 1, 1/
      DATA (NHEL(I,  28),I=1,6) / 1, 1, 1, 1, 1,-1/
      DATA (NHEL(I,  29),I=1,6) / 1, 1, 1,-1,-1, 1/
      DATA (NHEL(I,  30),I=1,6) / 1, 1, 1,-1,-1,-1/
      DATA (NHEL(I,  31),I=1,6) / 1, 1, 1,-1, 1, 1/
      DATA (NHEL(I,  32),I=1,6) / 1, 1, 1,-1, 1,-1/
      DATA (NHEL(I,  33),I=1,6) /-1,-1,-1, 1,-1, 1/
      DATA (NHEL(I,  34),I=1,6) /-1,-1,-1, 1,-1,-1/
      DATA (NHEL(I,  35),I=1,6) /-1,-1,-1, 1, 1, 1/
      DATA (NHEL(I,  36),I=1,6) /-1,-1,-1, 1, 1,-1/
      DATA (NHEL(I,  37),I=1,6) /-1,-1,-1,-1,-1, 1/
      DATA (NHEL(I,  38),I=1,6) /-1,-1,-1,-1,-1,-1/
      DATA (NHEL(I,  39),I=1,6) /-1,-1,-1,-1, 1, 1/
      DATA (NHEL(I,  40),I=1,6) /-1,-1,-1,-1, 1,-1/
      DATA (NHEL(I,  41),I=1,6) /-1,-1, 1, 1,-1, 1/
      DATA (NHEL(I,  42),I=1,6) /-1,-1, 1, 1,-1,-1/
      DATA (NHEL(I,  43),I=1,6) /-1,-1, 1, 1, 1, 1/
      DATA (NHEL(I,  44),I=1,6) /-1,-1, 1, 1, 1,-1/
      DATA (NHEL(I,  45),I=1,6) /-1,-1, 1,-1,-1, 1/
      DATA (NHEL(I,  46),I=1,6) /-1,-1, 1,-1,-1,-1/
      DATA (NHEL(I,  47),I=1,6) /-1,-1, 1,-1, 1, 1/
      DATA (NHEL(I,  48),I=1,6) /-1,-1, 1,-1, 1,-1/
      DATA (NHEL(I,  49),I=1,6) /-1, 1,-1, 1,-1, 1/
      DATA (NHEL(I,  50),I=1,6) /-1, 1,-1, 1,-1,-1/
      DATA (NHEL(I,  51),I=1,6) /-1, 1,-1, 1, 1, 1/
      DATA (NHEL(I,  52),I=1,6) /-1, 1,-1, 1, 1,-1/
      DATA (NHEL(I,  53),I=1,6) /-1, 1,-1,-1,-1, 1/
      DATA (NHEL(I,  54),I=1,6) /-1, 1,-1,-1,-1,-1/
      DATA (NHEL(I,  55),I=1,6) /-1, 1,-1,-1, 1, 1/
      DATA (NHEL(I,  56),I=1,6) /-1, 1,-1,-1, 1,-1/
      DATA (NHEL(I,  57),I=1,6) /-1, 1, 1, 1,-1, 1/
      DATA (NHEL(I,  58),I=1,6) /-1, 1, 1, 1,-1,-1/
      DATA (NHEL(I,  59),I=1,6) /-1, 1, 1, 1, 1, 1/
      DATA (NHEL(I,  60),I=1,6) /-1, 1, 1, 1, 1,-1/
      DATA (NHEL(I,  61),I=1,6) /-1, 1, 1,-1,-1, 1/
      DATA (NHEL(I,  62),I=1,6) /-1, 1, 1,-1,-1,-1/
      DATA (NHEL(I,  63),I=1,6) /-1, 1, 1,-1, 1, 1/
      DATA (NHEL(I,  64),I=1,6) /-1, 1, 1,-1, 1,-1/
      COMMON/PROCESS_NHEL/NHEL

      INTEGER USERHEL
      DATA USERHEL/-1/
      COMMON/HELUSERCHOICE/USERHEL

      INTEGER POLARIZATIONS(0:NEXTERNAL,0:5)
      COMMON/BORN_BEAM_POL/POLARIZATIONS
      DATA ((POLARIZATIONS(I,J),I=0,NEXTERNAL),J=0,5)/NPOLENTRIES*-1/

C     
C     FUNCTIONS
C     
      LOGICAL IS_BORN_HEL_SELECTED

C     ----------
C     BEGIN CODE
C     ----------
      NTRY=NTRY+1
      DO IHEL=1,NEXTERNAL
        JC(IHEL) = +1
      ENDDO
      DO I=1,NSQAMPSO
        ANS(I) = 0D0
      ENDDO
C     When spin-2 particles are involved, the Helicity filtering is
C      dangerous for the 2->1 topology.
C     This is because depending on the MC setup the initial PS points
C      have back-to-back initial states
C     for which some of the spin-2 helicity configurations are zero.
C      But they are no longer zero
C     if the point is boosted on the z-axis. Remember that HELAS
C      helicity amplitudes are no longer
C     lorentz invariant with expternal spin-2 particles (only the
C      helicity sum is).
C     For this reason, we simply remove the filterin when there is
C      only three external particles.
      IF (NEXTERNAL.LE.3) THEN
        DO IHEL=1,NCOMB
          GOODHEL(IHEL)=.TRUE.
        ENDDO
      ENDIF
      DO IHEL=1,NCOMB
        IF (USERHEL.EQ.-1.OR.USERHEL.EQ.IHEL) THEN
          IF (GOODHEL(IHEL) .OR. NTRY .LT. 2 .OR.USERHEL.NE.-1) THEN
            IF(NTRY.GE.2.AND.POLARIZATIONS(0,0).NE.
     $       -1.AND.(.NOT.IS_BORN_HEL_SELECTED(IHEL))) THEN
              CYCLE
            ENDIF
            CALL MATRIX(P ,NHEL(1,IHEL),JC(1), T)
            BUFF=0D0
            DO I=1,NSQAMPSO
              IF(POLARIZATIONS(0,0).EQ.-1.OR.IS_BORN_HEL_SELECTED(IHEL)
     $         ) THEN
                ANS(I)=ANS(I)+T(I)
              ENDIF
              BUFF=BUFF+T(I)
            ENDDO
            IF (BUFF .NE. 0D0 .AND. .NOT.    GOODHEL(IHEL)) THEN
              GOODHEL(IHEL)=.TRUE.
            ENDIF
          ENDIF
        ENDIF
      ENDDO
      ANS(0)=0.0D0
      DO I=1,NSQAMPSO
        ANS(I)=ANS(I)/DBLE(IDEN)
        IF (CHOSEN_SO_CONFIGS(I)) THEN
          ANS(0)=ANS(0)+ANS(I)
        ENDIF
      ENDDO
      IF(USERHEL.NE.-1) THEN
        DO I=0,NSQAMPSO
          ANS(I)=ANS(I)*HELAVGFACTOR
        ENDDO
      ELSE
        DO J=1,NINITIAL
          IF (POLARIZATIONS(J,0).NE.-1) THEN
            DO I=0,NSQAMPSO
              ANS(I)=ANS(I)*BEAMS_HELAVGFACTOR(J)
              ANS(I)=ANS(I)/POLARIZATIONS(J,0)
            ENDDO
          ENDIF
        ENDDO
      ENDIF
      END

      SUBROUTINE SMATRIXHEL_SPLITORDERS(P,HEL,ANS)
      IMPLICIT NONE
C     
C     CONSTANT
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=6)
      INTEGER                 NCOMB
      PARAMETER (             NCOMB=64)
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL),ANS(0:NSQAMPSO)
      INTEGER HEL
C     
C     GLOBAL VARIABLES
C     
      INTEGER USERHEL
      COMMON/HELUSERCHOICE/USERHEL
C     ----------
C     BEGIN CODE
C     ----------
      USERHEL=HEL
      CALL SMATRIX_SPLITORDERS(P,ANS)
      USERHEL=-1

      END

      SUBROUTINE MATRIX(P,NHEL,IC,RES)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Returns amplitude squared summed/avg over colors
C     for the point with external lines W(0:6,NEXTERNAL)
C     
C     Process: u u~ > u u~ u u~ QED^2<=6
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NGRAPHS
      PARAMETER (NGRAPHS=42)
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=6)
      INTEGER    NWAVEFUNCS, NCOLOR
      PARAMETER (NWAVEFUNCS=16, NCOLOR=6)
      INTEGER NAMPSO, NSQAMPSO
      PARAMETER (NAMPSO=1, NSQAMPSO=1)
      REAL*8     ZERO
      PARAMETER (ZERO=0D0)
      COMPLEX*16 IMAG1
      PARAMETER (IMAG1=(0D0,1D0))
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL)
      INTEGER NHEL(NEXTERNAL), IC(NEXTERNAL)
      REAL*8 RES(NSQAMPSO)
C     
C     LOCAL VARIABLES 
C     
      INTEGER I,J,M,N
      COMPLEX*16 ZTEMP
      REAL*8 CF(NCOLOR,NCOLOR)
      COMPLEX*16 AMP(NGRAPHS)
      COMPLEX*16 JAMP(NCOLOR,NAMPSO)
      COMPLEX*16 TMP_JAMP(55)
      COMPLEX*16 W(20,NWAVEFUNCS)
      COMPLEX*16 DUM0,DUM1
      DATA DUM0, DUM1/(0D0, 0D0), (1D0, 0D0)/
C     
C     FUNCTION
C     
      INTEGER SQSOINDEX
C     
C     GLOBAL VARIABLES
C     
      INCLUDE 'coupl.inc'
C     
C     COLOR DATA
C     
      DATA (CF(I,  1),I=  1,  6) /2.700000000000000D+01
     $ ,9.000000000000000D+00,9.000000000000000D+00,3.000000000000000D
     $ +00,3.000000000000000D+00,9.000000000000000D+00/
C     1 T(2,1) T(3,4) T(5,6)
      DATA (CF(I,  2),I=  1,  6) /9.000000000000000D+00
     $ ,2.700000000000000D+01,3.000000000000000D+00,9.000000000000000D
     $ +00,9.000000000000000D+00,3.000000000000000D+00/
C     1 T(2,1) T(3,6) T(5,4)
      DATA (CF(I,  3),I=  1,  6) /9.000000000000000D+00
     $ ,3.000000000000000D+00,2.700000000000000D+01,9.000000000000000D
     $ +00,9.000000000000000D+00,3.000000000000000D+00/
C     1 T(2,4) T(3,1) T(5,6)
      DATA (CF(I,  4),I=  1,  6) /3.000000000000000D+00
     $ ,9.000000000000000D+00,9.000000000000000D+00,2.700000000000000D
     $ +01,3.000000000000000D+00,9.000000000000000D+00/
C     1 T(2,4) T(3,6) T(5,1)
      DATA (CF(I,  5),I=  1,  6) /3.000000000000000D+00
     $ ,9.000000000000000D+00,9.000000000000000D+00,3.000000000000000D
     $ +00,2.700000000000000D+01,9.000000000000000D+00/
C     1 T(2,6) T(3,1) T(5,4)
      DATA (CF(I,  6),I=  1,  6) /9.000000000000000D+00
     $ ,3.000000000000000D+00,3.000000000000000D+00,9.000000000000000D
     $ +00,9.000000000000000D+00,2.700000000000000D+01/
C     1 T(2,6) T(3,4) T(5,1)
C     ----------
C     BEGIN CODE
C     ----------
      CALL IXXXXX(P(0,1),ZERO,NHEL(1),+1*IC(1),W(1,1))
      CALL OXXXXX(P(0,2),ZERO,NHEL(2),-1*IC(2),W(1,2))
      CALL OXXXXX(P(0,3),ZERO,NHEL(3),+1*IC(3),W(1,3))
      CALL IXXXXX(P(0,4),ZERO,NHEL(4),-1*IC(4),W(1,4))
      CALL OXXXXX(P(0,5),ZERO,NHEL(5),+1*IC(5),W(1,5))
      CALL IXXXXX(P(0,6),ZERO,NHEL(6),-1*IC(6),W(1,6))
      CALL JIOXXX(W(1,1),W(1,2),GG,ZERO,ZERO,W(1,7))
      CALL JIOXXX(W(1,4),W(1,3),GG,ZERO,ZERO,W(1,8))
      CALL FVOXXX(W(1,5),W(1,7),GG,ZERO,ZERO,W(1,9))
C     Amplitude(s) for diagram number 1
      CALL IOVXXX(W(1,6),W(1,9),W(1,8),GG,AMP(1))
      CALL FVIXXX(W(1,6),W(1,7),GG,ZERO,ZERO,W(1,10))
C     Amplitude(s) for diagram number 2
      CALL IOVXXX(W(1,10),W(1,5),W(1,8),GG,AMP(2))
      CALL JIOXXX(W(1,6),W(1,5),GG,ZERO,ZERO,W(1,11))
C     Amplitude(s) for diagram number 3
      CALL VVVXXX(W(1,7),W(1,8),W(1,11),GG,AMP(3))
      CALL JIOXXX(W(1,6),W(1,3),GG,ZERO,ZERO,W(1,12))
      CALL FVIXXX(W(1,4),W(1,7),GG,ZERO,ZERO,W(1,13))
C     Amplitude(s) for diagram number 4
      CALL IOVXXX(W(1,13),W(1,5),W(1,12),GG,AMP(4))
C     Amplitude(s) for diagram number 5
      CALL IOVXXX(W(1,4),W(1,9),W(1,12),GG,AMP(5))
      CALL JIOXXX(W(1,4),W(1,5),GG,ZERO,ZERO,W(1,9))
C     Amplitude(s) for diagram number 6
      CALL VVVXXX(W(1,7),W(1,12),W(1,9),GG,AMP(6))
      CALL FVOXXX(W(1,3),W(1,7),GG,ZERO,ZERO,W(1,14))
C     Amplitude(s) for diagram number 7
      CALL IOVXXX(W(1,6),W(1,14),W(1,9),GG,AMP(7))
C     Amplitude(s) for diagram number 8
      CALL IOVXXX(W(1,10),W(1,3),W(1,9),GG,AMP(8))
C     Amplitude(s) for diagram number 9
      CALL IOVXXX(W(1,4),W(1,14),W(1,11),GG,AMP(9))
C     Amplitude(s) for diagram number 10
      CALL IOVXXX(W(1,13),W(1,3),W(1,11),GG,AMP(10))
      CALL JIOXXX(W(1,1),W(1,3),GG,ZERO,ZERO,W(1,13))
      CALL JIOXXX(W(1,4),W(1,2),GG,ZERO,ZERO,W(1,14))
      CALL FVOXXX(W(1,5),W(1,13),GG,ZERO,ZERO,W(1,10))
C     Amplitude(s) for diagram number 11
      CALL IOVXXX(W(1,6),W(1,10),W(1,14),GG,AMP(11))
      CALL FVIXXX(W(1,6),W(1,13),GG,ZERO,ZERO,W(1,7))
C     Amplitude(s) for diagram number 12
      CALL IOVXXX(W(1,7),W(1,5),W(1,14),GG,AMP(12))
C     Amplitude(s) for diagram number 13
      CALL VVVXXX(W(1,13),W(1,14),W(1,11),GG,AMP(13))
      CALL JIOXXX(W(1,6),W(1,2),GG,ZERO,ZERO,W(1,15))
      CALL FVIXXX(W(1,4),W(1,13),GG,ZERO,ZERO,W(1,16))
C     Amplitude(s) for diagram number 14
      CALL IOVXXX(W(1,16),W(1,5),W(1,15),GG,AMP(14))
C     Amplitude(s) for diagram number 15
      CALL IOVXXX(W(1,4),W(1,10),W(1,15),GG,AMP(15))
C     Amplitude(s) for diagram number 16
      CALL VVVXXX(W(1,13),W(1,15),W(1,9),GG,AMP(16))
      CALL FVOXXX(W(1,2),W(1,13),GG,ZERO,ZERO,W(1,10))
C     Amplitude(s) for diagram number 17
      CALL IOVXXX(W(1,6),W(1,10),W(1,9),GG,AMP(17))
C     Amplitude(s) for diagram number 18
      CALL IOVXXX(W(1,7),W(1,2),W(1,9),GG,AMP(18))
C     Amplitude(s) for diagram number 19
      CALL IOVXXX(W(1,4),W(1,10),W(1,11),GG,AMP(19))
C     Amplitude(s) for diagram number 20
      CALL IOVXXX(W(1,16),W(1,2),W(1,11),GG,AMP(20))
      CALL JIOXXX(W(1,1),W(1,5),GG,ZERO,ZERO,W(1,16))
      CALL FVOXXX(W(1,3),W(1,16),GG,ZERO,ZERO,W(1,10))
C     Amplitude(s) for diagram number 21
      CALL IOVXXX(W(1,6),W(1,10),W(1,14),GG,AMP(21))
      CALL FVIXXX(W(1,6),W(1,16),GG,ZERO,ZERO,W(1,7))
C     Amplitude(s) for diagram number 22
      CALL IOVXXX(W(1,7),W(1,3),W(1,14),GG,AMP(22))
C     Amplitude(s) for diagram number 23
      CALL VVVXXX(W(1,16),W(1,14),W(1,12),GG,AMP(23))
C     Amplitude(s) for diagram number 24
      CALL IOVXXX(W(1,4),W(1,10),W(1,15),GG,AMP(24))
      CALL FVIXXX(W(1,4),W(1,16),GG,ZERO,ZERO,W(1,10))
C     Amplitude(s) for diagram number 25
      CALL IOVXXX(W(1,10),W(1,3),W(1,15),GG,AMP(25))
C     Amplitude(s) for diagram number 26
      CALL VVVXXX(W(1,16),W(1,15),W(1,8),GG,AMP(26))
      CALL FVOXXX(W(1,2),W(1,16),GG,ZERO,ZERO,W(1,13))
C     Amplitude(s) for diagram number 27
      CALL IOVXXX(W(1,6),W(1,13),W(1,8),GG,AMP(27))
C     Amplitude(s) for diagram number 28
      CALL IOVXXX(W(1,7),W(1,2),W(1,8),GG,AMP(28))
C     Amplitude(s) for diagram number 29
      CALL IOVXXX(W(1,4),W(1,13),W(1,12),GG,AMP(29))
C     Amplitude(s) for diagram number 30
      CALL IOVXXX(W(1,10),W(1,2),W(1,12),GG,AMP(30))
      CALL FVIXXX(W(1,1),W(1,14),GG,ZERO,ZERO,W(1,10))
C     Amplitude(s) for diagram number 31
      CALL IOVXXX(W(1,10),W(1,5),W(1,12),GG,AMP(31))
      CALL FVIXXX(W(1,1),W(1,12),GG,ZERO,ZERO,W(1,13))
C     Amplitude(s) for diagram number 32
      CALL IOVXXX(W(1,13),W(1,5),W(1,14),GG,AMP(32))
C     Amplitude(s) for diagram number 33
      CALL IOVXXX(W(1,10),W(1,3),W(1,11),GG,AMP(33))
      CALL FVIXXX(W(1,1),W(1,11),GG,ZERO,ZERO,W(1,10))
C     Amplitude(s) for diagram number 34
      CALL IOVXXX(W(1,10),W(1,3),W(1,14),GG,AMP(34))
      CALL FVIXXX(W(1,1),W(1,15),GG,ZERO,ZERO,W(1,14))
C     Amplitude(s) for diagram number 35
      CALL IOVXXX(W(1,14),W(1,5),W(1,8),GG,AMP(35))
      CALL FVIXXX(W(1,1),W(1,8),GG,ZERO,ZERO,W(1,4))
C     Amplitude(s) for diagram number 36
      CALL IOVXXX(W(1,4),W(1,5),W(1,15),GG,AMP(36))
C     Amplitude(s) for diagram number 37
      CALL IOVXXX(W(1,14),W(1,3),W(1,9),GG,AMP(37))
      CALL FVIXXX(W(1,1),W(1,9),GG,ZERO,ZERO,W(1,14))
C     Amplitude(s) for diagram number 38
      CALL IOVXXX(W(1,14),W(1,3),W(1,15),GG,AMP(38))
C     Amplitude(s) for diagram number 39
      CALL IOVXXX(W(1,4),W(1,2),W(1,11),GG,AMP(39))
C     Amplitude(s) for diagram number 40
      CALL IOVXXX(W(1,10),W(1,2),W(1,8),GG,AMP(40))
C     Amplitude(s) for diagram number 41
      CALL IOVXXX(W(1,13),W(1,2),W(1,9),GG,AMP(41))
C     Amplitude(s) for diagram number 42
      CALL IOVXXX(W(1,14),W(1,2),W(1,12),GG,AMP(42))
C     JAMPs contributing to orders QCD=4 QED=0
      TMP_JAMP(39) = AMP(39) +  AMP(40)  ! used 3 times
      TMP_JAMP(38) = AMP(37) +  AMP(38)  ! used 3 times
      TMP_JAMP(37) = AMP(35) +  AMP(36)  ! used 3 times
      TMP_JAMP(36) = AMP(29) +  AMP(37)  ! used 3 times
      TMP_JAMP(35) = AMP(29) +  AMP(30)  ! used 3 times
      TMP_JAMP(34) = AMP(28) +  AMP(36)  ! used 3 times
      TMP_JAMP(33) = AMP(27) +  AMP(35)  ! used 3 times
      TMP_JAMP(32) = AMP(27) +  AMP(28)  ! used 3 times
      TMP_JAMP(31) = AMP(25) +  AMP(35)  ! used 3 times
      TMP_JAMP(30) = AMP(25) +  AMP(27)  ! used 3 times
      TMP_JAMP(29) = AMP(24) +  AMP(25)  ! used 3 times
      TMP_JAMP(28) = AMP(21) +  AMP(22)  ! used 3 times
      TMP_JAMP(27) = AMP(20) +  AMP(34)  ! used 3 times
      TMP_JAMP(26) = AMP(14) +  AMP(22)  ! used 3 times
      TMP_JAMP(25) = AMP(14) +  AMP(15)  ! used 3 times
      TMP_JAMP(24) = AMP(11) +  AMP(34)  ! used 3 times
      TMP_JAMP(23) = AMP(11) +  AMP(20)  ! used 3 times
      TMP_JAMP(22) = AMP(5) +  AMP(8)  ! used 3 times
      TMP_JAMP(21) = AMP(1) +  AMP(2)  ! used 3 times
      TMP_JAMP(20) = AMP(41) +  AMP(42)  ! used 3 times
      TMP_JAMP(19) = AMP(30) +  AMP(32)  ! used 3 times
      TMP_JAMP(18) = AMP(24) +  AMP(41)  ! used 3 times
      TMP_JAMP(17) = AMP(21) +  AMP(32)  ! used 3 times
      TMP_JAMP(16) = AMP(19) +  AMP(20)  ! used 3 times
      TMP_JAMP(15) = AMP(18) +  AMP(38)  ! used 3 times
      TMP_JAMP(14) = AMP(15) +  AMP(18)  ! used 3 times
      TMP_JAMP(13) = AMP(14) +  AMP(17)  ! used 3 times
      TMP_JAMP(12) = AMP(12) +  AMP(25)  ! used 3 times
      TMP_JAMP(11) = AMP(11) +  AMP(12)  ! used 3 times
      TMP_JAMP(10) = AMP(7) +  AMP(8)  ! used 3 times
      TMP_JAMP(9) = AMP(2) +  AMP(9)  ! used 3 times
      TMP_JAMP(8) = AMP(22) +  AMP(31)  ! used 3 times
      TMP_JAMP(7) = AMP(12) +  AMP(33)  ! used 3 times
      TMP_JAMP(6) = AMP(4) +  AMP(5)  ! used 3 times
      TMP_JAMP(5) = AMP(1) +  AMP(10)  ! used 3 times
      TMP_JAMP(4) = AMP(19) +  AMP(33)  ! used 3 times
      TMP_JAMP(3) = AMP(17) +  AMP(31)  ! used 3 times
      TMP_JAMP(2) = AMP(9) +  AMP(10)  ! used 3 times
      TMP_JAMP(1) = AMP(4) +  AMP(7)  ! used 3 times
      TMP_JAMP(52) = TMP_JAMP(38) + (3.000000000000000D+00) * AMP(42)  ! used 2 times
      TMP_JAMP(51) = TMP_JAMP(37) +  TMP_JAMP(32)  ! used 2 times
      TMP_JAMP(50) = TMP_JAMP(36) + (3.333333333333333D-01) *
     $  TMP_JAMP(22)  ! used 2 times
      TMP_JAMP(49) = TMP_JAMP(35) + (3.000000000000000D+00) * AMP(42)  ! used 2 times
      TMP_JAMP(48) = TMP_JAMP(27) + (3.000000000000000D+00) *
     $  TMP_JAMP(26)  ! used 2 times
      TMP_JAMP(47) = TMP_JAMP(22) + (3.333333333333333D-01) *
     $  TMP_JAMP(21)  ! used 2 times
      TMP_JAMP(46) = TMP_JAMP(18) + (3.333333333333333D-01) *
     $  TMP_JAMP(14)  ! used 2 times
      TMP_JAMP(45) = TMP_JAMP(18) + (3.333333333333333D-01) *
     $  TMP_JAMP(17)  ! used 2 times
      TMP_JAMP(44) = TMP_JAMP(17) + (3.333333333333333D-01) *
     $  TMP_JAMP(11)  ! used 2 times
      TMP_JAMP(43) = TMP_JAMP(4) + (3.000000000000000D+00) *
     $  TMP_JAMP(3)  ! used 2 times
      TMP_JAMP(42) = TMP_JAMP(4) + (3.333333333333333D-01) *
     $  TMP_JAMP(2)  ! used 2 times
      TMP_JAMP(41) = TMP_JAMP(3) + (3.333333333333333D-01) *
     $  TMP_JAMP(1)  ! used 2 times
      TMP_JAMP(40) = TMP_JAMP(2) + (3.000000000000000D+00) *
     $  TMP_JAMP(1)  ! used 2 times
      TMP_JAMP(55) = TMP_JAMP(48) +  TMP_JAMP(43)  ! used 2 times
      TMP_JAMP(54) = TMP_JAMP(47) + (3.333333333333333D-01) *
     $  TMP_JAMP(39)  ! used 2 times
      TMP_JAMP(53) = TMP_JAMP(40) +  TMP_JAMP(39)  ! used 2 times
      JAMP(1,1) = (-2.500000000000000D-01)*AMP(16)+(
     $ -2.500000000000000D-01)*AMP(23)+(2.500000000000000D-01)
     $ *TMP_JAMP(36)+(8.333333333333333D-02)*TMP_JAMP(47)
     $ +(8.333333333333333D-02)*TMP_JAMP(51)+(2.777777777777778D-02)
     $ *TMP_JAMP(53)+(8.333333333333333D-02)*TMP_JAMP(55)
      JAMP(2,1) = (2.500000000000000D-01)*AMP(13)+(2.500000000000000D
     $ -01)*AMP(26)+(-2.500000000000000D-01)*TMP_JAMP(12)+(
     $ -8.333333333333333D-02)*TMP_JAMP(15)+(-8.333333333333333D-02)
     $ *TMP_JAMP(19)+(-2.777777777777778D-02)*TMP_JAMP(20)+(
     $ -8.333333333333333D-02)*TMP_JAMP(21)+(-2.500000000000000D-01)
     $ *TMP_JAMP(33)+(-8.333333333333333D-02)*TMP_JAMP(41)+(
     $ -2.500000000000000D-01)*TMP_JAMP(42)+(-8.333333333333333D-02)
     $ *TMP_JAMP(50)
      JAMP(3,1) = (2.500000000000000D-01)*AMP(6)+(-2.500000000000000D
     $ -01)*AMP(26)+(-2.500000000000000D-01)*TMP_JAMP(34)+(
     $ -8.333333333333333D-02)*TMP_JAMP(44)+(-2.500000000000000D-01)
     $ *TMP_JAMP(46)+(-8.333333333333333D-02)*TMP_JAMP(53)+(
     $ -2.777777777777778D-02)*TMP_JAMP(55)
      JAMP(4,1) = (2.500000000000000D-01)*AMP(3)+(2.500000000000000D
     $ -01)*AMP(16)+(8.333333333333333D-02)*AMP(28)
     $ +(2.500000000000000D-01)*AMP(38)+(2.500000000000000D-01)*AMP(40)
     $ +(2.500000000000000D-01)*TMP_JAMP(5)+(8.333333333333333D-02)
     $ *TMP_JAMP(6)+(8.333333333333333D-02)*TMP_JAMP(7)
     $ +(2.777777777777778D-02)*TMP_JAMP(8)+(2.500000000000000D-01)
     $ *TMP_JAMP(14)+(8.333333333333333D-02)*TMP_JAMP(24)
     $ +(8.333333333333333D-02)*TMP_JAMP(30)+(8.333333333333333D-02)
     $ *TMP_JAMP(45)+(2.777777777777778D-02)*TMP_JAMP(49)
      JAMP(5,1) = (-2.500000000000000D-01)*AMP(3)+(2.500000000000000D
     $ -01)*AMP(23)+(2.500000000000000D-01)*AMP(30)
     $ +(8.333333333333333D-02)*AMP(36)+(2.500000000000000D-01)*AMP(39)
     $ +(2.500000000000000D-01)*TMP_JAMP(9)+(8.333333333333333D-02)
     $ *TMP_JAMP(10)+(2.777777777777778D-02)*TMP_JAMP(13)
     $ +(8.333333333333333D-02)*TMP_JAMP(16)+(8.333333333333333D-02)
     $ *TMP_JAMP(31)+(2.500000000000000D-01)*TMP_JAMP(44)
     $ +(8.333333333333333D-02)*TMP_JAMP(46)+(2.777777777777778D-02)
     $ *TMP_JAMP(52)
      JAMP(6,1) = (-2.500000000000000D-01)*AMP(6)+(-2.500000000000000D
     $ -01)*AMP(13)+(-2.500000000000000D-01)*AMP(34)+(
     $ -2.500000000000000D-01)*TMP_JAMP(23)+(-8.333333333333333D-02)
     $ *TMP_JAMP(25)+(-8.333333333333333D-02)*TMP_JAMP(28)+(
     $ -2.777777777777778D-02)*TMP_JAMP(29)+(-8.333333333333333D-02)
     $ *TMP_JAMP(38)+(-8.333333333333333D-02)*TMP_JAMP(49)+(
     $ -2.777777777777778D-02)*TMP_JAMP(51)+(-2.500000000000000D-01)
     $ *TMP_JAMP(54)

      RES = 0.D0
      DO M = 1, NAMPSO
        DO I = 1, NCOLOR
          ZTEMP = (0.D0,0.D0)
          DO J = 1, NCOLOR
            ZTEMP = ZTEMP + CF(J,I)*JAMP(J,M)
          ENDDO
          DO N = 1, NAMPSO
            RES(SQSOINDEX(M,N)) = RES(SQSOINDEX(M,N)) + ZTEMP
     $       *DCONJG(JAMP(I,N))
          ENDDO
        ENDDO
      ENDDO

      END

      SUBROUTINE GET_VALUE(P, ALPHAS, NHEL ,ANS)
      IMPLICIT NONE
C     
C     CONSTANT
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=6)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL),ANS
      INTEGER NHEL
      DOUBLE PRECISION ALPHAS
      REAL*8 PI
CF2PY INTENT(OUT) :: ANS
CF2PY INTENT(IN) :: NHEL
CF2PY INTENT(IN) :: P(0:3,NEXTERNAL)
CF2PY INTENT(IN) :: ALPHAS
C     ROUTINE FOR F2PY to read the benchmark point.    
C     the include file with the values of the parameters and masses 
      INCLUDE 'coupl.inc'

      PI = 3.141592653589793D0
      G = 2* DSQRT(ALPHAS*PI)
      CALL UPDATE_AS_PARAM()
      IF (NHEL.NE.0) THEN
        CALL SMATRIXHEL(P, NHEL, ANS)
      ELSE
        CALL SMATRIX(P, ANS)
      ENDIF
      RETURN
      END

      SUBROUTINE INITIALISEMODEL(PATH)
C     ROUTINE FOR F2PY to read the benchmark point.    
      IMPLICIT NONE
      CHARACTER*512 PATH
CF2PY INTENT(IN) :: PATH
      CALL SETPARA(PATH)  !first call to setup the paramaters    
      RETURN
      END

      LOGICAL FUNCTION IS_BORN_HEL_SELECTED(HELID)
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=6)
      INTEGER    NCOMB
      PARAMETER (NCOMB=64)
C     
C     ARGUMENTS
C     
      INTEGER HELID
C     
C     LOCALS
C     
      INTEGER I,J
      LOGICAL FOUNDIT
C     
C     GLOBALS
C     
      INTEGER HELC(NEXTERNAL,NCOMB)
      COMMON/PROCESS_NHEL/HELC

      INTEGER POLARIZATIONS(0:NEXTERNAL,0:5)
      COMMON/BORN_BEAM_POL/POLARIZATIONS
C     ----------
C     BEGIN CODE
C     ----------

      IS_BORN_HEL_SELECTED = .TRUE.
      IF (POLARIZATIONS(0,0).EQ.-1) THEN
        RETURN
      ENDIF

      DO I=1,NEXTERNAL
        IF (POLARIZATIONS(I,0).EQ.-1) THEN
          CYCLE
        ENDIF
        FOUNDIT = .FALSE.
        DO J=1,POLARIZATIONS(I,0)
          IF (HELC(I,HELID).EQ.POLARIZATIONS(I,J)) THEN
            FOUNDIT = .TRUE.
            EXIT
          ENDIF
        ENDDO
        IF(.NOT.FOUNDIT) THEN
          IS_BORN_HEL_SELECTED = .FALSE.
          RETURN
        ENDIF
      ENDDO

      RETURN
      END


C     Set of functions to handle the array indices of the split orders


      INTEGER FUNCTION SQSOINDEX(ORDERINDEXA, ORDERINDEXB)
C     
C     This functions plays the role of the interference matrix. It can
C      be hardcoded or 
C     made more elegant using hashtables if its execution speed ever
C      becomes a relevant
C     factor. From two split order indices, it return the
C      corresponding index in the squared 
C     order canonical ordering.
C     
C     CONSTANTS
C     

      INTEGER    NSO, NSQUAREDSO, NAMPSO
      PARAMETER (NSO=2, NSQUAREDSO=1, NAMPSO=1)
C     
C     ARGUMENTS
C     
      INTEGER ORDERINDEXA, ORDERINDEXB
C     
C     LOCAL VARIABLES
C     
      INTEGER I, SQORDERS(NSO)
      INTEGER AMPSPLITORDERS(NAMPSO,NSO)
      DATA (AMPSPLITORDERS(  1,I),I=  1,  2) /    4,    0/
      COMMON/AMPSPLITORDERS/AMPSPLITORDERS
C     
C     FUNCTION
C     
      INTEGER SOINDEX_FOR_SQUARED_ORDERS
C     
C     BEGIN CODE
C     
      DO I=1,NSO
        SQORDERS(I)=AMPSPLITORDERS(ORDERINDEXA,I)
     $   +AMPSPLITORDERS(ORDERINDEXB,I)
      ENDDO
      SQSOINDEX=SOINDEX_FOR_SQUARED_ORDERS(SQORDERS)
      END

      INTEGER FUNCTION SOINDEX_FOR_SQUARED_ORDERS(ORDERS)
C     
C     This functions returns the integer index identifying the squared
C      split orders list passed in argument which corresponds to the
C      values of the following list of couplings (and in this order).
C     ['QCD', 'QED']
C     
C     CONSTANTS
C     
      INTEGER    NSO, NSQSO, NAMPSO
      PARAMETER (NSO=2, NSQSO=1, NAMPSO=1)
C     
C     ARGUMENTS
C     
      INTEGER ORDERS(NSO)
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J
      INTEGER SQSPLITORDERS(NSQSO,NSO)
      DATA (SQSPLITORDERS(  1,I),I=  1,  2) /    8,    0/
      COMMON/SQPLITORDERS/SQPLITORDERS
C     
C     BEGIN CODE
C     
      DO I=1,NSQSO
        DO J=1,NSO
          IF (ORDERS(J).NE.SQSPLITORDERS(I,J)) GOTO 1009
        ENDDO
        SOINDEX_FOR_SQUARED_ORDERS = I
        RETURN
 1009   CONTINUE
      ENDDO

      WRITE(*,*) 'ERROR:: Stopping in function'
      WRITE(*,*) 'SOINDEX_FOR_SQUARED_ORDERS'
      WRITE(*,*) 'Could not find squared orders ',(ORDERS(I),I=1,NSO)
      STOP

      END

      SUBROUTINE GET_NSQSO_BORN(NSQSO)
C     
C     Simple subroutine returning the number of squared split order
C     contributions returned when calling smatrix_split_orders 
C     

      INTEGER    NSQUAREDSO
      PARAMETER  (NSQUAREDSO=1)

      INTEGER NSQSO

      NSQSO=NSQUAREDSO

      END

C     This is the inverse subroutine of SOINDEX_FOR_SQUARED_ORDERS.
C      Not directly useful, but provided nonetheless.
      SUBROUTINE GET_SQUARED_ORDERS_FOR_SOINDEX(SOINDEX,ORDERS)
C     
C     This functions returns the orders identified by the squared
C      split order index in argument. Order values correspond to
C      following list of couplings (and in this order):
C     ['QCD', 'QED']
C     
C     CONSTANTS
C     
      INTEGER    NSO, NSQSO
      PARAMETER (NSO=2, NSQSO=1)
C     
C     ARGUMENTS
C     
      INTEGER SOINDEX, ORDERS(NSO)
C     
C     LOCAL VARIABLES
C     
      INTEGER I
      INTEGER SQPLITORDERS(NSQSO,NSO)
      COMMON/SQPLITORDERS/SQPLITORDERS
C     
C     BEGIN CODE
C     
      IF (SOINDEX.GT.0.AND.SOINDEX.LE.NSQSO) THEN
        DO I=1,NSO
          ORDERS(I) =  SQPLITORDERS(SOINDEX,I)
        ENDDO
        RETURN
      ENDIF

      WRITE(*,*) 'ERROR:: Stopping function'
     $ //' GET_SQUARED_ORDERS_FOR_SOINDEX'
      WRITE(*,*) 'Could not find squared orders index ',SOINDEX
      STOP

      END SUBROUTINE

C     This is the inverse subroutine of getting amplitude SO orders.
C      Not directly useful, but provided nonetheless.
      SUBROUTINE GET_ORDERS_FOR_AMPSOINDEX(SOINDEX,ORDERS)
C     
C     This functions returns the orders identified by the split order
C      index in argument. Order values correspond to following list of
C      couplings (and in this order):
C     ['QCD', 'QED']
C     
C     CONSTANTS
C     
      INTEGER    NSO, NAMPSO
      PARAMETER (NSO=2, NAMPSO=1)
C     
C     ARGUMENTS
C     
      INTEGER SOINDEX, ORDERS(NSO)
C     
C     LOCAL VARIABLES
C     
      INTEGER I
      INTEGER AMPSPLITORDERS(NAMPSO,NSO)
      COMMON/AMPSPLITORDERS/AMPSPLITORDERS
C     
C     BEGIN CODE
C     
      IF (SOINDEX.GT.0.AND.SOINDEX.LE.NAMPSO) THEN
        DO I=1,NSO
          ORDERS(I) =  AMPSPLITORDERS(SOINDEX,I)
        ENDDO
        RETURN
      ENDIF

      WRITE(*,*) 'ERROR:: Stopping function GET_ORDERS_FOR_AMPSOINDEX'
      WRITE(*,*) 'Could not find amplitude split orders index ',SOINDEX
      STOP

      END SUBROUTINE

C     This function is not directly useful, but included for
C      completeness
      INTEGER FUNCTION SOINDEX_FOR_AMPORDERS(ORDERS)
C     
C     This functions returns the integer index identifying the
C      amplitude split orders passed in argument which correspond to
C      the values of the following list of couplings (and in this
C      order):
C     ['QCD', 'QED']
C     
C     CONSTANTS
C     
      INTEGER    NSO, NAMPSO
      PARAMETER (NSO=2, NAMPSO=1)
C     
C     ARGUMENTS
C     
      INTEGER ORDERS(NSO)
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J
      INTEGER AMPSPLITORDERS(NAMPSO,NSO)
      COMMON/AMPSPLITORDERS/AMPSPLITORDERS
C     
C     BEGIN CODE
C     
      DO I=1,NAMPSO
        DO J=1,NSO
          IF (ORDERS(J).NE.AMPSPLITORDERS(I,J)) GOTO 1009
        ENDDO
        SOINDEX_FOR_AMPORDERS = I
        RETURN
 1009   CONTINUE
      ENDDO

      WRITE(*,*) 'ERROR:: Stopping function SOINDEX_FOR_AMPORDERS'
      WRITE(*,*) 'Could not find squared orders ',(ORDERS(I),I=1,NSO)
      STOP

      END

