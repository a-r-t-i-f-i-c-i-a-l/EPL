import itertools
import random
import json
import requests
import argparse
import numpy as np
from time import sleep

parser = argparse.ArgumentParser('Run Language Model tests using the Hugging Face or OpenAI API.')
parser.add_argument('token', help='Access token')
parser.add_argument('--test-containment', action='store_true', help='Tests containment (literal and non-literal).')
parser.add_argument('--test-source-path-goal', action='store_true', help='Tests SOURCE-PATH-GOAL schema detection.')
parser.add_argument('--test-fine-tuned', action='store_true', help='Tests the fine-tuned GPT-3 model.')
parser.add_argument('--alt-phrasing', action='store_true',
                    help='Phrase questions without asking for schema name, but what it implies')
parser.add_argument('model', help='Model to use: T0pp or GPT3')
parser.add_argument('output', help='Name of output file to store results.')

'''curl https://api.openai.com/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
  "model": "text-davinci-002",
  "prompt": "",
  "temperature": 0.7,
  "max_tokens": 256,
  "top_p": 1,
  "frequency_penalty": 0,
  "presence_penalty": 0
}'''
GPT3_QUERY = {
    "model": "text-davinci-002",
    "prompt": "",
    "temperature": 0.7,
    "max_tokens": 256,
}
OPENAI_API_URL = "https://api.openai.com/v1/completions"
BIGSCIENCE_API_URL = "https://api-inference.huggingface.co/models/bigscience/T0pp"
headers = {"Authorization": ""}


def query(api_url, payload, headers):
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()


def schema_type_question(objects, schema_name, yes_or_no=False, alt_phrasing=False):
    phrasing = NAME_TO_DESCRIPTION2[schema_name] if alt_phrasing else NAME_TO_DESCRIPTION[schema_name]
    if yes_or_no:
        return "Yes or no, is this sentence a case of {schema_name}? Sentence: ".format(
            schema_name=phrasing) + \
               NAME_TO_STATEMENT[generator if generator else schema_name](*objects)
    else:
        return "Is this sentence a case of a {schema_name}? Sentence: ".format(
            schema_name=phrasing) + \
               NAME_TO_STATEMENT[generator if generator else schema_name](*objects)


def containment_statement(contained, container):
    return 'A {0} is in a {1}.'.format(contained, container)


def source_path_goal_statement(object, source, goal):
    return 'The {obj} {starts} {source} and ends up at {goal}'.format(obj=object,
                                                                      starts=random.choice(['goes from',
                                                                                            'starts out at',
                                                                                            'travels from']),
                                                                      source=source, goal=goal)


def quality_statment(adj, quality, object):
    return 'The {adj} {quality} of a {object}.'.format(adj=adj, quality=quality, object=object)


NAME_TO_STATEMENT = {
    "source-path-goal": source_path_goal_statement,
    "containment": containment_statement,
    "quality": quality_statment
}

NAME_TO_DESCRIPTION = {
    "source-path-goal": "a source, path and goal relation",
    "containment": "a containment relation",
    "quality": "a quality relation"
}

NAME_TO_DESCRIPTION2 = {
    "source-path-goal": "something having a source and a goal",
    "containment": "something being in something else",
    "quality": "something describing something else"
}

QUALITIES = ['color', 'type', 'shape', 'profile', 'length', 'example', 'part', 'weight', 'surface']
QUALITIES_FT = ['diameter', 'size', 'mass', 'sheen', 'direction', 'position']
ADJECTIVES = ['peculiar', 'normal', 'strange', 'typical', 'specific']
ADJECTIVES_FT = ['average', 'measured', 'unusual', 'atypical', 'expected']

CONTAINED_LITERAL = [
    'apple', 'banana', 'yogurt', 'hammer', 'ball', 'doll', 'car', 'bird', 'vest', 'lamp', 'chicken', 'boat', 'curtain',
    'book', 'button', 'shirt', 'wheel', 'spinner', 'lightbulb', 'water', 'salt', 'peanut', 'pen', 'stylus', 'pencil',
    'clock', 'doorknob', 'cheese', 'stapler', 'battery'
]

CONTAINED_LITERAL_FT = [
    'cork', 'cabbage', 'quiche', 'file', 'ring', 'pair of shoes', 'bean', 'spoon', 'gel', 'pencil', 'envelope',
    'pepper', 'hat', 'soap', 'bunch of rice'
]

