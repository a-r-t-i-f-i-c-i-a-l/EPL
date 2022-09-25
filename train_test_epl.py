import hypotheses
from agent import Put, Take, Insert, Go, Moves
from textworld.logic import Proposition, Variable
from itertools import product
from random import choices, choice, randint
from copy import deepcopy
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--test-containment', action='store_true', help='Test performance on CONTAINMENT')
parser.add_argument('--test-source-path-goal', action='store_true', help='Test performance on SOURCE-PATH-GOAL')
parser.add_argument('output', help='Output file name')

CONTAINMENT_TRAINING = [
    (
        [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))],
        None,
        [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))]
    ),
    (
        [Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c')))],
        None,
        [Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c')))]
    ),
    (
        [Proposition('in', (Variable('orange', 'f'), Variable('box', 'c')))],
        None,
        [Proposition('in', (Variable('orange', 'f'), Variable('box', 'c')))]
    ),
    (
        [Proposition('in', (Variable('orange', 'f'), Variable('I', 'I')))],
        Insert(Variable('orange', 'f'), Variable('fridge', 'c')),
        [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))]
    ),
    (
        [Proposition('in', (Variable('bread', 'f'), Variable('I', 'I')))],
        Insert(Variable('bread', 'f'), Variable('fridge', 'c')),
        [Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c')))]
    ),
    (
        [Proposition('in', (Variable('bread', 'f'), Variable('I', 'I')))],
        Insert(Variable('bread', 'f'), Variable('box', 'c')),
        [Proposition('in', (Variable('bread', 'f'), Variable('box', 'c')))]
    ),
]

SOURCE_PATH_GOAL_TRAINING = [
    (
        [Proposition('at', (Variable('I', 'I'), Variable('kitchen', 'r')))],
        Go(Variable('corridor', 'r')),
        [Proposition('at', (Variable('I', 'I'), Variable('corridor', 'r')))]
    ),
    (
        [Proposition('at', (Variable('I', 'I'), Variable('corridor', 'r')))],
        Go(Variable('living room', 'r')),
        [Proposition('at', (Variable('I', 'I'), Variable('living room', 'r')))]
    ),
    (
        [Proposition('at', (Variable('ball', 'o'), Variable('kitchen', 'r')))],
        Moves(Variable('ball', 'o'), Variable('kitchen', 'r'), Variable('corridor', 'r')),
        [Proposition('at', (Variable('ball', 'o'), Variable('corridor', 'r')))]
    ),
    (
        [Proposition('at', (Variable('marble', 'o'), Variable('kitchen', 'r')))],
        Moves(Variable('marble', 'o'), Variable('kitchen', 'r'), Variable('corridor', 'r')),
        [Proposition('at', (Variable('marble', 'o'), Variable('corridor', 'r')))]
    ),
    (
        [Proposition('at', (Variable('marble', 'o'), Variable('kitchen', 'r')))],
        Moves(Variable('marble', 'o'), Variable('kitchen', 'r'), Variable('living room', 'r')),
        [Proposition('at', (Variable('marble', 'o'), Variable('living room', 'r')))]
    ),
    (
        [Proposition('at', (Variable('marble', 'o'), Variable('living room', 'r')))],
        Moves(Variable('marble', 'o'), Variable('living room', 'r'), Variable('corridor', 'r')),
        [Proposition('at', (Variable('marble', 'o'), Variable('corridor', 'r')))]
    ),
]


def train(experiences, schema_name, background_knowledge={}):
    store = background_knowledge
    for exp in experiences:
        store = hypotheses.learn(exp, schema_name, store)
    return store

CONTAINED_LITERAL = [
    'apple', 'banana', 'yogurt', 'hammer', 'ball', 'doll', 'car', 'bird', 'vest', 'lamp', 'chicken', 'boat', 'curtain',
    'book', 'button', 'shirt', 'wheel', 'spinner', 'lightbulb', 'water', 'salt', 'peanut', 'pen', 'stylus', 'pencil',
    'clock', 'doorknob', 'cheese', 'stapler', 'battery'
]

CONTAINER_LITERAL = [
    'jar', 'fridge', 'vase', 'room', 'garage', 'car', 'box', 'crate', 'shed', 'pocket', 'carriage'
]

MOVING_OBJECT = [
    'pedestrian', 'traveler', 'driver', 'tourist', 'party-goer', 'package', 'car', 'helicopter'
]

SOURCE_LITERAL = [
    'a garage', 'a shed', 'a bay', 'home', 'the bus stop', 'the mountains', 'London', 'Bristol',
    'the church', 'a party'
]

