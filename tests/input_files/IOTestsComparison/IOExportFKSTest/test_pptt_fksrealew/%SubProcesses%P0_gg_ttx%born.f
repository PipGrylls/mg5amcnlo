      SUBROUTINE SBORN(P,ANS_SUMMED)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     
C     Return the sum of the split orders which are required in
C      orders.inc (BORN_ORDERS)
C     Also the values needed for the counterterms are stored in the
C      C_BORN_CNT common block
C     
C     
C     Process: g g > t t~ [ real = QED QCD ] QCD^2=4 QED^2=2
C     
C     
C     CONSTANTS
C     
      IMPLICIT NONE
      INCLUDE 'nexternal.inc'
      INTEGER NAMPSO, NSQAMPSO
      PARAMETER (NAMPSO=1, NSQAMPSO=1)
      INTEGER NGRAPHS
      PARAMETER (NGRAPHS=   3)
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL-1)
C     
C     VARIABLES
C     
      INTEGER I,J,K
      INCLUDE 'orders.inc'
      DOUBLE PRECISION ANS_SUMMED
      COMPLEX*16 ANS(2,0:NSQAMPSO), ANS_CNT(2, NSPLITORDERS)
      LOGICAL KEEP_ORDER(NSQAMPSO), KEEP_ORDER_CNT(NSPLITORDERS,
     $  NSQAMPSO), FIRSTTIME
      DATA KEEP_ORDER / NSQAMPSO * .TRUE. /
      COMMON /C_KEEP_ORDER_CNT/ KEEP_ORDER_CNT
      COMMON /C_BORN_CNT/ ANS_CNT
      INTEGER ORD_SUBTRACT
      DATA FIRSTTIME / .TRUE. /
      INTEGER AMP_ORDERS(NSPLITORDERS)
      DOUBLE PRECISION TINY
      PARAMETER (TINY = 1D-12)
      DOUBLE PRECISION MAX_VAL
      DOUBLE PRECISION       WGT_ME_BORN,WGT_ME_REAL
      COMMON /C_WGT_ME_TREE/ WGT_ME_BORN,WGT_ME_REAL

      DOUBLE PRECISION AMP2B(3), JAMP2B(0:2,0:NAMPSO)
      COMMON/TO_AMPS_BORN/  AMP2B,       JAMP2B
      DOUBLE PRECISION AMP2(3), JAMP2(0:2)
      COMMON/TO_AMPS/  AMP2,       JAMP2
      LOGICAL SPLIT_TYPE_USED(NSPLITORDERS)
      COMMON/TO_SPLIT_TYPE_USED/SPLIT_TYPE_USED
C     
C     FUNCTIONS
C     
      INTEGER GETORDPOWFROMINDEX_B
      INTEGER ORDERS_TO_AMP_SPLIT_POS
C     
C     BEGIN CODE
C     
C     look for orders which match the born order constraint 

      IF (FIRSTTIME) THEN
        DO I = 1, NSQAMPSO
C         this is for the orders of the born to integrate
          DO J = 1, NSPLITORDERS
            IF(GETORDPOWFROMINDEX_B(J, I) .GT. BORN_ORDERS(J)) THEN
              KEEP_ORDER(I) = .FALSE.
              EXIT
            ENDIF
          ENDDO

C         this is for the orders of the counterterms
          DO J = 1, NSPLITORDERS
            KEEP_ORDER_CNT(J,I) = .TRUE.
            DO K = 1, NSPLITORDERS
              IF (J.EQ.K) THEN
                ORD_SUBTRACT=2
              ELSE
                ORD_SUBTRACT=0
              ENDIF
              IF(GETORDPOWFROMINDEX_B(K, I) .GT. NLO_ORDERS(K)
     $         -ORD_SUBTRACT) THEN
                KEEP_ORDER_CNT(J,I) = .FALSE.
                EXIT
              ENDIF
            ENDDO
          ENDDO
          IF (KEEP_ORDER(I)) THEN
            WRITE(*,*) 'BORN: keeping split order ', I
          ELSE
            WRITE(*,*) 'BORN: not keeping split order ', I
          ENDIF
        ENDDO

        DO J = 1, NSPLITORDERS
          WRITE(*,*) 'counterterm S.O', J, ORDERNAMES(J)
          DO I = 1, NSQAMPSO
            IF (KEEP_ORDER_CNT(J,I)) THEN
              WRITE(*,*) 'BORN: keeping split order', I
            ELSE
              WRITE(*,*) 'BORN: not keeping split order', I
            ENDIF
          ENDDO
        ENDDO
        FIRSTTIME = .FALSE.
      ENDIF

      CALL SBORN_SPLITORDERS(P,ANS)

