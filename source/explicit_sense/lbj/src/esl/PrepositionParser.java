package esl;

import LBJ2.nlp.*;
import LBJ2.nlp.seg.Token;
import LBJ2.parse.*;

public class PrepositionParser implements Parser
{
   protected Parser parser;
//   protected LinkedVector sentence;
   //protected Token token;
   protected LinkedVector currentSentence;
   protected LinkedVector labels;
   protected String tokenLabel;
//   protected LinkedVector nounPhrase;
   protected LinkedVector preposition;
   protected LinkedVector prepositionBoundaries;
  //index is the index to current word in sentence
   protected int index;   
   protected int sentenceIndex;
   //array of features of current sentence (total 14, skip first 3 - word, label, startend)
   protected String[][] sentenceFeatures;


 /**
    * The Parser that this constructor takes as an argument is
    * expected to return an array of Strings representing the information 
    * in the columns of this row from its next() method. Each row represents
    * an input word. Each column contains field_name::field_value. First column
    * is word form, second column is 'label' (e.g. 'the', 'a', '0', 'mid', 
    *'end'), other columns will correspond to features and values
   **/

  public PrepositionParser(Parser p)
  {
    parser = p;
    currentSentence = arrayToSentence (parser.next());
//    sentenceFeatures=null;
  }


  private static Word getField(Object wordFeatures, int fieldIndex)
  {
//	System.out.print(" getField processing "+((String[])wordFeatures)[fieldIndex]);
	
	if (wordFeatures == null) return null;
	Word w = new Word (((String[])wordFeatures)[fieldIndex]);
	return w;
  }


  private void AddFeatures(Object wordFeatures, int wordIndex)
  {
	if (wordFeatures == null) sentenceFeatures[wordIndex]=null;
	int i=0;
	//55 is the total number of columns in train/test file (change that if number of columns increases)
	//while (i<18)
	//while (i < 64)
	while (i<33)
	{
		String feature =((String[])wordFeatures)[i];
		sentenceFeatures[wordIndex][i]=feature;
	//	System.out.print(wordIndex+" "+ i+" "+ sentenceFeatures[wordIndex][i]);
		i++;
	
	}

  }
//this method calls next() in ColumnFormat parser until it encounters string signifying end of sentence
// the method also creates LinkedVector labels for the current sentence and LinkedVector prepositionBoundaries
  private LinkedVector arrayToSentence(Object wordFeatures)
  {
	labels = null;
	prepositionBoundaries = null;
	//array[0] is word form, array[1] is label, 
	//array[2] indicates start/end phrase e.g. start_id, end_id, None
	if (wordFeatures == null) return null;
	Token prevWord = null;
	Token prevLabel = null;
	Token prevBoundary = null;
	sentenceFeatures = new String[10000000][33];
	///call next() on parser until end of current sentence 
	// TO DO: end of sentence currently empty line
	int curWord=0;
	while(wordFeatures != null && (((String[])wordFeatures).length)>1) //(!w.form.equals ("end_sentence")))
	{	 
		
		Word w = getField(wordFeatures, 0);
		Word label = getField(wordFeatures, 1);
		Word boundary = getField(wordFeatures, 2);

		Token token = new Token (w, prevWord, null);
		//System.out.println(" word "+w);
		Token labelToken = new Token (label, prevLabel, null);
		//System.out.print("label " + label);
		Token boundaryToken = new Token (boundary, prevBoundary, null);
		//System.out.println("boundary " + boundary);
		
		if (prevWord != null)
		{
			prevWord.next=token;
			prevLabel.next=labelToken;
			prevBoundary.next=boundaryToken;
		}
		prevWord = token;
		prevLabel=labelToken;
		prevBoundary=boundaryToken;
		AddFeatures(wordFeatures, curWord);
		curWord++;
		wordFeatures = parser.next();		
	}

	labels = new LinkedVector(prevLabel);
	prepositionBoundaries = new LinkedVector(prevBoundary);
	//System.out.println("Sentence index " + ++sentenceIndex);
	return new LinkedVector(prevWord);
  }

  //return next Preposition Object
  public Object next()
  {
	if (currentSentence == null) return null;
	Preposition result = getPreposition();
		
	//iterate over sentences as long as result=null and there are sentences left
	while (result == null && currentSentence != null)
	{
		++index;
		//go to next sentence if reached end of current sentence
		while (currentSentence != null && index >= currentSentence.size())
		{
			currentSentence= arrayToSentence(parser.next());
			index = 0;	
		}
		
		if (currentSentence == null) return null; //case when previous loop reached end of file
		result = getPreposition();
	}
	if (result == null) return null; //case when previous loop reached end of file
	//maybe increment index here instead of in getNounPhrase()
	index++;
	
	//go to next sentence if reached end of current sentence
	while (currentSentence != null && index >= currentSentence.size())
	{
		currentSentence = arrayToSentence(parser.next());
		index = 0;
	}
	//System.out.println(result.toString());	
	return result;

  }


  //this method will be called on every index
  protected Preposition getPreposition()
  {
	//System.out.println("getNounPhrase");
	//System.out.println(index);
	//System.out.println(((Token)currentSentence.get(index)).form);
	//System.out.println(((Token)labels.get(index)).form);
//	System.out.println(sentenceFeatures[index][3]);//" "+sentenceFeatures[index][4]+" "sentenceFeatures[index][5]+" "sentenceFeatures[index][6]+" "sentenceFeatures[index][7]+" ");

	
	String wordLabel = ((Token)labels.get(index)).form ;
	String boundary = ((Token)prepositionBoundaries.get(index)).form;
	preposition = null;

//	assert currentWord != null
//		: "Current word is null! " + index + ", " + currentSentence.size();
	
	if (boundary.startsWith("start"))

	{
 	 // System.out.println(((Token)currentSentence.get(index)).form);
	   		
	   //if preposition is just one word
	   if (boundary.endsWith("end"))
	{

		return new Preposition(currentSentence, index, index, wordLabel, sentenceFeatures[index]);
	}
	   String phraseID = boundary.substring("start".length(), boundary.length());
	   String endPhraseID = "end"+phraseID;
	  // System.out.println(endPhraseID);
	   int j = index;
	   while (!boundary.equals(endPhraseID) &&  j < currentSentence.size())
	   {
		j++;
                boundary = ((Token)prepositionBoundaries.get(j)).form;
		
	   }
	//   System.out.println(index + " " + j);
	   return new Preposition(currentSentence, index, j, wordLabel,  sentenceFeatures[index]);
	}
	
	return null;
	}
   public void reset()
   {
	parser.reset();
	currentSentence = null;
   	labels = null;
   	tokenLabel = null;
   	preposition = null;
   	prepositionBoundaries = null;
   	index = 0;
	sentenceFeatures = null;

	
   }

   public void close()
   {
	
   }
}