GOAL_LITERAL = [
    'a parking lot', 'a restaurant', 'the sea', 'a city in another country', 'a bookstore', 'Rome\'s colosseum',
    'the airport', 'a beach'
]

def generate_test_data(objects1, objects2, type, n=50, sources=[]):
    args = list(product(objects1, objects2))
    result = []
    sources = deepcopy(sources)
    for i in range(n):
        part = randint(0, 2)
        (arg1, arg2) = choice(args)
        args.remove((arg1, arg2))
        if type == 'CONTAINMENT':
            if part == 0:
                experience = ([Proposition('in', (Variable(arg1, 'o'), Variable(arg2, 'c')))], None, [])
            elif part == 1:
                experience = ([], Insert(Variable(arg1, 'o'), Variable(arg2, 'c')), [])
            else:
                experience = ([], None, [Proposition('in', (Variable(arg1, 'o'), Variable(arg2, 'c')))])
        elif type == 'SOURCE-PATH-GOAL':
            src = choice(sources)
            if part == 0:
                experience = ([Proposition('at', (Variable(arg1, 'o'), Variable(arg2, 'r')))], None, [])
            elif part == 1:
                experience = ([], Moves(Variable(arg1, 'o'), Variable(src, 'r'), Variable(arg2, 'r')), [])
            else:
                experience = ([], None, [Proposition('at', (Variable(arg1, 'o'), Variable(arg2, 'r')))])
        else:
            if part == 0:
                experience = ([Proposition('on', (Variable(arg1, 'o'), Variable(arg2, 'o')))], None, [])
            elif part == 1:
                experience = ([], Put(Variable(arg1, 'o'), Variable(arg2, 'o')), [])
            else:
                experience = ([], None, [Proposition('on', (Variable(arg1, 'o'), Variable(arg2, 'o')))])
        result.append(experience)
    return result

