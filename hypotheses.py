import imageschemas
import agent
from textworld.logic import Proposition, Variable
from uuid import uuid4
from copy import deepcopy


class SpatialPrimitive(Proposition):
    def __init__(self):
        pass

    def holds(self):
        return


class In(SpatialPrimitive):
    def __init__(self, containee, container):
        self.container = container
        self.containee = containee

    def holds(self):
        return False


class Placeholder:
    def __init__(self):
        pass

    def matches():
        return True


class VariablePlaceholder(Placeholder):
    '''
    Placeholder for a variable in a Proposition. Can be filled to hold an actual variable.
    '''

    def __init__(self, var=None, position=None):
        self.position = position
        self.id = uuid4()  # unique variable placeholder identifier
        self.name = 'VAR-' + str(self.id)[-12:]
        self.type = '*'
        if type(var) == Variable or var is None:
            self.held_variable = var
        else:
            raise Exception('VariablePlaceholders can only hold instances of Variables')

    def fill(self, var):
        if type(var) == Variable and var is not None:
            self.held_variable = var
        else:
            raise Exception('VariablePlaceholders can only hold instances of Variables')
        return

    def holds_same_as(self, variable_placeholder):
        return self.held_variable is not None and variable_placeholder.held_variable == self.held_variable

    def __repr__(self):
        return '[VAR-%s]' % str(self.id)[-12:] if self.held_variable is None else '[%s]' % self.held_variable

    def __eq__(self, other):
        return type(other) == VariablePlaceholder and other.id == self.id and other.held_variable == self.held_variable

    def __hash__(self):
        return self.id.int


class WordPlaceholder(Placeholder):
    '''
    Placeholder for a word for NLP tasks. Can hold an actual string representing the word.
    '''

    def __init__(self, word=None, dep_=None):
        if (type(word) == str or word is None) and (type(dep_) == str or dep_ is None):
            self.word = word
            self.dep_ = dep_
        else:
            raise Exception('WordPlaceholders can only hold instances of strings')

    def fill(self, word=None, dep_=None):
        if (type(word) == str or word is None) and (type(dep_) == str or dep_ is None):
            self.word = word
            self.dep_ = dep_
        else:
            raise Exception('WordPlaceholders can only hold instances of strings')


class Hypothesis:
    def __init__(self, pre, action=None, post=None):
        '''Represents a hypothesis about the world in which the agent operates.
        :param pre - list of predicates presumed necessary for something to happen
        :param action - an action which attempts to act upon the world
        :param post - list of predicates presumed necessary as a result of the action upon the pre-world'''
        self.pre = pre
        self.action = action
        self.post = post


def align_prop_lists(props1, props2):
    prop_pairs = []
    props2_copy = deepcopy(props2)
    for prop in props1:
        match, score = match_propositions(prop, props2_copy)
        if match is None:  # exception since there are no matching Propositions in the other pattern
            return None, None
        prop_pairs.append((prop, match))
        props2_copy.remove(match)  # a matching prop can't be reused
    return prop_pairs


def reconcile_patterns(pat1, pat2) -> tuple:
    '''Attempts to find a suitable substitution for a pattern of Proposition - Action - Proposition, such as in an image
    schema like CONTAINMENT.

    :param pat1 tuple of (Proposition, Action, Proposition)
    :param pat2 tuple of (Proposition, Action, Proposition)
    :return (sub, dict) tuple of (pattern with substitutions, substitution dictionary) if reconciliation was possible,
    (None, None) otherwise - this in turn means either an exception or relaxation needs to take place.'''
    pre1, pre2 = pat1[0], pat2[0]
    act1, act2 = pat1[1], pat2[1]
    post1, post2 = pat1[2], pat2[2]

    if len(pre1) != len(pre2) or type(act1) != type(act2):
        return None, None  # either exception or relaxation, to be decided by calling function

    # first find appropriate substitutions for the pre-conditions
    pre_pairs = align_prop_lists(pre1, pre2)
    if pre_pairs == (None, None):
        return None, None

    pre_subs, pre_subs_dicts = reconcile_prop_pairs(pre_pairs)

    # substitute arguments in the action with VariablePlaceholder, assuming there is an action (i.e. non-static image
    # schema)
    act1_sub = substitute_action_arguments(act1, pre_subs_dicts[0]) if act1 is not None else None
    act2_sub = substitute_action_arguments(act2, pre_subs_dicts[1]) if act1 is not None else None

    # the actions can differ on arguments that haven't appeared in the pre-conditions (for example, we could speak
    # metaphorically "put something on hold" or haven't mentioned another object that is always there, like "throw
    # something behind"). we reconcile them so that we can further propagate the substitutions
    act_subs, act_subs_dicts = reconcile_actions(act1_sub, act2_sub, pre_subs_dicts[0], pre_subs_dicts[1])

    # there's no telling the two post-conditions must match, so first substitute then reconcile
    post_sub1 = [substitute(p, act_subs_dicts[0]) for p in post1]
    post_sub2 = [substitute(p, act_subs_dicts[1]) for p in post2]

    post_pairs = align_prop_lists(post_sub1, post_sub2)
    if post_pairs == (None, None):  # in case the post-conditions don't match, it's an exception (different pattern)
        return None, None
    post_rec, post_rec_subs_dicts = reconcile_prop_pairs(post_pairs)

    if post_rec is None or (len(post_rec_subs_dicts[0]) + len(post_rec_subs_dicts[1])) > 0:
        return None, None  # this is a separate sub-rule, the post-conditions express a different transition,
        # so it should be treated as an exception

    return (pre_subs, act_subs, post_rec), pre_subs_dicts


