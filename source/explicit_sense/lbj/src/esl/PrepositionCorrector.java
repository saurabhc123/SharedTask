package esl;
import java.util.*;
import LBJ2.parse.*;
import LBJ2.nlp.*;
import LBJ2.classify.*;
import LBJ2.learn.*;
public class PrepositionCorrector
{
   public static void main(String[] args)
   {
	 if (args.length != 1)
	{
	   System.err.println(
		"usage: java esl.PrepositionCorrector <testing set>");
	   System.exit(1);
	}
	
	String testingFile = args[0];
	
	PrepositionUnconfuse unconfuser = new PrepositionUnconfuse();
	PrepositionParser parser = new PrepositionParser (new ColumnFormat (testingFile));

	for (Preposition p = (Preposition) parser.next(); p != null; p = (Preposition) parser.next())
	{
//      System.out.println(p+" "+p.getFeature("headOfComplPhrase") +" "+p.getFeature("pathFromPrepToRoot")+" "+p.getFeature("governingPhraseHeadWord")+" " + p.getFeature("governingPhraseHeadTag")+" "+p.getFeature("complStructure")+ " "+p.getFeature("PPpositionInGoverningPhrase")+" "+p.getFeature("complTag")+ " " +p.getFeature("GoverningPhraseStructure")+" "+p.getFeature("tagOfHeadOfComplPhrase")+ " "+p.getFeature("parentTag")+" "+p.getFeature("governingPhraseTag"));

      String prediction = unconfuser.discreteValue(p);
      double k = 0.1;
      ScoreSet pScores = unconfuser.scores(p);
      Score[] scores =pScores.toArray();
      //System.out.print("label " + p.label+" prediction "+ prediction + " : ");
      //for (int i = 0; i<scores.length;i++)
      //{
       //  System.out.print(scores[i].toString()+" ");
     // }
       //System.out.println();

      for (int i = 0; i<scores.length;i++)
      {
	pScores.put(scores[i].value, scores[i].score*k);
      }

      //normalize scores
      //Sigmoid sig=new Sigmoid();
      Softmax soft = new Softmax();

      ScoreSet nomScores=soft.normalize(pScores);
      //ScoreSet nomScores=sig.normalize(pScores);
      Score[] normalized =nomScores.toArray();
      //Score[] scores =pScores.toArray();
      //System.out.print("label " + p.label+" prediction "+ prediction + " : ");
      System.out.print("source="+p.getFeature("source")+" label="+p.label+" prediction="+ prediction + " " +p.getFeature("exampleID")+ " : ");
      for (int i = 0; i<normalized.length;i++)
      {
      System.out.print(normalized[i].toString()+" ");
      }
      System.out.print(" "+p.getFeature("exampleID"));
      //System.out.print(":"+p.getFeature("wAfter"));
      //System.out.print(":"+p.getFeature("source"));
      //System.out.print(" norm");
      System.out.println();
      
	
//      for (int i = 0; i<predictions.length;i++)
  //    {
   ///   if (!prediction.equals(p.label))
        //System.out.println("Incorrect " + p.toString()+" label " + p.label + " prediction  " + prediction );
//	System.out.print(predictions[i]+" ");
//	System.out.println();
      //else
	//System.out.println("Correct " + p.toString()+" " + p.label);
  //    }

    	}
  }
}
