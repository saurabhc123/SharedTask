echo
echo "Creating LBJ configuration file from feature file..."
python writeLBJFile.py prep.lbj trainES.column 4 >ExplicitSense.lbj
echo "ExplicitSense.lbj done!"

echo
echo "Generating Preposition.java..."
python WritePrepositionJava.py specsFile trainES.column src/esl/Preposition.java18Feats >src/esl/Preposition.java
echo "Preposition.java done!"

echo
echo "Running Perceptron Classifier and making predictions..."
python runLBJ.py trainES.column ExplicitSense.lbj testES.column outputFile .
echo "Predictions done!"
