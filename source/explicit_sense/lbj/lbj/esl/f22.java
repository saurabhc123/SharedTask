// Modifying this comment will cause the next execution of LBJ2 to overwrite this file.
// F1B88000000000000000D6BC13A02C0401500DBAC76148992C41925D41636929ECA389FBA302B956762594EEE6E006FFEDC6EFC6C0E109BFE56C6CAB8B58D2505517932EB0BC019ADDB8173E41B63A4AD9625DE8566F785CB52DDFA9413C08C3D7C9AB7276172EFC2C901D65E91B16BF103BBD892AC7000000

package esl;

import LBJ2.classify.*;
import LBJ2.infer.*;
import LBJ2.learn.*;
import LBJ2.nlp.*;
import LBJ2.parse.*;
import java.util.LinkedList;
import java.util.Set;


public class f22 extends Classifier
{
  public f22()
  {
    containingPackage = "esl";
    name = "f22";
  }

  public String getInputType() { return "esl.Preposition"; }
  public String getOutputType() { return "discrete%"; }

  public FeatureVector classify(Object __example)
  {
    if (!(__example instanceof Preposition))
    {
      String type = __example == null ? "null" : __example.getClass().getName();
      System.err.println("Classifier 'f22(Preposition)' defined on line 122 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    Preposition p = (Preposition) __example;

    FeatureVector __result;
    __result = new FeatureVector();
    String __id;
    String __value;

    if ((p.getFeature("f22")).endsWith("NA") == false)
    {
      __id = "" + (p.getFeature("f22"));
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
      System.err.println("Classifier 'f22(Preposition)' defined on line 122 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    return super.classify(examples);
  }

  public int hashCode() { return "f22".hashCode(); }
  public boolean equals(Object o) { return o instanceof f22; }
}