C     the born to be integrated
      ANS_SUMMED = 0D0
      MAX_VAL = 0D0

C     reset the amp_split array
      AMP_SPLIT(1:AMP_SPLIT_SIZE) = 0D0
      AMP_SPLIT_CNT(1:AMP_SPLIT_SIZE,1:2,1:NSPLITORDERS) = DCMPLX(0D0
     $ ,0D0)

      DO I = 1, NSQAMPSO
        MAX_VAL = MAX(MAX_VAL, ABS(ANS(1,I)))
      ENDDO
      DO I = 1, NSQAMPSO
        IF (KEEP_ORDER(I)) THEN
          ANS_SUMMED = ANS_SUMMED + ANS(1,I)
C         keep track of the separate pieces correspoinding to
C          different coupling combinations
          DO J = 1, NSPLITORDERS
            AMP_ORDERS(J) = GETORDPOWFROMINDEX_B(J, I)
          ENDDO
          IF(ABS(ANS(1,I)).GT.MAX_VAL*TINY)
     $      AMP_SPLIT(ORDERS_TO_AMP_SPLIT_POS(AMP_ORDERS)) = ANS(1,I)
        ENDIF
      ENDDO
C     this is to avoid fake non-zero contributions 
      IF (ABS(ANS_SUMMED).LT.MAX_VAL*TINY) ANS_SUMMED=0D0

      WGT_ME_BORN=ANS_SUMMED

C     fill the amp2 and jamp2 arrays
      AMP2(1:NGRAPHS)=AMP2B(1:NGRAPHS)  ! amp2 just needs to be copyed

      DO I = 0, INT(JAMP2B(0,0))
        JAMP2(I)=0D0
        DO J = 1, NAMPSO
C         here sum all, this may be refined later
          JAMP2(I)=JAMP2(I)+JAMP2B(I,J)
        ENDDO
      ENDDO


C     quantities for the counterterms
      DO J = 1, NSPLITORDERS
        ANS_CNT(1:2,J) = (0D0, 0D0)
        IF (.NOT.SPLIT_TYPE_USED(J)) CYCLE
        DO I = 1, NSQAMPSO
          IF (KEEP_ORDER_CNT(J,I)) THEN
            ANS_CNT(1,J) = ANS_CNT(1,J) + ANS(1,I)
            ANS_CNT(2,J) = ANS_CNT(2,J) + ANS(2,I)
C           keep track of the separate pieces also for counterterms
            DO K = 1, NSPLITORDERS
              AMP_ORDERS(K) = GETORDPOWFROMINDEX_B(K, I)
C             take into account the fact that the counterterm for a
C              given split order
C             will be multiplied by the corresponding squared coupling
              IF (K.EQ.J) AMP_ORDERS(K) = AMP_ORDERS(K) + 2
            ENDDO
C           this is to avoid fake non-zero contributions 
            IF (ABS(ANS(1,I)).GT.MAX_VAL*TINY)
     $        AMP_SPLIT_CNT(ORDERS_TO_AMP_SPLIT_POS(AMP_ORDERS),1,J) =
     $        ANS(1,I)
            IF (ABS(ANS(2,I)).GT.MAX_VAL*TINY)
     $        AMP_SPLIT_CNT(ORDERS_TO_AMP_SPLIT_POS(AMP_ORDERS),2,J) =
     $        ANS(2,I)
          ENDIF
        ENDDO
C       this is to avoid fake non-zero contributions 
        IF (ABS(ANS_CNT(1,J)).LT.MAX_VAL*TINY) ANS_CNT(1,J)=(0D0,0D0)
        IF (ABS(ANS_CNT(2,J)).LT.MAX_VAL*TINY) ANS_CNT(2,J)=(0D0,0D0)
      ENDDO


 999  RETURN
      END



      SUBROUTINE SBORN_SPLITORDERS(P1,ANS)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     
