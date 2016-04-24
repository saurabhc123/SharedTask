// Modifying this comment will cause the next execution of LBJ2 to overwrite this file.
// F1B88000000000000000D4BCD4A02C0300501EBA461D282824FD3FFA2878073E90A6A09D425A9A7F733BBE666130FD735D96D8B5CE3CB7D8B49A96B452F72F452FCFBA1BBE478DDF0BC13CBEC16E147A6139B09B29B19B3970919C3B5430148012480124801248012481164811648116481164811E62EFF0A29BB45C000000

package esl;

import LBJ2.classify.*;
import LBJ2.infer.*;
import LBJ2.learn.*;
import LBJ2.nlp.*;
import LBJ2.parse.*;
import java.util.LinkedList;
import java.util.Set;


public class PrepositionUnconfuse$$1 extends Classifier
{
  private static final f01 __f01 = new f01();
  private static final f02 __f02 = new f02();
  private static final f03 __f03 = new f03();
  private static final f04 __f04 = new f04();
  private static final f05 __f05 = new f05();
  private static final f06 __f06 = new f06();
  private static final f07 __f07 = new f07();
  private static final f08 __f08 = new f08();
  private static final f09 __f09 = new f09();
  private static final f10 __f10 = new f10();
  private static final f11 __f11 = new f11();
  private static final f12 __f12 = new f12();
  private static final f13 __f13 = new f13();
  private static final f14 __f14 = new f14();
  private static final f15 __f15 = new f15();
  private static final f16 __f16 = new f16();
  private static final f17 __f17 = new f17();
  private static final f18 __f18 = new f18();
  private static final f19 __f19 = new f19();
  private static final f20 __f20 = new f20();
  private static final f21 __f21 = new f21();
  private static final f22 __f22 = new f22();
  private static final f23 __f23 = new f23();
  private static final f24 __f24 = new f24();
  private static final f25 __f25 = new f25();
  private static final f26 __f26 = new f26();
  private static final f27 __f27 = new f27();
  private static final f28 __f28 = new f28();
  private static final f29 __f29 = new f29();

  public PrepositionUnconfuse$$1()
  {
    containingPackage = "esl";
    name = "PrepositionUnconfuse$$1";
  }

  public String getInputType() { return "esl.Preposition"; }
  public String getOutputType() { return "discrete%"; }

  public FeatureVector classify(Object __example)
  {
    if (!(__example instanceof Preposition))
    {
      String type = __example == null ? "null" : __example.getClass().getName();
      System.err.println("Classifier 'PrepositionUnconfuse$$1(Preposition)' defined on line 166 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    FeatureVector __result;
    __result = new FeatureVector();
    __result.addFeatures(__f01.classify(__example));
    __result.addFeatures(__f02.classify(__example));
    __result.addFeatures(__f03.classify(__example));
    __result.addFeatures(__f04.classify(__example));
    __result.addFeatures(__f05.classify(__example));
    __result.addFeatures(__f06.classify(__example));
    __result.addFeatures(__f07.classify(__example));
    __result.addFeatures(__f08.classify(__example));
    __result.addFeatures(__f09.classify(__example));
    __result.addFeatures(__f10.classify(__example));
    __result.addFeatures(__f11.classify(__example));
    __result.addFeatures(__f12.classify(__example));
    __result.addFeatures(__f13.classify(__example));
    __result.addFeatures(__f14.classify(__example));
    __result.addFeatures(__f15.classify(__example));
    __result.addFeatures(__f16.classify(__example));
    __result.addFeatures(__f17.classify(__example));
    __result.addFeatures(__f18.classify(__example));
    __result.addFeatures(__f19.classify(__example));
    __result.addFeatures(__f20.classify(__example));
    __result.addFeatures(__f21.classify(__example));
    __result.addFeatures(__f22.classify(__example));
    __result.addFeatures(__f23.classify(__example));
    __result.addFeatures(__f24.classify(__example));
    __result.addFeatures(__f25.classify(__example));
    __result.addFeatures(__f26.classify(__example));
    __result.addFeatures(__f27.classify(__example));
    __result.addFeatures(__f28.classify(__example));
    __result.addFeatures(__f29.classify(__example));
    return __result;
  }

  public FeatureVector[] classify(Object[] examples)
  {
    if (!(examples instanceof Preposition[]))
    {
      String type = examples == null ? "null" : examples.getClass().getName();
      System.err.println("Classifier 'PrepositionUnconfuse$$1(Preposition)' defined on line 166 of ExplicitSense.lbj received '" + type + "' as input.");
      new Exception().printStackTrace();
      System.exit(1);
    }

    return super.classify(examples);
  }

  public int hashCode() { return "PrepositionUnconfuse$$1".hashCode(); }
  public boolean equals(Object o) { return o instanceof PrepositionUnconfuse$$1; }

  public java.util.LinkedList getCompositeChildren()
  {
    java.util.LinkedList result = new java.util.LinkedList();
    result.add(__f01);
    result.add(__f02);
    result.add(__f03);
    result.add(__f04);
    result.add(__f05);
    result.add(__f06);
    result.add(__f07);
    result.add(__f08);
    result.add(__f09);
    result.add(__f10);
    result.add(__f11);
    result.add(__f12);
    result.add(__f13);
    result.add(__f14);
    result.add(__f15);
    result.add(__f16);
    result.add(__f17);
    result.add(__f18);
    result.add(__f19);
    result.add(__f20);
    result.add(__f21);
    result.add(__f22);
    result.add(__f23);
    result.add(__f24);
    result.add(__f25);
    result.add(__f26);
    result.add(__f27);
    result.add(__f28);
    result.add(__f29);
    return result;
  }
}

