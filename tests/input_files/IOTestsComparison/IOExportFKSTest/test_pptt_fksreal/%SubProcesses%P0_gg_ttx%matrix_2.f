      SUBROUTINE SMATRIX2(P,ANS_SUMMED)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     
C     Return the sum of the split orders which are required in
C      orders.inc (NLO_ORDERS)
C     
C     
C     Process: d~ g > t t~ d~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: s~ g > t t~ s~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: u~ g > t t~ u~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: c~ g > t t~ c~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     
C     
C     CONSTANTS
C     
      IMPLICIT NONE
      INTEGER    NEXTERNAL
      PARAMETER (NEXTERNAL=5)
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL), ANS_SUMMED
C     
C     VARIABLES
C     
      INTEGER I,J
      REAL*8 ANS(0:NSQAMPSO)
      LOGICAL KEEP_ORDER(NSQAMPSO), FIRSTTIME
      INCLUDE 'orders.inc'
      DATA KEEP_ORDER / NSQAMPSO*.TRUE. /
      DATA FIRSTTIME / .TRUE. /
      INTEGER AMP_ORDERS(NSPLITORDERS)
      DOUBLE PRECISION ANS_MAX, TINY
      PARAMETER (TINY = 1D-12)
      DOUBLE PRECISION       WGT_ME_BORN,WGT_ME_REAL
      COMMON /C_WGT_ME_TREE/ WGT_ME_BORN,WGT_ME_REAL
C     
C     FUNCTIONS
C     
      INTEGER GETORDPOWFROMINDEX2
      INTEGER ORDERS_TO_AMP_SPLIT_POS
C     
C     BEGIN CODE
C     

C     look for orders which match the nlo order constraint 

      IF (FIRSTTIME) THEN
        DO I = 1, NSQAMPSO
          DO J = 1, NSPLITORDERS
            IF(GETORDPOWFROMINDEX2(J, I) .GT. NLO_ORDERS(J)) THEN
              KEEP_ORDER(I) = .FALSE.
              EXIT
            ENDIF
          ENDDO
          IF (KEEP_ORDER(I)) THEN
            WRITE(*,*) 'REAL 2: keeping split order ', I
          ELSE
            WRITE(*,*) 'REAL 2: not keeping split order ', I
          ENDIF
        ENDDO
        FIRSTTIME = .FALSE.
      ENDIF

      CALL SMATRIX2_SPLITORDERS(P,ANS)
      ANS_SUMMED = 0D0
      ANS_MAX = 0D0

C     reset the amp_split array
      AMP_SPLIT(1:AMP_SPLIT_SIZE) = 0D0

      DO I = 1, NSQAMPSO
        ANS_MAX = MAX(DABS(ANS(I)),ANS_MAX)
      ENDDO

      DO I = 1, NSQAMPSO
        IF (KEEP_ORDER(I)) THEN
          ANS_SUMMED = ANS_SUMMED + ANS(I)
C         keep track of the separate pieces correspoinding to
C          different coupling combinations
          DO J = 1, NSPLITORDERS
            AMP_ORDERS(J) = GETORDPOWFROMINDEX2(J, I)
          ENDDO
          IF (ABS(ANS(I)).GT.ANS_MAX*TINY)
     $      AMP_SPLIT(ORDERS_TO_AMP_SPLIT_POS(AMP_ORDERS)) = ANS(I)
        ENDIF
      ENDDO

C     avoid fake non-zeros
      IF (DABS(ANS_SUMMED).LT.TINY*ANS_MAX) ANS_SUMMED=0D0

      WGT_ME_REAL = ANS_SUMMED

      END



      SUBROUTINE SMATRIX2_SPLITORDERS(P,ANS)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Returns amplitude squared summed/avg over colors