C     RETURNS AMPLITUDE SQUARED SUMMED/AVG OVER COLORS
C     AND HELICITIES
C     FOR THE POINT IN PHASE SPACE P1(0:3,NEXTERNAL-1)
C     
C     Process: g g > t t~ [ real = QED QCD ] QCD^2=4 QED^2=2
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INCLUDE 'nexternal.inc'
      INCLUDE 'born_nhel.inc'
      INTEGER     NCOMB
      PARAMETER ( NCOMB=  16 )
      INTEGER NAMPSO, NSQAMPSO
      PARAMETER (NAMPSO=1, NSQAMPSO=1)
      INTEGER    THEL
      PARAMETER (THEL=NCOMB*10)
      INTEGER NGRAPHS
      PARAMETER (NGRAPHS=   3)
C     
C     ARGUMENTS 
C     
      REAL*8 P1(0:3,NEXTERNAL-1)
      COMPLEX*16 ANS(2,0:NSQAMPSO)
C     
C     LOCAL VARIABLES 
C     
      INTEGER IHEL,IDEN,I,J,JJ,GLU_IJ
      REAL*8 BORNS(2,0:NSQAMPSO)
      COMPLEX*16 BORNTILDE
      INTEGER NTRY(10)
      DATA NTRY /10*0/
      COMPLEX*16 T(2,NSQAMPSO)
      INTEGER NHEL(NEXTERNAL-1,NCOMB)
      DATA (NHEL(I,   1),I=1,4) /-1,-1,-1, 1/
      DATA (NHEL(I,   2),I=1,4) /-1,-1,-1,-1/
      DATA (NHEL(I,   3),I=1,4) /-1,-1, 1, 1/
      DATA (NHEL(I,   4),I=1,4) /-1,-1, 1,-1/
      DATA (NHEL(I,   5),I=1,4) /-1, 1,-1, 1/
      DATA (NHEL(I,   6),I=1,4) /-1, 1,-1,-1/
      DATA (NHEL(I,   7),I=1,4) /-1, 1, 1, 1/
      DATA (NHEL(I,   8),I=1,4) /-1, 1, 1,-1/
      DATA (NHEL(I,   9),I=1,4) / 1,-1,-1, 1/
      DATA (NHEL(I,  10),I=1,4) / 1,-1,-1,-1/
      DATA (NHEL(I,  11),I=1,4) / 1,-1, 1, 1/
      DATA (NHEL(I,  12),I=1,4) / 1,-1, 1,-1/
      DATA (NHEL(I,  13),I=1,4) / 1, 1,-1, 1/
      DATA (NHEL(I,  14),I=1,4) / 1, 1,-1,-1/
      DATA (NHEL(I,  15),I=1,4) / 1, 1, 1, 1/
      DATA (NHEL(I,  16),I=1,4) / 1, 1, 1,-1/
      INTEGER IDEN_VALUES(10)
      DATA IDEN_VALUES /256, 256, 256, 256, 256, 256, 256, 256, 256,
     $  256/
      INTEGER IJ_VALUES(10)
      DATA IJ_VALUES /1, 1, 1, 1, 2, 2, 2, 2, 0, 0/
C     
C     GLOBAL VARIABLES
C     
      DOUBLE PRECISION AMP2(NGRAPHS), JAMP2(0:2,0:NAMPSO)
      COMMON/TO_AMPS_BORN/  AMP2,       JAMP2
      DATA JAMP2(0,0) /   2/
      LOGICAL GOODHEL(NCOMB,10)
      COMMON /C_GOODHEL/GOODHEL
      DOUBLE COMPLEX SAVEAMP(NGRAPHS,MAX_BHEL)
      COMMON/TO_SAVEAMP/SAVEAMP
      DOUBLE PRECISION SAVEMOM(NEXTERNAL-1,2)
      COMMON/TO_SAVEMOM/SAVEMOM
      DOUBLE PRECISION HEL_FAC
      INTEGER GET_HEL,SKIP(10)
      COMMON/CBORN/HEL_FAC,GET_HEL,SKIP
      LOGICAL CALCULATEDBORN
      COMMON/CCALCULATEDBORN/CALCULATEDBORN
      INTEGER NFKSPROCESS
      COMMON/C_NFKSPROCESS/NFKSPROCESS
      LOGICAL COND_IJ
