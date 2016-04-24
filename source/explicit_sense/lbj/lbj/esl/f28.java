// Modifying this comment will cause the next execution of LBJ2 to overwrite this file.
// F1B88000000000000000D6BC13A02C0401500DBAC76148992C41652A6A0B1BC0676D1CCF5D109DC2B339A427773700BF7F623F76360778C783ACDB1BECE616371455C56F8F2C2344A67F26CD836C2D82963A945B3699CF161F6943C5392AFE197CF8357B4EC2E4CF958312AD2C3365CAF3E73423D9C7000000

package esl;

import LBJ2.classify.*;
import LBJ2.infer.*;
import LBJ2.learn.*;
import LBJ2.nlp.*;
import LBJ2.parse.*;
import java.util.LinkedList;
import java.util.Set;


public class f28 extends Classifier
{
  public f28()
  {
    containingPackage = "esl";
    name = "f28";
  }

  public String getInputType() { return "esl.Preposition"; }
  public String getOutputType() { return "discrete%"; }

  public FeatureVector classify(Object __example)
  {
    if (!(__example instanceof Preposition))
    {
      String type = __example == null ? "null" : __example.getClass().getName();
      System.err.println("Classifier 'f28(Preposition)' defined on line 152 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    Preposition p = (Preposition) __example;

    FeatureVector __result;
    __result = new FeatureVector();
    String __id;
    String __value;

    if ((p.getFeature("f28")).endsWith("NA") == false)
    {
      __id = "" + (p.getFeature("f28"));
      __value = "true";
      __result.addFeature(new DiscretePrimitiveStringFeature(this.containingPackage, this.name, __id, __value, valueIndexOf(__value), (short) 0));
    }
    return __result;
  }

  public FeatureVector[] classify(Object[] examples)
  {
    if (!(examples instanceof Preposition[]))
    {
      String type = examples == null ? "null" : examples.getClass().getName();
      System.err.println("Classifier 'f28(Preposition)' defined on line 152 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    return super.classify(examples);
  }

  public int hashCode() { return "f28".hashCode(); }
  public boolean equals(Object o) { return o instanceof f28; }
}

