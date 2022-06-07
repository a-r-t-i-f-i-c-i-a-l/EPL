import itertools


def schema_type_question(objects, schema_name):
    return "Is this sentence a case of {schema_name}? Sentence: ".format(schema_name=schema_name) + NAME_TO_STATEMENT[schema_name] \
        (*objects)

def containment_statement(contained, container):
    return 'A {0} is in a {1}'.format(contained, container)

def source_path_goal_statement(object, prefix1, source, prefix2, goal):
    return 'A {obj} starts {pre1} {source} and ends up at {pre2} {goal}'.format(obj=object, pre1=prefix1,
                                                                                source=source, pre2=prefix2, goal=goal)


NAME_TO_STATEMENT = {
    "source-path-goal": source_path_goal_statement,
    "containment": containment_statement
}

CONTAINED_LITERAL = [
    'apple', 'banana', 'yogurt', 'hammer', 'ball', 'doll', 'car', 'bird', 'vest', 'lamp', 'chicken', 'boat', 'curtain',
    'book', 'button', 'shirt', 'wheel', 'spinner', 'lightbulb', 'water', 'salt', 'peanut', 'pen', 'stylus', 'pencil',
    'clock', 'doorknob', 'cheese', 'stapler', 'battery'
]

CONTAINER_LITERAL = [
    'jar', 'fridge', 'vase', 'room', 'garage', 'car', 'box', 'crate', 'shed', 'pocket', 'carriage'
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
    'Wander around in the dark.',
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

SOURCE_LITERAL = [
    'garage',
]