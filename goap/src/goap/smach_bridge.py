# Copyright (c) 2013, Felix Kolbe
# All rights reserved. BSD License
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# * Neither the name of the {organization} nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import tf

from smach import State

from common import *

from uashh_smach.manipulator.look_around import get_lookaround_smach
from uashh_smach.manipulator.move_arm import get_move_arm_to_joints_positions_state


ARM_FOLDED_POSE = [0, 0.52, 052, -1.57, 0]
ARM_FOLDED_POSE_NAMES = ['DH_1_2', 'DH_2_3', 'DH_4_4', 'DH_4_5', 'DH_5_6']
ARM_FOLDED_POSE_NAMED = dict(zip(ARM_FOLDED_POSE_NAMES, ARM_FOLDED_POSE))


class GOAPActionWrapperState(State):
    # FIXME: actually wraps nodes, not actions
    """Used (by the planner) to add GOAP actions to a SMACH state machine"""
    def __init__(self, action, next_worldstate):
        State.__init__(self, outcomes=['succeeded', 'aborted'])
        self.action = action
        self._next_worldstate = next_worldstate

    def execute(self, userdata):
        if not self.action.check_freeform_context():
            print 'Action\'s freeform context isn\'t valid! Aborting wrapping state for %s', self.action
            return 'aborted'
        self.action.run(self._next_worldstate)
        return 'succeeded'


class SmachStateAction(Action):

    def __init__(self, state, preconditions, effects, **kwargs):
        Action.__init__(self, preconditions, effects, **kwargs)
        self.state = state

    def get_remapping(self):
        """Overload this to set a remapping.
        Actually planned for future use"""
        return {}

    def translate_worldstate_to_userdata(self, next_worldstate, userdata):
        """Overload to make worldstate data available to the state."""
        pass




class LookAroundAction(SmachStateAction):

    class IncEffect(VariableEffect):
        # TODO: simplify such var effects to a global ReachableVariableEffect
        def __init__(self, condition):
            VariableEffect.__init__(self, condition)
        def _is_reachable(self, value):
            return True


    def __init__(self):
        SmachStateAction.__init__(self, get_lookaround_smach(glimpse=True),
                                  [Precondition(Condition.get('arm_can_move'), True)],
                                  [LookAroundAction.IncEffect(Condition.get('awareness'))])

    def apply_adhoc_preconditions_for_vareffects(self, var_effects, worldstate, start_worldstate):
        effect = var_effects.pop()  # this action has one variable effect
        assert effect.__class__ == LookAroundAction.IncEffect
        # increase awareness by one
        precond_value = worldstate.get_condition_value(effect._condition) - 1
        Precondition(effect._condition, precond_value, None).apply(worldstate)




class FoldArmAction(SmachStateAction):

    def __init__(self):
        SmachStateAction.__init__(self, get_move_arm_to_joints_positions_state(ARM_FOLDED_POSE),
                                  [Precondition(Condition.get('arm_can_move'), True),
                                   # TODO: why is this anti-effect-precondition needed?
                                   Precondition(Condition.get('robot.arm_folded'), False)],
                                  [Effect(Condition.get('robot.arm_folded'), True)])