def reconcile_prop_pairs(prop_pairs):
    '''Reconciles a list of pairs of Propositions, if possible.
    :param prop_pairs list of (Proposition, Proposition), usually matched through align_prop_lists.
    :return list of reconciled Propositions, and a dictionary of substitutions, or None, None if reconciliation failed
    at any step'''
    prop_subs = []
    prop_subs_dicts = [{}, {}]
    for prop, match in prop_pairs:
        prop_subbed = deepcopy(prop)
        match_subbed = deepcopy(match)
        sub_dicts_1, sub_dicts_2 = prop_subs_dicts  # first make sure previous substitutions are taken into account
        prop_subbed = substitute(prop_subbed, sub_dicts_1)
        match_subbed = substitute(match_subbed, sub_dicts_2)
        prop_sub, prop_subs_dict = reconcile_props(prop_subbed, match_subbed)  # derive any unresolved substitutions
        if prop_sub is None:
            prop_subs = None
            break
        else:
            prop_subs.append(prop_sub)
            prop_subs_dicts[0].update(prop_subs_dict[0])
            prop_subs_dicts[1].update(prop_subs_dict[1])
    if prop_subs is None:
        return None, None  # can't reconcile
    return prop_subs, prop_subs_dicts


def reconcile_actions(act1, act2, already_subbed1={}, already_subbed2={}):
    '''Reconciles two Actions - they can be reconciled if both are of the same type and have the same amount of
    arguments.
    :param act1 Action
    :param act2 Action
    :param already_subbed1 Dictionary of already made substitutions (for example, if reconcile_actions is called after
    reconcile_props in a forward inference for the first proposition list
    :param already_subbed2 same as already_subbed1 but for the second proposition list
    :return (Action, {Variable: VariablePlaceholder}) tuple of substituted Action and substitution dictionary.'''
    subs_dict1 = {}
    subs_dict2 = {}
    vars = []
    if act1 and act2:
        if type(act1) == type(act2):
            for var1, var2 in zip(act1.vars, act2.vars):
                if var1 == var2:
                    vars.append(var1)
                else:
                    # the most straightforward case
                    if type(var1) == Variable and type(var2) == Variable and var1 != var2:
                        vp1 = VariablePlaceholder()
                        vp2 = VariablePlaceholder()
                        subs_dict1[var1] = vp1
                        subs_dict2[var2] = vp2
                        vars.append(vp1)
                    # if both are variable placeholders...
                    elif type(var1) == VariablePlaceholder and type(var2) == VariablePlaceholder:
                        # if the two placeholders were from different contexts (as indicated by position)
                        if var1.position != var2.position:
                            return None, None
                        # of if both are variable placeholders, but one is a result of previous substitutions and other
                        # isn't, meaning this is also a different context, such as
                        # P(A, B) -> Act(A, X) ...
                        # P(C, D) -> Act(VP,Y) ...
                        elif (var1 in already_subbed1.values() and var2 not in already_subbed2.values() or \
                              (var1 not in already_subbed1.values() and var2 in already_subbed1.values())):
                            return None, None
                        # both are fine and don't need any substituting (either because they are already a result
                        # of substitution, or because they existed as variable placeholders from the start)
                        else:
                            vars.append(var1)
                    # or if the there is a variable against a placeholder from the previous step's substitution,
                    # and not a pre-existing variable placeholder,
                    # meaning there wasn't a substitution where there should have been - hence a different situation
                    # and so a new pattern. (if this was the same pattern, there would be two corresponding
                    # variable placeholders)
                    elif (type(var1) == VariablePlaceholder and type(var2) == Variable and \
                        (var1 in already_subbed1.values())) or \
                            (type(var1) == Variable and type(var2) == VariablePlaceholder and \
                             var2 in already_subbed2.values()):
                        return None, None
                    # otherwise, it's a variable placeholder against a variable, and the variable placeholder isn't
                    # a result of a previous substitution
                    else:
                        vp1 = VariablePlaceholder()
                        vp2 = VariablePlaceholder()
                        subs_dict1[var1] = vp1
                        subs_dict2[var2] = vp2
                        vars.append(vp1)
    else:
        if not act1 and not act2:  # both actions are None
            return None, (already_subbed1, already_subbed2)
        else:  # one action is None, another isn't
            return None, None
    if len(vars) != len(act1.vars): # something else failed, a correct reconciliation cannot shorten the amount of vars
        return None, None
    else:
        already_subbed1.update(subs_dict1)
        already_subbed2.update(subs_dict2)
        return type(act1)(*vars), (already_subbed1, already_subbed2)


