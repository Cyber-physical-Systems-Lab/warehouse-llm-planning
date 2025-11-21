import time
import pybullet as p
import pybullet_data
from make_world import make_world

def move_box_with_side_robot(box_id, robot_id, start, end, steps=150, delay=0.01, side_offset=0.15):
    """Move box with robot following from the side (visually clear)."""
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
    print("World loaded. Adding side-follow robots...")

    robot_colors = {
        "robotA": [1, 0.7, 0.2, 1],
        "robotC": [1, 0.4, 0.0, 1],
        "robotB": [0.5, 1.0, 0.5, 1],
        "robotD": [0.2, 0.7, 0.2, 1],
    }

    robot_ids = {}
    for r, c in robot_colors.items():
        robot_ids[r] = p.loadURDF("cube_small.urdf", [0, 0, 0.05], useFixedBase=False)
        p.changeVisualShape(robot_ids[r], -1, rgbaColor=c)

    # Unified names
    redbox = w["objects"]["redbox"]
    bluebox = w["objects"]["bluebox"]
    slots = w["slots"]

    print("Running S4 visual demo (side follow)...")

    # Red chain
    move_box_with_side_robot(redbox, robot_ids["robotA"], slots["Shelf.red.slot"], slots["Inspection.slot"], side_offset=0.15)
    time.sleep(0.5)
    move_box_with_side_robot(redbox, robot_ids["robotC"], slots["Inspection.slot"], slots["RedBin.slot"], side_offset=0.15)

    # Blue chain
    move_box_with_side_robot(bluebox, robot_ids["robotB"], slots["Shelf.blue.slot"], slots["Inspection.slot"], side_offset=-0.15)
    time.sleep(0.5)
    move_box_with_side_robot(bluebox, robot_ids["robotD"], slots["Inspection.slot"], slots["BlueBin.slot"], side_offset=-0.15)

    print("All relay tasks complete.")
    input("Press Enter to exit...")