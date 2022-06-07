from unittest import TestCase

import textworld
from textworld.logic import Proposition, Variable
import agent


def experience_is_in(experience, experiences):
    for exp in experiences:
        if set(experience[0]) == set(exp[0]) and set(experience[2]) == set(exp[2]) and experience[1] == exp[1]:
            return True
    return False


class Test_Agent(TestCase):
    def test_get_experience_from_walkthrough(self):
        et = textworld.start('test_games/simplest_1o_1r.z8', agent.infos)
        state = et.reset()
        state2 = et.step('take Microsoft limited edition key')[0]
        state3 = et.step('unlock Microsoft limited edition safe with Microsoft limited edition key')[0]
        state4 = et.step('open Microsoft limited edition safe')[0]
        state5 = et.step('take type N latchkey from Microsoft limited edition safe')[0]
        state6 = et.step('unlock type N safe with type N latchkey')[0]
        tuples = [
            (state.facts, 'take Microsoft limited edition key', state2.facts),
            (state2.facts, 'unlock Microsoft limited edition safe with Microsoft limited edition key', state3.facts),
            (state3.facts, 'open Microsoft limited edition safe', state4.facts),
            (state4.facts, 'take type N latchkey from Microsoft limited edition safe', state5.facts),
            (state5.facts, 'unlock type N safe with type N latchkey', state6.facts)
        ]
        vartuples = [
            (state.facts, agent.Take('Microsoft limited edition key', facts=state.facts), state2.facts),
            (state2.facts,
             agent.Unlock('Microsoft limited edition safe', 'Microsoft limited edition key', facts=state2.facts),
             state3.facts),
            (state3.facts, agent.Open('Microsoft limited edition safe', facts=state3.facts), state4.facts),
            (state4.facts, agent.Take('type N latchkey', 'Microsoft limited edition safe', facts=state4.facts),
             state5.facts),
            (state5.facts, agent.Unlock('type N safe', 'type N latchkey', facts=state5.facts), state6.facts)
        ]
        env = textworld.start('test_games/simplest_1o_1r.z8', agent.infos)
        self.assertEqual(tuples, agent.get_experience_from_walkthrough(env), 'extracted experience must be equal to '
                                                                             'manual playthrough')
        self.assertEqual(agent.Take('Microsoft limited edition key', facts=state.facts),
                         agent.get_experience_from_walkthrough(env, True)[0][1],
                         'extracted experience with variables must have proper variables in actions')
        self.assertEqual(vartuples, agent.get_experience_from_walkthrough(env, True), 'extracted experience must be '
                                                                                      'equal to manual playthrough '
                                                                                      'and the variables must be '
                                                                                      'instanced in commands')

    def test_collect_facts(self):
        facts = [Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                 Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c'))),
                 Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r'))),
                 Proposition('in', (Variable('foo', 'c'), Variable('bar', 'c')))]
        collected = [Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                     Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c'))),
                     Proposition('in', (Variable('foo', 'c'), Variable('bar', 'c')))]
        self.assertEqual(collected, agent.collect_facts_by_object(facts, Variable('foo', 'c')), 'must collect all '
                                                                                                'facts pertaining to '
                                                                                                'object')

    def test_diff_facts(self):
        facts1 = [Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                  Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c'))),
                  Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r')))]
        facts2 = [Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                  Proposition('at', (Variable('bagel', 'f'), Variable('foo', 'c'))),
                  Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r')))]
        facts3 = [Proposition('at', (Variable('foo', 'c'), Variable('living room', 'r'))),
                  Proposition('in', (Variable('bagel', 'f'), Variable('bar', 'c'))),
                  Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r')))]
        facts4 = [Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                  Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r')))]
        facts5 = [Proposition('at', (Variable('foo', 'c'), Variable('living room', 'r'))),
                  Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r')))]
        facts6 = [Proposition('at', (Variable('foo', 'c'), Variable('living room', 'r'))),
                  Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c'))),
                  Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r')))]

        diff12 = [{Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c')))},
                  {Proposition('at', (Variable('bagel', 'f'), Variable('foo', 'c')))}]
        diff13 = [(Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                   Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c')))),
                  (Proposition('at', (Variable('foo', 'c'), Variable('living room', 'r'))),
                   Proposition('at', (Variable('bagel', 'f'), Variable('kitchen', 'r'))))]
        diff14 = [{Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c')))},
                  set([])]
        diff15 = [(Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                   Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c')))),
                  (Proposition('at', (Variable('foo', 'c'), Variable('living room', 'r'))))]
        diff16 = [{Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r')))},
                  {Proposition('at', (Variable('foo', 'c'), Variable('living room', 'r')))}]

        self.assertEqual(diff12, agent.diff_facts(facts1, facts2), 'must detect proposition type changes')
        # self.assertEqual(diff13, agent.diff_facts(facts1, facts3), 'must detect multiple different proposition changes')
        self.assertEqual(diff14, agent.diff_facts(facts1, facts4), 'must detect disappearance and signal appropriately')
        # self.assertEqual(diff15, agent.diff_facts(facts1, facts5), 'must detect disappareance along with other '
        #                                                           'proposition changes at once')
        self.assertEqual(diff16, agent.diff_facts(facts1, facts6), 'must detect proposition argument changes')

    def test_command_to_action(self):
        facts = [Proposition('at', (Variable('foo', 'c'), Variable('kitchen', 'r'))),
                 Proposition('in', (Variable('bagel', 'f'), Variable('foo', 'c'))),
                 Proposition('at', (Variable('bar', 'c'), Variable('kitchen', 'r')))]
        look_cmd = 'look'
        eat_cmd = 'eat foo'
        examine_cmd = 'examine bar'
        drop_cmd = 'drop baz'
        close_cmd = 'close qux'
        open_cmd = 'open asdf'
        go_cmd = 'go east'
        unlock_cmd = 'unlock qwer'
        lock_cmd = 'lock zxcv'
        unlock_cmd = 'unlock 123'
        lock_with_cmd = 'lock door with key'
        unlock_with_cmd = 'unlock car with salmon'
        unlock_with_multiword_cmd = 'unlock big door with small key'
        take_cmd = 'take part'
        take_from_cmd = 'take tuna from can'
        insert_cmd = 'insert chicken into zeppelin'
        put_cmd = 'put bus on space shuttle'

        self.assertEqual(agent.command_to_action(look_cmd), agent.Look())
        self.assertEqual(agent.command_to_action(eat_cmd), agent.Eat('foo'))
        self.assertEqual([Variable('foo', 'c')], agent.command_to_action(eat_cmd, facts).vars, 'must properly extract '
                                                                                               'variables')
        self.assertEqual(agent.command_to_action(examine_cmd), agent.Examine('bar'))
        self.assertEqual(agent.command_to_action(drop_cmd), agent.Drop('baz'))
        self.assertEqual([None], agent.command_to_action(drop_cmd, facts).vars, 'must not extract unidentifiable '
                                                                                'variables')
        self.assertEqual(agent.command_to_action(close_cmd), agent.Close('qux'))
        self.assertEqual(agent.command_to_action(open_cmd), agent.Open('asdf'))
        self.assertEqual(agent.command_to_action(go_cmd), agent.Go('east'))
        self.assertEqual(agent.command_to_action(unlock_cmd), agent.Unlock('123'))
        self.assertEqual(agent.command_to_action(lock_cmd), agent.Lock('zxcv'))
        self.assertEqual(agent.command_to_action(lock_with_cmd), agent.Lock('door', 'key'))
        self.assertEqual(agent.command_to_action(unlock_with_cmd), agent.Unlock('car', 'salmon'))
        self.assertEqual(agent.Unlock('big door', 'small key'), agent.command_to_action(unlock_with_multiword_cmd))
        self.assertEqual(agent.command_to_action(take_cmd), agent.Take('part'))
        self.assertEqual(agent.command_to_action(take_from_cmd), agent.Take('tuna', 'can'))
        self.assertEqual(agent.command_to_action(insert_cmd), agent.Insert('chicken', 'zeppelin'))
        self.assertEqual(agent.command_to_action(put_cmd), agent.Put('bus', 'space shuttle'))

    def test_fact_commonalities(self):
        fact1 = Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))
        fact2 = Proposition('at', (Variable('table', 'o'), Variable('kitchen', 'r')))
        fact3 = Proposition('in', (Variable('sandwich', 'f'), Variable('fridge', 'c')))
        fact4 = Proposition('at', (Variable('plant', 'o'), Variable('fridge', 'c')))
        fact5 = Proposition('open', (Variable('fridge', 'c'),))
        fact6 = Proposition('closed', (Variable('door', 'd'),))
        fact7 = Proposition('in', (Variable('wall', 'o'), Variable('hole', 'o')))
        self.assertEqual(agent.fact_commonalities(fact1, fact2),
                         {'name': 'at', 'arguments': [{'type': 'o'}, {'name': 'kitchen', 'type': 'r'}]},
                         'must detect commonality of type')
        self.assertEqual(agent.fact_commonalities(fact3, fact4), {'arguments': [{}, {'name': 'fridge', 'type': 'c'}]},
                         'must detect commonality of object')
        self.assertEqual(agent.fact_commonalities(fact2, fact7), {'arguments': [{'type': 'o'}, {}]},
                         'must detect commonality of subject type')
        self.assertEqual(agent.fact_commonalities(fact5, fact6), {'arguments': [{}]}, 'must recognize lack of '
                                                                                      'commonalities')
        self.assertEqual(agent.fact_commonalities(fact1, fact6), {'arguments': [{}]}, 'must work with propositions of '
                                                                                      'different size')

    def test_check_predicate(self):
        facts1 = [Proposition('at', (Variable('sink', 'c'), Variable('kitchen', 'r'))),
                  Proposition('in', (Variable('cup', 'c'), Variable('sink', 'c'))),
                  Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))]
        facts2 = [Proposition('at', (Variable('sink', 'c'), Variable('kitchen', 'r'))),
                  Proposition('in', (Variable('cup', 'c'), Variable('fridge', 'c'))),
                  Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))]
        facts3 = [Proposition('open', (Variable('door', 'd'),)),
                  Proposition('closed', (Variable('chest', 'c'),)),
                  Proposition('link', (Variable('kitchen', 'r'), Variable('door', 'd'), Variable('backyard', 'r')))]

        state1 = textworld.core.GameState()
        state1.facts = facts1

        state3 = textworld.core.GameState()
        state3.facts = facts3
        pred_p_name = agent.Exists([(agent.Selector.PROPOSITION_NAME, agent.is_equal, 'at')])
        pred_h_name = agent.Exists([(agent.Selector.PROPOSITION_HEAD_NAME, agent.is_equal, 'cup')])
        pred_h_type = agent.Exists([(agent.Selector.PROPOSITION_HEAD_TYPE, agent.is_equal, 'o')])
        pred_t_name = agent.Exists([(agent.Selector.PROPOSITION_TAIL_NAME, agent.is_equal, 'kitchen')])
        pred_t_name_nonexistent = agent.Exists([(agent.Selector.PROPOSITION_TAIL_NAME, agent.is_equal, 'fridge')])
        pred_t_type = agent.Exists([(agent.Selector.PROPOSITION_TAIL_TYPE, agent.is_equal, 'c')])
        pred_t_type_nonexistent = agent.Exists([(agent.Selector.PROPOSITION_TAIL_TYPE, agent.is_equal, 'r')])
        pred_any_name = agent.Exists([(agent.Selector.PROPOSITION_ANY_ARG_NAME, agent.is_equal, 'sink')])
        pred_any_name2 = agent.Exists([(agent.Selector.PROPOSITION_ANY_ARG_NAME, agent.is_equal, 'backyard')])
        pred_any_type = agent.Exists([(agent.Selector.PROPOSITION_ANY_ARG_TYPE, agent.is_equal, 'o')])
        self.assertEqual((True, Proposition('at', (Variable('sink', 'c'), Variable('kitchen', 'r')))),
                         agent.check_predicate(pred_p_name, state1), 'must properly accept met predicate')
        self.assertEqual((False, None), agent.check_predicate(pred_p_name, state3), 'must properly recognize no '
                                                                                    'proposition matches name')
        self.assertEqual((True, Proposition('in', (Variable('cup', 'c'), Variable('sink', 'c')))),
                         agent.check_predicate(pred_h_name, state1), 'must properly recognize proposition head name '
                                                                     'match')
        self.assertEqual((False, None), agent.check_predicate(pred_h_name, state3), 'must properly recognize lack of '
                                                                                    'proposition head name match')
        self.assertEqual((True, Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))),
                         agent.check_predicate(pred_h_type, state1), 'must properly recognize proposition head type '
                                                                     'match')
        self.assertEqual((False, None), agent.check_predicate(pred_h_type, state3), 'must properly recognize lack of '
                                                                                    'proposition head type match')
        self.assertEqual((True, Proposition('at', (Variable('sink', 'c'), Variable('kitchen', 'r')))),
                         agent.check_predicate(pred_t_name, state1), 'must propertly recognize proposition tail name '
                                                                     'match')
        self.assertEqual((False, None), agent.check_predicate(pred_t_name, state3), 'must properly recognize when '
                                                                                    'there is no proposition\'s tail '
                                                                                    'to name-check')
        self.assertEqual((False, None), agent.check_predicate(pred_t_name_nonexistent, state1), 'must properly '
                                                                                                'recognize when a '
                                                                                                'tail with a given '
                                                                                                'name does not exist')
        self.assertEqual((True, Proposition('in', (Variable('cup', 'c'), Variable('sink', 'c')))),
                         agent.check_predicate(pred_t_type, state1), 'must properly recognize existence of '
                                                                     'proposition tail meeting type requirements')
        self.assertEqual((False, None),
                         agent.check_predicate(pred_t_type_nonexistent, state3), 'must properly recognize '
                                                                                 'nonexistence of proposition tail '
                                                                                 'meeting type requirements')
        self.assertEqual((True, Proposition('at', (Variable('sink', 'c'), Variable('kitchen', 'r')))),
                         agent.check_predicate(pred_any_name, state1), 'must properly recognize existence of an '
                                                                       'argument meeting the name requirement')
        self.assertEqual((True, Proposition('link', (Variable('kitchen', 'r'), Variable('door', 'd'),
                                                     Variable('backyard', 'r')))),
                         agent.check_predicate(pred_any_name2, state3), 'must properly recognize existence of an '
                                                                        'argument meeting the name requirement')
        self.assertEqual((False, None), agent.check_predicate(pred_any_name2, state1), 'must properly recognize '
                                                                                       'nonexistence of any argumennt'
                                                                                       ' meeting the name requirement')
        self.assertEqual((True, Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))),
                         agent.check_predicate(pred_any_type, state1), 'must properly recognize existence of an '
                                                                       'argument meeting the type requirement')
        self.assertEqual((False, None), agent.check_predicate(pred_any_type, state3), 'must properly recognize '
                                                                                      'nonexistence of an '
                                                                                      'argument meeting the type '
                                                                                      'requirement')

    def test_extract_variables(self):
        facts1 = [Proposition('at', (Variable('sink', 'c'), Variable('kitchen', 'r'))),
                  Proposition('in', (Variable('cup', 'c'), Variable('sink', 'c'))),
                  Proposition('at', (Variable('chair', 'o'), Variable('kitchen', 'r')))]

        self.assertEqual([Variable('sink', 'c')], agent.Examine('sink', facts=facts1).vars, 'must properly extract '
                                                                                            'existing variable')

        self.assertEqual([Variable('sink', 'c'), Variable('kitchen', 'r')],
                         agent.Take('sink', 'kitchen', facts=facts1).vars, 'must properly extract multiple variables')

        self.assertEqual([Variable('sink', 'c'), Variable('chair', 'o')],
                         agent.Unlock('sink', 'chair', facts=facts1).vars,
                         'must properly extract variables from different propositions')

        self.assertEqual([Variable('cup', 'c'), None], agent.Insert('cup', 'fridge', facts=facts1).vars,
                         'must properly extract the variables that do exist, even if some don\'t')

        self.assertEqual([None], agent.Take('christmas tree', facts=facts1).vars, 'must properly signal lack of '
                                                                                  'corresponding variable')
        self.assertEqual([], agent.Eat('waffle').vars, 'must not fill the vars list unless asked to')

    def test_experience_gatherer(self):
        facts = [Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                 Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                 Proposition('at', (Variable('insect', 'o'), Variable('pantry', 'r'))),
                 Proposition('open', (Variable('crate', 'c'),))]
        exp_gathering_agent = agent.ExperienceGatheringAgent(2235101)  # not all seeds will work, some result in crate
        # being closed before attempts to insert insect are made, others never pick up the insect after dropping it,
        # even in a couple thousand tries
        exp_gatherer = agent.ExperienceGatherer(exp_gathering_agent)
        walkthrough_exp = [([Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                             Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                             Proposition('at', (Variable('insect', 'o'), Variable('pantry', 'r'))),
                             Proposition('open', (Variable('crate', 'c'),))],
                            agent.Take('insect', facts=facts),
                            [Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                             Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                             Proposition('open', (Variable('crate', 'c'),)),
                             Proposition('in', (Variable('insect', 'o'), Variable('I', 'I')))]),
                           ([Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                             Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                             Proposition('open', (Variable('crate', 'c'),)),
                             Proposition('in', (Variable('insect', 'o'), Variable('I', 'I')))],
                            agent.Insert('insect', 'crate', facts=facts),
                            [Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                             Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                             Proposition('open', (Variable('crate', 'c'),)),
                             Proposition('in', (Variable('insect', 'o'), Variable('crate', 'c')))])]
        env = textworld.start('games/1ob_1room.z8', agent.infos)
        experiences = exp_gatherer.gather_experience(env, 2000)
        exp1_is_in = experience_is_in(walkthrough_exp[0], experiences)
        self.assertEqual(exp1_is_in, True, 'a part of walkthrough experience should show up in '
                                           'random choice experience')
        exp2_is_in = experience_is_in(walkthrough_exp[1], experiences)
        self.assertEqual(exp2_is_in, True, 'second part of walkthrough experience should show up in random choice '
                                           'experience')

    def test_gather_multiple(self):
        facts1 = [Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                  Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                  Proposition('at', (Variable('insect', 'o'), Variable('pantry', 'r'))),
                  Proposition('open', (Variable('crate', 'c'),))]
        walkthrough_exp1 = [([Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                              Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                              Proposition('at', (Variable('insect', 'o'), Variable('pantry', 'r'))),
                              Proposition('open', (Variable('crate', 'c'),))],
                             agent.Take('insect', facts=facts1),
                             [Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                              Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                              Proposition('open', (Variable('crate', 'c'),)),
                              Proposition('in', (Variable('insect', 'o'), Variable('I', 'I')))]),
                            ([Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                              Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                              Proposition('open', (Variable('crate', 'c'),)),
                              Proposition('in', (Variable('insect', 'o'), Variable('I', 'I')))],
                             agent.Insert('insect', 'crate', facts=facts1),
                             [Proposition('at', (Variable('P', 'P'), Variable('pantry', 'r'))),
                              Proposition('at', (Variable('crate', 'c'), Variable('pantry', 'r'))),
                              Proposition('open', (Variable('crate', 'c'),)),
                              Proposition('in', (Variable('insect', 'o'), Variable('crate', 'c')))])]
        facts2 = [Proposition('at', (Variable('P', 'P'), Variable('parlor', 'r'))),
                  Proposition('at', (Variable('Microsoft limited edition safe', 'c'), Variable('parlor', 'r'))),
                  Proposition('at', (Variable('type N safe', 'c'), Variable('parlor', 'r'))),
                  Proposition('at', (Variable('Microsoft limited edition key', 'k'), Variable('parlor', 'r'))),
                  Proposition('in',
                              (Variable('type N latchkey', 'k'), Variable('Microsoft limited edition safe', 'c'))),
                  Proposition('locked', (Variable('Microsoft limited edition safe', 'c'),)),
                  Proposition('locked', (Variable('type N safe', 'c'),)),
                  Proposition('match', (
                      Variable('Microsoft limited edition key', 'k'), Variable('Microsoft limited edition safe', 'c'))),
                  Proposition('match', (Variable('type N latchkey', 'k'), Variable('type N safe', 'c')))]
        walkthrough_exp2 = [([Proposition('at', (Variable('P', 'P'), Variable('parlor', 'r'))),
                              Proposition('at', (Variable('type N safe', 'c'), Variable('parlor', 'r'))),
                              Proposition('at',
                                          (Variable('Microsoft limited edition safe', 'c'), Variable('parlor', 'r'))),
                              Proposition('at',
                                          (Variable('Microsoft limited edition key', 'k'), Variable('parlor', 'r'))),
                              Proposition('in', (
                                  Variable('type N latchkey', 'k'), Variable('Microsoft limited edition safe', 'c'))),
                              Proposition('locked', (Variable('Microsoft limited edition safe', 'c'),)),
                              Proposition('locked', (Variable('type N safe', 'c'),)),
                              Proposition('match', (Variable('Microsoft limited edition key', 'k'),
                                                    Variable('Microsoft limited edition safe', 'c'))),
                              Proposition('match', (Variable('type N latchkey', 'k'), Variable('type N safe', 'c')))],
                             agent.Take('Microsoft limited edition key', facts=facts2),
                             [Proposition('at', (Variable('P', 'P'), Variable('parlor', 'r'))),
                              Proposition('at', (Variable('type N safe', 'c'), Variable('parlor', 'r'))),
                              Proposition('at',
                                          (Variable('Microsoft limited edition safe', 'c'), Variable('parlor', 'r'))),
                              Proposition('in', (
                                  Variable('type N latchkey', 'k'), Variable('Microsoft limited edition safe', 'c'))),
                              Proposition('locked', (Variable('Microsoft limited edition safe', 'c'),)),
                              Proposition('locked', (Variable('type N safe', 'c'),)),
                              Proposition('match', (Variable('Microsoft limited edition key', 'k'),
                                                    Variable('Microsoft limited edition safe', 'c'))),
                              Proposition('match', (Variable('type N latchkey', 'k'), Variable('type N safe', 'c'))),
                              Proposition('in', (Variable('Microsoft limited edition key', 'k'), Variable('I', 'I')))])]

        exp_agent = agent.ExperienceGatheringAgent(2567121)
        exp_gatherer = agent.ExperienceGatherer(exp_agent)
        exp_gatherer.gather_experience_multiple(['games/simplest_1o_1r.z8', 'games/1ob_1room.z8'], 1000)

        exp1_is_present = False
        exp2_is_present = False
        for exp in exp_gatherer.experience:
            if set(walkthrough_exp2[0][0]) == set(exp[0]) and set(walkthrough_exp2[0][2]) == set(exp[2]) and \
                    walkthrough_exp2[0][1] == exp[1]:
                exp2_is_present = True
            if set(walkthrough_exp1[0][0]) == set(exp[0]) and set(walkthrough_exp1[0][2]) == set(exp[2]) and \
                    walkthrough_exp1[0][1] == exp[1]:
                exp1_is_present = True
        self.assertEqual(exp1_is_present, True,
                         'should gather parts of actual walkthrough in the random play on multiple games')
        self.assertEqual(exp2_is_present, True, 'should gather parts of actual walkthrough in the random play on '
                                                'multiple games')
