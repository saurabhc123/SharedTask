#!/usr/bin/python
from sys import argv, exit, stderr
import os
import cvFunc
if len(argv) < 6:
	print """
	./runLBJ.py <trainFile> <lbjFile> <testFile> <resultFile> <eslDirPath> <optional:NB>
	<trainFile> column format normalized *Note* full path
	<lbjFile> *.lbj
	<testFile> column format *Note* full path
	<resultFile> - output will be saved here *Note* full path
	<eslDirName> e.g. /scratch/rozovska/learner/prep/esl/
	<NB> if it's set to NB - PrepositionCorrectorNB will be run instead of PrepositionCorrector
	"""
	exit()


trainF=str(argv[1])
lbjScript=str(argv[2])
testF=str(argv[3])
resultF=str(argv[4])
eslDirName=str(argv[5])
oldConstantsF=eslDirName+'/src/esl/Constants.java.copy'
os.system("cp %s/src/esl/Constants.java %s/src/esl/Constants.java.copy" % (eslDirName, eslDirName))
constantsF=open(eslDirName+'/src/esl/Constants.java','w')
oldF=open(oldConstantsF,'r')
for l in oldF:
	if 'public static final String trainingData' in l:
		constantsF.write('public static final String trainingData = "%s";\n' % (trainF))
	else:
		constantsF.write(l)
oldF.close()
constantsF.close()

newF=open
NB='None'
if len(argv)>6:
	NB=str(argv[6])
testFiles=[testF]
resultFiles={}
resultFiles[testF]=resultF
package='esl'
LBJprogramName='None'
testProgramName='PrepositionCorrector'
if NB=='NB':
	testProgramName='PrepositionCorrectorNB'

#cvFunc.runLBJArticle(trainF, testFiles,resultFiles, package, LBJprogramName, testProgramName, dir, lbjScript)
cvFunc.TrainLBJ(trainF, eslDirName, lbjScript)
cvFunc.TestLBJ(testProgramName,eslDirName, testFiles,resultFiles)
#uncomment to write feature weights file
#featureFileName=trainF+'_featureWeights_'+lbjScript.split('/')[-1]
#featureFileName=resultF+'_featureWeights'
#print 'feature file', featureFileName
#cvFunc.WriteLBJFeatureWeights(eslDirName,featureFileName)