def match_propositions(prop, prop_list):
    '''Finds the most-matching Proposition from a list of Propositions. The most-matching Proposition is always the one
    with the most concrete Variables that match, and the least matching one is always the one with the most non-matching
    concrete Variables.'''

    eligible_props = [p for p in prop_list if p.name == prop.name and len(p.arguments) == len(prop.arguments)]
    ratings = []
    if not eligible_props:
        return None, None

    for candidate in eligible_props:
        rating = 0
        for arg, c_arg in zip(prop.arguments, candidate.arguments):
            if arg == c_arg or type(arg) == VariablePlaceholder and type(c_arg) == VariablePlaceholder:
                rating += 1
            elif type(arg) == VariablePlaceholder and type(c_arg) != VariablePlaceholder \
                    or type(arg) != VariablePlaceholder and type(c_arg) == VariablePlaceholder:
                rating += 0
            else:
                rating -= 1
        ratings.append((candidate, rating))
    return sorted(ratings, key=lambda r: r[1], reverse=True)[0]


# def reconcile_actions(action1, action2):

def reconcile_props(prop1, prop2):
    '''Attempts to find a shared way to reconcile two statements in propositional logic.
    :param pat1 - first Proposition list
    :param pat2 - second Proposition list '''
    if prop1.name != prop2.name:
        return None, {}  # two different propositions can't be reconciled
    subs = ({}, {})  # two separate dictionaries are needed to keep track of where the substitutions occur, since
    # a variable need not occur in the same place across propositions
    args = []

    for ix in range(len(prop1.arguments)):
        if prop2.arguments[ix] == prop1.arguments[ix] or \
                (type(prop1.arguments[ix]) == VariablePlaceholder and type(prop2.arguments[ix]) == VariablePlaceholder
                 and prop1.arguments[ix].position == prop2.arguments[ix].position):
            args.append(prop1.arguments[ix])
        else:
            # if two Propositions have a variable placeholder that refers to a different position (such as, if we are
            # considering two post-conditions, where variable placeholder occuring in the first place in the first one
            # stems from the first place in the pre-condition proposition, but the one in the first place in the second
            # one occured in the second place in its pre-condition, the two cannot be reconciled, because they are most
            # likely describing two different patterns)
            # e.g. Proposition(X, ([Var from position 1], [Var from position 2])) cannot be reconciled with
            #      Proposition(X, ([Var from position 2], [Var from position 1]))
            # such as in cases of swapping orders of objects - a different case occurs when we try to swap immovable
            # objects (the first proposition, the two stay as they were) vs when they can (the second proposition, the
            # two swap position from their original ones)
            arg1 = prop1.arguments[ix]
            arg2 = prop2.arguments[ix]
            if type(arg1) == VariablePlaceholder and type(arg2) == VariablePlaceholder \
                    and prop1.arguments[ix].position != prop2.arguments[ix].position:
                return None, {}
            else:
                vp1 = VariablePlaceholder(position=ix)
                args.append(vp1)  # add a placeholder on mismatched variables
                vp2 = VariablePlaceholder(position=ix)
                subs[0][arg1] = vp1  # store the position and placeholder in a dictionary for lookup
                subs[1][arg2] = vp2  # both variables go under the same substitution
    return Proposition(prop1.name, args), subs


