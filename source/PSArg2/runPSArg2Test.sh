#!/bin/bash
relationsF=$1
parsesF=$2
outRelations=$3
echo $relationsF
#echo 'pwd', $PWD
topDir=$PWD
curDirName=$PWD/PSArg2
rm -f $curDirName/columnFile*
#dev data
echo 'Extracting features'
$curDirName/psArg2.py $relationsF $parsesF $curDirName/columnFile >$curDirName/columnFile.out 2>$curDirName/columnFile.out2
##########################
echo 'Classifying clauses'
testFile=$curDirName/columnFile
lbjDir=$curDirName/lbj
java -Xmx6g  -XX:MaxPermSize=7G -cp $CLASSPATH:/$lbjDir/class esl.PrepositionCorrector $testFile >$testFile.res
#threshold
echo 'Threshold'
$curDirName/threshold.py $testFile.res 0.6 >$testFile.res.th
echo $testFile.res.th
echo 'Adding predictions'
echo  $relationsF
echo $parsesF
echo $testFile.res.th
echo $testFile.output
$curDirName/addPredictionPSArg2.py $relationsF $parsesF $testFile.res.th $testFile.output >$testFile.output.out 2>$testFile.output.out2
$curDirName/convertOutputToRelation.py $testFile.output $parsesF $outRelations
#./scorer.py $goldF $outF.pred >c
#Arg 1 extractor              : Precision 0.6948 Recall 0.6948 F1 0.6948
