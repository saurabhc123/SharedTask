#!/usr/bin/python
from sys import argv, exit, stderr, path
#path.append("/scratch/rozovska/learner/article/evaluate/")
from random import shuffle, random
from os import listdir, popen, chdir, system, getcwd

#start col (0, 1, 2, etc.)
#e.g. if start col=2, and total features is 3, then pruning will happen
#for columns 2, 3, 4
def prune(trainFile, threshold, newTrain, startColumn,prepList='None'):
	print >>stderr, prepList
	flag=1	
	featCounts={}
	trainF=open(trainFile,'r')
	newF=open(newTrain,'w')
	if threshold<2 and prepList=='None':
		system("cp %s %s" % (trainFile, newTrain))
		return
	if threshold<2 and prepList!='None':
	    for l in trainF:
		if l.strip():
                   terms=l.split()
                   source=terms[0]
		   if source in prepList:
			newF.write("%s\n" % (l.strip()))
	    newF.close()
	    return
	curL=0
	print >>stderr, 'Counting features'
	for l in trainF:
		curL+=1
		if curL%100000==0:
			print >>stderr, curL
		if l.strip():
		   terms=l.split()
		   source=terms[0]
		   if prepList=='None' or source in prepList:
		   	for i in range(len(terms)):
				#skip column1 (source), column2(target), column3(startend), second to last column(source), last column exampleID
				if i >=startColumn:
					if i not in featCounts:
					   featCounts[i]={}
					#print >>stderr, i, terms[i],
					f=terms[i]
					if ':' not in f:
						flag=0 #featureVal not preceded by featName, such as wAfter
					if f not in featCounts[i]:
						featCounts[i][f]=0.0
					featCounts[i][f]+=1
	trainF.close()
	trainF=open(trainFile,'r')
	curL=0
	print >>stderr, 'Replacing features'
	for l in trainF:

		curL+=1
		if curL%100000==0:
			print >>stderr, curL
		if l.strip():
		   terms=l.split()
		   source=terms[0]
		   if prepList=='None' or source in prepList:
			for i in range(len(terms)):
				#if i >=startCol and i <startCol+totalFeats:
				#skip column1 (source), column2(target), column3(startend) and last column(source)
                                if i >=startColumn:

					f=terms[i]
					if featCounts[i][f]<threshold:
					  	if flag:
						 f=f.split(':',1)[0]+':NA'
						else:
							f='NA'
					newF.write(" %s " % f)
				else:
					newF.write(" %s " % terms[i])
			newF.write("\n")
		else:
			newF.write("\n")
	allFeatsBeforePruning=0
        allFeatsAfterPruning=0
	for f in featCounts:
		for i in featCounts[f]:
			if featCounts[f][i]>=threshold:
				allFeatsAfterPruning+=1
			allFeatsBeforePruning+=1
	print >>stderr, 'Features before pruning:', allFeatsBeforePruning
	print >>stderr, 'Features after pruning: ', allFeatsAfterPruning
	print >>stderr, 'Percentage of features removed',  (float(allFeatsBeforePruning-allFeatsAfterPruning)/allFeatsBeforePruning)

	trainF.close()
	newF.close()


#randomize the order of files in dataDir before selecting files for train/test
#randomize lines in each file; do not use excluded files
#normalize the resulting file
#excluded files (list of files that are reserved - will not be used in development)
def MakeRandomTrainTest(dataDir, trainSize, trainF, excludedFiles):
	outputTrain=open(trainF,'w')
	fileList=os.listdir(dataDir)
	for f in excludedFiles:
		fileList.remove(f)
	examplesPerFile=trainSize/len(fileList)
	shuffle(fileList)
	curExample=0.0
	tempTrain=open("tempTrain",'w')
	trainTotal=0
	selectedLines=[]
	for i in range(len(fileList)):
	   f=fileList[i]
           if f not in excludedFiles:
		print >>stderr, f
		if trainTotal>=trainSize:
			break
		outF=open(dataDir+f,'r').readlines()
		shuffle(outF)
		curExample=0
		for l in outF:
			if curExample>=examplesPerFile and i<len(fileList)-1:
				print >>stderr, curExample,
				break
			elif trainTotal>=trainSize:
				break
			selectedLines.append(l)
			#tempTrain.write(l)
			if l.strip() !='':
				trainTotal+=1
				curExample+=1
	shuffle(selectedLines)
	for l in selectedLines:
		tempTrain.write(l)
	tempTrain.close()
	#normalize test and train data
	system("/scratch/rozovska/learner/prep/experiments/normTrainTest.py tempTrain %s" %  trainF)