CONTAINMENT_NON_LITERAL = [
    ([Proposition('in', (Variable('solved', 'o'), Variable('nick of time', 'o')))], None, []),
    ([Proposition('in', (Variable('two peas', 'o'), Variable('pod', 'o')))], None, []),
    ([Proposition('in', (Variable('be done', 'o'), Variable('a minute', 'o')))], None, []),
    ([Proposition('in', (Variable('one', 'o'), Variable('a million', 'o')))], None, []),
    ([Proposition('in', (Variable('once', 'o'), Variable('a blue moon', 'o')))], None, []),
    ([Proposition('in', (Variable('marching', 'o'), Variable('lockstep', 'o')))], None, []),
    ([Proposition('in', (Variable('lost', 'o'), Variable('thought', 'o')))], None, []),
    ([Proposition('in', (Variable('missing', 'o'), Variable('action', 'o')))], None, []),
    ([Proposition('in', (Variable('brothers', 'o'), Variable('arms', 'o')))], None, []),
    ([Proposition('in', (Variable('locked', 'o'), Variable('embrace', 'o')))], None, []),
    ([Proposition('in', (Variable('nothing', 'o'), Variable('the room', 'o')))], None, []),
    ([Proposition('in', (Variable('hand', 'o'), Variable('hand', 'o')))], None, []),
    ([Proposition('in', (Variable('best', 'o'), Variable('class', 'o')))], None, []),
    ([Proposition('in', (Variable('care', 'o'), Variable('the world', 'o')))], None, []),
    ([Proposition('in', (Variable('stopped dead', 'o'), Variable('his tracks', 'o')))], None, []),
    ([Proposition('in', (Variable('in', 'o'), Variable('he', 'o')))], None, []),
    ([Proposition('in', (Variable('shirt', 'o'), Variable('vogue', 'o')))], None, []),
    ([Proposition('in', (Variable('it depends', 'o'), Variable('some measure on time', 'o')))], None, []),
    ([Proposition('in', (Variable('two', 'o'), Variable('one', 'o')))], None, []),
    ([Proposition('in', (Variable('pig', 'o'), Variable('mud', 'o')))], None, []),
    ([Proposition('in', (Variable('what', 'o'), Variable('tarnation', 'o')))], None, []),
    ([Proposition('in', (Variable('head', 'o'), Variable('the sand', 'o')))], None, []),
    ([Proposition('in', (Variable('heart', 'o'), Variable('the right place', 'o')))], None, []),
    ([Proposition('in', (Variable('out', 'o'), Variable('the cold', 'o')))], None, []),
    ([Proposition('in', (Variable('stuck', 'o'), Variable('rut', 'o')))], None, []),
    ([Proposition('in', (Variable('tongue', 'o'), Variable('cheek', 'o')))], None, []),
    ([Proposition('in', (Variable('footnote', 'o'), Variable('history', 'o')))], None, []),
    ([Proposition('in', (Variable('flash', 'o'), Variable('the pan', 'o')))], None, []),
    ([Proposition('in', (Variable('damsel', 'o'), Variable('distress', 'o')))], None, []),
    ([Proposition('in', (Variable('leave', 'o'), Variable('hurry', 'o')))], None, []),
    ([Proposition('in', (Variable('case study', 'o'), Variable('good writing', 'o')))], None, []),
    ([Proposition('in', (Variable('foot', 'o'), Variable('the door', 'o')))], None, []),
    ([Proposition('in', (Variable('match', 'o'), Variable('heaven', 'o')))], None, []),
    ([Proposition('in', (Variable('storm', 'o'), Variable('teacup', 'o')))], None, []),
    ([Proposition('in', (Variable('extra spring', 'o'), Variable('one\'s step', 'o')))], None, []),
    ([Proposition('in', (Variable('everything', 'o'), Variable('its place', 'o')))], None, []),
    ([Proposition('in', (Variable('all', 'o'), Variable('all', 'o')))], None, []),
    ([Proposition('in', (Variable('done', 'o'), Variable('one sitting', 'o')))], None, []),
    ([Proposition('in', (Variable('bask', 'o'), Variable('the glow', 'o')))], None, []),
    ([Proposition('in', (Variable('step', 'o'), Variable('right direction', 'o')))], None, []),
    ([Proposition('in', (Variable('agree', 'o'), Variable('principle', 'o')))], None, []),
    ([Proposition('in', (Variable('all', 'o'), Variable('due course', 'o')))], None, []),
    ([Proposition('in', (Variable('back', 'o'), Variable('business', 'o')))], None, []),
    ([Proposition('in', (Variable('I\'m', 'o'), Variable('possession', 'o')))], None, []),
    ([Proposition('in', (Variable('She\'s', 'o'), Variable('control', 'o')))], None, []),
    ([Proposition('in', (Variable('they\'re', 'o'), Variable('good mood', 'o')))], None, []),
    ([Proposition('in', (Variable('State', 'o'), Variable('plain English', 'o')))], None, []),
    ([Proposition('in', (Variable('keep', 'o'), Variable('touch', 'o')))], None, []),
    ([Proposition('in', (Variable('You\'re', 'o'), Variable('luck', 'o')))], None, []),
    ([Proposition('in', (Variable('Fall', 'o'), Variable('love', 'o')))], None, [])
]

