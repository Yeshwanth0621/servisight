from pathlib import Path

import numpy as np
import pandas as pd
import trimesh


ASSEMBLY_DIR = Path("data/assembly")
CLEARANCE_MM = 3.0


def load_obstacles():
    obstacle_names = [
        "gearbox_housing.stl",
        "front_cover.stl",
        "blocking_rib.stl",
    ]

    obstacles = {}

    for filename in obstacle_names:
        mesh = trimesh.load_mesh(ASSEMBLY_DIR / filename)
        obstacles[filename.replace(".stl", "")] = mesh

    return obstacles


def normalize(vector):
    vector = np.asarray(vector, dtype=float)
    magnitude = np.linalg.norm(vector)

    if magnitude == 0:
        raise ValueError("Approach vector cannot be zero.")

    return vector / magnitude


def create_tool_mesh(tool, target_position, approach_vector):
    position = np.asarray(target_position, dtype=float)
    direction = normalize(approach_vector)

    length = float(tool["length_mm"])
    width = float(tool["width_mm"]) + 2 * CLEARANCE_MM
    height = float(tool["height_mm"]) + 2 * CLEARANCE_MM

    if tool["shape"].lower() == "cylinder":
        radius = width / 2
        end_position = position - direction * length

        return trimesh.creation.cylinder(
            radius=radius,
            segment=np.array([position, end_position]),
            sections=32,
        )

    tool_mesh = trimesh.creation.box(
        extents=[width, height, length]
    )

    center_position = position - direction * (length / 2)
    tool_mesh.apply_translation(center_position)

    return tool_mesh


def compatible(tool, target):
    correct_size = float(tool["tip_size_mm"]) == float(target["fastener_size_mm"])
    enough_torque = float(tool["torque_capacity_nm"]) >= float(target["required_torque_nm"])

    return correct_size and enough_torque


def collision_result(tool_mesh, obstacles):
    manager = trimesh.collision.CollisionManager()

    for name, mesh in obstacles.items():
        manager.add_object(name, mesh)

    collides, blockers = manager.in_collision_single(
        tool_mesh,
        return_names=True,
    )

    return collides, sorted(blockers)


def analyze_target(target, tools, obstacles):
    results = []

    target_position = [
        target["x_mm"],
        target["y_mm"],
        target["z_mm"],
    ]

    approach_vector = [
        target["approach_x"],
        target["approach_y"],
        target["approach_z"],
    ]

    for _, tool in tools.iterrows():

        is_compatible = (
            float(tool["tip_size_mm"]) == float(target["fastener_size_mm"])
            and float(tool["torque_capacity_nm"]) >= float(target["required_torque_nm"])
        )

        if not is_compatible:
            results.append({
                "tool": tool["tool_name"],
                "status": "REJECTED",
                "reason": "Wrong tool size or insufficient torque capacity",
            })
            continue

        tool_mesh = create_tool_mesh(
            tool,
            target_position,
            approach_vector,
        )

        collides, blockers = collision_result(
            tool_mesh,
            obstacles,
        )

        if collides:
            results.append({
                "tool": tool["tool_name"],
                "status": "BLOCKED",
                "reason": f"Collides with: {', '.join(blockers)}",
            })
        else:
            results.append({
                "tool": tool["tool_name"],
                "status": "VALID",
                "reason": "Correct size, adequate torque, and collision-free access",
            })

    return results

def main():
    tools = pd.read_csv("data/tools.csv")
    targets = pd.read_csv("data/targets.csv")
    obstacles = load_obstacles()

    for _, target in targets.iterrows():
        print()
        print("=" * 70)
        print(f"Target: {target['target_name']}")
        print(f"Required tool size: {target['fastener_size_mm']} mm")
        print(f"Required torque: {target['required_torque_nm']} Nm")
        print("-" * 70)

        results = analyze_target(target, tools, obstacles)

        for result in results:
            print(f"[{result['status']:<8}] {result['tool']}")
            print(f"           {result['reason']}")


if __name__ == "__main__":
    main()