#trainFiles is a list; do cv: train one one trainFile, test on the rest; also test on learner files
#params: learning_rate, threshold, thickness, features
#learnerOutputFiles: dict: key e.g. 'CLEC' value: filehandle to outputfile (file already open for writing)
def RunOneSetting(trainFiles,learnerTestFiles, resultsDir, lbjScriptFile, learnerOutputFiles, remove, neg_th, th, learning_rate, number_rounds, trainName):
	totalRuns=len(trainFiles)
	resultFilesForAllRuns={} #key learner file value: list of result files
	for f in learnerTestFiles:
		resultFilesForAllRuns[f]=[]

	print >>stderr, 'Total runs', totalRuns
	for i in range(totalRuns):
		
		print >>stderr, 'Run', i+1
		trainFile=trainFiles[i]
		system("rm -f /scratch/rozovska/learner/prep/experiments/temp")
		resultFiles={}
		scriptName=str(lbjScriptFile).split('/')[-1]
		for f in learnerTestFiles:
			resultFile=resultsDir+'/'+'Train_'+trainFile.split('/')[-1].strip()+'_learning_rate_'+str(learning_rate)+'_neg_thickness_'+str(neg_th)+'_thickness_'+str(th)+'_number_rounds_'+str(number_rounds)+'_Test_'+f.split('/')[-1]
			print >>stderr, 'Train file', trainFile.split('/')[-1].strip()
			print >>stderr, 'Test file', f.split('/')[-1]
			print >>stderr, 'resultFile', resultFile
			resultFiles[f]=resultFile
		#train and test
		package='esl'
#		LBJprogramName="prepositionLearner.lbj"
		LBJprogramName=lbjScriptFile
		print >>stderr, lbjScriptFile
		testProgramName="PrepositionCorrector"
		lbjPackageDir="/scratch/rozovska/learner/prep/esl/"
		testFiles=learnerTestFiles
		#testFiles=learnerTestFiles+[trainFile]
		print >>stderr, 'TrainFile', trainFile 
		print >>stderr, 'TestFiles', testFiles
		print >>stderr,  'ResultsDir', resultsDir
		print >>stderr,  'lbjScriptFile', lbjScriptFile
		
		runLBJArticle(trainFile, testFiles,resultFiles, package, LBJprogramName, testProgramName, lbjPackageDir, lbjScriptFile)
		
		chdir("/scratch/rozovska/learner/prep/experiments/")
		
	
#evaluate w.r.t. fMeasure/Pr/Recall and Accuracy for each file in the run and save individual results and average results over numberRuns
def WriteResultsToFile(resultFilesList, outputF, numberRuns):
	totalRuns=numberRuns
	totalAcc=0.0
        totPr=0.0
        totRecall=0.0
        totF=0.0
	i=0
	for f in resultFilesList:
		i+=1
		acc=Accuracy(f)
		totalAcc+=acc
		(pr, recall, fMeasure)=EvaluateFMeasure(f)
		totPr+=pr
		totRecall+=recall
		totF+=fMeasure
		outputF.write("Run %s\n" % i)
		outputF.write("Accuracy %.2f \n" % (acc*100.0))
                outputF.write("Precision %.2f Recall %.2f FMeasure %.2f\n\n" % ((pr*100.0), (recall*100.0), (fMeasure*100.0)))
	outputF.write("Total Accuracy %.2f Precision  %.2f Recall %.2f FMeasure %.2f\n" % (((totalAcc*100.0)/totalRuns), ((totPr*100.0)/totalRuns), ((totRecall*100.0)/totalRuns), ((totF*100.0)/totalRuns)))
        outputF.write("---------------------------\n")

