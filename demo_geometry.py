from pathlib import Path
import trimesh


OUTPUT = Path("data/assembly")


def export_demo_assembly():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    housing = trimesh.creation.box(extents=[180, 120, 60])
    housing.apply_translation([0, 0, 0])
    housing.export(OUTPUT / "gearbox_housing.stl")

    cover = trimesh.creation.box(extents=[140, 90, 8])
    cover.apply_translation([0, 0, 34])
    cover.export(OUTPUT / "front_cover.stl")

    open_bolt = trimesh.creation.cylinder(radius=6, height=12)
    open_bolt.apply_translation([-45, 0, 44])
    open_bolt.export(OUTPUT / "bolt_open.stl")

    blocked_bolt = trimesh.creation.cylinder(radius=6, height=12)
    blocked_bolt.apply_translation([45, 0, 44])
    blocked_bolt.export(OUTPUT / "bolt_blocked.stl")

    blocking_rib = trimesh.creation.box(extents=[40, 50, 35])
    blocking_rib.apply_translation([45, 0, 54])
    blocking_rib.export(OUTPUT / "blocking_rib.stl")


if __name__ == "__main__":
    export_demo_assembly()