import time
import pybullet as p
import pybullet_data
from make_world import make_world


def move_box_with_robot(box_id, robot_id, start, end, steps=150, delay=0.01, side_offset=0.12):
    """S1可视化展示：机器人在箱子侧面伴随移动"""
    z_offset = 0.05
    for i in range(steps + 1):
        alpha = i / steps
        pos = [start[j] + alpha * (end[j] - start[j]) for j in range(3)]
        box_pos = [pos[0], pos[1], pos[2]]
        robot_pos = [pos[0] - side_offset, pos[1], pos[2] - z_offset]
        p.resetBasePositionAndOrientation(box_id, box_pos, [0, 0, 0, 1])
        p.resetBasePositionAndOrientation(robot_id, robot_pos, [0, 0, 0, 1])
        p.stepSimulation()
        time.sleep(delay)


if __name__ == "__main__":
    w = make_world(gui=True)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    print("Starting S1 visual demo...")

    redbox = w["objects"]["redbox"]
    robot_id = w["robot"]
    slots = w["slots"]

    move_box_with_robot(redbox, robot_id, slots["Shelf.red.slot"], slots["Worktable.slot"])
    time.sleep(0.5)
    move_box_with_robot(redbox, robot_id, slots["Worktable.slot"], slots["RedBin.slot"])

    print("S1 visual demonstration complete.")
    input("Press Enter to exit...")