def WriteLBJScript(baseScript, newLBJFile, lbjParams):
	baseF=open(baseScript, 'r')
	baseScriptF=baseF.readlines()
	baseF.close()
	newLBJWrite=open(newLBJFile,'w')
	params=lbjParams
	featFlag=0
	for i in range(len( baseScriptF)):
		l=baseScriptF[i]
		if featFlag:
			newLBJWrite.write("\t%s\n" % (params["features"]))
			featFlag=0
		elif l.strip()=='2 rounds' or l.strip()=='6 rounds':
			newLBJWrite.write("   %s rounds\n" % (params["number_rounds"]))
		elif l.strip()=='with new SparseNetworkLearner(new SparsePerceptron(.1, 0, 2))':
			newLBJWrite.write("with SparseNetworkLearner\n")
			newLBJWrite.write("{\n")
			newLBJWrite.write("SparseAveragedPerceptron.Parameters p =\n")
			newLBJWrite.write("new SparseAveragedPerceptron.Parameters();\n")
			newLBJWrite.write("p.learningRate =%s;\n" % params["learning_rate"])
			newLBJWrite.write("p.positiveThickness =%s;\n" % params["thickness"])
			newLBJWrite.write("p.negativeThickness =%s;\n" % params["neg_thickness"])
			newLBJWrite.write("baseLTU = new SparseAveragedPerceptron(p);\n")
			newLBJWrite.write("}\n")
			
			#newLBJWrite.write("  with new SparseNetworkLearner(new SparseAveragedPerceptron(%s, 0, %s, %s))\n" % (params["learning_rate"], params["thickness"], params['neg_thickness']))
		else:
			newLBJWrite.write(l)
		if l.strip()=='using':
			featFlag=1
	newLBJWrite.close()
	
#set probTable to "None" if no errors should be added		
def SplitWikiDataAndAddErrors(wikiFile, wikiFiles, examplesPerFile, probTable):
	lines=[]
	wikiF=open(wikiFile,'r')
	total=len(lines)
	curDir=getcwd()
	f=open(curDir+'/wikiTemp','w')
	linesWrittenInFile=0
	curFile=1
	finished=0
        numberPartitions=len(wikiFiles)
	skipStep=examplesPerFile
	if examplesPerFile>4000000:
		skipStep=4000000
	while not finished:
	
		if linesWrittenInFile==examplesPerFile:
			f.close()
			fileName=wikiFiles[curFile-1]
			tempF=curDir+'/wikiTemp'
			#tempF='/scratch/rozovska/learner/prep/experiments/wikiTemp'
			#generate errors and normalize (insert empty lines)
			if probTable !='None':
			   outF=('wikiTemp.perturbed')
			   PerturbData(tempF, outF, probTable)
			   NormTrainTest(outF, fileName)
			else:
			   NormTrainTest(tempF, fileName)
			if curFile==numberPartitions:
				finished=1
				break
			linesWrittenInFile=0
			#if examplesPerFile >2000000:
			wikiF.close()
			skip=skipStep*curFile
			print >>stderr, 'skip', skip
			wikiF=open(wikiFile,'r')
			while skip:
				
				line=wikiF.readline()
				if line:
				  if line.strip():
				    skip-=1
				else:
					 wikiF.close()
					 wikiF=open(wikiFile,'r')
			curFile+=1
			f=open('wikiTemp','w')
		if not finished:	
		   line=wikiF.readline()
		   if line:
			if line.strip():
				f.write(line)
				linesWrittenInFile+=1
		   else: #end of file
			wikiF.close()
			wikiF=open(wikiFile,'r')
			
		
	system("rm -f wikiTemp")
	system("rm -f wikiTemp.perturbed")
	#print >>stderr, wikiFiles
	#return wikiFiles

	
#params: dict: key: param (learning_rate, threshold, thickenss, number_rounds, features, value: list	
def getLBJParams(paramsFile):
	params={}
	f=open(paramsFile,'r')
	for l in f:
		terms=l.split(':')
		p=terms[0].strip()
		values=terms[1].strip().split()
		params[p]=values
	f.close()
	return params

