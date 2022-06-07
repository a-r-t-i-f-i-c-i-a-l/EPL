import textworld
import re
import enum
import random

import hypotheses

location_regex = re.compile(r'-=\s([\w\s]*)\s=-')
infos = textworld.EnvInfos(description=True, entities=True, facts=True, feedback=True, game=True, policy_commands=True,
                           inventory=True, location=True, moves=True, score=True, win_facts=True, lost=True, won=True,
                           admissible_commands=True)


class Object:

    def __init__(self, representation, location):
        self.representation = representation
        self.properties = {}

    def set_property(self, prop, val):
        self.properties[prop] = val


class Memory:
    def __init__(self):
        pass


class Action:
    # create object (as in, in memory)
    # edit object
    ## assign property
    ## edit property
    ## remove property
    # forget object (remove from memory)
    # create rule
    # remove rule
    # output command
    # observe (take input and interpret)
    ## pick salient bit
    ## process salient bit (use create/edit/forget actions on extracted info)
    pass


class CreateObject(Action):
    def __init__(self, obj_rep, obj_loc):
        pass


class Rule:
    pass


class Agent:
    def __init__(self):
        self.self = Object('me', '')


# Two necessary elements:
# 1. action generator - generates viable actions in a given state
# 2. action rater - rates the actions to be taken
# 3. instead of deciding on each action in turn as we encounter it,
#    decide on a plan of actions (like a policy)
# Plan of actions - a list of sets of actions in future states, with
# weights assigned to each action, allowing for the choice of one of
# them, either deterministically or stochastically.
# Action creation - instead of just naively listing all actions, base
# the generated actions on existing beliefs.
# Action rating - after each action, compare the expected state of the
# world (embedded in the action), with the actual result. Weigh the
# reward/penalty appropriately and score BOTH action AND the belief that
# led to its production. Once the belief loses points, it undergoes
# re-evaluation, so that a more preferable one is chosen.
# Belief - a structure of the form of a three-element conditional:
# if STATE then ACTION gives NEW_STATE,
# with an attached number expressing the strength of the belief.
# Problem - sometimes changes in state can be very lengthy. How do we
# limit the belief chains? Proposal: use heuristics to abbreviate, so
# instead of belief1 -> belief2 -> belief3 -> belief_final,
# we have belief1 -> (...) -> belief_final
# Thus the heuristic must anticipate that the change in state from
# belief1 brings the agent closer to the final goal.


# Before all of this, create the basics:
# State extraction:
#   1. the world state - what objects are around
#   2. the agent state - what inventory they have
#   3. the game state - what is to be done

# location extraction
def get_current_location(text):
    return re.search(location_regex, text).group(1)


class Entity:
    """
    A representation of an entity in the AI agent's world.
    :return:
    """

    def __init__(self, name, loc):
        self.name = name
        self.location = loc

    def set_location(self, loc):
        self.location = loc


def get_world_state(game_state):
    return game_state.facts


def get_experience_from_walkthrough(env: textworld.core.Wrapper, commands_to_actions=False):
    """
    Plays the game as instructed by the walkthrough, storing the sequences of state-action-state for learning about
    the relations between the two.
    :param env: environment (wrapper) with a state from which to commence the game
    :return: list of triples of the form (facts, action, facts)
    """
    state = env.reset()
    curr_facts = state.facts
    optimal_policy = state.policy_commands
    tuples = []
    for command in optimal_policy:
        new_state = env.step(command)[0]
        new_facts = new_state.facts
        if commands_to_actions:  # populate variables in actions with Variables from game state
            tuples.append((curr_facts, command_to_action(command, curr_facts), new_facts))
        else:
            tuples.append((curr_facts, command, new_facts))
        curr_facts = new_facts
    return tuples


def collect_facts_by_object(facts: [textworld.logic.Proposition], object: textworld.logic.Variable):
    """Collect all facts relating to a given object."""
    return [prop for prop in facts if object in prop.arguments]


