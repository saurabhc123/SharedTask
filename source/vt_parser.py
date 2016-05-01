
import json
import sys
import explicitconnective.evaluate_connective_classifier_maxent
import implicit_args.argumentClassifier
import subprocess
import os

class DiscourseParser(object):

    def __init__(self):
        pass

    final_output_file_name = "output.json"
    explicit_connective_output_file_name = "explicit_connective_relations.json"
    ps_arg1_extractor_output_file_name = "ps_arg1_extractor_relations.json"
    ps_arg2_extractor_output_file_name = "ps_arg2_extractor_relations.json"
    explicit_args_output_file_name = "explicit_args_relations.json"
    explicit_sense_output_file_name = "explicit_sense_relations.json"
    implicit_sense_output_file_name = "implicit_sense_relations.json"
    implicit_args_output_file_name = "implicit_args_relations.json"
    explicit_sense_lbj_folder = "explicit_sense/lbj"

    def run_connective_classifier(self, input_parses_file, output_path):
        output_relations_file = output_path + self.explicit_connective_output_file_name
        explicitconnective.evaluate_connective_classifier_maxent.main(input_parses_file, output_relations_file)

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

    def run_implicit_args_extractor(self, input_parses_file, output_path):
        input_relations_file = output_path + "relations_gold.json"
        output_relations_file = output_path + self.implicit_args_output_file_name
        implicit_args.argumentClassifier.extract_implicit_arguments(input_relations_file, input_parses_file, output_relations_file)


if __name__ == '__main__':
    input_parses_file = sys.argv[1]
    output_dir = sys.argv[2]
    parser = DiscourseParser()
    #parser.run_connective_classifier(input_parses_file, output_dir)
    #parser.run_explicit_args_extractor(input_parses_file, output_dir)
    #parser.run_ps_arg1_extractor(input_parses_file, output_dir)
    #parser.run_ps_arg2_extractor(input_parses_file, output_dir)
    #parser.run_explicit_sense_classifier(input_parses_file, output_dir)
    parser.run_implicit_args_extractor(input_parses_file, output_dir)
