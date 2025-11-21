import pybullet as p
import pybullet_data

RGB = {
    "shelf": [0.85, 0.85, 0.85, 1],    # light gray
    "redbin": [1.0, 0.6, 0.6, 1],
    "bluebin": [0.6, 0.7, 1.0, 1],
    "redbox": [1.0, 0.4, 0.4, 1],
    "bluebox": [0.4, 0.6, 1.0, 1],
    "robotA": [1.0, 0.7, 0.2, 1],
    "robotB": [0.4, 1.0, 0.6, 1],
}


def create_box(half_extents, pose, color):
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
    """S2 visual world — same scale and color style as S3/S4."""
    cid = p.connect(p.GUI if gui else p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.resetSimulation()
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")

    # --- Clean visuals (disable PyBullet overlays) ---
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_WIREFRAME, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)

    # --- Static objects (aligned to S3 layout, no inspection area in S2) ---
    create_box([0.4, 0.15, 0.3], [0.0, 0.6, 0.3, 0, 0, 0, 1], RGB["shelf"])
    create_box([0.2, 0.2, 0.15], [0.0, -0.7, 0.15, 0, 0, 0, 1], RGB["redbin"])
    create_box([0.2, 0.2, 0.15], [0.6, -0.7, 0.15, 0, 0, 0, 1], RGB["bluebin"])

    # --- Slots (simpler: no inspection slot in S2) ---
    slots = {
        "Shelf.red.slot": [0.0, 0.6, 0.55],
        "Shelf.blue.slot": [-0.2, 0.6, 0.55],
        "RedBin.slot": [0.0, -0.7, 0.35],
        "BlueBin.slot": [0.6, -0.7, 0.35],
    }

    # --- Boxes (same size as S3/S4) ---
    col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04])
    vis_red = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04], rgbaColor=RGB["redbox"])
    vis_blue = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04], rgbaColor=RGB["bluebox"])
    redbox = p.createMultiBody(0.2, col, vis_red, basePosition=slots["Shelf.red.slot"])
    bluebox = p.createMultiBody(0.2, col, vis_blue, basePosition=slots["Shelf.blue.slot"])

    # --- Robots (same position + color scheme as S3) ---
    robotA = p.loadURDF("cube_small.urdf", [0.15, 0.6, 0.05], useFixedBase=False)
    robotB = p.loadURDF("cube_small.urdf", [-0.05, 0.6, 0.05], useFixedBase=False)
    p.changeVisualShape(robotA, -1, rgbaColor=RGB["robotA"])
    p.changeVisualShape(robotB, -1, rgbaColor=RGB["robotB"])

    # ========= symbolic occupancy 状态 =========
    occupancy = {
        "Shelf.red.slot": "redbox",
        "Shelf.blue.slot": "bluebox",
        "RedBin.slot": None,
        "BlueBin.slot": None,
    }

    # ========= poses，用于 base.goto / is_pose =========
    poses = {
        "Shelf.front.dock",
        "RedBin.dock",
        "BlueBin.dock",
    }
    # ===================================================

    # --- Return world dictionary ---
    world = {
        "client": cid,
        "slots": slots,
        "objects": {"redbox": redbox, "bluebox": bluebox},
        "robots": {"robotA": robotA, "robotB": robotB},
        # Add reachability_map mapping for validator compatibility
        "reachability_map": {
            "Shelf.red.slot": "Shelf.front.dock",
            "Shelf.blue.slot": "Shelf.front.dock",
            "RedBin.slot": "RedBin.dock",
            "BlueBin.slot": "BlueBin.dock",
        },
        "state": {"occupancy": occupancy},  
        "poses": poses,                    
    }
    return world


if __name__ == "__main__":
    make_world(gui=True)
    input("Press Enter to exit...")