C     and helicities
C     for the point in phase space P(0:3,NEXTERNAL)
C     
C     Process: d~ g > t t~ d~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: s~ g > t t~ s~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: u~ g > t t~ u~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: c~ g > t t~ c~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INCLUDE 'nexternal.inc'
      INTEGER     NCOMB
      PARAMETER ( NCOMB=32)
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL),ANS(0:NSQAMPSO)
C     
C     LOCAL VARIABLES 
C     
      INTEGER IHEL,IDEN,I,J,T_IDENT(NCOMB)
      REAL*8 T(0:NSQAMPSO),T_SAVE(NCOMB,0:NSQAMPSO)
      SAVE T_SAVE,T_IDENT
      INTEGER NHEL(NEXTERNAL,NCOMB)
      DATA (NHEL(I,   1),I=1,5) /-1,-1,-1, 1, 1/
      DATA (NHEL(I,   2),I=1,5) /-1,-1,-1, 1,-1/
      DATA (NHEL(I,   3),I=1,5) /-1,-1,-1,-1, 1/
      DATA (NHEL(I,   4),I=1,5) /-1,-1,-1,-1,-1/
      DATA (NHEL(I,   5),I=1,5) /-1,-1, 1, 1, 1/
      DATA (NHEL(I,   6),I=1,5) /-1,-1, 1, 1,-1/
      DATA (NHEL(I,   7),I=1,5) /-1,-1, 1,-1, 1/
      DATA (NHEL(I,   8),I=1,5) /-1,-1, 1,-1,-1/
      DATA (NHEL(I,   9),I=1,5) /-1, 1,-1, 1, 1/
      DATA (NHEL(I,  10),I=1,5) /-1, 1,-1, 1,-1/
      DATA (NHEL(I,  11),I=1,5) /-1, 1,-1,-1, 1/
      DATA (NHEL(I,  12),I=1,5) /-1, 1,-1,-1,-1/
      DATA (NHEL(I,  13),I=1,5) /-1, 1, 1, 1, 1/
      DATA (NHEL(I,  14),I=1,5) /-1, 1, 1, 1,-1/
      DATA (NHEL(I,  15),I=1,5) /-1, 1, 1,-1, 1/
      DATA (NHEL(I,  16),I=1,5) /-1, 1, 1,-1,-1/
      DATA (NHEL(I,  17),I=1,5) / 1,-1,-1, 1, 1/
      DATA (NHEL(I,  18),I=1,5) / 1,-1,-1, 1,-1/
      DATA (NHEL(I,  19),I=1,5) / 1,-1,-1,-1, 1/
      DATA (NHEL(I,  20),I=1,5) / 1,-1,-1,-1,-1/
      DATA (NHEL(I,  21),I=1,5) / 1,-1, 1, 1, 1/
      DATA (NHEL(I,  22),I=1,5) / 1,-1, 1, 1,-1/
      DATA (NHEL(I,  23),I=1,5) / 1,-1, 1,-1, 1/
      DATA (NHEL(I,  24),I=1,5) / 1,-1, 1,-1,-1/
      DATA (NHEL(I,  25),I=1,5) / 1, 1,-1, 1, 1/
      DATA (NHEL(I,  26),I=1,5) / 1, 1,-1, 1,-1/
      DATA (NHEL(I,  27),I=1,5) / 1, 1,-1,-1, 1/
      DATA (NHEL(I,  28),I=1,5) / 1, 1,-1,-1,-1/
      DATA (NHEL(I,  29),I=1,5) / 1, 1, 1, 1, 1/
      DATA (NHEL(I,  30),I=1,5) / 1, 1, 1, 1,-1/
      DATA (NHEL(I,  31),I=1,5) / 1, 1, 1,-1, 1/
      DATA (NHEL(I,  32),I=1,5) / 1, 1, 1,-1,-1/
      LOGICAL GOODHEL(NCOMB)
      DATA GOODHEL/NCOMB*.FALSE./
      INTEGER NTRY
      DATA NTRY/0/
      DATA IDEN/96/
C     ----------
C     BEGIN CODE
C     ----------
      NTRY=NTRY+1
      DO I=0,NSQAMPSO
        ANS(I) = 0D0
      ENDDO
      DO IHEL=1,NCOMB
        IF (GOODHEL(IHEL) .OR. NTRY .LT. 2) THEN
          IF (NTRY.LT.2) THEN
