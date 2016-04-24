#files that are required: 
(1) train.small (see the format)
(2) test.small (same format as train)
(3) prep.lbj -- use the file in this directory

#(1) (generate feature file)
./writeLBJFile.py prep.lbj train.small 4 >prepNew.lbj
#(2) Generate preposition java from your input file
./WritePrepositionJava.py specsFile train.small src/esl/Preposition.java18Feats >src/esl/Preposition.java
#(3) Train classifier and test it (output saved to outputFile
/home/alla/lbj/runLBJ.py /home/alla/lbj/train.small /home/alla/lbj/prepNew.lbj /home/alla/lbj/test.small outputFile /home/alla/lbj/
