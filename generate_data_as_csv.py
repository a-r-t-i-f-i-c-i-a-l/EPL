from test_language_models import CONTAINED_LITERAL, CONTAINER_LITERAL, CONTAINED_LITERAL_FT, CONTAINER_LITERAL_FT, \
    CONTAINMENT_NON_LITERAL, CONTAINMENT_NON_LITERAL_FT, SOURCE_LITERAL, SOURCE_LITERAL_FT, MOVING_OBJECT, \
    MOVING_OBJECT_FT, GOAL_LITERAL, \
    GOAL_LITERAL_FT, SOURCE_PATH_GOAL_NON_LITERAL, SOURCE_PATH_GOAL_NON_LITERAL_FT, ADJECTIVES, ADJECTIVES_FT, \
    QUALITIES, NAME_TO_DESCRIPTION, NAME_TO_DESCRIPTION2, NAME_TO_STATEMENT, \
    QUALITIES_FT, schema_type_question, source_path_goal_statement, containment_statement, quality_statment

from train_test_epl import CONTAINMENT_NON_LITERAL as CNL_VARS, SOURCE_PATH_GOAL_NON_LITERAL as SPGNL_VARS

from itertools import product
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('output', help='Output file name')


def extract_var_names(exp):
    # the variable names for non-literal cases exist in the EPL train/test dataset, so we extract them from there
    var_names = []
    pre, action, post = exp

    pre = pre if pre else []
    action_args = action.args if action else []
    post = post if post else []
    for part in pre:
        for arg in part.arguments:
            if arg.name not in var_names:
                var_names.append(arg.name)
    for arg in action_args:
        if arg.name not in var_names:
            var_names.append(arg.name)
    for part in post if post else []:
        for arg in part.arguments:
            if arg.name not in var_names:
                var_names.append(arg.name)
    return var_names


CLASSES = ['containment', 'source-path-goal', 'quality']
TYPES = ['literal', 'non-literal']
NATURAL_PHRASING = [0, 1]
YES_OR_NO_QUESTION = [0, 1]

CONTAINED_TOTAL = CONTAINED_LITERAL + CONTAINED_LITERAL_FT
CONTAINER_TOTAL = CONTAINER_LITERAL + CONTAINER_LITERAL_FT
MOVING_OBJECT_TOTAL = MOVING_OBJECT + MOVING_OBJECT_FT
SOURCE_TOTAL = SOURCE_LITERAL + SOURCE_LITERAL_FT
GOAL_TOTAL = GOAL_LITERAL + GOAL_LITERAL_FT
ADJECTIVES_TOTAL = ADJECTIVES + ADJECTIVES_FT
QUALITIES_TOTAL = QUALITIES + QUALITIES_FT


def literal_question_by_spec(objects, q_class, q_phrasing, q_yes_or_no, generator=None):
    phrasing = NAME_TO_DESCRIPTION2[q_class] if q_phrasing else NAME_TO_DESCRIPTION[q_class]
    if q_yes_or_no:
        return 'Yes or no, is this sentence a case of {schema_name}? Sentence: '.format(schema_name=phrasing), \
               NAME_TO_STATEMENT[generator if generator else q_class](*objects)
    else:
        return 'Is this sentence a case of a {schema_name}? Sentence: '.format(schema_name=phrasing), \
               NAME_TO_STATEMENT[generator if generator else q_class](*objects)


def nonliteral_question_by_spec(sentence, q_class, q_phrasing, q_yes_or_no):
    phrasing = NAME_TO_DESCRIPTION2[q_class] if q_phrasing else NAME_TO_DESCRIPTION[q_class]
    if q_yes_or_no:
        return "Yes or no, is this sentence a case of {schema_name}? Sentence: ".format(
            schema_name=phrasing), sentence
    else:
        return "Is this sentence a case of a {schema_name}? Sentence: ".format(
            schema_name=phrasing), sentence
    return


def generate_dataset():
    containment_tuples = product(CONTAINED_TOTAL, CONTAINER_TOTAL)
    spg_tuples = product(MOVING_OBJECT_TOTAL, SOURCE_TOTAL, GOAL_TOTAL)
    quality_tuples = product(ADJECTIVES_TOTAL, QUALITIES_TOTAL, CONTAINED_TOTAL)
    class_to_tuples = {'containment': containment_tuples, 'source-path-goal': spg_tuples,
                       'quality': quality_tuples}
    results = [('Question', 'Sentence', 'Class', 'Type', 'Natural_phrasing', 'Yes_or_no_question',
                'Variable1', 'Variable2', 'Variable3')]
    for q_class in CLASSES:  # for each class
        for tuple in class_to_tuples[q_class]:  # for each possible tuple
            for variation in product(NATURAL_PHRASING, YES_OR_NO_QUESTION):  # for each phrasing and y/n type
                results.append(
                    (*literal_question_by_spec(tuple, q_class, *variation), q_class, 'literal', *variation, *tuple)
                )  # generate the appropriate data

    # repeat for non-literal statements:
    containment_non_literal_total = CONTAINMENT_NON_LITERAL + CONTAINMENT_NON_LITERAL_FT
    spg_non_literal_total = SOURCE_PATH_GOAL_NON_LITERAL + SOURCE_PATH_GOAL_NON_LITERAL_FT
    class_to_sentences = {'containment': containment_non_literal_total, 'source-path-goal': spg_non_literal_total}
    variables = {'containment': [extract_var_names(s) for s in CNL_VARS],
                 'source-path-goal': [extract_var_names(s) for s in SPGNL_VARS]}
    for q_class in CLASSES[:-1]:
        vars = variables[q_class]
        for i, statement in enumerate(class_to_sentences[q_class]):
            for variation in product(NATURAL_PHRASING, YES_OR_NO_QUESTION):
                if i < len(vars):  # not all non-literal statements have extractable variables
                    results.append(
                        (*nonliteral_question_by_spec(statement, q_class, *variation), q_class, 'non-literal',
                         *variation, *vars[i])
                    )
                else:
                    results.append(
                        (*nonliteral_question_by_spec(statement, q_class, *variation), q_class, 'non-literal',
                         *variation)
                    )

    return results


if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.output, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(generate_dataset())