def diff_facts(facts1: [textworld.logic.Proposition], facts2: [textworld.logic.Proposition]):
    """Differentiates between two fact sets. Compares facts of the same type with the same left-hand-side object
    to establish whether there has been a change of state."""
    befores = set([])
    afters = set([])
    objects = []
    for fact in facts1:
        object = fact.arguments[0]
        if object not in objects:
            objects.append(object)

    for object in objects:
        object_facts1_set = set(collect_facts_by_object(facts1, object))
        object_facts2_set = set(collect_facts_by_object(facts2, object))
        # things that are true about object now but not in the future
        befores = befores.union(object_facts1_set - object_facts2_set)
        # things that are true about object in the future but not now
        afters = afters.union(object_facts2_set - object_facts1_set)
    return [befores, afters]


class Action:
    def __init__(self, command_template: str, *args, facts=None):
        self.args = args
        self.repr = command_template.format(*args)
        self.command_template = command_template
        self.vars = self.extract_variables(args, facts)

    def __repr__(self):
        return 'Action: ' + self.command_template.format(*[str(var.name) if var is not None else arg for var, arg in zip(self.vars, self.args)])

    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return other.command_template == self.command_template and other.args == self.args and other.vars == self.vars

    def extract_variables(self, args, facts):
        """Extracts all the variables with the same name as the args.
        :returns A list of textworld Variables"""
        variables = []
        #  if facts is None:
        #      return [None] * len(args) # if there are no facts, then no variable can occur in them

        def find_var(name, facts):
            if facts is None:
                return None
            for prop in facts:
                for arg in prop.arguments:
                    if arg.name == name:
                        return arg
            return None

        for arg in args:
            if isinstance(arg, textworld.logic.Variable) or isinstance(arg, hypotheses.VariablePlaceholder):
                variables.append(arg)
            else:
                variables.append(find_var(arg, facts))
        return variables

    def as_command(self):
        return self.repr


class Go(Action):
    def __init__(self, direction: str, facts=None):
        """
        Movement action.
        :type direction: string
        """
        super(Go, self).__init__('go {0}', direction, facts=facts)
        self.direction = direction


class Look(Action):
    def __init__(self):
        super(Look, self).__init__('look')


class Open(Action):
    def __init__(self, thing, facts=None):
        super(Open, self).__init__('open {0}', thing, facts=facts)
        self.thing = thing


class Close(Action):
    def __init__(self, thing, facts=None):
        super(Close, self).__init__('close {0}', thing, facts=facts)
        self.thing = thing


class Take(Action):
    def __init__(self, thing, container=None, facts=None):
        if container is None:
            super(Take, self).__init__('take {0}', thing, facts=facts)
        else:
            super(Take, self).__init__('take {0} from {1}', thing, container, facts=facts)
        #self.thing = thing
        #self.container = container


class Lock(Action):
    def __init__(self, thing, key=None, facts=None):
        if key is None:
            super(Lock, self).__init__('lock {0}', thing, facts=facts)
            self.key = None
        else:
            super(Lock, self).__init__('lock {0} with {1}', thing, key, facts=facts)
        self.key = key
        self.thing = thing


class Unlock(Action):
    def __init__(self, thing, key=None, facts=None):
        if key is None:
            super(Unlock, self).__init__('unlock {0}', thing, facts=facts)
        else:
            super(Unlock, self).__init__('unlock {0} with {1}', thing, key, facts=facts)
        self.thing = thing
        self.key = key


class Put(Action):
    def __init__(self, thing, place, facts=None):
        super(Put, self).__init__('put {0} on {1}', thing, place, facts=facts)
        self.thing = thing
        self.place = place


class Insert(Action):
    def __init__(self, thing, container, facts=None):
        super(Insert, self).__init__('insert {0} into {1}', thing, container, facts=facts)
        self.thing = thing
        self.container = container


class Drop(Action):
    def __init__(self, thing, facts=None):
        super(Drop, self).__init__('drop {0}', thing, facts=facts)
        self.thing = thing


