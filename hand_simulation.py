import bpy
import mathutils
import numpy as np
from math import pi
import random  # Import the random module

# Define bone names
BONE_NAMES = (
    'Camera',  # roll
    'Camera',  # elevation
    'Camera',  # azimuth
    'wrist.R', # hori
    'wrist.R', # vert
    'finger1.R',
    'finger2-1.R',
    'finger3-1.R',
    'finger4-1.R',
    'finger5-1.R',
)

# Define min and max angles for the bones
BONE_MIN = np.array([-30, 0, 0, -10, -30, -5, -5, -5, -5, -5])
BONE_MAX = np.array([90, 360, 360, 10, 30, 40, 40, 40, 40, 40])
BONE_RAND_RANGE = BONE_MAX - BONE_MIN

def setup():
    '''Changes to the POSE mode.'''
    view_layer = bpy.context.view_layer
    ob = bpy.data.objects['Hand']
    ob.select_set(True)
    view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='POSE')

def random_angles():
    '''Returns random angles as a numpy array for relevant bones only.'''
    relevant_indices = list(range(3, 10))
    initial_randoms = np.random.random(len(relevant_indices))
    angles = initial_randoms * BONE_RAND_RANGE[3:10] + BONE_MIN[3:10]
    for i in range(6, 9):
        t = random.random()
        if t < 0.4:
            angles[i-3] = 0.0
        elif t < 0.6:
            angles[i-3] = BONE_MAX[i]
    if random.random() < 0.8:
        # Outer fingers are easier to be flexed.
        angles[7-3] = max(angles[6-3], angles[7-3])
        angles[8-3] = max(angles[7-3], angles[8-3])
    angles[9-3] = angles[8-3]  # ring and baby move together.
    return angles

def get_current_angles():
    '''Gets the current angles of the hand bones.'''
    ob = bpy.data.objects['Hand']
    current_angles = []
    for i in range(3, 10):
        bone = ob.pose.bones[BONE_NAMES[i]]
        if i == 4:  # vert
            current_angles.append(bone.rotation_quaternion.z * 180 / pi)
        else:
            current_angles.append(bone.rotation_quaternion.x * 180 / pi)
    return np.array(current_angles)

def apply_handpose(angles):
    '''Applies angles to the hand bones.'''
    ob = bpy.data.objects['Hand']
    for i in range(3, 10):
        bonename = BONE_NAMES[i]
        bone = ob.pose.bones[bonename]
        angle = angles[i-3]
        if i == 4:  # vert
            bone.rotation_quaternion.z = angle * pi / 180
        else:
            bone.rotation_quaternion.x = angle * pi / 180 

def interpolate_poses(initial_angles, final_angles, num_frames=250):
    '''Generates interpolated angles between the initial and final angles over the specified number of frames.'''
    return [initial_angles + (final_angles - initial_angles) * (frame / (num_frames - 1)) for frame in range(num_frames)]

def apply_keyframes(initial_angles, final_angles, num_frames=250):
    '''Applies keyframes to interpolate hand pose from initial to final angles over the specified number of frames.'''
    ob = bpy.data.objects['Hand']
    for frame in range(num_frames):
        bpy.context.scene.frame_set(frame)
        interpolated_angles = interpolate_poses(initial_angles, final_angles, num_frames)[frame]
        apply_handpose(interpolated_angles)
        for i in range(3, 10):
            bonename = BONE_NAMES[i]
            bone = ob.pose.bones[bonename]
            bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

def apply_random_hand_pose_with_keyframes():
    '''Sets up the hand object, generates random angles, and applies keyframes for interpolation.'''
    setup()
    initial_angles = get_current_angles()
    final_angles = random_angles()
    apply_keyframes(initial_angles, final_angles)

# Entry point for the Blender script
if __name__ == "__main__":
    apply_random_hand_pose_with_keyframes()
