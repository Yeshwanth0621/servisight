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

    for name in obstacle_names:
        mesh = trimesh.load_mesh(ASSEMBLY_DIR / name)
        obstacles[name.replace(".stl", "")] = mesh

    return obstacles


def create_socket_tool(tool_row, target_position, approach_vector):
    radius = tool_row["width_mm"] / 2 + CLEARANCE_MM
    length = tool_row["length_mm"]

    start = np.array(target_position, dtype=float)
    direction = np.array(approach_vector, dtype=float)
    direction = direction / np.linalg.norm(direction)

    end = start - direction * length

    tool_mesh = trimesh.creation.cylinder(
        radius=radius,
        segment=np.array([start, end]),
        sections=32,
    )

    return tool_mesh


def check_tool_collision(tool_mesh, obstacles):
    collision_manager = trimesh.collision.CollisionManager()

    for name, mesh in obstacles.items():
        collision_manager.add_object(name, mesh)

    is_collision, collided_names = collision_manager.in_collision_single(
        tool_mesh,
        return_names=True,
    )

    return is_collision, sorted(collided_names)


def main():
    tools = pd.read_csv("data/tools.csv")
    targets = pd.read_csv("data/targets.csv")
    obstacles = load_obstacles()

    socket = tools.loc[tools["tool_id"] == "T001"].iloc[0]

    for _, target in targets.iterrows():
        tool_mesh = create_socket_tool(
            tool_row=socket,
            target_position=[
                target["x_mm"],
                target["y_mm"],
                target["z_mm"],
            ],
            approach_vector=[
                target["approach_x"],
                target["approach_y"],
                target["approach_z"],
            ],
        )

        collided, blockers = check_tool_collision(tool_mesh, obstacles)

        result = "BLOCKED" if collided else "ACCESSIBLE"

        print(f"Target: {target['target_name']}")
        print(f"Tool: {socket['tool_name']}")
        print(f"Result: {result}")
        print(f"Expected: {target['expected_result']}")
        print(f"Blockers: {', '.join(blockers) if blockers else 'None'}")


if __name__ == "__main__":
    main()