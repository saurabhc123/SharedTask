// Modifying this comment will cause the next execution of LBJ2 to overwrite this file.
// F1B88000000000000000D6BC13A02C0401500DBAC76148992C04A55358D85A4A3BE06EFAE08C669D994529BBB9308DFB73B9F3B138704EEB791B1BE2E616B41455C5E88F2C2344A67F26CD835CAD82967A945B3699DF161F6947FB625C0302F4F17AEE9C95C98F3B07244B5976C68DE7756E8768C7000000

package esl;

import LBJ2.classify.*;
import LBJ2.infer.*;
import LBJ2.learn.*;
import LBJ2.nlp.*;
import LBJ2.parse.*;
import java.util.LinkedList;
import java.util.Set;


public class f11 extends Classifier
{
  public f11()
  {
    containingPackage = "esl";
    name = "f11";
  }

  public String getInputType() { return "esl.Preposition"; }
  public String getOutputType() { return "discrete%"; }

  public FeatureVector classify(Object __example)
  {
    if (!(__example instanceof Preposition))
    {
      String type = __example == null ? "null" : __example.getClass().getName();
      System.err.println("Classifier 'f11(Preposition)' defined on line 67 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    Preposition p = (Preposition) __example;

    FeatureVector __result;
    __result = new FeatureVector();
    String __id;
    String __value;

    if ((p.getFeature("f11")).endsWith("NA") == false)
    {
      __id = "" + (p.getFeature("f11"));
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
      System.err.println("Classifier 'f11(Preposition)' defined on line 67 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    return super.classify(examples);
  }

  public int hashCode() { return "f11".hashCode(); }
  public boolean equals(Object o) { return o instanceof f11; }
}

