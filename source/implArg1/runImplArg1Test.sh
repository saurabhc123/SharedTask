#!/bin/bash
relationsF=$1
parsesF=$2
outRelations=$3
echo $relationsF
#echo 'pwd', $PWD
topDir=$PWD
curDirName=$PWD/implArg1
#dev data
echo 'Extracting features'
$curDirName/implArg1.py $relationsF $parsesF $curDirName/columnFile
##########################
echo 'Classifying clauses'
testFile=$curDirName/columnFile
lbjDir=$curDirName/lbj
java -Xmx6g  -XX:MaxPermSize=4G -cp $CLASSPATH:/$lbjDir/class esl.PrepositionCorrector $testFile >$testFile.res
#threshold

$curDirName/addPredictionImplArg1.py $relationsF $parsesF $testFile.res $testFile.output
$curDirName/convertOutputToRelation.py $testFile.output $parsesF $outRelations
#./scorer.py $goldF $outF.pred >c
#Arg 1 extractor              : Precision 0.6948 Recall 0.6948 F1 0.6948

