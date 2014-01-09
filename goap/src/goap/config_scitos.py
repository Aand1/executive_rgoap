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


from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from metralabs_msgs.msg import ScitosG5Bumper


from common_ros import MoveBaseAction, ResetBumperAction, ROSTopicCondition
from common_ros import LocalAwareGoal
from inheriting import MemoryCondition
from smach_bridge import LookAroundAction, FoldArmAction, MoveArmFloorAction




ARM_NAMES = ['DH_1_2', 'DH_2_3', 'DH_4_4', 'DH_4_5', 'DH_5_6']

ARM_POSE_FOLDED = [0, 0.52, 0.52, -1.57, 0]
ARM_POSE_FOLDED_NAMED = dict(zip(ARM_NAMES, ARM_POSE_FOLDED))

ARM_POSE_FLOOR = [0, 0.96, 0.96, -2.0, -1.57]
ARM_POSE_FLOOR_NAMED = dict(zip(ARM_NAMES, ARM_POSE_FLOOR))





def check_joint_msg_matches_pose(msg, pose_dict):
    return all([abs(pose_dict[name] - position) < 0.01
                for (name, position)
                in zip(msg.name, msg.position)
                if name in pose_dict]
               )


def get_all_conditions(memory):
    return [
        # memory
        MemoryCondition(memory, 'arm_can_move', True),
        MemoryCondition(memory, 'awareness', 0),
        # ROS
        ROSTopicCondition('robot.pose', '/odom', Odometry, '/pose/pose'),
        ROSTopicCondition('robot.bumpered', '/bumper', ScitosG5Bumper, '/motor_stop'),
        ROSTopicCondition('robot.arm_folded', '/joint_states', JointState,
                          msgeval=lambda msg: check_joint_msg_matches_pose(msg, ARM_POSE_FOLDED_NAMED)),
        ROSTopicCondition('robot.arm_pose_floor', '/joint_states', JointState,
                          msgeval=lambda msg: check_joint_msg_matches_pose(msg, ARM_POSE_FLOOR_NAMED))
        ]


def get_all_actions(memory):
    return [
        # memory
        # ROS - pure actions
        ResetBumperAction(),
        # ROS - wrapped SMACH states
        MoveBaseAction(),
        LookAroundAction(),
        FoldArmAction(),
        MoveArmFloorAction()
        ]



def get_all_goals(memory):
    return [
        # memory
        # ROS
#        MoveAroundGoal(),
        LocalAwareGoal()
        ]