class Eat(Action):
    def __init__(self, thing, facts=None):
        super(Eat, self).__init__('eat {0}', thing, facts=facts)
        self.thing = thing


class Examine(Action):
    def __init__(self, thing, facts=None):
        super(Examine, self).__init__('examine {0}', thing, facts=facts)
        self.thing = thing


class Inventory(Action):
    def __init__(self):
        super(Inventory, self).__init__('inventory')


class YES(Action):
    def __init__(self):
        super(YES, self).__init__('YES')


separators = {
    'take': 'from',
    'put': 'on',
    'lock': 'with',
    'unlock': 'with',
    'insert': 'into'
}

name_to_action = {
    'look': Look,
    'eat': Eat,
    'go': Go,
    'take': Take,
    'put': Put,
    'drop': Drop,
    'insert': Insert,
    'close': Close,
    'open': Open,
    'examine': Examine,
    'lock': Lock,
    'unlock': Unlock,
    'inventory': Inventory,
    'YES': YES
}


def command_to_action(command: str, facts=None):
    """Extracts the information within a text command and converts it to an Action object.
    :param facts - if provided, will be used to find Variable representations of entity identifiers
    """

    parts = command.split()
    command_id = parts[0]  # command identifier (examine, eat, etc)
    spec = ' '.join(parts[1:]).strip()  # rest of the command
    if command_id in separators and separators[command_id] in command:
        arg1, arg2 = spec.split(separators[command_id])
        action = name_to_action[command_id](arg1.strip(), arg2.strip(), facts=facts)
    else:
        arg = spec
        if arg == '':
            action = name_to_action[command_id]()
        else:
            action = name_to_action[command_id](arg, facts=facts)
    return action


def fact_commonalities(fact1: textworld.logic.Proposition, fact2: textworld.logic.Proposition):
    """Finds the largest subset of commonalities between two facts, where those are coincidence between variables and
    fact names. Used for finding commonalities between states for causal reasoning from correlation.
    """
    commonalities = {}
    if fact1.name == fact2.name:
        commonalities['name'] = fact1.name
    commonalities['arguments'] = []
    for arg1, arg2 in zip(fact1.arguments, fact2.arguments):
        details = {}
        if arg1.name == arg2.name:
            details['name'] = arg1.name
        if arg1.type == arg2.type:
            details['type'] = arg1.type
        commonalities['arguments'].append(details)
    return commonalities


class ExperienceGatheringAgent(Agent):
    def __init__(self, seed=123):
        self.seed = seed
        self.rng = random.Random(seed)

    def reset(self):
        self.rng = random.Random(self.seed)

    def act(self, game_state, reward, done):
        considered_entities = self.select_entities(game_state)
        action = self.select_action(game_state)
        if action in [YES, Look, Inventory]:
            filled_action = action()
        elif action in [Eat, Examine, Go, Open, Close, Drop]:
            filled_action = action(considered_entities[0], facts=game_state['facts'])
        elif action in [Insert, Put]:
            filled_action = action(*considered_entities, facts=game_state['facts'])
        else:  # two-argument action, but can also take on a single argument
            filled_action = action(*considered_entities[0:self.rng.randint(1, 2)], facts=game_state['facts'])
        return filled_action

    def select_entities(self, game_state):
        """Selects entities for use in making the next move. Currently no weighting, just a random selector."""
        return self.rng.choices(game_state['entities'], k=2)

    def select_action(self, game_state):
        return self.rng.choice(list(name_to_action.values()))


class ExperienceGatherer:
    def __init__(self, agent):
        self.agent = agent
        self.experience = []

    def gather_experience(self, env, steps):
        steps_left = steps
        state = env.reset()
        while True:
            if steps_left > 0:
                steps_left -= 1
                action = self.agent.act(state, 0, False)
                new_state, reward, done = env.step(action.repr)
                if (state.facts, action, new_state.facts) not in self.experience:
                    self.experience.append((state.facts, action, new_state.facts))
                    state = new_state
                if done:
                    break
            else:
                break
        return self.experience

    def gather_experience_multiple(self, game_paths, steps_per_game=500):
        for game_path in game_paths:
            env = textworld.start(game_path, infos)
            self.gather_experience(env, steps_per_game)
        return self.experience