def GetPartOfTrain(trainF, testF, total):
	f=open(trainF,'r')
	f1=open('tempShort','w')
	lines=f.readlines()
	shuffle(lines)
	extracted=0
	for l in lines:
		if extracted>=total:
			break
		f1.write(l)
		extracted+=1
	f.close()	
	f1.close()
	NormTrainTest('tempShort', testF)
		
#dir full directory path to the lbj package top directory
#programName: e.g. articleLearner.lbj
#testProgramName: e.g. ArticleCorrector
#testFiles - list if test files
#resultFiles - dict: key test File value: result file (full path to result file for that test file)
def runLBJArticle(trainFile, testFiles,resultFiles, package, LBJprogramName, testProgramName, dir, lbjScript):
	
	#change working directory
	chdir("%s" % dir)
	print >>stderr, dir
	#fOut=popen("cp %s %s" % (LBJprogramName, '/scratch/rozovska/esl/prepositionLearner.lbj'))
	LBJprogramName='/scratch/rozovska/learner/prep/esl/prepositionLearner.lbj'
	#write train file to main lbj dir
	#remove old files
	fOut=popen("rm -f ../../prep/esl/class/esl/*")
	fOut=popen("rm -f ../../prep/esl/lbj/esl/*")
	fOut=popen("rm -f ../../article/esl/class/esl/*")
	fOut=popen("rm -f ../../article/esl/lbj/esl/*")
	#compile
	print >>stderr, 'Training LBJ'
	print >>stderr, 'Copying training file', trainFile
	#remove old trainFile
	fOut=popen("rm -f /scratch/rozovska/learner/prep/esl/trainFile")
	system("ln -s %s /scratch/rozovska/learner/prep/esl/trainFile" % trainFile)
	#fOut=popen("cp %s /scratch/rozovska/learner/prep/esl/trainFile" % trainFile)
	#***for harmony***
	#os.system("java -Xmx1G -XX:MaxPermSize=1500m -cp $CLASSPATH:class LBJ2.Main -sourcepath src -gsp lbj -d class %s" % (LBJprogramName))
	#for gargamel replace above line with
	#e.g. LBJprogramName prepositionLearner.lbj
	system("java -Xmx3G -XX:MaxPermSize=3G -cp $CLASSPATH:class LBJ2.Main -sourcepath src -gsp lbj -d class %s" % (LBJprogramName))
	system("javac -classpath $CLASSPATH:class -sourcepath lbj:src -d class src/%s/*.java" % package)
	system("export CLASSPATH=$CLASSPATH:%s/class/" % dir)
	#write feature weights to file
	terms=resultFiles[testFiles[0]].split('Train_')

	name=terms[0]+'featureFile'+terms[1]
	#uncomment to save feature file
	system("java -Xmx4G -XX:MaxPermSize=4G LBJ2.learn.LearnerToText  esl.PrepositionUnconfuse >%s" % name)
	#test
	print >>stderr, 'Testing'
	curTestF=0
	for i in range (len(testFiles)):
		testFile=testFiles[i]
		resultFile=resultFiles[testFile]
		inputToTestF = testFile
		outputResultFile=resultFiles[testFile]
		print >>stderr, 'Testing on file', testFile
		print >>stderr, 'Result file', outputResultFile
		#***Uncomment for harmony***
		#os.system("java -Xmx1g  -XX:MaxPermSize=1g %s.%s %s >%s" % (package, testProgramName, inputToTestF, outputResultFile))
		#***Uncomment for gargamel***
		print >>stderr, 'resultFile', outputResultFile
		fOut=popen("java -Xmx5g  -XX:MaxPermSize=7G %s.%s %s >%s" % (package, testProgramName, inputToTestF, outputResultFile))

