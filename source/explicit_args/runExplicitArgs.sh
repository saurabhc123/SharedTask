#!/bin/bash
relationsF=$1
parsesF=$2
outRelations=$4
echo $relationsF
#echo 'pwd', $PWD
topDir=$PWD
curDirName=$PWD
#dev data
echo 'Extracting features'
python $curDirName/pc2.py $relationsF $parsesF . $outRelations