C     ----------
C     BEGIN CODE
C     ----------
      IDEN=IDEN_VALUES(NFKSPROCESS)
      GLU_IJ = IJ_VALUES(NFKSPROCESS)
      NTRY(NFKSPROCESS)=NTRY(NFKSPROCESS)+1
      IF (NTRY(NFKSPROCESS).LT.2) THEN
        IF (GLU_IJ.EQ.0) THEN
          SKIP(NFKSPROCESS)=0
        ELSE
          SKIP(NFKSPROCESS)=1
          DO WHILE(NHEL(GLU_IJ ,SKIP(NFKSPROCESS)).NE.-NHEL(GLU_IJ ,1))
            SKIP(NFKSPROCESS)=SKIP(NFKSPROCESS)+1
          ENDDO
          SKIP(NFKSPROCESS)=SKIP(NFKSPROCESS)-1
        ENDIF
      ENDIF
      DO JJ=1,NGRAPHS
        AMP2(JJ)=0D0
      ENDDO
      DO I=0,NAMPSO
        DO JJ=1,INT(JAMP2(0,0))
          JAMP2(JJ,I)=0D0
        ENDDO
      ENDDO
      IF (CALCULATEDBORN) THEN
        DO J=1,NEXTERNAL-1
          IF (SAVEMOM(J,1).NE.P1(0,J) .OR. SAVEMOM(J,2).NE.P1(3,J))
     $      THEN
            CALCULATEDBORN=.FALSE.
            WRITE (*,*) 'momenta not the same in Born'
            STOP
          ENDIF
        ENDDO
      ENDIF
      IF (.NOT.CALCULATEDBORN) THEN
        DO J=1,NEXTERNAL-1
          SAVEMOM(J,1)=P1(0,J)
          SAVEMOM(J,2)=P1(3,J)
        ENDDO
        DO J=1,MAX_BHEL
          DO JJ=1,NGRAPHS
            SAVEAMP(JJ,J)=(0D0,0D0)
          ENDDO
        ENDDO
      ENDIF
      DO I=0,NSQAMPSO
        ANS(1,I) = 0D0
        ANS(2,I) = 0D0
      ENDDO
      HEL_FAC=1D0
      DO IHEL=1,NCOMB
          ! the following lines are to avoid segfaults when glu_ij=0
        COND_IJ=SKIP(NFKSPROCESS).EQ.0
        IF (.NOT.COND_IJ) COND_IJ=COND_IJ.OR.NHEL(GLU_IJ,IHEL)
     $   .EQ.NHEL(GLU_IJ,1)
          !if (nhel(glu_ij,ihel).EQ.NHEL(GLU_IJ,1).or.skip(nfksprocess).eq.0) then
        IF (COND_IJ) THEN
          IF ((GOODHEL(IHEL,NFKSPROCESS) .OR. GOODHEL(IHEL
     $     +SKIP(NFKSPROCESS),NFKSPROCESS) .OR. NTRY(NFKSPROCESS) .LT.
     $      2) ) THEN

            CALL BORN(P1,NHEL(1,IHEL),IHEL,T,BORNS)
            DO I=1,NSQAMPSO
              ANS(1,I)=ANS(1,I)+T(1,I)
              ANS(2,I)=ANS(2,I)+T(2,I)
            ENDDO
            IF ( BORNS(1,0).NE.0D0 .AND. .NOT. GOODHEL(IHEL
     $       ,NFKSPROCESS) ) THEN
              GOODHEL(IHEL,NFKSPROCESS)=.TRUE.
            ENDIF
            IF ( BORNS(2,0).NE.0D0 .AND. .NOT. GOODHEL(IHEL
     $       +SKIP(NFKSPROCESS),NFKSPROCESS) ) THEN
              GOODHEL(IHEL+SKIP(NFKSPROCESS),NFKSPROCESS)=.TRUE.
            ENDIF
          ENDIF
        ENDIF
      ENDDO
      DO I=1,NSQAMPSO
        ANS(1,I)=ANS(1,I)/DBLE(IDEN)
        ANS(2,I)=ANS(2,I)/DBLE(IDEN)
        ANS(1,0)=ANS(1,0)+ANS(1,I)
        ANS(2,0)=ANS(2,0)+ANS(2,I)
      ENDDO
      CALCULATEDBORN=.TRUE.
      END


      SUBROUTINE BORN(P,NHEL,HELL,ANS,BORNS)