#dir full directory path to the lbj package top directory
#programName: e.g. articleLearner.lbj
def TrainLBJ(trainFile, eslDirName, lbjScript):
	#copy training file
	#fOut=popen("rm -f %s/trainFile" % eslDirName)
	#fOut=popen("ls -l %s/trainFile" % eslDirName)
	#fOut=popen("ln -s  %s %s/trainFile" % (trainFile,eslDirName))
 	classPath=eslDirName+':'+eslDirName+'/class/'
        #change working directory
        chdir("%s" % eslDirName)
        print >>stderr, eslDirName
        #remove old files
        fOut=popen("rm -f %s/class/esl/*" % eslDirName)
        fOut=popen("rm -f %s/lbj/esl/*" % eslDirName)
        #fOut=popen("rm -f ../../article/esl/class/esl/*")
        #fOut=popen("rm -f ../../article/esl/lbj/esl/*")
        #compile
        print >>stderr, 'Training LBJ'

        #***for harmony***
        #os.system("java -Xmx1G -XX:MaxPermSize=1500m -cp $CLASSPATH:class LBJ2.Main -sourcepath src -gsp lbj -d class %s" % (LBJprogramName))
        #for gargamel replace above line with
        #e.g. LBJprogramName prepositionLearner.lbj
        #system("java -Xmx7G -XX:MaxPermSize=5G -cp $CLASSPATH:class LBJ2.Main -sourcepath src -gsp lbj -d class %s" % (lbjScript))
	system("java -Xmx5G -XX:MaxPermSize=5G -cp $CLASSPATH:%s:class LBJ2.Main -sourcepath src -gsp lbj -d class %s" % (classPath,lbjScript))
        system("javac -classpath $CLASSPATH:%s:class -sourcepath lbj:src -d class src/esl/*.java" % classPath)
        #system("export CLASSPATH=$CLASSPATH:%s/class/:%s" % (eslDirName,eslDirName))
	

#testFiles is a list
#resultFiles={} testFileName=resultFileName
def TestLBJ(testProgramName,eslDirName, testFiles,resultFiles):
 chdir("%s" % eslDirName)
 #system("export CLASSPATH=$CLASSPATH:%s/class/" % eslDirName)
 classPath=eslDirName+':'+eslDirName+'/class/'
 #system("export CLASSPATH=$CLASSPATH:%s/class/:%s/" % (eslDirName,eslDirName))
 print >>stderr, 'Testing'
 #system("echo CLASSPATH $CLASSPATH")
 curTestF=0
 for i in range (len(testFiles)):
                testFile=testFiles[i]
                resultFile=resultFiles[testFile]
                inputToTestF = testFile
                outputResultFile=resultFiles[testFile]
                print >>stderr, 'Testing on file', testFile
                print >>stderr, 'Result file', outputResultFile
                #***Uncomment for harmony***
                #os.system("java -Xmx1g  -XX:MaxPermSize=1g %s.%s %s >%s" % (package, testProgramName, inputToTestF, outputResultFile))
                #***Uncomment for gargamel***
                print >>stderr, 'resultFile', outputResultFile
                fOut=popen("java -Xmx6g  -XX:MaxPermSize=4G -cp $CLASSPATH:%s:class esl.%s %s >%s" % (classPath,testProgramName, inputToTestF, outputResultFile))

def WriteLBJFeatureWeights(eslDirName,featureFileName):
  #uncomment to save feature file
  classPath=eslDirName+':'+eslDirName+'/class/'
  chdir("%s" % eslDirName)
  system("java -Xmx20G -XX:MaxPermSize=7G -cp $CLASSPATH:%s:class LBJ2.learn.LearnerToText esl.PrepositionUnconfuse >%s" % (classPath, featureFileName))


#split data into train/test (take for training as much as needed, the rest will go into test file)
#use new distribution of labels to create training data
#if necessary perturb the sources using source transition probs
#set labelProbsF and sourceProbsF to "None" if don't want to perturb the data
def MakeTrainTestWithLabelProbsPerturbSourceProbs(dataDir, trainSize, startTrain, trainF, testF, labelProbsF, sourceProbsF, testSize):
        curDir=getcwd()
 	if labelProbsF!='None':
	   probsF=open(labelProbsF, 'r')
	   labelNumber={}
	   for l in probsF:
		terms=l.split()
		label=terms[0]
		p=float(terms[1])
		number=p*trainSize
		labelNumber[label]=number

	   probsF.close()
		