C           for the first ps-point, check for helicities that give
C           identical matrix elements
            CALL MATRIX_2(P ,NHEL(1,IHEL),T)
            DO I=0,NSQAMPSO
              T_SAVE(IHEL,I)=T(I)
            ENDDO
            T_IDENT(IHEL)=-1
            DO I=1,IHEL-1
              IF (T(0).EQ.0D0) EXIT
              IF (T_SAVE(I,0).EQ.0D0) CYCLE
              DO J = 0, NSQAMPSO
                IF (ABS(T(J)/T_SAVE(I,J)-1D0) .GT. 1D-12) GOTO 444
              ENDDO
              T_IDENT(IHEL) = I
 444          CONTINUE
            ENDDO
          ELSE
            IF (T_IDENT(IHEL).GT.0) THEN
C             if two helicity states are identical, dont recompute
              DO I=0,NSQAMPSO
                T(I)=T_SAVE(T_IDENT(IHEL),I)
                T_SAVE(IHEL,I)=T(I)
              ENDDO
            ELSE
              CALL MATRIX_2(P ,NHEL(1,IHEL),T)
              DO I=0,NSQAMPSO
                T_SAVE(IHEL,I)=T(I)
              ENDDO
            ENDIF
          ENDIF
C         add to the sum of helicities
          DO I=1,NSQAMPSO  !keep loop from 1!!
            ANS(I)=ANS(I)+T(I)
          ENDDO
          IF (T(0) .NE. 0D0 .AND. .NOT. GOODHEL(IHEL)) THEN
            GOODHEL(IHEL)=.TRUE.
          ENDIF
        ENDIF
      ENDDO
      DO I=1,NSQAMPSO
        ANS(I)=ANS(I)/DBLE(IDEN)
        ANS(0)=ANS(0)+ANS(I)
      ENDDO
      END


      SUBROUTINE MATRIX_2(P,NHEL,RES)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     Returns amplitude squared summed/avg over colors
C     for the point with external lines W(0:6,NEXTERNAL)
C     
C     Process: d~ g > t t~ d~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: s~ g > t t~ s~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: u~ g > t t~ u~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     Process: c~ g > t t~ c~ [ real = QCD QED ] QCD^2<=6 QED^2<=0
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER    NGRAPHS
      PARAMETER (NGRAPHS=5)
      INTEGER    NWAVEFUNCS, NCOLOR
      PARAMETER (NWAVEFUNCS=8, NCOLOR=4)
      INTEGER NAMPSO, NSQAMPSO
      PARAMETER (NAMPSO=1, NSQAMPSO=1)
      REAL*8     ZERO
      PARAMETER (ZERO=0D0)
      COMPLEX*16 IMAG1
      PARAMETER (IMAG1=(0D0,1D0))
      INCLUDE 'nexternal.inc'
      INCLUDE 'coupl.inc'
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL)
      INTEGER NHEL(NEXTERNAL)
      REAL*8 RES(0:NSQAMPSO)
C     
C     LOCAL VARIABLES 
C     
      INTEGER I,J,M,N
      INTEGER IC(NEXTERNAL)
      DATA IC /NEXTERNAL*1/
      REAL*8  CF(NCOLOR,NCOLOR)
      COMPLEX*16 ZTEMP, AMP(NGRAPHS), JAMP(NCOLOR,NAMPSO), W(8
     $ ,NWAVEFUNCS)
      COMPLEX*16 TMP_JAMP(0)
C     
C     FUNCTION
C     
      INTEGER SQSOINDEX2
C     
C     COLOR DATA
C     
      DATA (CF(I,  1),I=  1,  4) /1.200000000000000D+01
     $ ,4.000000000000000D+00,0.000000000000000D+00,4.000000000000000D
     $ +00/
C     1 T(1,4) T(2,3,5)
      DATA (CF(I,  2),I=  1,  4) /4.000000000000000D+00
     $ ,1.200000000000000D+01,4.000000000000000D+00,0.000000000000000D
     $ +00/
C     1 T(1,5) T(2,3,4)
      DATA (CF(I,  3),I=  1,  4) /0.000000000000000D+00
     $ ,4.000000000000000D+00,1.200000000000000D+01,4.000000000000000D
     $ +00/
C     1 T(2,1,4) T(3,5)
      DATA (CF(I,  4),I=  1,  4) /4.000000000000000D+00
     $ ,0.000000000000000D+00,4.000000000000000D+00,1.200000000000000D
     $ +01/