SOURCE_PATH_GOAL_NON_LITERAL = [
    ([], None, [Proposition('at', (Variable('we', 'o'), (Variable('situation', 'o'))))]),
    ([Proposition('at', (Variable('we', 'o'), Variable('dusk', 'o')))], None, [Proposition('at', (Variable('we', 'o'), Variable('dawn', 'o')))]),
    ([], Moves(Variable('things', 'o'), Variable('bad', 'o'), Variable('worse', 'o')), []),
    ([Proposition('at', (Variable('their life', 'o'), Variable('hand', 'o')))], None, [Proposition('at', (Variable('their life', 'o'), Variable('mouth', 'o')))]),
    ([Proposition('at', (Variable('decorated', 'o'), Variable('head', 'o')))], None, [Proposition('at', (Variable('decorated', 'o'), Variable('toe', 'o')))]),
    ([Proposition('at', (Variable('grinned', 'o'), Variable('ear', 'o')))], None, [Proposition('at', (Variable('grinned', 'o'), Variable('ear', 'o')))]),
    ([Proposition('at', (Variable('place', 'o'), Variable('shack', 'o')))], None, [Proposition('at', (Variable('place', 'o'), Variable('bungalow', 'o')))]),
    ([Proposition('at', (Variable('he', 'o'), Variable('sergeant', 'o')))], None, [Proposition('at', (Variable('he', 'o'), Variable('corporal', 'o')))]),
    ([Proposition('at', (Variable('she', 'o'), Variable('beginner', 'o')))], None,
     [Proposition('at', (Variable('she', 'o'), Variable('chess master', 'o')))]),
    ([Proposition('at', (Variable('everything', 'o'), Variable('A', 'o')))], None, [Proposition('at', (Variable('everything', 'o'), Variable('Z', 'o')))]),
    ([Proposition('at', (Variable('every store', 'o'), Variable('here', 'o')))], None, [Proposition('at', (Variable('every store', 'o'), Variable('Sunday', 'o')))]),
    ([], Moves(Variable('situation', 'o'), Variable('frying pan', 'o'), Variable('fire', 'o')), []),
    ([Proposition('at', (Variable('you', 'o'), Variable('one extreme', 'o')))], None, [Proposition('at', (Variable('you', 'o'), Variable('the other', 'o')))]),
    ([], Moves(Variable('I', 'o'), Variable('pillar', 'o'), Variable('post', 'o')), []),
    ([], Moves(Variable('he', 'o'), Variable('rags', 'o'), Variable('riches', 'o')), []),
    ([], Moves(Variable('boat', 'o'), Variable('side', 'o'), Variable('side', 'o')), []),
    ([], Moves(Variable('she', 'o'), Variable('strength', 'o'), Variable('strength', 'o')), []),
    ([Proposition('at', (Variable('I', 'o'), Variable('time', 'o')))], None, [Proposition('at', (Variable('I', 'o'), Variable('time', 'o')))]),
    ([], Moves(Variable('he', 'o'), Variable('zero', 'o'), Variable('hero', 'o')), []),
    ([Proposition('at', (Variable('staff', 'o'), Variable('fifty', 'o')))], None, [Proposition('at', (Variable('staff', 'o'), Variable('ten', 'o')))]),
    ([Proposition('at', (Variable('she', 'o'), Variable('knitting', 'o')))], None, [Proposition('at', (Variable('she', 'o'), Variable('painting', 'o')))]),
    ([Proposition('at', (Variable('this', 'o'), Variable('English', 'o')))], None, [Proposition('at', (Variable('this', 'o'), Variable('Japanese', 'o')))]),
    ([], Moves(Variable('he', 'o'), Variable('bark', 'o'), Variable('tree', 'o')), []),
    ([], Moves(Variable('panel', 'o'), Variable('1 pm', 'o'), Variable('5 pm', 'o')), []),
    ([], Moves(Variable('us', 'o'), Variable('top', 'o'), Variable('bottom', 'o')), []),
    ([Proposition('at', (Variable('cost', 'o'), Variable('ten thousand', 'o')))], None, [Proposition('at', (Variable('cost', 'o'), Variable('fifteen thousand', 'o')))]),
    ([Proposition('at', (Variable('email', 'o'), Variable('day', 'o')))], None, [Proposition('at', (Variable('email', 'o'), Variable('day', 'o')))]),
    ([], Moves(Variable('they', 'o'), Variable('one end of the Earth', 'o'), Variable('the other', 'o')), []),
    ([Proposition('at', (Variable('things', 'o'), Variable('one day', 'o')))], None, [Proposition('at', (Variable('things', 'o'), Variable('the next', 'o')))]),
    ([], Moves(Variable('explanation', 'o'), Variable('point A', 'o'), Variable('point B', 'o')), []),
    ([Proposition('at', (Variable('me', 'o'), Variable('start', 'o')))], None, [Proposition('at', (Variable('me', 'o'), Variable('finish', 'o')))]),
    ([], Moves(Variable('you', 'o'), Variable('your premise', 'o'), Variable('your conclusion', 'o')), []),
    ([], Moves(Variable('he', 'o'), Variable('out of his way', 'o'), Variable('make the point', 'o')), []),
    ([], Moves(Variable('she', 'o'), Variable('mediocre student', 'o'), Variable('college professor', 'o')), []),
    ([], Moves(Variable('marble', 'o'), Variable('moment it dropped', 'o'), Variable('freefall', 'o')), []),
    ([Proposition('at', (Variable('you', 'o'), Variable('your looks', 'o')))], None, [Proposition('at', (Variable('you', 'o'), Variable('your demeanor', 'o')))]),
    ([Proposition('at', (Variable('the system', 'o'), Variable('get go', 'o')))], None, [Proposition('at', (Variable('system', 'o'), Variable('use', 'o')))]),
    ([], Moves(Variable('the memo', 'o'), Variable('his office', 'o'), Variable('effect', 'o')), []),
    ([], Moves(Variable('you', 'o'), Variable('very morning', 'o'), Variable('there', 'o')), []),
    ([], Moves(Variable('it', 'o'), Variable('the moment they met', 'o'), Variable('this', 'o')), []),
    ([], Moves(Variable('she', 'o'), Variable('only one conclusion', 'o'), Variable('this', 'o')), []),
    ([], Moves(Variable('there', 'o'), Variable('here', 'o'), Variable('nowhere', 'o')), []),
    ([], Moves(Variable('me', 'o'), Variable('what you\'re telling me', 'o'), Variable('only one conclusion', 'o')), []),
    ([], Moves(Variable('you', 'o'), Variable('what they say', 'o'), Variable('different conclusion', 'o')), []),
    ([Proposition('at', (Variable('I', 'o'), Variable('what I know', 'o')))], None, [Proposition('at', (Variable('I', 'o'), Variable('that far', 'o')))]),
    ([], Moves(Variable('I', 'o'), Variable('that moment on', 'o'), Variable('prove them wrong', 'o')), []),
    ([], Moves(Variable('she', 'o'), Variable('her earliest days', 'o'), Variable('pinnacle of her career', 'o')), []),
    ([], Moves(Variable('we', 'o'), Variable('subject', 'o'), Variable('subject', 'o')), []),
    ([], Moves(Variable('he', 'o'), Variable('the company', 'o'), Variable('broke', 'o')), []),
    ([], Moves(Variable('she', 'o'), Variable('', 'o'), Variable('even further in her claims', 'o')), []),
    ([Proposition('at', (Variable('we', 'o'), Variable('like this', 'o')))], None, [Proposition('at', (Variable('we', 'o'), Variable('nowhere', 'o')))])
]
# test_data_distraction = generate_test_data(CONTAINED_LITERAL, CONTAINER_LITERAL, 'DISTRACTION')
# kb = train(CONTAINMENT_TRAINING, 'CONTAINMENT')
# t = ([], Insert(Variable('stylus', 'o'), Variable('garage', 'c')), [])
# #ms = hypotheses.most_similar_pattern(t, kb)
# #sub = hypotheses.infer(ms[0], t)
# distr = test_data_distraction[0]
# res = hypotheses.make_inference(distr, kb)

