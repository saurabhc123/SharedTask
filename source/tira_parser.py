
import json
import sys
import explicitconnective.evaluate_connective_classifier_maxent2
import implicit_args.argumentClassifier
import subprocess
import os
import implicit_sense.ImplicitSense 
import implicit_sense_xz.extract_adjacent_sentences

class DiscourseParser(object):

    def __init__(self):
        pass
    
    os.environ["PATH"] = "/home/VTNLPS16/jdk1.8.0_91/bin:" + os.environ["PATH"]
    os.environ["CLASSPATH"] = "/home/VTNLPS16/lbjClassifier/LBJ2Library.jar:/home/VTNLPS16/lbjClassifier/LBJ2.jar"
    final_output_file_name = "/output_relations.json"
    explicit_connective_output_file_name = "/explicit_connective_relations.json"
    ps_arg1_extractor_output_file_name = "/ps_arg1_extractor_relations.json"
    ps_arg2_extractor_output_file_name = "/ps_arg2_extractor_relations.json"
    explicit_args_output_file_name = "/explicit_args_relations.json"
    explicit_sense_output_file_name = "/explicit_sense_relations.json"
    implicit_sense_output_file_name = "/implicit_sense_relations.json"
    implicit_args_output_file_name = "/implicit_args_relations.json"
    explicit_sense_lbj_folder = "explicit_sense/lbj"
    implicit_adjacent_sentences_output_file_name = "/implicit_adjacent_sentences_relations.json"

    def run_connective_classifier(self, input_parses_file, output_path):
        output_relations_file = output_path + self.explicit_connective_output_file_name
        explicitconnective.evaluate_connective_classifier_maxent2.main(input_parses_file, output_relations_file)

    def run_explicit_args_extractor(self,input_parses_file ,output_path):
        input_relations_file = output_path + self.explicit_connective_output_file_name
        output_relations_file = output_path + self.explicit_args_output_file_name
        os.system("explicit_args/runExplicitArgs.sh %s %s %s %s" % (input_relations_file, input_parses_file, ".", output_relations_file))

    def run_ps_arg1_extractor(self,input_parses_file, output_path):
        input_relations_file = output_path + self.explicit_args_output_file_name
        output_relations_file = output_path + self.ps_arg1_extractor_output_file_name
        return os.system("PSArg1/runPSArg1Test.sh %s %s %s" % (input_relations_file, input_parses_file, output_relations_file))

    def run_ps_arg2_extractor(self,input_parses_file, output_path):
        input_relations_file = output_path + self.ps_arg1_extractor_output_file_name
        output_relations_file = output_path + self.ps_arg2_extractor_output_file_name
        os.system("PSArg2/runPSArg2Test.sh %s %s %s" % (input_relations_file, input_parses_file, output_relations_file))

    def run_explicit_sense_classifier(self,input_parses_file ,output_path):
        input_relations_file = output_path + self.ps_arg2_extractor_output_file_name
        output_relations_file = output_path + self.explicit_sense_output_file_name
        return subprocess.call(["explicit_sense/runExplicitSense.sh",input_relations_file, input_parses_file, self.explicit_sense_lbj_folder , output_relations_file])

    def run_implicit_adjacent_sentence_classifier(self, input_parses_file, output_path, input_folder):
        input_relations_file = output_path + self.explicit_sense_output_file_name
        output_relations_file = output_path + self.implicit_adjacent_sentences_output_file_name
        implicit_sense_xz.extract_adjacent_sentences.produceRelationsFile(input_relations_file, input_parses_file, input_folder  , output_relations_file )

    def run_implicit_sense_classifierPass1(self, input_parses_file, output_path):
        input_relations_file = output_path + self.implicit_adjacent_sentences_output_file_name
        output_relations_file = output_path + self.implicit_sense_output_file_name
        implicit_sense.ImplicitSense.implicitSense(input_relations_file, input_parses_file, output_relations_file)

    def run_implicit_args_extractor(self, input_parses_file, output_path):
        input_relations_file = output_path + self.implicit_sense_output_file_name
        output_relations_file = output_path + self.implicit_args_output_file_name
        implicit_args.argumentClassifier.extract_implicit_arguments(input_relations_file, input_parses_file, output_relations_file)
    
    def run_implicit_sense_classifierPass2(self, input_parses_file, output_path):
        input_relations_file = output_path + self.implicit_args_output_file_name
        output_relations_file = output_path + self.final_output_file_name
        implicit_sense.ImplicitSense.implicitSense(input_relations_file, input_parses_file, output_relations_file)

if __name__ == '__main__':
    input_parses_file = sys.argv[1]+ "/parses.json";
    output_dir = sys.argv[3]
    print "Input Dir: ", input_parses_file;
    print "Output Dir: ", output_dir;
    input_folder = os.path.dirname(os.path.abspath(input_parses_file)) + '/raw';
    parser = DiscourseParser()
    parser.run_connective_classifier(input_parses_file, output_dir)
    parser.run_explicit_args_extractor(input_parses_file, output_dir)
    parser.run_ps_arg1_extractor(input_parses_file, output_dir)
    parser.run_ps_arg2_extractor(input_parses_file, output_dir)
    parser.run_explicit_sense_classifier(input_parses_file, output_dir)
    parser.run_implicit_adjacent_sentence_classifier(input_parses_file, output_dir, input_folder ) 
    parser.run_implicit_sense_classifierPass1(input_parses_file, output_dir)
    parser.run_implicit_args_extractor(input_parses_file, output_dir)
    parser.run_implicit_sense_classifierPass2(input_parses_file, output_dir)
    os.system("/home/VTNLPS16/SharedTask/output/convertRelationOutput.py %s/output_relations.json %s/output.json" % (output_dir, output_dir))