C     1 T(2,1,5) T(3,4)
C     ----------
C     BEGIN CODE
C     ----------
      CALL OXXXXX(P(0,1),ZERO,NHEL(1),-1*IC(1),W(1,1))
      CALL VXXXXX(P(0,2),ZERO,NHEL(2),-1*IC(2),W(1,2))
      CALL OXXXXX(P(0,3),MDL_MT,NHEL(3),+1*IC(3),W(1,3))
      CALL IXXXXX(P(0,4),MDL_MT,NHEL(4),-1*IC(4),W(1,4))
      CALL IXXXXX(P(0,5),ZERO,NHEL(5),-1*IC(5),W(1,5))
      CALL FFV1_1(W(1,1),W(1,2),GC_11,ZERO,ZERO,W(1,6))
      CALL FFV1P0_3(W(1,4),W(1,3),GC_11,ZERO,ZERO,W(1,7))
C     Amplitude(s) for diagram number 1
      CALL FFV1_0(W(1,5),W(1,6),W(1,7),GC_11,AMP(1))
      CALL FFV1P0_3(W(1,5),W(1,1),GC_11,ZERO,ZERO,W(1,6))
      CALL FFV1_1(W(1,3),W(1,2),GC_11,MDL_MT,MDL_WT,W(1,8))
C     Amplitude(s) for diagram number 2
      CALL FFV1_0(W(1,4),W(1,8),W(1,6),GC_11,AMP(2))
      CALL FFV1_2(W(1,4),W(1,2),GC_11,MDL_MT,MDL_WT,W(1,8))
C     Amplitude(s) for diagram number 3
      CALL FFV1_0(W(1,8),W(1,3),W(1,6),GC_11,AMP(3))
C     Amplitude(s) for diagram number 4
      CALL VVV1_0(W(1,6),W(1,2),W(1,7),GC_10,AMP(4))
      CALL FFV1_2(W(1,5),W(1,2),GC_11,ZERO,ZERO,W(1,6))
C     Amplitude(s) for diagram number 5
      CALL FFV1_0(W(1,6),W(1,1),W(1,7),GC_11,AMP(5))
C     JAMPs contributing to orders QCD=3 QED=0
      JAMP(1,1) = (5.000000000000000D-01)*AMP(2)+((0.000000000000000D
     $ +00,5.000000000000000D-01))*AMP(4)+(5.000000000000000D-01)
     $ *AMP(5)
      JAMP(2,1) = (-1.666666666666667D-01)*AMP(2)+(-1.666666666666667D
     $ -01)*AMP(3)
      JAMP(3,1) = (5.000000000000000D-01)*AMP(1)+(5.000000000000000D
     $ -01)*AMP(3)+((0.000000000000000D+00,-5.000000000000000D-01))
     $ *AMP(4)
      JAMP(4,1) = (-1.666666666666667D-01)*AMP(1)+(-1.666666666666667D
     $ -01)*AMP(5)

      DO I=0,NSQAMPSO
        RES(I)=0D0
      ENDDO
      DO M = 1, NAMPSO
        DO I = 1, NCOLOR
          ZTEMP = (0.D0,0.D0)
          DO J = 1, NCOLOR
            ZTEMP = ZTEMP + CF(J,I)*JAMP(J,M)
          ENDDO
          DO N = 1, NAMPSO
            RES(SQSOINDEX2(M,N)) = RES(SQSOINDEX2(M,N)) + ZTEMP
     $       *DCONJG(JAMP(I,N))
          ENDDO
        ENDDO
      ENDDO

      DO I=1,NSQAMPSO
        RES(0)=RES(0)+RES(I)
      ENDDO

      END

C     
C     Helper functions to deal with the split orders.
C     

      INTEGER FUNCTION SQSOINDEX2(AMPORDERA,AMPORDERB)
C     
C     This functions plays the role of the interference matrix. It can
C      be hardcoded or 
C     made more elegant using hashtables if its execution speed ever
C      becomes a relevant
C     factor. From two split order indices of the jamps, it return the
C      corresponding
C     index in the squared order canonical ordering.
C     
C     CONSTANTS
C     
      IMPLICIT NONE
      INTEGER NAMPSO, NSQAMPSO
      PARAMETER (NAMPSO=1, NSQAMPSO=1)
      INTEGER NSPLITORDERS
      PARAMETER (NSPLITORDERS=2)