CONTAINER_LITERAL = [
    'jar', 'fridge', 'vase', 'room', 'garage', 'car', 'box', 'crate', 'shed', 'pocket', 'carriage'
]

CONTAINER_LITERAL_FT = [
    'attic', 'drawer', 'garden', 'bag', 'backpack', 'suitcase', 'package', 'store'
]

CONTAINMENT_NON_LITERAL = [
    'Solved in a nick of time.',
    'Two peas in a pod.',
    'Be done in a minute.',
    'One in a million.',
    'Once in a blue moon.',
    'Marching in lockstep.',
    'Lost in thought.',
    'Missing in action.',
    'Brothers in arms.',
    'Locked in an embrace.',
    'There\'s nothing in the room.',
    'Hand in hand.',
    'Best in class.',
    'Without a care in the world.',
    'Stopped dead in his tracks.',
    'I have an in with them.',
    'This shirt is in vogue.',
    'It depends in some measure on time.',
    'Two in one.',
    'Happy as a pig in mud.',
    'What in tarnation?',
    'Head in the sand.',
    'Heart in the right place.',
    'Out in the cold.',
    'Stuck in a rut.',
    'Tongue in cheek.',
    'A footnote in history.',
    'A flash in the pan.',
    'A damsel in distress.',
    'Leave in a hurry.',
    'A case study in good writing.',
    'A foot in the door.',
    'A match made in heaven.',
    'A storm in a teacup.',
    'Extra spring in one\'s step.',
    'Everything in its place.',
    'All in all, it was ok.',
    'Done in one sitting.',
    'Bask in the glow.',
    'A step in the right direction.',
    'We agree in principle.',
    'All in due course.',
    'We\'re back in business.',
    'I\'m in possession of important data.',
    'She\'s in control.',
    'They\'re in a good mood.',
    'State in plain English.',
    'Keep in touch with us.',
    'You\'re in luck.',
    'Fall in love.'
]

CONTAINMENT_NON_LITERAL_FT = [
    'One in seven don\'t know the answer.',
    'We made it in the end.',
    'The proof is in the pudding.',
    'He\'s the apple in his mother\'s eye.',
    'We have much in common.',
    'Nothing in science is certain.',
    'Creating this means dipping our toes in regulatory issues.',
    'It\'s the only game in town.',
    'Split the cookie in two.',
    'Believe in me.',
    'The meaning was lost in translation.',
    'Stuck in between.',
    'This car is in a class of its own.',
    'A step in the right direction.',
    'The construction advances in stages.',
    'There is no place in this town one can buy cigarettes.',
    'They worked in equal measures with academia and journalists.',
    'No shame in admitting defeat.',
    'We trade in everyday commodities.',
    'This report is a good case in point.',
    'He was stopped in his tracks',
    'Nip the problem in the bud.',
    'Wait in line.',
    'I am in search of my glasses.',
    'A boss in name only.',
    #    'They act in Bob\'s name.'
]

MOVING_OBJECT = [
    'pedestrian', 'traveler', 'driver', 'tourist', 'party-goer', 'package', 'car', 'helicopter'
]

MOVING_OBJECT_FT = [
    'walker', 'plane', 'bicycle', 'voyager', 'scooter', 'robot'
]

SOURCE_LITERAL = [
    'a garage', 'a shed', 'a bay', 'home', 'the bus stop', 'the mountains', 'London', 'Bristol',
    'the church', 'a party'
]

SOURCE_LITERAL_FT = [
    'a kitchen', 'a park', 'the driveway', 'the stadium', 'Paris', 'Barcelona', 'their backyard', 'the train station'
]

GOAL_LITERAL = [
    'a parking lot', 'a restaurant', 'the sea', 'a city in another country', 'a bookstore', 'Rome\'s colosseum',
    'the airport', 'a beach'
]

GOAL_LITERAL_FT = [
    'a bar', 'their living room', 'an island', 'a small village', 'a supermarket', 'the Natural History Museum',
    'the finish line'
]