def substitute(prop, substitutions):
    '''Substitutes occurrences of arguments in a Proposition using a provided dictionary.
    :param prop Proposition to be processed
    :param substitutions a dictionary of substitutions to be carried out
    :return a Proposition with substituted elements'''

    args = []
    for arg in prop.arguments:
        if arg in substitutions:
            args.append(substitutions[arg])
        else:
            args.append(arg)
    return Proposition(prop.name, args)


def substitute_pairs(props, substitutions):
    '''Substitutes occurrences of arguments in a Proposition using a provided dictionary. Only substitutes in instances
    where there is a mismatch between the Propositions.
    :param props Propositions to be processed
    :param substitutions a dictionary of substitutions to be carried out
    :return a Proposition with substituted elements'''
    prop1, prop2 = props
    subs1, subs2 = substitutions
    args1 = []
    args2 = []
    for arg1, arg2 in zip(prop1.arguments, prop2.arguments):
        if arg1 != arg2 and type(arg1) != VariablePlaceholder and type(arg2) != VariablePlaceholder and arg1 in subs1 \
                and arg2 in subs2:
            args1.append(substitutions[arg1])
            args2.append(substitutions[arg2])
        else:
            args.append(arg)
    return Proposition(prop.name, args)


def substitute_action_arguments(action, substitutions):
    '''Substitutes occurrences of arguments in an Action using a provided dictionary.
        :param action Action to be processed
        :param substitutions a dictionary of substitutions to be carried out
        :return an Action with substituted elements'''

    new_args = []
    new_vars = []
    for arg, var in zip(action.args, action.vars):
        if var in substitutions:
            new_args.append(substitutions[var].name)
            new_vars.append(substitutions[var])
        else:
            new_args.append(arg)
            new_vars.append(var)
    subbed_action = type(action)(*new_args)
    subbed_action.vars = new_vars
    return subbed_action


def propositions_actions_names_match(pattern1, pattern2):
    '''Helper function to check if the names of propositions and actions in a pattern agree.'''
    pre1, act1, post1 = pattern1
    pre2, act2, post2 = pattern2
    return set([p.name for p in pre1]) == set([p.name for p in pre2]) and type(act1) == type(act2) \
           and set([p.name for p in post2]) == set([p.name for p in post2])


def matching_pattern(pattern, name, pattern_store):
    '''Returns the most similar pattern stored under the named hypothesis'''
    if name not in pattern_store:  # this category of schemas doesn't exist
        return None, None
    patterns = pattern_store[name]

    for ix, candidate_pattern in enumerate(patterns):
        if propositions_actions_names_match(candidate_pattern, pattern):
            return ix, candidate_pattern  # return the pattern and its index in the store
    return None, None  # couldn't find anything


def learn(pattern, name, pattern_store):
    '''Learns by either updating an existing pattern or creating a new one in the pattern store. Currently uses a
    simplified logic in which every non-matching length of pre- or post-conditions is an exception.
    '''
    if pattern == ([], None, []):
        return pattern_store
    store = deepcopy(pattern_store)
    if name not in store:  # if this is a completely new concept, it can just be added as-is
        store[name] = [pattern]
    else:  # otherwise, find if a matching pattern exists
        ix, existing_pattern = matching_pattern(pattern, name, store)
        if existing_pattern is None:  # this is a novel pattern for this schema, append it to existing ones
            store[name].append(pattern)
        else:  # there already exists a matching pattern, see if we can reconcile it
            reconciled = reconcile_patterns(existing_pattern, pattern)
            if reconciled == (None, None):  # not possible, need to make an exception
                store[name].append(pattern)
            else:  # reconciliation successful, replace the old pattern with the new one
                store[name][ix] = reconciled[0]
    return store


