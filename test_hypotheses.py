from unittest import TestCase
from textworld.logic import Proposition, Variable

import agent
import hypotheses


class TestHypotheses(TestCase):
    bread_in_fridge = Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c')))
    chair_at_kitchen = Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))
    bread_in_box = Proposition('in', (Variable('bread', 'f'), Variable('box', 'c')))
    orange_in_fridge = Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))

    def test_VariablePlaceholder(self):
        vp = hypotheses.VariablePlaceholder()
        self.assertEqual(None, vp.held_variable, 'unfilled VariablePlaceholders must hold None')
        self.assertRaises(Exception, hypotheses.VariablePlaceholder, 'asdf',
                          'wrong arguments to VariablePlaceholder constructor must raise exception')

        vp.fill(Variable('bread', 'f'))
        self.assertEqual(Variable('bread', 'f'), vp.held_variable,
                         'filled variable must be contained by VariablePlaceholder')
        self.assertRaises(Exception, vp.fill, 'foo')
        self.assertEqual('orange', hypotheses.WordPlaceholder('orange', 'dobj').word,
                         'filled WordPlaceholder must hold words')
        self.assertEqual('dobj', hypotheses.WordPlaceholder('orange', 'dobj').dep_,
                         'filled WordPlaceholder must hold deps')
        self.assertEqual(None, hypotheses.WordPlaceholder('orange').dep_,
                         'filled WordPlaceholder must hold deps')
        self.assertRaises(Exception, hypotheses.WordPlaceholder, 'orange', Variable('fridge', 'c'))
        vp2 = hypotheses.VariablePlaceholder(Variable('bread', 'f'))
        self.assertEqual(True, vp.holds_same_as(vp2), 'must recognize same variable held')
        self.assertEqual(False, vp.holds_same_as(hypotheses.VariablePlaceholder()), 'must recognize when another '
                                                                                    'placeholder has no contents')
        self.assertEqual(False, vp.holds_same_as(hypotheses.VariablePlaceholder(Variable('pickle', 'f'))),
                         'must recognize when another placeholder holds a different variable')

    def test_reconcile_patterns(self):
        first_vp = hypotheses.VariablePlaceholder()
        first_var_placeholder_pattern = ([Proposition('in', (first_vp, Variable('fridge', 'c')))], None,
                                         [Proposition('in', (first_vp, Variable('fridge', 'c')))])
        result_first_var_pat, result_first_var_dicts = \
            hypotheses.reconcile_patterns(([self.bread_in_fridge], None, [self.bread_in_fridge]),
                                          ([self.orange_in_fridge], None, [self.orange_in_fridge]))
        self.assertEqual(type(first_var_placeholder_pattern[0][0].arguments[0]),
                         type(result_first_var_pat[0][0].arguments[0]),
                         'must correctly assign placeholders even if there is no action')

        self.assertEqual((None, None),
                         hypotheses.reconcile_patterns(([self.bread_in_fridge], None, [self.bread_in_fridge]),
                                                       ([self.chair_at_kitchen], None, [self.chair_at_kitchen])),
                         'must not reconcile irreconcilable patterns')
        #reconcile, _ = hypotheses.reconcile_patterns(([self.bread_in_fridge], None, [self.bread_in_fridge]),
        #                                               ([self.bread_in_fridge], None, [self.bread_in_box]))
        self.assertEqual((None, None),
                         hypotheses.reconcile_patterns(([self.bread_in_fridge], None, [self.bread_in_fridge]),
                                                      ([self.bread_in_fridge], None, [self.bread_in_box])),
                         'must not reconcile irreconcilable patterns')
        # (bread in fridge) - None - (bread  in fridge)
        # (bread in box)    - None - (orange in fridge)
        # not irreconcilable - it might make sense that whenever there is bread in a box, there is an orange in fridge
        self.assertEqual((None, None),
                         hypotheses.reconcile_patterns(([self.bread_in_fridge], None, [self.bread_in_fridge]),
                                                       ([self.bread_in_box], None, [self.orange_in_fridge])),
                         'must not reconcile irreconcilable patterns')
        self.assertEqual((None, None),
                         hypotheses.reconcile_patterns(([self.bread_in_fridge], None, [self.bread_in_fridge]),
                                                       ([self.bread_in_box], None, [self.chair_at_kitchen])),
                         'must not reconcile irreconcilable patterns where post-conditions differ too much')
        return

    def test_match_props(self):
        self.assertEqual((None, None),
                         hypotheses.match_propositions(Proposition('closed', (Variable('door', 'd'),)), []),
                         'must return None if no good match exists')
        self.assertEqual((None, None), hypotheses.match_propositions(Proposition('closed', (Variable('door', 'd'),)),
                                                                     [Proposition('open', (Variable('door', 'd'),))]),
                         'must return None if no good match exists')
        self.assertEqual((Proposition('closed', (Variable('door', 'd'),)), 1),
                         hypotheses.match_propositions(Proposition('closed', (Variable('door', 'd'),)),
                                                       [Proposition('closed', (Variable('door', 'd'),))]),
                         'must return a match if it exists')
        candidates_door = [Proposition('open', (Variable('door', 'd'),)),
                           Proposition('closed', (Variable('door', 'd'),))]
        self.assertEqual((Proposition('closed', (Variable('door', 'd'),)), 1),
                         hypotheses.match_propositions(Proposition('closed', (Variable('door', 'd'),)),
                                                       candidates_door),
                         'must return a match if it exists')
        candidates_door_placeholder = [Proposition('open', (Variable('door', 'd'),)),
                                       Proposition('closed', (hypotheses.VariablePlaceholder(),))]
        self.assertEqual((candidates_door_placeholder[1], 0),
                         hypotheses.match_propositions(Proposition('closed', (Variable('door', 'd'),)),
                                                       candidates_door_placeholder),
                         'must return a match with proper rating if it exists')
        candidates_door_different = [Proposition('open', (Variable('door', 'd'),)),
                                     Proposition('closed', (Variable('red door', 'd'),))]
        self.assertEqual((candidates_door_different[1], -1),
                         hypotheses.match_propositions(Proposition('closed', (Variable('door', 'd'),)),
                                                       candidates_door_different),
                         'must return a match with proper rating if it exists')
        candidates_door_diff_ph = [Proposition('open', (Variable('door', 'd'),)),
                                   Proposition('closed', (Variable('red door', 'd'),)),
                                   Proposition('closed', (hypotheses.VariablePlaceholder(),))]
        self.assertEqual((candidates_door_diff_ph[2], 0),
                         hypotheses.match_propositions(Proposition('closed', (Variable('door', 'd'),)),
                                                       candidates_door_diff_ph),
                         'must return a match with proper rating if it exists')
        self.assertEqual((candidates_door_placeholder[1], 1),
                         hypotheses.match_propositions(Proposition('closed', (hypotheses.VariablePlaceholder(),)),
                                                       candidates_door_placeholder),
                         'must return a match with proper rating if it exists')
        self.assertEqual((Proposition('closed', (Variable('door', 'd'),)), 0),
                         hypotheses.match_propositions(Proposition('closed', (hypotheses.VariablePlaceholder(),)),
                                                       candidates_door),
                         'must return a match with proper rating if it exists')

        candidates_in_fridge = [self.bread_in_fridge, self.orange_in_fridge]
        self.assertEqual((self.bread_in_fridge, 2),
                         hypotheses.match_propositions(
                             Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c'))),
                             candidates_in_fridge),
                         'must return a match with proper rating if it exists')
        candidates_in_fridge_ph1 = [Proposition('in', (hypotheses.VariablePlaceholder(), Variable('fridge', 'c'))),
                                    self.orange_in_fridge]
        self.assertEqual((candidates_in_fridge_ph1[0], 1),
                         hypotheses.match_propositions(
                             Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c'))),
                             candidates_in_fridge_ph1),
                         'must return a match with proper rating if it exists')

        candidates_in_fridge_ph2 = [self.orange_in_fridge,
                                    Proposition('in', (Variable('bread', 'f'), hypotheses.VariablePlaceholder()))]
        self.assertEqual((candidates_in_fridge_ph2[1], 1),
                         hypotheses.match_propositions(
                             Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c'))),
                             candidates_in_fridge_ph2),
                         'must return a match with proper rating if it exists')

    def test_reconcile_props(self):
        result1 = hypotheses.reconcile_props(self.bread_in_fridge, self.chair_at_kitchen)
        self.assertEqual(None, result1[0], 'must not reconcile unreconcilable propositions')
        second_var_placeholder = Proposition('in', (Variable('bread', 'f'), hypotheses.VariablePlaceholder()))
        result_second_var = hypotheses.reconcile_props(self.bread_in_fridge, self.bread_in_box)
        self.assertEqual(type(second_var_placeholder.arguments[1]), type(result_second_var[0].arguments[1]),
                         'must reconcile two props on differing direct objects')
        self.assertEqual(type(hypotheses.VariablePlaceholder()), type(result_second_var[1][0][Variable('fridge', 'c')]),
                         'must provide appropriate substitution dictionary')
        self.assertEqual(type(hypotheses.VariablePlaceholder()), type(result_second_var[1][1][Variable('box', 'c')]),
                         'must provide appropriate substitution dictionary')

        first_var_placeholder = Proposition('in', (hypotheses.VariablePlaceholder(), Variable('fridge', 'c')))
        result_first_var = hypotheses.reconcile_props(self.bread_in_fridge, self.orange_in_fridge)
        self.assertEqual(type(first_var_placeholder.arguments[0]), type(result_first_var[0].arguments[0]),
                         'must reconcile two props on differing direct subjects')
        self.assertEqual(type(hypotheses.VariablePlaceholder()), type(result_first_var[1][0][Variable('bread', 'f')]),
                         'must provide appropriate substitution dictionary')
        self.assertEqual(type(hypotheses.VariablePlaceholder()), type(result_first_var[1][1][Variable('orange', 'f')]),
                         'must provide appropriate substitution dictionary')

        first_var_placeholder2 = Proposition('in', (hypotheses.VariablePlaceholder(), Variable('fridge', 'c')))
        both_placeholder_result = hypotheses.reconcile_props(first_var_placeholder, first_var_placeholder2)
        self.assertEqual(
            type(Proposition('in', (hypotheses.VariablePlaceholder(), Variable('fridge', 'c'))).arguments[0]),
            type(both_placeholder_result[0].arguments[0]),
            'must properly reconcile two Propositions with placeholders')
        self.assertEqual(
            first_var_placeholder,
            both_placeholder_result[0],
            'must properly reconcile two Propositions with placeholders')
        self.assertEqual(({}, {}), both_placeholder_result[1], 'must not re-substitute existing placeholders')
        self.assertEqual(type(hypotheses.VariablePlaceholder()),
                         type(hypotheses.reconcile_props(
                             Proposition('in', (Variable('box', 'c'), Variable('fridge', 'c'))),
                             Proposition('in', (Variable('fridge', 'c'), Variable('box', 'c'))))[0].arguments[0]),
                         'must not confuse argument order when two variables share names')

    def test_substitute(self):
        self.assertEqual(self.bread_in_fridge, hypotheses.substitute(self.bread_in_fridge, {}),
                         'must not perform any substitutions when not requested')
        self.assertEqual(self.orange_in_fridge,
                         hypotheses.substitute(self.bread_in_fridge, {Variable('bread', 'f'): Variable('orange', 'f')}),
                         'must properly perform substitutions')
        self.assertEqual(self.bread_in_fridge,
                         hypotheses.substitute(self.bread_in_fridge, {Variable('apple', 'f'): Variable('orange', 'f')}),
                         'must not substitute elements that don\'t appear')

    def test_substitute_action_arguments(self):
        self.assertEqual(agent.Take('key', 'pocket',
                                    [Proposition('in', (Variable('key', 'o'), Variable('pocket', 'c')))]),
                         hypotheses.substitute_action_arguments(
                             agent.Take('key', 'pocket',
                                        [Proposition('in', (Variable('key', 'o'), Variable('pocket', 'c')))]),
                             {}
                         ),
                         'must leave action untouched if there are no substitutions to be made')
        subbed_action_first_var = agent.Take('orange', 'fridge',
                                             [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))])
        subbed_action_first_var.vars[0] = hypotheses.VariablePlaceholder()
        result_action_sub_first = hypotheses.substitute_action_arguments(agent.Take('orange', 'fridge',
                                                                                    [Proposition('in', (
                                                                                        Variable('orange', 'f'),
                                                                                        Variable('fridge', 'c')))]),
                                                                         {Variable('orange',
                                                                                   'f'): hypotheses.VariablePlaceholder()})
        self.assertEqual(type(subbed_action_first_var.vars[0]), type(result_action_sub_first.vars[0]),
                         'must substitute within actions')
        result_action_sub_first_c = hypotheses.substitute_action_arguments(agent.Take('orange', 'fridge',
                                                                                      [Proposition('in', (
                                                                                          Variable('orange', 'f'),
                                                                                          Variable('fridge', 'c')))]),
                                                                           {Variable('orange',
                                                                                     'f'): Variable('sandwich', 'f')})
        self.assertEqual(agent.Take('sandwich', 'fridge', [Proposition('in', (Variable('sandwich', 'f'),
                                                                              Variable('fridge', 'c')))]),
                         result_action_sub_first_c,
                         'must properly substitute concrete objects')

    def test_propositions_actions_names_match(self):
        self.assertEqual(True, hypotheses.propositions_actions_names_match(([], None, []), ([], None, [])),
                         'must return True when comparing element names of two empty patterns')

    def test_align_prop_lists(self):
        self.assertEqual([], hypotheses.align_prop_lists([], []))

    def test_matching_pattern(self):
        closed_box = (
            [Proposition('closed', (Variable('box', 'c'),))],
            None,
            [Proposition('closed', (Variable('box', 'c'),))]
        )
        self.assertEqual((None, None), hypotheses.matching_pattern((None, None, None), 'CONTAINER', {}),
                         'must not match nonexistent patterns')
        blockage_store = {'BLOCKAGE':
            [
                ([Proposition('closed', (Variable('box', 'c'),))],
                 None,
                 [Proposition('closed', (Variable('box', 'c'),))])
            ]
        }
        self.assertEqual((0, closed_box),
                         hypotheses.matching_pattern(closed_box, 'BLOCKAGE', blockage_store),
                         'must match existing verbatim equal pattern')

    def test_learn(self):
        kb = {'CONTAINMENT': []}
        self.assertEqual(kb, hypotheses.learn(([], None, []), 'CONTAINMENT', kb),
                         'must not learn anything from an empty pattern')
        result_init = hypotheses.learn(([self.orange_in_fridge], None, [self.orange_in_fridge]), 'CONTAINMENT', kb)
        self.assertEqual({'CONTAINMENT':
            [
                (
                    [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))],
                    None,
                    [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))]
                )
            ]},
            result_init,
            'must learn basic fact if no previous knowledge existed')
        vp = hypotheses.VariablePlaceholder()
        abstracted_first = (
            [Proposition('in', (vp, Variable('fridge', 'c')))], None,
            [Proposition('in', (vp, Variable('fridge', 'c')))]
        )
        result_second = hypotheses.learn(([self.orange_in_fridge], None, [self.orange_in_fridge]), 'CONTAINMENT',
                                         result_init)
        self.assertEqual(1, len(result_second['CONTAINMENT']),
                         'must not inflate the pattern list when reconciliation is possible')
        presumed_second = {'CONTAINMENT':
            [
                (
                    [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))],
                    None,
                    [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))]
                )
            ]}
        self.assertEqual(presumed_second, result_second,
                         'must not change anything about the knowledge base if no new knowledge was provided')
        result_third = hypotheses.learn(([self.bread_in_fridge], None, [self.bread_in_fridge]), 'CONTAINMENT',
                                        result_second)
        self.assertEqual(type(vp), type(result_third['CONTAINMENT'][0][0][0].arguments[0]),
                         'must properly substitute variable placeholders where possible')
        self.assertEqual(type(vp), type(result_third['CONTAINMENT'][0][2][0].arguments[0]),
                         'must properly substitute variable placeholders where possible')
        self.assertEqual(Variable('fridge', 'c'), result_third['CONTAINMENT'][0][0][0].arguments[1],
                         'must not substitute variables where not called for')
        self.assertEqual(Variable('fridge', 'c'), result_third['CONTAINMENT'][0][2][0].arguments[1],
                         'must not substitute variables where not called for')
        self.assertEqual(None, result_third['CONTAINMENT'][0][1],
                         'must not change actions where not called for')
        facts = [Proposition('at', (Variable('box', 'c'), Variable('room', 'r'))),
                 Proposition('at', (Variable('drawer', 'c'), Variable('room', 'r'))),
                 Proposition('in', (Variable('key', 'o'), Variable('I', 'I'))),
                 Proposition('in', (Variable('map', 'o'), Variable('I', 'I'))),
                 Proposition('in', (Variable('pencil', 'o'), Variable('I', 'I')))]
        result_fourth = hypotheses.learn(([Proposition('in', (Variable('key', 'o'), Variable('I', 'I')))],
                                          agent.Put('key', 'box', facts),
                                          [Proposition('in', (Variable('key', 'o'), Variable('box', 'c')))]),
                                         'CONTAINMENT', result_third)
        self.assertEqual(2, len(result_fourth['CONTAINMENT']), 'must add an exception to the list of schema patterns')
        self.assertEqual(([Proposition('in', (Variable('key', 'o'), Variable('I', 'I')))],
                          agent.Put('key', 'box', facts),
                          [Proposition('in', (Variable('key', 'o'), Variable('box', 'c')))]),
                         result_fourth['CONTAINMENT'][1],
                         'must add exceptions verbatim')
        result_fifth = hypotheses.learn(([Proposition('in', (Variable('map', 'o'), Variable('I', 'I')))],
                                         agent.Put('map', 'box', facts),
                                         [Proposition('in', (Variable('map', 'o'), Variable('box', 'c')))]),
                                        'CONTAINMENT', result_fourth)
        self.assertEqual(2, len(result_fourth['CONTAINMENT']), 'must properly reconcile with multiple patterns present')
        self.assertEqual(type(hypotheses.VariablePlaceholder()),
                         type(result_fifth['CONTAINMENT'][1][0][0].arguments[0]),
                         'must correctly assign placeholders with multiple patterns present')
        self.assertEqual(type(hypotheses.VariablePlaceholder()),
                         type(result_fifth['CONTAINMENT'][1][1].vars[0]),
                         'must correctly assign placeholders in actions with multiple patterns present')
        self.assertEqual(type(hypotheses.VariablePlaceholder()),
                         type(result_fifth['CONTAINMENT'][1][2][0].arguments[0]),
                         'must correctly assign placeholders with multiple patterns present')
        result_sixth_source_goal = \
            hypotheses.learn(([Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))],
                              None,
                              [Proposition('at', (Variable('chair', 'o'), Variable('living room', 'r')))]),
                             'SOURCE_GOAL', result_fifth)
        self.assertEqual(2, len(result_sixth_source_goal),
                         'must properly extend the amount of image schemas in the knowledge base')
        self.assertEqual(([Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))],
                          None,
                          [Proposition('at', (Variable('chair', 'o'), Variable('living room', 'r')))]),
                         result_sixth_source_goal['SOURCE_GOAL'][0],
                         'must properly insert the new pattern under a new image schemab in the knowledge base')
        result_sixth_source_goal_2 = \
            hypotheses.learn(([Proposition('at', (Variable('chair', 'o'), Variable('bathroom', 'r')))],
                              None,
                              [Proposition('at', (Variable('chair', 'o'), Variable('living room', 'r')))]),
                             'SOURCE_GOAL', result_sixth_source_goal)
        self.assertEqual(1, len(result_sixth_source_goal_2['SOURCE_GOAL']),
                         'must properly abstract an existing image schema in the relevant list instead of extending it')
        self.assertEqual(2, len(result_sixth_source_goal_2),
                         'must properly abstract an existing image schema in the relevant list')
        self.assertEqual(type(hypotheses.VariablePlaceholder()),
                         type(result_sixth_source_goal_2['SOURCE_GOAL'][0][0][0].arguments[1]),
                         'must properly abstract the proper variable')
        result_seventh = hypotheses.learn(([Proposition('in', (Variable('pencil', 'o'), Variable('I', 'I')))],
                                           agent.Put('pencil', 'drawer', facts),
                                           [Proposition('in', (Variable('pencil', 'o'), Variable('drawer', 'c')))]),
                                          'CONTAINMENT', result_sixth_source_goal_2)
        self.assertEqual(hypotheses.VariablePlaceholder, type(result_seventh['CONTAINMENT'][1][2][0].arguments[0]),
                         'must properly abstract variables in post-conditions in proper patterns')
        self.assertEqual(hypotheses.VariablePlaceholder, type(result_seventh['CONTAINMENT'][1][2][0].arguments[1]),
                         'must properly abstract variables in post-conditions in proper patterns')

    def test_most_similar_pattern(self):
        empty_store = {}
        self.assertEqual((None, None, None), hypotheses.most_similar_pattern(([], None, []), empty_store),
                         'must return empty 3-tuple if no patterns were available for matching')
        kb = {'CONTAINMENT': []}
        result_init = hypotheses.learn(([self.orange_in_fridge], None, [self.orange_in_fridge]), 'CONTAINMENT', kb)

        vp = hypotheses.VariablePlaceholder()
        abstracted_first = (
            [Proposition('in', (vp, Variable('fridge', 'c')))], None,
            [Proposition('in', (vp, Variable('fridge', 'c')))]
        )
        result_second = hypotheses.learn(([self.orange_in_fridge], None, [self.orange_in_fridge]), 'CONTAINMENT',
                                         result_init)

        presumed_second = {'CONTAINMENT':
            [
                (
                    [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))],
                    None,
                    [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))]
                )
            ]}
        result_third = hypotheses.learn(([self.bread_in_fridge], None, [self.bread_in_fridge]), 'CONTAINMENT',
                                        result_second)
        facts = [Proposition('at', (Variable('box', 'c'), Variable('room', 'r'))),
                 Proposition('in', (Variable('key', 'o'), Variable('I', 'I'))),
                 Proposition('in', (Variable('map', 'o'), Variable('I', 'I')))]
        result_fourth = hypotheses.learn(([Proposition('in', (Variable('key', 'o'), Variable('I', 'I')))],
                                          agent.Put('key', 'box', facts),
                                          [Proposition('in', (Variable('key', 'o'), Variable('box', 'c')))]),
                                         'CONTAINMENT', result_third)

        result_fifth = hypotheses.learn(([Proposition('in', (Variable('map', 'o'), Variable('I', 'I')))],
                                         agent.Put('map', 'box', facts),
                                         [Proposition('in', (Variable('map', 'o'), Variable('box', 'c')))]),
                                        'CONTAINMENT', result_fourth)
        result_sixth_source_goal = \
            hypotheses.learn(([Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))],
                              None,
                              [Proposition('at', (Variable('chair', 'o'), Variable('living room', 'r')))]),
                             'SOURCE_GOAL', result_fifth)
        result_sixth_source_goal_2 = \
            hypotheses.learn(([Proposition('at', (Variable('chair', 'o'), Variable('bathroom', 'r')))],
                              None,
                              [Proposition('at', (Variable('chair', 'o'), Variable('living room', 'r')))]),
                             'SOURCE_GOAL', result_sixth_source_goal)
        self.assertEqual((result_init['CONTAINMENT'][0], 'CONTAINMENT', 1),
                         hypotheses.most_similar_pattern(
                             ([Proposition('in', (Variable('carrot', 'f'), Variable('fridge', 'c')))],
                              None, []), result_init), 'must find appropriate fitting pattern where one exists')
        pat_with_placeholder = hypotheses.most_similar_pattern(
            ([Proposition('in', (Variable('carrot', 'f'), Variable('fridge', 'c')))],
             None, []), result_third)
        self.assertEqual((result_third['CONTAINMENT'][0], 'CONTAINMENT', 2), pat_with_placeholder,
                         'must find appropriate pattern')
        self.assertEqual(type(pat_with_placeholder[0][0][0].arguments[0]), hypotheses.VariablePlaceholder,
                         'matched pattern must have placeholder')

        self.assertEqual((result_fourth['CONTAINMENT'][0], 'CONTAINMENT', 0),
                         hypotheses.most_similar_pattern(
                             ([Proposition('in', (Variable('key', 'o'), Variable('I', 'I')))], None, []),
                             result_fourth),
                         'must find best pattern among multiple patterns')
        self.assertEqual((result_fourth['CONTAINMENT'][1], 'CONTAINMENT', 3),
                         hypotheses.most_similar_pattern(
                             ([Proposition('in', (Variable('key', 'o'), Variable('I', 'I')))],
                              agent.Put('key', 'pocket', facts), []),
                             result_fourth),
                         'must find best pattern among multiple patterns')
        self.assertEqual((result_fourth['CONTAINMENT'][1], 'CONTAINMENT', 5),
                         hypotheses.most_similar_pattern(
                             ([Proposition('in', (Variable('key', 'o'), Variable('I', 'I')))],
                              agent.Put('key', 'box', facts), []),
                             result_fourth),
                         'must find best pattern among multiple patterns and assign it correct score')
        self.assertEqual((result_sixth_source_goal['SOURCE_GOAL'][0], 'SOURCE_GOAL', -1),
                         hypotheses.most_similar_pattern(
                             ([Proposition('at', (Variable('chest', 'c'), Variable('bedroom', 'r')))],
                              None, []), result_sixth_source_goal),
                         'must find best pattern among multiple patterns and assign it correct score')
        self.assertEqual((result_sixth_source_goal_2['CONTAINMENT'][1], 'CONTAINMENT', -1),
                         hypotheses.most_similar_pattern(([], agent.Put('carrot', 'bowl'), []),
                                                         result_sixth_source_goal_2),
                         'must select pattern by action type alone')
        result_seventh = hypotheses.learn(([Proposition('in', (Variable('pencil', 'o'), Variable('I', 'I')))],
                                         agent.Put('pencil', 'drawer', facts),
                                         [Proposition('in', (Variable('pencil', 'o'), Variable('drawer', 'c')))]),
                                        'CONTAINMENT', result_sixth_source_goal_2)
        #self.assertEqual(hypotheses.VariablePlaceholder, type(result_seventh['CONTAINMENT'][1])

    def test_infer(self):
        self.assertEqual((([], None, []), {}), hypotheses.infer(([], None, []), ([], None, [])),
                         'must return empty inferences from empty target and source patterns')
        self.assertEqual((None, None),
                         hypotheses.infer(([], None, []),
                                          ([Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'f')))],
                                           None, [])),
                         'must return no inferences from empty target patterns')
        self.assertEqual((None, None),
                         hypotheses.infer((
                             [Proposition('in', (Variable('apple', 'f'), Variable('basket', 'c')))],
                             None,
                             [Proposition('in', (Variable('apple', 'f'), Variable('basket', 'c')))]
                         ),
                             (
                                 [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))],
                                 None,
                                 [Proposition('in', (Variable('orange', 'f'), Variable('fridge', 'c')))]
                             )),
                         'must not infer anything from patterns which don\'t agree on any variables')
        vp1 = hypotheses.VariablePlaceholder()
        targ1 = (
            [Proposition('in', (vp1, Variable('fridge', 'c')))],
            None,
            [Proposition('in', (vp1, Variable('fridge', 'c')))]
        )
        self.assertEqual((None, None),
                         hypotheses.infer(targ1,
                                          (
                                              [Proposition('in', (Variable('bread', 'f'), Variable('box', 'c')))],
                                              None,
                                              []
                                          )),
                         'must not infer if even one variable is mismatched')
        inferred_bread_in_fridge, _ = hypotheses.infer(targ1, (
            [Proposition('in', (Variable('bread', 'f'), Variable('fridge', 'c')))],
            None,
            []
        ))
        self.assertEqual(None, targ1[0][0].arguments[0].held_variable, 'inference must not affect the target pattern')
        self.assertEqual(hypotheses.VariablePlaceholder, type(inferred_bread_in_fridge[0][0].arguments[0]),
                         'inference must preserve placeholders')
        self.assertEqual(Variable('bread', 'f'), inferred_bread_in_fridge[0][0].arguments[0].held_variable,
                         'inference must assign correct variables')
        self.assertEqual(Variable('bread', 'f'), inferred_bread_in_fridge[2][0].arguments[0].held_variable,
                         'inference must assign correct variables')
        self.assertEqual(inferred_bread_in_fridge[0][0].arguments[0], inferred_bread_in_fridge[2][0].arguments[0],
                         'must assign variables all across the patterns')
        vp2, vp3 = hypotheses.VariablePlaceholder(), hypotheses.VariablePlaceholder()
        targ2 = (
            [Proposition('in', (vp2, vp3))],
            None,
            [Proposition('in', (vp2, vp3))]
        )
        inferred_orange_in_basket, _ = hypotheses.infer(targ2,
                                                        (
                                                            [Proposition('in', (
                                                                Variable('orange', 'f'), Variable('basket', 'c')))],
                                                            None,
                                                            []
                                                        ))
        self.assertEqual(Variable('orange', 'f'), inferred_orange_in_basket[0][0].arguments[0].held_variable,
                         'inference must properly assign variables to VariablePlaceholders')
        self.assertEqual(Variable('orange', 'f'), inferred_orange_in_basket[2][0].arguments[0].held_variable,
                         'inference must properly assign variables to VariablePlaceholders')
        self.assertEqual(Variable('basket', 'c'), inferred_orange_in_basket[0][0].arguments[1].held_variable,
                         'inference must properly assign variables to VariablePlaceholders')
        self.assertEqual(Variable('basket', 'c'), inferred_orange_in_basket[2][0].arguments[1].held_variable,
                         'inference must properly assign variables to VariablePlaceholders')
        self.assertEqual(None, vp2.held_variable, 'inference must not fill the original target VariablePlaceholders')
        self.assertEqual(None, vp3.held_variable, 'inference must not fill the original target VariablePlaceholders')
        self.assertEqual(None, targ2[0][0].arguments[0].held_variable,
                         'inference must not fill the original target VariablePlaceholders')
        self.assertEqual(None, targ2[2][0].arguments[0].held_variable,
                         'inference must not fill the original target VariablePlaceholders')
        self.assertEqual(None, targ2[0][0].arguments[1].held_variable,
                         'inference must not fill the original target VariablePlaceholders')
        self.assertEqual(None, targ2[2][0].arguments[1].held_variable,
                         'inference must not fill the original target VariablePlaceholders')
        vp4, vp5 = hypotheses.VariablePlaceholder(), hypotheses.VariablePlaceholder()
        targ3 = (
            [Proposition('in', (vp4, Variable('I', 'I')))],
            agent.Insert(vp4, vp5),
            [Proposition('in', (vp4, vp5))]
        )
        infer_insert_envelope_into_box, _ = hypotheses.infer(targ3,
                                                             (
                                                                 [Proposition('in', (
                                                                 Variable('envelope', 'o'), Variable('I', 'I')))],
                                                                 agent.Insert(Variable('envelope', 'o'),
                                                                              Variable('box', 'c')),
                                                                 []
                                                             ))
        self.assertEqual(Variable('envelope', 'o'), infer_insert_envelope_into_box[0][0].arguments[0].held_variable,
                         'must correctly assign variables to VariablePlaceholders in pre-conditions')
        self.assertEqual(Variable('envelope', 'o'), infer_insert_envelope_into_box[1].vars[0].held_variable,
                         'must correctly assign variables to VariablePlaceholders in actions')
        self.assertEqual(Variable('box', 'c'), infer_insert_envelope_into_box[1].vars[1].held_variable,
                         'must correctly assign variables to VariablePlaceholders in actions')
        self.assertEqual(Variable('envelope', 'o'), infer_insert_envelope_into_box[2][0].arguments[0].held_variable,
                         'must correctly assign variables to VariablePlaceholders in post-conditions')
        self.assertEqual(Variable('box', 'c'), infer_insert_envelope_into_box[2][0].arguments[1].held_variable,
                         'must correctly assign variables to VariablePlaceholders in post-conditions')
        vp6, vp7, vp8 = hypotheses.VariablePlaceholder(), hypotheses.VariablePlaceholder(), hypotheses.VariablePlaceholder()
        targ4 = (
            [Proposition('in', (vp6, vp7))],
            agent.Insert(vp6, vp8),
            [Proposition('in', (vp6, vp8))]
        )

        infer_potato_was_in_somewhere, _ = hypotheses.infer(targ4,
                                                         (
                                                             [],
                                                             None,
                                                             [Proposition('in', (Variable('potato', 'f'),
                                                                                Variable('basket', 'c')))]
                                                         ))
        self.assertEqual(Variable('potato', 'f'), infer_potato_was_in_somewhere[0][0].arguments[0].held_variable,
                         'must correctly infer pre-conditions from post-conditions')
        self.assertEqual(hypotheses.VariablePlaceholder,
                         type(infer_potato_was_in_somewhere[0][0].arguments[1]),
                         'must correctly infer pre-conditions from post-conditions')
        self.assertEqual(Variable('potato', 'f'), infer_potato_was_in_somewhere[1].vars[0].held_variable,
                         'must correctly infer action arguments')
        self.assertEqual(Variable('basket', 'c'), infer_potato_was_in_somewhere[1].vars[1].held_variable,
                         'must correctly infer action arguments')

        targ5 = (
            [Proposition('in', (vp6, vp7))],
            agent.Take(vp6, vp7),
            [Proposition('in', (vp6, Variable('I', 'I')))]
        )

        infer_potato_was_in_basket, _ = hypotheses.infer(targ5,
                                                         (
                                                             [],
                                                             agent.Take(Variable('potato', 'f'), Variable('basket', 'c')),
                                                             [Proposition('in', (Variable('potato', 'f'),
                                                                                Variable('I', 'I')))]
                                                         ))
        self.assertEqual(Variable('potato', 'f'), infer_potato_was_in_basket[0][0].arguments[0].held_variable,
                         'must correctly infer backwards')
        self.assertEqual(Variable('basket', 'c'), infer_potato_was_in_basket[0][0].arguments[1].held_variable,
                         'must correctly infer backwards')
