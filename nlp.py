import spacy
import re
import random

import textworld

location_namer = re.compile(r'\n-=\s([\w\s]*)\s=-\n')
nlp = spacy.load('en_core_web_md')


# The NLP module of the AI, responsible for generating rules that inform
# the textual cognition. For example, we'd expect it to generate a ruleset
# that identifies ascribing locations to the agent ("you are in ..."), so
# that the agent can reason about its position in the world.

# the first step is to simply convert the text as input into linguistic objects
def extract_info(text: str) -> list:
    primitives = [{'text': tok.text, 'lemma': tok.lemma_,
                   'pos': tok.pos_, 'dep': tok.dep_, 'lefts': tok.lefts, 'rights': tok.rights,
                   'head': tok.head} for tok in nlp(text)]
    return primitives


def entity_property_is(entity, prop: str, value: str) -> bool:
    """
    Checks if entity's property is exactly as given
    :param entity: entity to query
    :param prop: property to check
    :type value: bool
    """
    return entity.get(prop, '') == value


def select_random_property(entity):
    return random.choice(list(entity.items()))


def create_salience_map(entities):
    return


def is_entity_with_prop_after(entities, index, prop, value):
    for ent in entities[index:]:
        if ent[prop] == value:
            return True
    return False


def select_random_entity(entities):
    return random.choice(entities)


class Result:
    def __init__(self, res):
        self.value = res


def return_entity(ent):
    return Result(ent)


def return_nothing():
    return Result(None)

class Rule:
    def __init__(self, condition, prop, val):
        self.condition = condition
        self.prop = prop
        self.value = val

    def apply(self, entity):
        return self.condition(entity, self.prop, self.value)


def create_unary_conditional(condition, prop, val):
    return Rule(condition, prop, val)


def apply_rule(rule, entity):
    return rule(entity)


def algo(entities, answer):
    rules = []
    for i in range(10000):
        ent = select_random_entity(entities)
        prop, val = select_random_property(ent)
        rule = Rule(entity_property_is, prop, val)
        score = 0
        for ent_ in entities:
            if rule.apply(ent_):

                if ent_['text'] == answer:
                    rules.append(rule)
                    score += 1
                else:
                    score -= 1
        rules.append((rule, score))
    return sorted(rules, key=lambda x: x[1], reverse=True)

def train(data):
    """
    Trains a rule-set based on what information is meant to be extracted.
    The goal is to find a minimum-size rule-set for uncovering the training
    answers from the training data.
    Optimizes in accordance to rule size and rule complexity, for example,
    a rule of X.prop == a or Y.prop == b where X and Y are primitives (i.e. no sub-rules)
    is more complex than if X.prop == a then z, but less complex than
    if X.prop == a or (Y.prop == b and Z is before Y) then b otherwise c.
    :param data: data for training, consisting of tuples of (entities, answer(s)) form
    :return:
    """
def extract_example_entities():
    env = textworld.start('games/simple_challenge.z8')
    state = env.reset()
    state_l = env.step('look')
    return extract_info(state_l[0]['feedback'])
