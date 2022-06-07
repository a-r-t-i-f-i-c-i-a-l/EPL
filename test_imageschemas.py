from unittest import TestCase

import spacy
from textworld.logic import Proposition, Variable

import agent
import imageschemas

nlp = spacy.load('en_core_web_md')

class TestImageSchemas(TestCase):
    def test_schema_detector(self):
        facts = [Proposition('in', (Variable('sandwich', 'f'), Variable('refrigerator', 'c')))]

        def any_of_type(t, iterlist):
            return any(map(lambda x: type(x) == t, iterlist))

        self.assertEqual(True,
                         any_of_type(imageschemas.Container, imageschemas.schema_detector(facts)),
                         'must correctly detect containment')
        facts_before = [Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))]
        facts_after = [Proposition('at', (Variable('chair', 'o'), Variable('hallway', 'r')))]
        # schemas = imageschemas.schema_detector(facts_before, facts_after=facts_after)
        self.assertEqual(True, any_of_type(imageschemas.Source_Path,
                                           imageschemas.schema_detector(facts_before, facts_after=facts_after)),
                         'must detect sources of paths')
        self.assertEqual(True, any_of_type(imageschemas.Goal_Path,
                                           imageschemas.schema_detector(facts_before, facts_after=facts_after)),
                         'must detect goals of paths')

        facts_before_move = [Proposition('in', (Variable('sandwich', 'f'), Variable('fridge', 'c')))]
        action = agent.Take('sandwich', facts=facts_before_move)
        facts_after_move = facts_before_move
        facts_after_successful_move = [Proposition('in', (Variable('sandwich', 'f'), Variable('I', 'I')))]
        self.assertEqual(True, any_of_type(imageschemas.Blockage,
                                           imageschemas.schema_detector(facts_before_move, action, facts_after_move)),
                         'must detect blockage of objects')
        self.assertEqual(False, any_of_type(imageschemas.Blockage,
                                           imageschemas.schema_detector(facts_before_move, action,
                                                                        facts_after_successful_move)),
                         'must detect when no blockage occurs')
        facts_before_go = [Proposition('at', (Variable('P', 'P'), Variable('parlor', 'r')))]
        action_go = agent.Go('east')
        facts_after_go = facts_before_go
        self.assertEqual(True, any_of_type(imageschemas.Blockage,
                                           imageschemas.schema_detector(facts_before_go, action_go, facts_after_go)),
                         'must detect player movement blockage')




    def test_get_root(self):
        doc = nlp('I see a very cute cat.')

        self.assertEqual(doc[1], imageschemas.get_root(doc))