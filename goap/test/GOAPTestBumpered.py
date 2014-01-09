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


import unittest

import tf

from std_msgs.msg import Bool
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry
from metralabs_msgs.msg import ScitosG5Bumper

from goap.goap import *
from goap.inheriting import *
from goap.common_ros import *
from goap.planning import Planner, PlanExecutor


class Test(unittest.TestCase):

    def test(self):
        pass



def calc_Pose(x, y, yaw):
    quat = tf.transformations.quaternion_from_euler(0, 0, yaw)
    orientation = Quaternion(*quat)
    position = Point(x, y, 0)
    return Pose(orientation, position)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()


    rospy.init_node('goap_bumper_test')

    memory = Memory()

    Condition.add('robot.pose', ROSTopicCondition(
                    'robot.pose', '/odom', Odometry, '/pose/pose'))
    Condition.add('robot.bumpered', ROSTopicCondition(
                    'robot.bumpered', '/bumper_state', ScitosG5Bumper, '/bumper_pressed'))
    Condition.add('memory.reminded_myself', MemoryCondition(memory, 'reminded_myself'))

    worldstate = WorldState()

    print 'Waiting to let conditions represent reality...'
    rospy.sleep(2)
    Condition.initialize_worldstate(worldstate)

    actionbag = ActionBag()
    actionbag.add(ResetBumperAction())
    actionbag.add(MoveBaseAction())


    goal = Goal([Precondition(Condition.get('robot.pose'), calc_Pose(3, 2, 1))])

    planner = Planner(actionbag, worldstate, goal)

    start_node = planner.plan()

    print 'start_node: ', start_node

    PlanExecutor().execute(start_node)


    ## init / spin to let conditions know reality




