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
{"source","0"}, {"label","1"}, {"startend","2"}, {"exampleID","3"}, {"wBefore","4"}, {"w2B","5"}, {"w3B","6"}, {"wAfter","7"}, {"w2A","8"}, {"w3A","9"}, {"pB","10"}, {"p2B","11"}, {"p3B","12"}, {"pA","13"}, {"p2A","14"}, {"p3A","15"}, {"pBpA","16"}, {"p2BpB","17"}, {"pAp2A","18"}, {"pBwB","19"}, {"pAwA","20"}, {"wBpA","21"}, {"p2Bw2B","22"}, {"p2Aw2A","23"}, {"p2BpBpA","24"}, {"pBpAp2A","25"}, {"pAp2Ap3A","26"}, {"p3Bp2BpB","27"}, {"p2BpBwA","28"}, {"p2BwBwA","29"}, {"p2BwBpA","30"}, {"w2BpBpA","31"}, {"w2BwBpA","32"}, {"p3Bp2BpBpA","33"}, {"p2BpBpAp2A","34"}, {"pBpAp2Ap3A","35"}, {"pBwAw2A","36"}, {"p2BpBwAw2A","37"}, {"compHead","38"}, {"comp","39"}, {"prevW","40"}, {"prevV","41"}, {"headP","42"}, {"wBCompHead","43"}, {"w2BwBCompHead","44"}, {"vWBCompHead","45"}, {"vWBHeadPos","46"}, {"wBHeadPos","47"}, {"pBCompHead","48"}, {"p2BPBCompHead","49"}, {"vCompHead","50"}, {"vHeadPos","51"}, {"wBWA","52"}, {"w2BWB","53"}, {"wAW2A","54"}, {"wAW2AW3A","55"}, {"w2BwBwA","56"}, {"wBwAw2A","57"}, {"w3Bw2BwB","58"}, {"w4Bw3Bw2BwB","59"}, {"w3Bw2BwBwA","60"}, {"w2BwBwAw2A","61"}, {"wBwAw2Aw3A","62"}, {"wAw2Aw3Aw4A","63"}, 
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
  