SOURCE_PATH_GOAL_NON_LITERAL = [
    'From the very beginning, I knew we\'d end up in this situation.',
    'We partied from dusk till dawn.',
    'Things went from bad to worse.',
    'Their life is from hand to mouth.',
    'The general is decorated from head to toe.',
    'She grinned from ear to ear.',
    'The place has been converted from a shack to a bungalow.',
    'He was demoted from sergeant to corporal.',
    'She developed from a beginner into a chess master.',
    'List everything from A to Z.',
    'Every store from here to Sunday is full of customers.',
    'The situation went from frying pan to fire.',
    'You have gone from one extreme to the other.',
    'I\'ve been going from pillar to post.',
    'He went from rags to riches.',
    'This boat moves from side to side too much.',
    'She went from strength to strength since starting her career.',
    'I like doing nothing from time to time.',
    'Overnight, he went from zero to hero.',
    'We reduced staff from fifty to just ten.',
    'She switched from knitting to painting.',
    'Translate this from English to Japanese, please.',
    'He constantly goes between the bark and the tree.',
    'The panel will go from 1 pm to 5 pm tomorrow.',
    'Let\'s begin and go from top to bottom.',
    'The cost would be anywhere from ten to fifteen thousand.',
    'Check your mail from day to day.',
    'They\'re going from one end of the Earth to the other, looking for him.',
    'Things can change from one day to the next.',
    'His explanation clearly went from point A to point B.',
    'Hear me out from start to finish.',
    'How did you go from your premise to this conclusion?',
    'He went out of his way to make the point.',
    'She went from a mediocre student to a college professor.',
    'From the moment it dropped, the marble went into free fall.',
    'From your looks to your demeanor, you don\'t seem like a local.',
    'From the get-go, the new system came into use.',
    'After the memo left his office, it went into effect.',
    'Do you really want to go there, from the very morning?',
    'From the moment they met, you knew it would come to this.',
    'There\'s only one conclusion she could come to from this.',
    'There\'s nowhere to go from here.',
    'From what you\'re telling me, there\'s only one conclusion to arrive at.',
    'Go beyond what they say and you\'ll reach a different conclusion.',
    'There\'s no reason to go that far from what I know.',
    'From that moment on, I set out to prove them wrong, and I got there.',
    'In her memoire, she goes from her earliest days to the pinnacle of her career.',
    'We\'re jumping from subject to subject.',
    'After leaving the company, he went broke.',
    'Setting out to challenge them, she went even further in her claims.',
    'If we start out like this, we\'ll go nowhere.'
]

