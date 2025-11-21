import pybullet as p
import pybullet_data

RGB = {
    "soft_gray": [0.85, 0.85, 0.85, 1],
    "mint": [0.7, 1.0, 0.7, 1],
    "salmon": [1.0, 0.6, 0.6, 1],
    "light_blue": [0.6, 0.7, 1.0, 1],
    "red": [1, 0.4, 0.4, 1],
    "blue": [0.4, 0.6, 1, 1],
}


def create_box(half_extents, pose, color):
    """Create static world geometry."""
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
    """构建 S4 仿真世界：Shelf + Inspection + RedBin + BlueBin + 四机器人"""
    cid = p.connect(p.GUI if gui else p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.resetSimulation()
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")

    # --- Clean visual layout ---
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_WIREFRAME, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)

    # --- Static structures ---
    create_box([0.4, 0.15, 0.3], [0.0, 0.6, 0.3, 0, 0, 0, 1], RGB["soft_gray"])    # Shelf
    create_box([0.3, 0.2, 0.2], [0.3, -0.2, 0.2, 0, 0, 0, 1], RGB["mint"])        # Inspection
    create_box([0.2, 0.2, 0.15], [0.0, -0.7, 0.15, 0, 0, 0, 1], RGB["salmon"])    # RedBin
    create_box([0.2, 0.2, 0.15], [0.6, -0.7, 0.15, 0, 0, 0, 1], RGB["light_blue"])  # BlueBin

    # --- Slot positions (最终命名) ---
    slots = {
        "Shelf.red.slot": [0.0, 0.6, 0.55],
        "Shelf.blue.slot": [0.0, 0.6, 0.35],
        "Inspection.slot": [0.3, -0.2, 0.45],
        "RedBin.slot": [0.0, -0.7, 0.35],
        "BlueBin.slot": [0.6, -0.7, 0.35],
    }

    # --- Symbolic poses (for base.goto / is_pose) ---
    poses = {
        "Shelf.front.dock",
        "Inspection.dock",
        "RedBin.dock",
        "BlueBin.dock",
    }

    # --- Boxes ---
    col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04])
    vis_r = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04], rgbaColor=RGB["red"])
    vis_b = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.04], rgbaColor=RGB["blue"])
    redbox = p.createMultiBody(0.2, col, vis_r, basePosition=slots["Shelf.red.slot"])
    bluebox = p.createMultiBody(0.2, col, vis_b, basePosition=slots["Shelf.blue.slot"])

    # --- World structure ---
    world = {
        "client": cid,
        "slots": slots,
        "poses": poses,
        "objects": {"redbox": redbox, "bluebox": bluebox},
        "robots": {
            "robotA": {"holding": None, "dock": "Shelf.dock"},
            "robotB": {"holding": None, "dock": "Shelf.dock"},
            "robotC": {"holding": None, "dock": "RedBin.dock"},
            "robotD": {"holding": None, "dock": "BlueBin.dock"},
        },
        "state": {"occupancy": {k: None for k in slots.keys()}},
        "reachability_map": {    
            "Shelf.red.slot": "Shelf.front.dock",
            "Shelf.blue.slot": "Shelf.front.dock",
            "RedBin.slot": "RedBin.dock",
            "BlueBin.slot": "BlueBin.dock",
            "Inspection.slot": "Inspection.dock"
        },
    }

    # --- Initial occupancy ---
    world["state"]["occupancy"]["Shelf.red.slot"] = "redbox"
    world["state"]["occupancy"]["Shelf.blue.slot"] = "bluebox"

    return world


if __name__ == "__main__":
    make_world(gui=True)
    input("Press Enter to exit...")