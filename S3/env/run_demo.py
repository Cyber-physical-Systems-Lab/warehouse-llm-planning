import time
import pybullet as p
import pybullet_data
from make_world import make_world


def move_box_with_robot(box_id, robot_id, start, end, steps=150, delay=0.01, side_offset=0.12):
    """Move a box and its corresponding robot side by side (smooth animation)."""
    z_offset = 0.05
    for i in range(steps + 1):
        alpha = i / steps
        pos = [start[j] + alpha * (end[j] - start[j]) for j in range(3)]
        box_pos = [pos[0], pos[1], pos[2]]
        robot_pos = [pos[0] + side_offset, pos[1], pos[2] - z_offset]
        p.resetBasePositionAndOrientation(box_id, box_pos, [0, 0, 0, 1])
        p.resetBasePositionAndOrientation(robot_id, robot_pos, [0, 0, 0, 1])
        p.stepSimulation()
        time.sleep(delay)


def clean_visuals():
    """Hide GUI and overlays for clean visual presentation (manual camera control)."""
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_WIREFRAME, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)


if __name__ == "__main__":
    w = make_world(gui=True)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())

    # Clean the interface but leave camera free
    clean_visuals()

    print("Starting S3 visual demo...")

    redbox = w["objects"]["redbox"]
    bluebox = w["objects"]["bluebox"]
    robotA = w["robots"]["robotA"]
    robotB = w["robots"]["robotB"]
    slots = w["slots"]

    # --- Stage 1: Robot A handles red box (Shelf -> Inspection -> RedBin) ---
    print("Robot A moving red box...")
    move_box_with_robot(redbox, robotA, slots["Shelf.red.slot"], slots["Inspection.slot"])
    time.sleep(0.5)
    move_box_with_robot(redbox, robotA, slots["Inspection.slot"], slots["RedBin.slot"])

    # --- Stage 2: Robot B handles blue box (Shelf -> Inspection -> BlueBin) ---
    print("Robot B waiting for inspection to be free...")
    time.sleep(1.0)
    print("Robot B moving blue box...")
    move_box_with_robot(bluebox, robotB, slots["Shelf.blue.slot"], slots["Inspection.slot"])
    time.sleep(0.5)
    move_box_with_robot(bluebox, robotB, slots["Inspection.slot"], slots["BlueBin.slot"])

    print("S3 visual demonstration complete.")
    input("Press Enter to exit...")