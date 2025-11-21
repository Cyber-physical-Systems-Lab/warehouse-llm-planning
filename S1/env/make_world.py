import pybullet as p
import pybullet_data

RGB = {
    "shelf":  [0.85, 0.85, 0.85, 1],
    "table":  [0.7, 1.0, 0.7, 1],
    "redbin": [1.0, 0.6, 0.6, 1],
    "box":    [1.0, 0.4, 0.4, 1],
    "robot":  [1.0, 0.7, 0.2, 1],
}


def create_box(half_extents, pose, color):
    """Create static box-like object for world construction."""
    col = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_extents)
    vis = p.createVisualShape(p.GEOM_BOX, halfExtents=half_extents, rgbaColor=color)
    return p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=col,
        baseVisualShapeIndex=vis,
        basePosition=pose[:3],
        baseOrientation=pose[3:],
    )


def make_world(gui=False):
    """S1 visual world (Shelf → Worktable → RedBin)."""
    cid = p.connect(p.GUI if gui else p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.resetSimulation()
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")

    # --- Clean GUI ---
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_WIREFRAME, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)

    # --- Static structures ---
    create_box([0.4, 0.15, 0.3], [0.0, 0.6, 0.3, 0, 0, 0, 1], RGB["shelf"])    # Shelf
    create_box([0.4, 0.2, 0.25], [0.8, 0.0, 0.25, 0, 0, 0, 1], RGB["table"])    # Worktable
    create_box([0.2, 0.2, 0.15], [0.0, -0.7, 0.15, 0, 0, 0, 1], RGB["redbin"])  # RedBin

    # --- Slot positions (final unified naming) ---
    slots = {
        "Shelf.red.slot":     [0.0, 0.6, 0.55],
        "Worktable.slot":     [0.8, 0.0, 0.55],
        "RedBin.slot":        [0.0, -0.7, 0.35],
    }

    # --- Movable box (redbox) ---
    col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04])
    vis = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04], rgbaColor=RGB["box"])
    redbox = p.createMultiBody(
        baseMass=0.2,
        baseCollisionShapeIndex=col,
        baseVisualShapeIndex=vis,
        basePosition=slots["Shelf.red.slot"],
        baseOrientation=[0, 0, 0, 1],
    )

    # --- Robot ---
    robot_id = p.loadURDF("cube_small.urdf", [0.2, 0.6, 0.05], useFixedBase=False)
    p.changeVisualShape(robot_id, -1, rgbaColor=RGB["robot"])

    # --- World dict ---

    poses = {
        "Shelf.front.dock",
        "Worktable.dock",
        "RedBin.dock",
    }

    world = {
        "client": cid,
        "slots": slots,
        "objects": {"redbox": redbox},
        "robot": robot_id,
        "state": {"occupancy": {"Shelf.red.slot": "redbox"}},
        "reachability_map": {
            "Shelf.red.slot": "Shelf.front.dock",
            "Worktable.slot": "Worktable.dock",
            "RedBin.slot": "RedBin.dock",
        },
        "poses": poses,
    }
    return world


if __name__ == "__main__":
    make_world(gui=True)
    input("Press Enter to exit...")