C     
C     ARGUMENTS
C     
      INTEGER AMPORDERA, AMPORDERB
C     
C     LOCAL VARIABLES
C     
      INTEGER I, SQORDERS(NSPLITORDERS)
      INTEGER AMPSPLITORDERS(NAMPSO,NSPLITORDERS)
      DATA (AMPSPLITORDERS(  1,I),I=  1,  2) /    3,    0/
C     
C     FUNCTION
C     
      INTEGER SQSOINDEX_FROM_ORDERS2
C     
C     BEGIN CODE
C     
      DO I=1,NSPLITORDERS
        SQORDERS(I)=AMPSPLITORDERS(AMPORDERA,I)
     $   +AMPSPLITORDERS(AMPORDERB,I)
      ENDDO
      SQSOINDEX2=SQSOINDEX_FROM_ORDERS2(SQORDERS)
      END



      INTEGER FUNCTION SQSOINDEX_FROM_ORDERS2(ORDERS)
C     
C     From a list of values for the split orders, this function
C      returns the
C     corresponding index in the squared orders canonical ordering.
C     
      IMPLICIT NONE
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
      INTEGER NSPLITORDERS
      PARAMETER (NSPLITORDERS=2)
C     
C     ARGUMENTS
C     
      INTEGER ORDERS(NSPLITORDERS)
C     
C     LOCAL VARIABLES
C     
      INTEGER I,J
      INTEGER SQSPLITORDERS(NSQAMPSO,NSPLITORDERS)
C     the values listed below are for QCD, QED
      DATA (SQSPLITORDERS(  1,I),I=  1,  2) /    6,    0/
C     
C     BEGIN CODE
C     
      DO I=1,NSQAMPSO
        DO J=1,NSPLITORDERS
          IF (ORDERS(J).NE.SQSPLITORDERS(I,J)) GOTO 1009
        ENDDO
        SQSOINDEX_FROM_ORDERS2 = I
        RETURN
 1009   CONTINUE
      ENDDO

      WRITE(*,*) 'ERROR:: Stopping function sqsoindex_from_orders'
      WRITE(*,*) 'Could not find squared orders ',(ORDERS(I),I=1
     $ ,NSPLITORDERS)
      STOP

      END



      INTEGER FUNCTION GETORDPOWFROMINDEX2(IORDER, INDX)
C     
C     Return the power of the IORDER-th order appearing at position
C      INDX
C     in the split-orders output
C     
      IMPLICIT NONE
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
      INTEGER NSPLITORDERS
      PARAMETER (NSPLITORDERS=2)
C     
C     ARGUMENTS
C     
      INTEGER IORDER, INDX
C     
C     LOCAL VARIABLES
C     
      INTEGER I
      INTEGER SQSPLITORDERS(NSQAMPSO,NSPLITORDERS)
C     the values listed below are for QCD, QED
      DATA (SQSPLITORDERS(  1,I),I=  1,  2) /    6,    0/
C     
C     BEGIN CODE
C     
      IF (IORDER.GT.NSPLITORDERS.OR.IORDER.LT.1) THEN
        WRITE(*,*) 'INVALID IORDER 2', IORDER
        WRITE(*,*) 'SHOULD BE BETWEEN 1 AND ', NSPLITORDERS
        STOP
      ENDIF

      IF (INDX.GT.NSQAMPSO.OR.INDX.LT.1) THEN
        WRITE(*,*) 'INVALID INDX 2', INDX
        WRITE(*,*) 'SHOULD BE BETWEEN 1 AND ', NSQAMPSO
        STOP
      ENDIF

      GETORDPOWFROMINDEX2=SQSPLITORDERS(INDX, IORDER)
      END



      SUBROUTINE GET_NSQSO_REAL2(NSQSO)
C     
C     Simple subroutine returning the number of squared split order
C     contributions returned in ANS when calling SMATRIX_SPLITORDERS
C     
      IMPLICIT NONE
      INTEGER NSQAMPSO
      PARAMETER (NSQAMPSO=1)
      INTEGER NSQSO

      NSQSO=NSQAMPSO

      END

