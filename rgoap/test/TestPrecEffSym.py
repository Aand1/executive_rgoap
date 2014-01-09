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

"""
RGOAPTestPreconditionEffectSymmetry
"""


from rgoap import Condition, Precondition, Effect, Action, Goal
from rgoap import MemoryCondition
from rgoap import Runner



class SymmetricAction(Action):

    def __init__(self):
        Action.__init__(self,
                        [Precondition(Condition.get('robot.bumpered'), True)],
                        [Effect(Condition.get('robot.bumpered'), False)])

    def run(self, next_worldstate):
        print '%s: resetting bumper..' % self.__class__



if __name__ == "__main__":

    runner = Runner()

    Condition.add(MemoryCondition(runner.memory, 'robot.bumpered', True))

    runner.actions.add(SymmetricAction())


    Condition.initialize_worldstate(runner.worldstate)
    print 'worldstate now is: ', runner.worldstate


    goal = Goal([Precondition(Condition.get('robot.bumpered'), False)])

    start_node = runner.update_and_plan(goal, introspection=True)

    print 'start_node: ', start_node


    if start_node is None:
        print 'No plan found! Check your ROS graph!'
    else:
        runner.execute(start_node)
