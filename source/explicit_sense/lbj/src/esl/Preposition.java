package esl;

import LBJ2.nlp.*;
import LBJ2.nlp.seg.Token;
import LBJ2.parse.*;

public class Preposition
{
   public LinkedVector sentence;
//   public LinkedVector sentenceWithoutPrep; //same as origSentence but with preposition removed
			
   public int startPhrase, endPhrase; //indices of first and last members of preposition (for multi-word prepositions)
   public String label; //label 'with', 'on', 'before', etc.
   protected String[] wordFeatures;
   
   //maybe add more variables here for other features
public static final String[][] features=
{
{"source","0"}, {"label","1"}, {"startend","2"}, {"exampleID","3"}, {"f01","4"}, {"f02","5"}, {"f03","6"}, {"f04","7"}, {"f05","8"}, {"f06","9"}, {"f07","10"}, {"f08","11"}, {"f09","12"}, {"f10","13"}, {"f11","14"}, {"f12","15"}, {"f13","16"}, {"f14","17"}, {"f15","18"}, {"f16","19"}, {"f17","20"}, {"f18","21"}, {"f19","22"}, {"f20","23"}, {"f21","24"}, {"f22","25"}, {"f23","26"}, {"f24","27"}, {"f25","28"}, {"f26","29"}, {"f27","30"}, {"f28","31"}, {"f29","32"}, 
};
//System.out.println(1);
   public  Preposition (LinkedVector sen, int s, int e, String lab, String[] currentFeatures)
   {
	startPhrase = s;//index of first word of prep
	
	endPhrase = e;//index of last word of prep
	label = lab;
	sentence=sen;
	wordFeatures=currentFeatures;
//	sentenceWithoutPrep = getPhraseSentence(sen)
   }


  //return word immediately before the noun phrase
  public Token getPrevious()
  {
    if (startPhrase - 1 >= 0) return (Token) sentence.get(startPhrase - 1);
    return null;
  }

  //return word immediately after the noun phrase
  public Token getNext()
  {
    if (endPhrase + 1 < sentence.size()) return (Token) sentence.get(endPhrase + 1);
    return null;
  }

  public String toString()
  {
    String result = ((Token) sentence.get(startPhrase)).form;
    for (int i = startPhrase + 1; i <= endPhrase; ++i)
    {
      result +=" ";
      result += ((Token) sentence.get(i)).form;
    }
    return result;
  }
 

  public String getFeature(String featureName)
  {
	int featureIndex=-1;
	for (int i=0; i<features.length;i++)
	{
	    if (features[i][0].equals(featureName))
	    {
		featureIndex = Integer.parseInt(features[i][1]);
		break;
	    }
	}
	
	return (String) wordFeatures[featureIndex];		
  }
}
  