C     
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     RETURNS AMPLITUDE SQUARED SUMMED/AVG OVER COLORS
C     FOR THE POINT WITH EXTERNAL LINES W(0:6,NEXTERNAL-1)

C     Process: g g > t t~ [ real = QED QCD ] QCD^2=4 QED^2=2
C     
      IMPLICIT NONE
C     
C     CONSTANTS
C     
      INTEGER NAMPSO, NSQAMPSO
      PARAMETER (NAMPSO=1, NSQAMPSO=1)
      INTEGER    NGRAPHS,    NEIGEN
      PARAMETER (NGRAPHS=   3,NEIGEN=  1)
      INTEGER    NWAVEFUNCS, NCOLOR
      PARAMETER (NWAVEFUNCS=5, NCOLOR=2)
      REAL*8     ZERO
      PARAMETER (ZERO=0D0)
      COMPLEX*16 IMAG1
      PARAMETER (IMAG1 = (0D0,1D0))
      INCLUDE 'nexternal.inc'
      INCLUDE 'born_nhel.inc'
      INCLUDE 'coupl.inc'
C     
C     ARGUMENTS 
C     
      REAL*8 P(0:3,NEXTERNAL-1),BORNS(2,0:NSQAMPSO)
      INTEGER NHEL(NEXTERNAL-1), HELL
      COMPLEX*16 ANS(2,NSQAMPSO)
C     
C     LOCAL VARIABLES 
C     
      INTEGER I,J,M,N,IHEL,BACK_HEL,GLU_IJ
      INTEGER IC(NEXTERNAL-1),NMO
      PARAMETER (NMO=NEXTERNAL-1)
      DATA IC /NMO*1/
      REAL*8 DENOM(NCOLOR), CF(NCOLOR,NCOLOR)
      COMPLEX*16 ZTEMP, AMP(NGRAPHS), JAMP(NCOLOR,NAMPSO), W(8
     $ ,NWAVEFUNCS), JAMPH(2, NCOLOR,NAMPSO)
C     
C     GLOBAL VARIABLES
C     
      DOUBLE PRECISION AMP2(3), JAMP2(0:2,0:NAMPSO)
      COMMON/TO_AMPS_BORN/  AMP2,       JAMP2
      DOUBLE COMPLEX SAVEAMP(NGRAPHS,MAX_BHEL)
      COMMON/TO_SAVEAMP/SAVEAMP
      DOUBLE PRECISION HEL_FAC
      INTEGER GET_HEL,SKIP(10)
      COMMON/CBORN/HEL_FAC,GET_HEL,SKIP
      LOGICAL CALCULATEDBORN
      COMMON/CCALCULATEDBORN/CALCULATEDBORN
      INTEGER NFKSPROCESS
      COMMON/C_NFKSPROCESS/NFKSPROCESS
      INTEGER STEP_HEL
      LOGICAL COND_IJ

C     
C     FUNCTION
C     
      INTEGER SQSOINDEXB

      INTEGER IJ_VALUES(10)
      DATA IJ_VALUES /1, 1, 1, 1, 2, 2, 2, 2, 0, 0/
C     
C     COLOR DATA
C     
      DATA DENOM(1)/3/
      DATA (CF(I,  1),I=  1,  2) /   16,   -2/
C     1 T(1,2,3,4)
      DATA DENOM(2)/3/
      DATA (CF(I,  2),I=  1,  2) /   -2,   16/