if __name__ == '__main__':
    args = parser.parse_args()
    kb = train(CONTAINMENT_TRAINING, 'CONTAINMENT')
    kb = train(SOURCE_PATH_GOAL_TRAINING, 'SOURCE-PATH-GOAL', kb)
    test_data_literal = []
    test_data_nonliteral = []
    test_data_distraction = generate_test_data(CONTAINED_LITERAL, CONTAINER_LITERAL, 'DISTRACTION')
    if args.test_containment:
        test_data_literal = generate_test_data(CONTAINED_LITERAL, CONTAINER_LITERAL, 'CONTAINMENT')
        test_data_nonliteral = CONTAINMENT_NON_LITERAL
    elif args.test_source_path_goal:
        test_data_literal = generate_test_data(MOVING_OBJECT, GOAL_LITERAL, 'SOURCE-PATH-GOAL', sources=SOURCE_LITERAL)
        test_data_nonliteral = SOURCE_PATH_GOAL_NON_LITERAL
    results = {'literal':{}, 'non-literal':{}, 'distraction':{}}

    stats_correct = {'literal': 0, 'non-literal': 0, 'distraction': 0}
    for i in range(50):
        question_l = test_data_literal[i]
        _, _, name, _ = hypotheses.make_inference(question_l, kb)

        results['literal'][i] = {'question': str(question_l), 'answer': name}
        if (args.test_containment and name == 'CONTAINMENT') or \
                (args.test_source_path_goal and name == 'SOURCE-PATH-GOAL'):
            stats_correct['literal'] += 1

        question_n = test_data_nonliteral[i]
        _, _, name, _ = hypotheses.make_inference(question_n, kb)

        results['non-literal'][i] = {'question': str(question_n), 'answer': name}
        if (args.test_containment and name == 'CONTAINMENT') or \
                (args.test_source_path_goal and name == 'SOURCE-PATH-GOAL'):
            stats_correct['non-literal'] += 1

        question_d = test_data_distraction[i]
        _, _, name, _ = hypotheses.make_inference(question_d, kb)

        results['distraction'][i] = {'question': str(question_d), 'answer': name}
        if not (name == 'SOURCE-PATH-GOAL' or name == 'CONTAINMENT'):
            stats_correct['distraction'] += 1

    ttype = 'containment' if args.test_containment else 'source-path-goal'
    with open(args.output + '_qna_' + ttype + '.json', 'w') as outfile:
        json.dump(results, outfile)
    with open(args.output + '_stats_' + ttype + '.json', 'w') as outfile:
        json.dump(stats_correct, outfile)