#!/bin/bash
relationsF=$1
parsesF=$2
lbjFolder=$3
outRelations=$4
echo $relationsF
#echo 'pwd', $PWD
topDir=$PWD
curDirName=$PWD
#dev data
echo 'Extracting features for explicit senses'
python $curDirName/explicit_sense/explicit_sense_perceptron_predict.py $relationsF $parsesF $lblFolder $outRelations
