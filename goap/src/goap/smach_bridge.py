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


from smach import State

from common import Condition, Precondition, Effect, VariableEffect, Action

from uashh_smach.manipulator.look_around import get_lookaround_smach
from uashh_smach.manipulator.move_arm import get_move_arm_to_joints_positions_state


ARM_FOLDED_POSE = [0, 0.52, 0.52, -1.57, 0]
ARM_FOLDED_POSE_NAMES = ['DH_1_2', 'DH_2_3', 'DH_4_4', 'DH_4_5', 'DH_5_6']
ARM_FOLDED_POSE_NAMED = dict(zip(ARM_FOLDED_POSE_NAMES, ARM_FOLDED_POSE))


class GOAPNodeWrapperState(State):
    """Used (by the runner) to add GOAP nodes (aka instances of GOAP actions)
    to a SMACH state machine"""
    def __init__(self, node):
        State.__init__(self, outcomes=['succeeded', 'aborted'])
        self.node = node

    def execute(self, userdata):
#        if not self.node.action.is_valid(current_worldstate): TODO: current worldstate not known
#            print "Action isn't valid to worldstate! Aborting executor"
#            print ' action: %r' % self.node.action
#            print ' worldstate:', self.node.worldstate
#            return 'aborted'
#        print "Action %s valid to worldstate" % self.node.action
        if not self.node.action.check_freeform_context():
            print "Action's freeform context isn't valid! Aborting wrapping state for %s", self.node.action
            return 'aborted'
        next_node = self.node.parent_node()
        self.node.action.run(next_node.worldstate)
        return 'succeeded'


class SMACHStateWrapperAction(Action):
    """A special Action to wrap a SMACH state.

    Subclass this class to make a SMACH state available to GOAP planning.
    """
    def __init__(self, state, preconditions, effects, **kwargs):
        Action.__init__(self, preconditions, effects, **kwargs)
        self.state = state

    def get_remapping(self):
        """Override this to set a remapping.
        Actually planned for future use"""
        return {}

    def translate_worldstate_to_userdata(self, next_worldstate, userdata):
        """Override to make worldstate data available to the state."""
        pass

    def translate_userdata_to_worldstate(self, userdata, next_worldstate):
        """Override to make the state's output available to the worldstate."""
        pass

    def run(self, next_worldstate):
        userdata = UserData()
        self.translate_worldstate_to_userdata(next_worldstate, userdata)
        self.state.execute(userdata)
        raise NotImplementedError, "write a test and remove this raise" # TODO: write test, remove raise




class LookAroundAction(SMACHStateWrapperAction):

    def __init__(self):
        SMACHStateWrapperAction.__init__(self, get_lookaround_smach(glimpse=True),
                                  [Precondition(Condition.get('arm_can_move'), True)],
                                  [VariableEffect(Condition.get('awareness'))])

    def apply_adhoc_preconditions_for_vareffects(self, var_effects, worldstate, start_worldstate):
        effect = var_effects.pop()  # this action has one variable effect
        assert effect is self._effects[0]
        # increase awareness by one
        precond_value = worldstate.get_condition_value(effect._condition) - 1
        Precondition(effect._condition, precond_value, None).apply(worldstate)




class FoldArmAction(SMACHStateWrapperAction):

    def __init__(self):
        SMACHStateWrapperAction.__init__(self, get_move_arm_to_joints_positions_state(ARM_FOLDED_POSE),
                                  [Precondition(Condition.get('arm_can_move'), True),
                                   # TODO: maybe remove necessary anti-effect-preconditions
                                   # the currently available alternative would be to use a
                                   # variable effect that can reach any value
                                   Precondition(Condition.get('robot.arm_folded'), False)],
                                  [Effect(Condition.get('robot.arm_folded'), True)])


