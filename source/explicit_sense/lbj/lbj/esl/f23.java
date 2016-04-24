// Modifying this comment will cause the next execution of LBJ2 to overwrite this file.
// F1B88000000000000000D6BC13A02C0401500DBAC76148992C41AD9A92C6C238D95703F7570463BCEC4A29CDDDC10CEFDB9CCF9D81CD12F1E827F6CA3BB58DC5055179D3EB0BC019ADDB8173E81B43A4AD8625DE8562F785CB52D07D4A8EB74E1F3E4DD293B831F761E4886B0FC851BEF081C4E9FFC7000000

package esl;

import LBJ2.classify.*;
import LBJ2.infer.*;
import LBJ2.learn.*;
import LBJ2.nlp.*;
import LBJ2.parse.*;
import java.util.LinkedList;
import java.util.Set;


public class f23 extends Classifier
{
  public f23()
  {
    containingPackage = "esl";
    name = "f23";
  }

  public String getInputType() { return "esl.Preposition"; }
  public String getOutputType() { return "discrete%"; }

  public FeatureVector classify(Object __example)
  {
    if (!(__example instanceof Preposition))
    {
      String type = __example == null ? "null" : __example.getClass().getName();
      System.err.println("Classifier 'f23(Preposition)' defined on line 127 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    Preposition p = (Preposition) __example;

    FeatureVector __result;
    __result = new FeatureVector();
    String __id;
    String __value;

    if ((p.getFeature("f23")).endsWith("NA") == false)
    {
      __id = "" + (p.getFeature("f23"));
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
      System.err.println("Classifier 'f23(Preposition)' defined on line 127 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    return super.classify(examples);
  }

  public int hashCode() { return "f23".hashCode(); }
  public boolean equals(Object o) { return o instanceof f23; }
}