SOURCE_PATH_GOAL_NON_LITERAL_FT = [
    'We chatted from midday till lunch time.',
    'I knew this would go nowhere from the very beginning.',
    'They would go so far as to call it unfeasible.',
    'This business went from no customers to over a million.',
    'I go to work from nine till five.',
    'It all started from almost nothing.',
    'There\'s a lot of change from the first to the second version.',
    'The group went on national television, and ended up being the most-watched act ever.',
    'The story goes from one unbelievable claim to the next.',
    'Jim went job-hunting to get away from his current work.',
    'It starts out high and goes even higher.',
    'Started with the right premise then went off on a tangent.',
    'From what they\'re saying, this can\'t go on.',
    'We went ahead to win five more contests.',
    'Where do we go from here?',
    'Start from the beginning and we might get somewhere.',
    'Go see the movie and come back with your own opinion.',
    'Please move my reservation from Tuesday to Friday.',
    'From rest to elation, the music moved the audience deeply.',
    'There\'s no need for you to go to such depths.',
    'The news came out of nowhere.',
    'Stop at this step before you go any further.',
    'Don\'t go out on a limb with these statistics.',
    'From that day on, the specialists left for greener pastures.',
    'Go out to see the world.',
    #    'They made a move to secure their standing.'
]

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    headers['Authorization'] = 'Bearer ' + args.token
    print(headers)


    def query_fake(payload, headers):
        return {'generated_text': 'yes', 'choices':[{'text':'proposition in proposition at'}]}


    if args.test_containment:
        arg_pairs_literal = itertools.product(CONTAINED_LITERAL, CONTAINER_LITERAL)
        chosen_literal = random.choices(list(arg_pairs_literal), k=50)
        arg_tuples_distractions = itertools.product(ADJECTIVES, QUALITIES, CONTAINED_LITERAL)
        chosen_distractions = random.choices(list(arg_tuples_distractions), k=50)
        chosen_nonliteral = np.random.permutation(CONTAINMENT_NON_LITERAL)
        result = {'literal': {}, 'non-literal': {}, 'distraction': {}}
        stats_correct = {'literal': 0, 'non-literal': 0, 'distraction': 0}
        phrasing = NAME_TO_DESCRIPTION2['containment'] if args.alt_phrasing else NAME_TO_DESCRIPTION['containment']
        for i in range(50):
            question = schema_type_question(chosen_literal[i], schema_name='containment', yes_or_no=True,
                                            alt_phrasing=args.alt_phrasing)
            if args.model.lower() == 't0pp':
                try:
                    answer_literal = query(BIGSCIENCE_API_URL, question, headers)[0]['generated_text']
                except:
                    answer_literal = '(no answer)'


            elif args.model.lower() == 'gpt3':
                filled_query = GPT3_QUERY
                filled_query['prompt'] = question
                try:
                    answer_literal = query(OPENAI_API_URL, filled_query, headers)['choices'][0]['text']
                except:
                    answer_literal = '(no answer)'

            result['literal'][i] = {'question': question, 'answer': answer_literal}
            if 'yes' in answer_literal.lower():
                stats_correct['literal'] += 1
            print('Asking literal question', i, ':', question, '\nAnswer:', answer_literal)

            sleep(random.randint(2, 5))
            question = "Yes or no, is this sentence a case of {phrasing}? Sentence: ".format(phrasing=phrasing) + \
                       chosen_nonliteral[i]

            if args.model.lower() == 't0pp':
                try:
                    answer_nonliteral = query(BIGSCIENCE_API_URL, question, headers)[0]['generated_text']
                except:
                    answer_nonliteral = '(no answer)'


            elif args.model.lower() == 'gpt3':
                filled_query = GPT3_QUERY
                filled_query['prompt'] = question
                try:
                    answer_nonliteral = query(OPENAI_API_URL, filled_query, headers)['choices'][0]['text']
                except:
                    answer_nonliteral = '(no answer)'

            result['non-literal'][i] = {'question': question, 'answer': answer_nonliteral}
            if 'yes' in answer_nonliteral.lower():
                stats_correct['non-literal'] += 1

            print('Asking non-literal question', i, ':', question, '\nAnswer:', answer_nonliteral)
            sleep(random.randint(2, 5))
            question = "Yes or no, is this sentence a case of {phrasing}? Sentence: ".format(phrasing=phrasing) + \
                       quality_statment(*chosen_distractions[i])

            if args.model.lower() == 't0pp':
                try:
                    answer_distraction = query(BIGSCIENCE_API_URL, question, headers)[0]['generated_text']
                except:
                    answer_distraction = '(no answer)'


            elif args.model.lower() == 'gpt3':
                filled_query = GPT3_QUERY
                filled_query['prompt'] = question
                try:
                    answer_distraction = query(OPENAI_API_URL, filled_query, headers)['choices'][0]['text']
                except:
                    answer_distraction = '(no answer)'

            result['distraction'][i] = {'question': question, 'answer': answer_distraction}
            if 'yes' not in answer_distraction.lower():
                stats_correct['distraction'] += 1
            print('Asking distraction question', i, ':', question, '\nAnswer:', answer_distraction)
        with open(args.output + '_qna_containment.json', 'w') as file:
            json.dump(result, file, indent=4)
        with open(args.output + '_stats_containment.json', 'w') as file:
            json.dump(stats_correct, file, indent=4)

    if args.test_source_path_goal:
        arg_tuples_literal = itertools.product(MOVING_OBJECT, SOURCE_LITERAL, GOAL_LITERAL)
        chosen_literal = random.choices(list(arg_tuples_literal), k=50)
        arg_tuples_distractions = itertools.product(ADJECTIVES, QUALITIES, CONTAINED_LITERAL)
        chosen_distractions = random.choices(list(arg_tuples_distractions), k=50)
        chosen_nonliteral = np.random.permutation(SOURCE_PATH_GOAL_NON_LITERAL)
        result = {'literal': {}, 'non-literal': {}, 'distraction': {}}
        stats_correct = {'literal': 0, 'non-literal': 0, 'distraction': 0}
        phrasing = NAME_TO_DESCRIPTION2['source-path-goal'] if args.alt_phrasing else NAME_TO_DESCRIPTION[
            'source-path-goal']
        for i in range(50):
            question = schema_type_question(chosen_literal[i], schema_name='source-path-goal', yes_or_no=True,
                                            alt_phrasing=args.alt_phrasing)
            if args.model.lower() == 't0pp':
                try:
                    answer_literal = query(BIGSCIENCE_API_URL, question, headers)[0]['generated_text']
                except:
                    answer_literal = '(no answer)'


            elif args.model.lower() == 'gpt3':
                filled_query = GPT3_QUERY
                filled_query['prompt'] = question
                try:
                    answer_literal = query(OPENAI_API_URL, filled_query, headers)['choices'][0]['text']
                except:
                    answer_literal = '(no answer)'

            result['literal'][i] = {'question': question, 'answer': answer_literal}
            if 'yes' in answer_literal.lower():
                stats_correct['literal'] += 1
            print('Asking literal question', i, ':', question, '\nAnswer:', answer_literal)
            sleep(random.randint(2, 5))

            question = "Yes or no, is this sentence a case of {phrasing}? Sentence: ".format(phrasing=phrasing) + \
                       chosen_nonliteral[i]

            if args.model.lower() == 't0pp':
                try:
                    answer_nonliteral = query(BIGSCIENCE_API_URL, question, headers)[0]['generated_text']
                except:
                    answer_nonliteral = '(no answer)'


            elif args.model.lower() == 'gpt3':
                filled_query = GPT3_QUERY
                filled_query['prompt'] = question
                try:
                    answer_nonliteral = query(OPENAI_API_URL, filled_query, headers)['choices'][0]['text']
                except:
                    answer_nonliteral = '(no answer)'

            result['non-literal'][i] = {'question': question, 'answer': answer_nonliteral}
            if 'yes' in answer_nonliteral.lower():
                stats_correct['non-literal'] += 1

            print('Asking non-literal question', i, ':', question, '\nAnswer:', answer_literal)
            sleep(random.randint(2, 5))

            question = "Yes or no, is this sentence a case of {phrasing}? Sentence: ".format(phrasing=phrasing) + \
                       quality_statment(*chosen_distractions[i])

            if args.model.lower() == 't0pp':
                try:
                    answer_distraction = query(BIGSCIENCE_API_URL, question, headers)[0]['generated_text']
                except:
                    answer_distraction = '(no answer)'


            elif args.model.lower() == 'gpt3':
                filled_query = GPT3_QUERY
                filled_query['prompt'] = question
                try:
                    answer_distraction = query(OPENAI_API_URL, filled_query, headers)['choices'][0]['text']
                except:
                    answer_distraction = '(no answer)'

            result['distraction'][i] = {'question': question, 'answer': answer_distraction}
            if 'yes' not in answer_distraction.lower():
                stats_correct['distraction'] += 1
            print('Asking distraction question', i, ':', question, '\nAnswer:', answer_distraction)

        with open(args.output + '_qna_source-path-goal.json', 'w') as file:
            json.dump(result, file, indent=4)
        with open(args.output + '_stats_source-path-goal.json', 'w') as file:
            json.dump(stats_correct, file, indent=4)

    if args.test_fine_tuned:
        containment_args_literal = list(itertools.product(CONTAINED_LITERAL_FT, CONTAINER_LITERAL_FT))
        random.shuffle(containment_args_literal)
        containment_args_literal = containment_args_literal[:50]
        spg_args_literal = list(itertools.product(MOVING_OBJECT_FT, SOURCE_LITERAL_FT, GOAL_LITERAL_FT))
        random.shuffle(spg_args_literal)
        spg_args_literal = spg_args_literal[:50]
        distraction_args = list(itertools.product(ADJECTIVES_FT, QUALITIES_FT, CONTAINED_LITERAL_FT))
        random.shuffle(distraction_args)
        distraction_args = distraction_args[:100]

        containment_non_literal = CONTAINMENT_NON_LITERAL[25:] + CONTAINMENT_NON_LITERAL_FT
        spg_non_literal = SOURCE_PATH_GOAL_NON_LITERAL[25:] + SOURCE_PATH_GOAL_NON_LITERAL_FT

        results_containment = {'literal': {}, 'non-literal': {}, 'distraction': {}}
        results_spg = {'literal': {}, 'non-literal': {}, 'distraction': {}}
        stats_containment = {'literal': 0, 'non-literal': 0, 'distraction': 0}
        stats_spg = {'literal': 0, 'non-literal': 0, 'distraction': 0}
        for i in range(50):
            prompt_c = containment_statement(*containment_args_literal[i])
            query_c = {"model": args.model, "prompt": prompt_c}
            response_c = query(OPENAI_API_URL, query_c, headers)['choices'][0]['text']
            results_containment['literal'][i] = {'question':prompt_c, 'answer':response_c}
            if 'proposition in' in response_c.lower() or 'action insert' in response_c.lower():
                stats_containment['literal'] += 1
            print('asked', query_c, 'got response:', response_c)

            sleep(random.randint(2, 5))

            prompt_nl_c = containment_non_literal[i]
            query_nl_c = {"model": args.model, "prompt": prompt_nl_c}
            response_nl_c = query(OPENAI_API_URL, query_nl_c, headers)['choices'][0]['text']
            results_containment['non-literal'][i] = {'question':prompt_nl_c, 'answer':response_nl_c}
            if 'proposition in' in response_nl_c.lower() or 'action insert' in response_nl_c.lower():
                stats_containment['non-literal'] += 1
            print('asked', query_nl_c, 'got response:', response_nl_c)

            sleep(random.randint(2, 5))

            prompt_d_c = quality_statment(*distraction_args[i])
            query_d_c = {"model": args.model, "prompt": prompt_d_c}
            response_d_c = query(OPENAI_API_URL, query_d_c, headers)['choices'][0]['text']
            results_containment['distraction'][i] = {'question': prompt_d_c, 'answer': response_d_c}
            if not('proposition in' in response_d_c.lower() or 'action insert' in response_d_c.lower() or \
                'proposition at' in response_d_c.lower() or 'action moves' in response_d_c.lower()):
                stats_containment['distraction'] += 1
            print('asked', query_d_c, 'got response:', response_d_c)

            sleep(random.randint(2, 5))
            #########################
            
            prompt_spg = source_path_goal_statement(*spg_args_literal[i])
            query_spg = {"model": args.model, "prompt": prompt_spg}
            response_spg = query(OPENAI_API_URL, query_spg, headers)['choices'][0]['text']
            results_spg['literal'][i] = {'question': prompt_spg, 'answer': response_spg}
            if 'proposition at' in response_spg.lower() or 'action moves' in response_spg.lower():
                stats_spg['literal'] += 1
            print('asked', query_spg, 'got response:', response_spg)

            sleep(random.randint(2, 5))

            prompt_nl_spg = spg_non_literal[i]
            query_nl_spg = {"model": args.model, "prompt": prompt_nl_spg}
            response_nl_spg = query(OPENAI_API_URL, query_nl_spg, headers)['choices'][0]['text']
            results_spg['non-literal'][i] = {'question': prompt_nl_spg, 'answer': response_nl_spg}
            if 'proposition at' in response_nl_spg.lower() or 'action moves' in response_nl_spg.lower():
                stats_spg['non-literal'] += 1
            print('asked', query_nl_spg, 'got response:', response_nl_spg)

            sleep(random.randint(2, 5))

            prompt_d_spg = quality_statment(*distraction_args[50+i])
            query_d_spg = {"model": args.model, "prompt": prompt_d_spg}
            response_d_spg = query(OPENAI_API_URL, query_d_spg, headers)['choices'][0]['text']
            results_spg['distraction'][i] = {'question': prompt_d_spg, 'answer': response_d_spg}
            if not ('proposition in' in response_d_spg.lower() or 'action insert' in response_d_spg.lower() or \
                    'proposition at' in response_d_spg.lower() or 'action moves' in response_d_spg.lower()):
                stats_spg['distraction'] += 1
            print('asked', query_d_spg, 'got response:', response_d_spg)
        with open(args.output + '_qna_containment.json', 'w') as file:
            json.dump(results_containment, file, indent=4)
        with open(args.output + '_stats_containment.json', 'w') as file:
            json.dump(stats_containment, file, indent=4)

        with open(args.output + '_qna_source-path-goal.json', 'w') as file:
            json.dump(results_spg, file, indent=4)
        with open(args.output + '_stats_source-path-goal.json', 'w') as file:
            json.dump(stats_spg, file, indent=4)

    # print(query("are ducks birds?", {'Authorization': 'Bearer ' + args.token}))