def most_similar_pattern(pattern, pattern_store):
    '''Returns the name of the image schema as well as the pattern that best matches the given input pattern.
    :param pattern - a pattern of the form ([Proposition...], Action, [Proposition])
    :param pattern_store - a store of patterns
    :return tuple (matched pattern, name, score) specifying the pattern found, the name of it and the score it was
    assigned, or (None, None, None) if no patterns could be matched.'''
    if len(pattern_store) == 0:
        return None, None, None
    else:
        ranking = []
        pre, act, post = pattern
        for schema_name in pattern_store:
            for candidate in pattern_store[schema_name]:
                pre_candidate, post_candidate = deepcopy(candidate[0]), deepcopy(candidate[2])
                total_score = 0
                # score every proposition in pre-propositions
                for prop in pre:
                    _, score = match_propositions(prop, pre_candidate)
                    if score is not None:
                        total_score += score
                    else:
                        break
                if pre and score is None:
                    continue

                # score the action
                if type(act) == type(candidate[1]):
                    total_score += 1
                    if isinstance(act, agent.Action) and isinstance(candidate[1], agent.Action):
                        for var1, var2 in zip(act.vars, candidate[1].vars):
                            if var1 == var2:
                                total_score += 1
                            elif not (isinstance(var1, VariablePlaceholder) and isinstance(var2, VariablePlaceholder)):
                                total_score -= 1
                else:
                    continue

                # score every proposition in post-propositions
                for prop in post:
                    _, score = match_propositions(prop, post_candidate)
                    if score is not None:
                        total_score += score
                    else:
                        break
                if post and score is None:  # go to next candidate in case an error occurred anywhere
                    continue

                # store the candidate, schema_name, score (sum of prop and action similarity scores in the ranking list)
                ranking.append((candidate, schema_name, total_score))
        # return the most fitting entry based on the score key
    return sorted(ranking, key=lambda x: x[2], reverse=True)[0]


def infer(pat_target, pat_source):
    '''Tests if the given source pattern can be substituted into the target. This is only possible if either all the
    variables agree, or the variables from source can be lined up with variable placeholders in target. If so, returns
    the pattern with the substituted variables, with the post-conditions being the inferred results. If the substitution
    is possible, returns the filled in pattern and a substitution dictionary. If it isn't possible, returns None, None.
    :param pat_target the target to substitute into, presumably from the existing storage of patterns
    :param pat_source the source pattern to take variables from, presumably a new hypothetical scenario we're trying to
    predict consequences of
    :return tuple (pattern, dict) of pattern filled in and a dictionary of substitutions made or None, None if the
    patterns couldn't be made to agree (no inference could have been made)'''

    def merge_props(aligned_props):  # helper function to merge two props lists
        for prop_t, prop_s in aligned_props:
            for var_t, var_s in zip(prop_t.arguments, prop_s.arguments):
                if isinstance(var_t, VariablePlaceholder):
                    subs_dict[var_t] = var_s
                    var_t.fill(var_s)
                elif var_t != var_s:
                    return None, None

    pre_target, act_target, post_target = deepcopy(pat_target)
    pre_source, act_source, post_source = pat_source

    aligned_props_pre = align_prop_lists(pre_target, pre_source)
    subs_dict = {}
    if not aligned_props_pre and (pre_target or pre_source):  # no inferences can be made if props can't be aligned
        return None, None
    else:
        if pre_source:  # skip in case the pre-source is empty (inferring about causes from results)
            if merge_props(aligned_props_pre) == (None, None):
                return None, None  # signal if merging failed

    if type(act_target) != type(act_source) and act_source is not None:
        # can't infer from an action mismatch (wrong pattern)
        return None, None
    elif act_target and act_source:  # if actions aren't None
        if len(act_target.vars) != len(act_source.vars):
            return None, None  # can't infer because one action takes more arguments than other
        for var_t, var_s in zip(act_target.vars, act_source.vars):
            if isinstance(var_t, VariablePlaceholder):
                if var_t.held_variable:
                    if var_t.held_variable != var_s:
                        # can't infer because of a mismatch between action arguments and known pattern actin arguments
                        return None, None
                else:
                    subs_dict[var_t] = var_s
                    var_t.fill(var_s)

    aligned_props_post = align_prop_lists(post_target, post_source)  # in case the query is about causes
    if not aligned_props_post and (post_target or post_source):
        return None, None
    else:
        if post_source:
            if merge_props(aligned_props_post) == (None, None):
                return None, None

    return (pre_target, act_target, post_target), subs_dict
