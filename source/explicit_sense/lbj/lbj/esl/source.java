// Modifying this comment will cause the next execution of LBJ2 to overwrite this file.
// F1B88000000000000000B49CC2E4E2A4D2945582ECF2D2A4E45D8082A4D28CF2ECC29CCCFC35820D450B1D558A6500AC7961109BA79E9A52E69A9804E4AA682144DB296A5B24D20024507CA744000000

package esl;

import LBJ2.classify.*;
import LBJ2.infer.*;
import LBJ2.learn.*;
import LBJ2.nlp.*;
import LBJ2.parse.*;
import java.util.LinkedList;
import java.util.Set;


public class source extends Classifier
{
  public source()
  {
    containingPackage = "esl";
    name = "source";
  }

  public String getInputType() { return "esl.Preposition"; }
  public String getOutputType() { return "discrete"; }


  public FeatureVector classify(Object __example)
  {
    return new FeatureVector(featureValue(__example));
  }

  public Feature featureValue(Object __example)
  {
    String result = discreteValue(__example);
    return new DiscretePrimitiveStringFeature(containingPackage, name, "", result, valueIndexOf(result), (short) allowableValues().length);
  }

  public String discreteValue(Object __example)
  {
    if (!(__example instanceof Preposition))
    {
      String type = __example == null ? "null" : __example.getClass().getName();
      System.err.println("Classifier 'source(Preposition)' defined on line 12 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    Preposition p = (Preposition) __example;

    return "" + (p.getFeature("source"));
  }

  public FeatureVector[] classify(Object[] examples)
  {
    if (!(examples instanceof Preposition[]))
    {
      String type = examples == null ? "null" : examples.getClass().getName();
      System.err.println("Classifier 'source(Preposition)' defined on line 12 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    return super.classify(examples);
  }

  public int hashCode() { return "source".hashCode(); }
  public boolean equals(Object o) { return o instanceof source; }
}