C     1 T(2,1,3,4)
C     ----------
C     BEGIN CODE
C     ----------
      GLU_IJ = IJ_VALUES(NFKSPROCESS)
      DO I = 1, NSQAMPSO
        ANS(1,I)=0D0
        ANS(2,I)=0D0
        BORNS(1,I)=0D0
        BORNS(2,I)=0D0
      ENDDO
      BORNS(1,0)=0D0
      BORNS(2,0)=0D0
      IF (GLU_IJ.NE.0) THEN
        BACK_HEL = NHEL(GLU_IJ)
        IF (BACK_HEL.NE.0) THEN
          STEP_HEL=-2*BACK_HEL
        ELSE
          STEP_HEL=1
        ENDIF
      ELSE
        BACK_HEL=0
        STEP_HEL=1
      ENDIF
      DO IHEL=BACK_HEL,-BACK_HEL,STEP_HEL
        IF (GLU_IJ.NE.0) THEN
          COND_IJ=IHEL.EQ.BACK_HEL.OR.NHEL(GLU_IJ).NE.0
        ELSE
          COND_IJ=IHEL.EQ.BACK_HEL
        ENDIF
        IF (COND_IJ) THEN
          IF (GLU_IJ.NE.0) THEN
            IF (NHEL(GLU_IJ).NE.0) NHEL(GLU_IJ) = IHEL
          ENDIF
          IF (.NOT. CALCULATEDBORN) THEN
            CALL VXXXXX(P(0,1),ZERO,NHEL(1),-1*IC(1),W(1,1))
            CALL VXXXXX(P(0,2),ZERO,NHEL(2),-1*IC(2),W(1,2))
            CALL OXXXXX(P(0,3),MDL_MT,NHEL(3),+1*IC(3),W(1,3))
            CALL IXXXXX(P(0,4),MDL_MT,NHEL(4),-1*IC(4),W(1,4))
            CALL VVV1P0_1(W(1,1),W(1,2),GC_10,ZERO,ZERO,W(1,5))
C           Amplitude(s) for diagram number 1
            CALL FFV1_0(W(1,4),W(1,3),W(1,5),GC_11,AMP(1))
            CALL FFV1_1(W(1,3),W(1,1),GC_11,MDL_MT,MDL_WT,W(1,5))
C           Amplitude(s) for diagram number 2
            CALL FFV1_0(W(1,4),W(1,5),W(1,2),GC_11,AMP(2))
            CALL FFV1_2(W(1,4),W(1,1),GC_11,MDL_MT,MDL_WT,W(1,5))
C           Amplitude(s) for diagram number 3
            CALL FFV1_0(W(1,5),W(1,3),W(1,2),GC_11,AMP(3))
            DO I=1,NGRAPHS
              IF(IHEL.EQ.BACK_HEL)THEN
                SAVEAMP(I,HELL)=AMP(I)
              ELSEIF(IHEL.EQ.-BACK_HEL)THEN
                SAVEAMP(I,HELL+SKIP(NFKSPROCESS))=AMP(I)
              ELSE
                WRITE(*,*) 'ERROR #1 in born.f'
                STOP
              ENDIF
            ENDDO
          ELSEIF (CALCULATEDBORN) THEN
            DO I=1,NGRAPHS
              IF(IHEL.EQ.BACK_HEL)THEN
                AMP(I)=SAVEAMP(I,HELL)
              ELSEIF(IHEL.EQ.-BACK_HEL)THEN
                AMP(I)=SAVEAMP(I,HELL+SKIP(NFKSPROCESS))
              ELSE
                WRITE(*,*) 'ERROR #1 in born.f'
                STOP
              ENDIF
            ENDDO
          ENDIF