# Predicate structure:
# There exists x/For all x:
#       Predicate OR Predicate | NOT Predicate | Predicate OR Predicate | IsEqual(x, what, value)

# Predicates work over the propositions. Each predicate has a set of requirements ranging over the elements of the
# proposition. For example, that the proposition is named 'at', or that the proposition has a variable named 'table' or
# that the proposition has a Variable of type 'f', or some combination.
# Therefore a predicate is of type:
# For all props x/There exists prop x: Requirements(x)
# Checking the predicate is therefore reducible to traversing the list of known propositions.
# Requirements consist of: list of (a selector and a check).
# A selector is either: proposition name | head of proposition's attribute | body of proposition's attribute | arbitrary
#   argument's attribute | all arguments' attributes
# A check is a value check of the attribute: isEqual
# E.g. There exists prop x: x.name == 'at' AND head(x).type == 'c'
# Planning actions is stringing together the most likely Predicate -> Action sequences. Starting from the end state.

# Hypothesis: State, Predicates -> Action -> State. Each hypothesis has a weight attached to it based on its observed
# validity.
# Planning: End state <- Action <- State <- Action <- ... <- Current state. Use heuristics to estimate the probability
# of achieving the intermediate states. In planning, use a depth-limit to not ponder too deeply. Use state-similarity
# metric to store cached plans (memorized reactions).
class Predicate:
    def __init__(self):
        pass

    def is_met(self, state):
        return


class Selector(enum.Enum):
    PROPOSITION_NAME = enum.auto()
    PROPOSITION_HEAD_NAME = enum.auto()
    PROPOSITION_HEAD_TYPE = enum.auto()
    PROPOSITION_TAIL_NAME = enum.auto()
    PROPOSITION_TAIL_TYPE = enum.auto()
    PROPOSITION_ANY_ARG_NAME = enum.auto()
    PROPOSITION_ANY_ARG_TYPE = enum.auto()


class Exists(Predicate):
    """Encapsulates the notion of existential quantifier."""

    def __init__(self, selectors_checkers_values):
        """Creates an instance of an existential quantifier.
        param selectors_checkers_values: a list of tuples forming a CNF. Corresponds to the "such that x = y" part, i.e.
            "prop.name == 'at' AND prop.head.type == 'f'"""
        self.selectors_checkers_values = selectors_checkers_values

    def is_met(self, state):
        """Checks if any of the propositions in the state meet the criteria."""
        facts = state.facts
        for prop in facts:
            if any([checker(prop, selector, value) for selector, checker, value in self.selectors_checkers_values]):
                return True, prop  # return first proposition which meets the criteria
        return False, None

    def __repr__(self):
        return 'Exists P, s.t.: ' + ' AND '.join([' '.join([sel.name, c.__name__, str(val)])
                                                  for (sel, c, val) in self.selectors_checkers_values])


def is_equal(prop, selector, value):
    if selector == Selector.PROPOSITION_NAME:
        return prop.name == value
    elif selector == Selector.PROPOSITION_HEAD_NAME:
        return prop.arguments[0].name == value
    elif selector == Selector.PROPOSITION_HEAD_TYPE:
        return prop.arguments[0].type == value
    elif selector == Selector.PROPOSITION_TAIL_NAME:
        return prop.arguments[1].name == value if len(prop.arguments) > 1 else None
    elif selector == Selector.PROPOSITION_TAIL_TYPE:
        return prop.arguments[1].type == value if len(prop.arguments) > 1 else None
    elif selector == Selector.PROPOSITION_ANY_ARG_NAME:
        return any([arg.name == value for arg in prop.arguments])
    elif selector == Selector.PROPOSITION_ANY_ARG_TYPE:
        return any([arg.type == value for arg in prop.arguments])


def check_predicate(predicate, state):
    return predicate.is_met(state)
