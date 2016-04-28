echo "input_relations gold_relations output_file "
input_relations=$1
gold_relations=$2
output_file=$3
python convertRelationOutput.py $input_relations $output_file
python scorer/scorer.py $gold_relations $output_file