C         JAMPs contributing to orders QCD=2 QED=0
          JAMP(1,1)=+IMAG1*AMP(1)-AMP(2)
          JAMP(2,1)=-IMAG1*AMP(1)-AMP(3)
          DO M = 1, NAMPSO
            DO I = 1, NCOLOR
              ZTEMP = (0.D0,0.D0)
              DO J = 1, NCOLOR
                ZTEMP = ZTEMP + CF(J,I)*JAMP(J,M)
              ENDDO
              DO N = 1, NAMPSO
                BORNS(2-(1+BACK_HEL*IHEL)/2,SQSOINDEXB(M,N))=BORNS(2
     $           -(1+BACK_HEL*IHEL)/2,SQSOINDEXB(M,N))+ZTEMP
     $           *DCONJG(JAMP(I,N))/DENOM(I)
              ENDDO
            ENDDO
          ENDDO
          DO I = 1, NGRAPHS
            AMP2(I)=AMP2(I)+AMP(I)*DCONJG(AMP(I))
          ENDDO
          DO J = 1,NAMPSO
            DO I = 1, NCOLOR
              JAMP2(I,J)=JAMP2(I,J)+JAMP(I,J)*DCONJG(JAMP(I,J))
              JAMPH(2-(1+BACK_HEL*IHEL)/2,I,J)=JAMP(I,J)
            ENDDO
          ENDDO
        ENDIF
      ENDDO
      DO I = 1, NSQAMPSO
        BORNS(1,0)=BORNS(1,0)+BORNS(1,I)
        BORNS(2,0)=BORNS(2,0)+BORNS(2,I)
        ANS(1,I) = BORNS(1,I) + BORNS(2,I)
      ENDDO
      DO M = 1, NAMPSO
        DO I = 1, NCOLOR
          ZTEMP = (0.D0,0.D0)
          DO J = 1, NCOLOR
            ZTEMP = ZTEMP + CF(J,I)*JAMPH(2,J,M)
          ENDDO
          DO N = 1, NAMPSO
            ANS(2,SQSOINDEXB(M,N))= ANS(2,SQSOINDEXB(M,N)) + ZTEMP
     $       *DCONJG(JAMPH(1,I,N))/DENOM(I)
          ENDDO
        ENDDO
      ENDDO
      IF (GLU_IJ.NE.0) NHEL(GLU_IJ) = BACK_HEL
      END


      BLOCK DATA GOODHELS
      INTEGER     NCOMB
      PARAMETER ( NCOMB=  16 )
      INTEGER    THEL
      PARAMETER (THEL=NCOMB*10)
      LOGICAL GOODHEL(NCOMB,10)
      COMMON /C_GOODHEL/GOODHEL
      DATA GOODHEL/THEL*.FALSE./
      END



C     
C     Helper functions to deal with the split orders.
C     

      INTEGER FUNCTION SQSOINDEXB(AMPORDERA,AMPORDERB)
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
      DATA (AMPSPLITORDERS(  1,I),I=  1,  2) /    2,    0/
C     
C     FUNCTION
C     
      INTEGER SQSOINDEXB_FROM_ORDERS
C     
C     BEGIN CODE
C     
      DO I=1,NSPLITORDERS
        SQORDERS(I)=AMPSPLITORDERS(AMPORDERA,I)
     $   +AMPSPLITORDERS(AMPORDERB,I)
      ENDDO
      SQSOINDEXB=SQSOINDEXB_FROM_ORDERS(SQORDERS)
      END



      INTEGER FUNCTION SQSOINDEXB_FROM_ORDERS(ORDERS)
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
      DATA (SQSPLITORDERS(  1,I),I=  1,  2) /    4,    0/
C     
C     BEGIN CODE
C     
      DO I=1,NSQAMPSO
        DO J=1,NSPLITORDERS
          IF (ORDERS(J).NE.SQSPLITORDERS(I,J)) GOTO 1009
        ENDDO
        SQSOINDEXB_FROM_ORDERS = I
        RETURN
 1009   CONTINUE
      ENDDO

      WRITE(*,*) 'ERROR:: Stopping function sqsoindex_from_orders'
      WRITE(*,*) 'Could not find squared orders ',(ORDERS(I),I=1
     $ ,NSPLITORDERS)
      STOP

      END



      INTEGER FUNCTION GETORDPOWFROMINDEX_B(IORDER, INDX)
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
      DATA (SQSPLITORDERS(  1,I),I=  1,  2) /    4,    0/
C     
C     BEGIN CODE
C     
      IF (IORDER.GT.NSPLITORDERS.OR.IORDER.LT.1) THEN
        WRITE(*,*) 'INVALID IORDER B', IORDER
        WRITE(*,*) 'SHOULD BE BETWEEN 1 AND ', NSPLITORDERS
        STOP
      ENDIF

      IF (INDX.GT.NSQAMPSO.OR.INDX.LT.1) THEN
        WRITE(*,*) 'INVALID INDX B', INDX
        WRITE(*,*) 'SHOULD BE BETWEEN 1 AND ', NSQAMPSO
        STOP
      ENDIF

      GETORDPOWFROMINDEX_B=SQSPLITORDERS(INDX, IORDER)
      END


      SUBROUTINE GET_NSQSO_B(NSQSO)
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



