#!/bin/bash
relationsF=$1
parsesF=$2
outRelations=$3
echo $relationsF
#echo 'pwd', $PWD
topDir=$PWD
curDirName=$PWD/PSArg1
#dev data
echo 'Extracting features'
$curDirName/psArg1.py $relationsF $parsesF $curDirName/columnFile >$curDirName/columnFile.out 2>$curDirName/columnFile.out2
##########################
echo 'Classifying clauses'
testFile=$curDirName/columnFile
lbjDir=$curDirName/lbj
java -Xmx6g  -XX:MaxPermSize=4G -cp $CLASSPATH:/$lbjDir/class esl.PrepositionCorrector $testFile >$testFile.res
#threshold
$curDirName/threshold.py $testFile.res 0.54 >$testFile.res.th

$curDirName/addPredictionPSArg1.py $relationsF $parsesF $testFile.res.th $testFile.output >a 2>b
$curDirName/convertOutputToRelation.py $testFile.output $parsesF $outRelations
#./scorer.py $goldF $outF.pred >c
#Arg 1 extractor              : Precision 0.6948 Recall 0.6948 F1 0.6948
