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
{"source","0"}, {"wBefore","3"},  {"w2Before","4"},  {"w3Before","5"},  {"wAfter","6"},  {"w2After","7"},  {"w3After","8"},  {"posBefore","9"},  {"pos2Before","10"},  {"pos3Before","11"},  {"posAfter","12"},  {"pos2After","13"},  {"pos3After","14"},  {"pBpA","15"},  {"p2BpB","16"},  {"pAp2A","17"},  {"pBwB","18"},  {"pAwA","19"},  {"p2Bw2B","20"},  {"p2Aw2A","21"},  {"p2BpBpA","22"},  {"pBpAp2A","23"},  {"pAp2Ap3A","24"},  {"p3Bp2BpB","25"},  {"p2BpBwA","26"},  {"p2BwBwA","27"},  {"p2BwBpA","28"},  {"w2BpBpA","29"},  {"w2BwBpA","30"},  {"p3Bp2BpBpA","31"},  {"p2BpBpAp2A","32"},  {"pBpAp2Ap3A","33"},  {"pBwAw2A","34"},  {"p2BpBwAw2A","35"},  {"headWord","36"},  {"wBAndHeadWord","37"},  {"w2BwBAndHeadWord","38"},  {"posBAndHeadWord","39"},  {"pos2BposBAndHeadWord","40"},  {"wBeforeWAfter","41"},  {"w2BeforeWBefore","42"},  {"wAfterW2After","43"},  {"wAfterW2AfterW3After","44"},  {"w2BwBwA","45"},  {"wBwAw2A","46"},  {"w3Bw2BwB","47"},  {"w4Bw3Bw2BwB","48"},  {"w3Bw2BwBwA","49"},  {"w2BwBwAw2A","50"},  {"wBwAw2Aw3A","51"},  {"wAw2Aw3Aw4A","52"},  {"exampleID","54"},
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
  
