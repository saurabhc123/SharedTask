
import json
import sys
import explicitconnective.evaluate_connective_classifier_maxent
import subprocess

class DiscourseParser(object):

    def __init__(self):
        pass

    final_output_file_name = "output.json"
    explicit_connective_output_file_name = "explicit_connective_relations.json"
    ps_arg1_extractor_output_file_name = "ps_arg1_extractor_relations.json"
    ps_arg2_extractor_output_file_name = "ps_arg2_extractor_relations.json"
    explicit_args_output_file_name = "explicit_args_relations.json"
    explicit_sense_output_file_name = "explicit_sense_relations.json"
    explicit_sense_lbj_folder = "/lbj"

    def run_connective_classifier(self, input_parses_file, output_path):
        output_relations_file = output_path + self.explicit_connective_output_file_name
        explicitconnective.evaluate_connective_classifier_maxent.main(input_parses_file, output_relations_file)

    def run_explicit_args_extractor(self,input_parses_file ,output_path):
        input_relations_file = output_path + self.explicit_connective_output_file_name
        output_relations_file = output_path + self.explicit_args_output_file_name
        return subprocess.call(["explicit_args/runExplicitArgs.sh", input_parses_file, input_relations_file, output_relations_file])

    def run_ps_arg1_extractor(self,input_parses_file, output_path):
        input_relations_file = output_path + self.explicit_args_output_file_name
        output_relations_file = output_path + self.ps_arg1_extractor_output_file_name
        return subprocess.call(["PSArg1/runPSArg1Test.sh", input_parses_file, input_relations_file, output_relations_file])

    def run_ps_arg2_extractor(self,input_parses_file, output_path):
        input_relations_file = output_path + self.ps_arg1_extractor_output_file_name
        output_relations_file = output_path + self.ps_arg2_extractor_output_file_name

    def run_explicit_sense_classifier(self,input_parses_file ,output_path):
        input_relations_file = output_path + self.ps_arg2_extractor_output_file_name
        output_relations_file = output_path + self.explicit_sense_output_file_name


if __name__ == '__main__':
    input_parses_file = sys.argv[1]
    output_dir = sys.argv[2]
    parser = DiscourseParser()
    parser.run_connective_classifier(input_parses_file, output_dir)
    parser.run_explicit_args_extractor(input_parses_file, output_dir)
    if parser.run_ps_arg1_extractor(input_parses_file, output_dir) == 0:
        if parser.run_ps_arg2_extractor(input_parses_file, output_dir) == 0:
            parser.run_explicit_sense_classifier(input_parses_file, output_dir)
        else:
            print "Error encountered while running the ps_arg2 extractor"
    else:
        print "Error encountered while running the ps_arg2 extractor"

