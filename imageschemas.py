from textworld.logic import Proposition, Variable

import agent


class ImageSchema:
    def __init__(self):
        pass


class Container(ImageSchema):
    def __init__(self):
        pass


class Support(ImageSchema):
    def __init__(self):
        pass


class Source_Path_Goal(ImageSchema):
    def __init__(self):
        pass


class Source_Path(ImageSchema):
    def __init__(self):
        pass


class Goal_Path(ImageSchema):
    def __init__(self):
        pass


class Blockage(ImageSchema):
    def __init__(self):
        pass


def get_root(doc):
    for tok in doc:
        if tok.dep_ == 'ROOT':
            return tok


def schema_detector(facts_before, action=None, facts_after=None):
    '''Detects and assigns an image schema from a list of known schemas. '''
    schemas = []
    if action == None and facts_after == None:
        # detecting a static image schemas
        for prop in facts_before:
            if prop.name == 'in':
                schemas.append(Container())
    else:
        # detecting motion-based image schemas
        for prop_before in facts_before:
            object_move_blocked = False
            player_move_blocked = False
            for prop_after in facts_after:
                if prop_after.arguments[0] == prop_before.arguments[0] and prop_before.arguments[1] != \
                        prop_after.arguments[1]:
                    schemas.append(Source_Path())
                    schemas.append(Goal_Path())
                    pass
                if prop_after.name == 'in' and prop_after.arguments[0] == prop_before.arguments[0] \
                        and (
                        prop_before.arguments[1] != Variable('I', 'I') and prop_after.arguments[1] != Variable('I', 'I') \
                        and type(action) == agent.Take) or \
                        (prop_before.arguments[1] == Variable('I', 'I') and prop_after.arguments[1] == Variable('I',
                                                                                                                'I') \
                         and type(action) == agent.Put):
                    object_move_blocked = True
                if prop_before.name == 'at' \
                        and prop_before.arguments[0] == Variable('P', 'P') and prop_after.arguments[0] == Variable('P',
                                                                                                                   'P') \
                        and type(action) == agent.Go \
                        and prop_before.arguments[1] == prop_after.arguments[1]:
                    player_move_blocked = True
            # arguments = prop.arguments
            if object_move_blocked:
                schemas.append(Blockage())
            if player_move_blocked:
                schemas.append(Blockage())
    return schemas
