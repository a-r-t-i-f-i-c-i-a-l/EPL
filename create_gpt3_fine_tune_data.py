import json

from test_language_models import CONTAINED_LITERAL, CONTAINER_LITERAL, CONTAINMENT_NON_LITERAL, MOVING_OBJECT, \
    SOURCE_LITERAL, GOAL_LITERAL, SOURCE_PATH_GOAL_NON_LITERAL, QUALITIES, ADJECTIVES, containment_statement, \
    source_path_goal_statement, quality_statment
from train_test_epl import CONTAINMENT_NON_LITERAL as EPL_CONTAINMENT_NON_LITERAL
from train_test_epl import SOURCE_PATH_GOAL_NON_LITERAL as EPL_SOURCE_PATH_GOAL_NON_LITERAL

from numpy.random import shuffle
from itertools import product
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--n_literal', default=330, help='Amount of literal examples (default:330)')
parser.add_argument('--n_non_literal', default=25, help='Amount of non-literal examples (default:25)')
parser.add_argument('output', help='Output file name')


def create_train_data(type, n=330, n_nonliteral=25):
    result = []
    if type == 'CONTAINMENT':
        pairs = list(product(CONTAINED_LITERAL, CONTAINER_LITERAL))
        shuffle(pairs)
        result = [{"prompt": containment_statement(*pair),
                   "completion": "proposition in;{obj};{container} END".format(obj=pair[0], container=pair[1])}
                  for pair in pairs][:n]
        result += nonliteral_train_data('CONTAINMENT')[:n_nonliteral]
    elif type == 'SOURCE-PATH-GOAL':
        triples = list(product(MOVING_OBJECT, SOURCE_LITERAL, GOAL_LITERAL))
        shuffle(triples)
        result = [{"prompt": source_path_goal_statement(*triple),
                   "completion": "action moves;{obj};{src};{goal} END".format(obj=triple[0], src=triple[1],
                                                                              goal=triple[2])}
                  for triple in triples][:n]
        result += nonliteral_train_data('SOURCE-PATH-GOAL')[:n_nonliteral]
    elif type == 'DISTRACTION':
        triples = list(product(ADJECTIVES, QUALITIES, CONTAINED_LITERAL))
        shuffle(triples)
        result = [{"prompt": quality_statment(*triple),
                   "completion": "proposition of;{adj};{qual};{obj} END".format(adj=triple[0], qual=triple[1],
                                                                                obj=triple[2])}
                  for triple in triples][:n]
    shuffle(result)
    return result


def nonliteral_train_data(type):
    result = []
    if type == 'CONTAINMENT':
        prompts = CONTAINMENT_NON_LITERAL
        exps = EPL_CONTAINMENT_NON_LITERAL

        for prompt, exp in zip(prompts, exps):
            answer = list(filter(lambda x: x, exp))[0]  # find non-empty part of the experience
            if isinstance(answer, list):
                prop = answer[0]
                obj, container = prop.arguments[0].name, prop.arguments[1].name
                completion = "proposition in;{obj};{container} END".format(obj=obj, container=container)
            else:  # it must be an action
                obj, container = answer.vars[0].name, answer.vars[1].name
                completion = "action insert;{obj};{container} END".format(obj=obj, container=container)
            result.append({'prompt': prompt, "completion": completion})
    elif type == 'SOURCE-PATH-GOAL':
        prompts = SOURCE_PATH_GOAL_NON_LITERAL
        exps = EPL_SOURCE_PATH_GOAL_NON_LITERAL

        for prompt, exp in zip(prompts, exps):
            answer = list(filter(lambda x: x, exp))[0]
            if isinstance(answer, list):
                prop = answer[0]
                obj, location = prop.arguments[0].name, prop.arguments[1].name
                completion = "proposition at;{obj};{location} END".format(obj=obj, location=location)
            else:
                obj, src, goal = answer.vars[0].name, answer.vars[1].name, answer.vars[2].name
                completion = "action moves;{obj};{src};{goal} END".format(obj=obj, src=src, goal=goal)
            result.append({"prompt": prompt, "completion": completion})
    return result


if __name__ == '__main__2':
    args = parser.parse_args()
    data_containment = create_train_data('CONTAINMENT', args.n_literal, args.n_non_literal)
    data_source_path_goal = create_train_data('SOURCE-PATH-GOAL', args.n_literal, args.n_non_literal)
    data_distraction = create_train_data('DISTRACTION', args.n_literal, args.n_non_literal)
    data = data_containment + data_source_path_goal + data_distraction
    shuffle(data)
    with open(args.output, 'w') as file:
        for line in data:
            file.write(json.dumps(line) + '\n')
