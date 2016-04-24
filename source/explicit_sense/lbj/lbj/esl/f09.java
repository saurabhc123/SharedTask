// Modifying this comment will cause the next execution of LBJ2 to overwrite this file.
// F1B88000000000000000D6BCBBA02C0401500DF59BC28033581C6D74A0B1BC0676D1CCD5D109DC2B339A42FFE6E30CEFC99CCF9D81CD12F1E827F6CA3BB58DC5055179D3EB0BC019ADDB8173E81B43A4AD8625DE8562F785CB52D07D4A8EB74E1F3E4DD293B831F761E4886B0FC851BEF0B3D26824C7000000

package esl;

import LBJ2.classify.*;
import LBJ2.infer.*;
import LBJ2.learn.*;
import LBJ2.nlp.*;
import LBJ2.parse.*;
import java.util.LinkedList;
import java.util.Set;


public class f09 extends Classifier
{
  public f09()
  {
    containingPackage = "esl";
    name = "f09";
  }

  public String getInputType() { return "esl.Preposition"; }
  public String getOutputType() { return "discrete%"; }

  public FeatureVector classify(Object __example)
  {
    if (!(__example instanceof Preposition))
    {
      String type = __example == null ? "null" : __example.getClass().getName();
      System.err.println("Classifier 'f09(Preposition)' defined on line 57 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    Preposition p = (Preposition) __example;

    FeatureVector __result;
    __result = new FeatureVector();
    String __id;
    String __value;

    if ((p.getFeature("f09")).endsWith("NA") == false)
    {
      __id = "" + (p.getFeature("f09"));
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
      System.err.println("Classifier 'f09(Preposition)' defined on line 57 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    return super.classify(examples);
  }

  public int hashCode() { return "f09".hashCode(); }
  public boolean equals(Object o) { return o instanceof f09; }
}