#	outputTrain=open(trainF,'w')
	#outputTest=open(testF,'w')
	fileList=listdir(dataDir)
	curExample=0.0
	tempTrain=open(curDir+"/tempTrain",'w')
	tempTest=open(curDir+"/tempTest",'w')
	trainTotal=0
	testTotal=0
	for f in fileList:
		if trainTotal == trainSize and testTotal==testSize:
		#	tempTrain.close()
		#	tempTest.close()
			#normalize and perturb the data
			break
		outF=open(dataDir+f,'r')
		for l in outF:
			if curExample>=startTrain and trainTotal<trainSize:
				if l.strip()=='':
					tempTrain.write(l)
				else:
					terms=l.split()
					lab=terms[1]
					if labelProbsF=='None':
						tempTrain.write(l)
						trainTotal+=1
					elif labelNumber[lab] >0:
						labelNumber[lab]=labelNumber[lab]-1
						tempTrain.write(l)
						trainTotal+=1
			elif curExample<startTrain or trainTotal>=trainSize:
			   if l.strip():
				curExample+=1
			   if testTotal<testSize:
				if l.strip()=='':
					tempTest.write(l)
				else:
					testTotal+=1
					tempTest.write(l)
	#perturb  the train data
	tempTrain.close()
        tempTest.close()
	tempTest=curDir+'/tempTest'
	tempTrain=curDir+"/tempTrain"
	if sourceProbsF!='None':
		system("/scratch/rozovska/learner/prep/experiments/perturbData.py %s %s  >%s/trainTempPerturb" % (tempTrain,sourceProbsF,curDir))
		system("/scratch/rozovska/learner/prep/experiments/perturbData.py %s %s  >%s/testTempPerturb" % (tempTest,sourceProbsF,curDir))
		tempTrain=curDir+"/trainTempPerturb"
		tempTest=curDir+"/testTempPerturb"
	#normalize test and train data
	system("/scratch/rozovska/learner/prep/experiments/normTrainTest.py %s %s" % (tempTrain, trainF))
	system("/scratch/rozovska/learner/prep/experiments/normTrainTest.py %s %s" % (tempTest, testF))

def NormTrainTest(inputF, outputF):
   f=open(inputF,'r')
   outputFile=open(outputF,'w')

   nonEmptyLines=0
   flag=1
   curL=0
   for l in f:
		curL+=1
		if nonEmptyLines > 999:
			outputFile.write("\n")
			flag=1
			nonEmptyLines=0
		if 'startend' in l:
			nonEmptyLines+=1
			terms=l.split()
			newL=' '.join(terms)
			outputFile.write("%s\n" % newL)
			flag=0
		elif l.strip()=='':
			if flag==0:
				outputFile.write("\n")
				flag=1
				nonEmptyLines=0
   f.close()
   outputFile.close()

def MakeProbTable(confusionProbF):
	probTable={}
	for l in confusionProbF:
		terms=l.split()
		label=terms[0]
		probTable[label]={}
	
		for i in terms[1:]:
			pair=i.split(':')
			source=pair[0]
			prob=float(pair[1])
			probTable[label][source]=prob
	return probTable

def GenerateSource(probTable, label):
        randomProb=random()
        sortedProbs=[]
        start=0.0
        for i in probTable[label]:
                if probTable[label][i]>0:
                 sortedProbs.append((probTable[label][i]+start, i))
                 start+=probTable[label][i]
        sortedProbs.sort()
        #print >>stderr, sortedProbs, label
        start=0.0
	source='NotFound'
        for i in sortedProbs:
                p=i[0]
                if randomProb > start and randomProb <p:
                        source=i[1]
                        break
                start=p
        #print >>stderr, label, source
	if source=='NotFound':
		source=label
        return source


def PerturbData(columnFile, outputF, probTableF):
   f=open(columnFile,'r')
   confusionProbF=open(probTableF,'r')
   outF=open(outputF,'w')

   probTable=MakeProbTable(confusionProbF)
   curL=0
   for l in f:
	curL+=1
	if curL%100000==0:
		pass
	if l.strip()=='':
		#print
		outF.write('\n')
	else:
		terms=l.split()
		w=terms[0]
		source=GenerateSource(probTable, w)
		#print source,
		outF.write(" %s" % source)
		for t in terms[1:]:
			   outF.write(" %s " % t)
		outF.write("\n")
   f.close()
   confusionProbF.close()
   outF.close()

