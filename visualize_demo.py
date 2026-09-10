from pathlib import Path

import numpy as np
import pandas as pd
import pyvista as pv


ASSEMBLY_DIR = Path("data/assembly")

COLORS = {
    "housing": "#64748B",
    "cover": "#94A3B8",
    "open_bolt": "#22C55E",
    "blocked_bolt": "#EF4444",
    "blocking_rib": "#F97316",
    "tool": "#38BDF8",
}


def load_mesh(filename):
    return pv.read(ASSEMBLY_DIR / filename)


def create_tool_cylinder(target_position, approach_vector, radius_mm=11, length_mm=70):
    start = np.asarray(target_position, dtype=float)
    direction = np.asarray(approach_vector, dtype=float)
    direction = direction / np.linalg.norm(direction)

    center = start - direction * (length_mm / 2)

    return pv.Cylinder(
        center=center,
        direction=direction,
        radius=radius_mm,
        height=length_mm,
        resolution=48,
    )


def main():
    targets = pd.read_csv("data/targets.csv")

    open_target = targets.loc[targets["target_id"] == "B001"].iloc[0]
    blocked_target = targets.loc[targets["target_id"] == "B002"].iloc[0]

    tool = create_tool_cylinder(
        target_position=[
            blocked_target["x_mm"],
            blocked_target["y_mm"],
            blocked_target["z_mm"],
        ],
        approach_vector=[
            blocked_target["approach_x"],
            blocked_target["approach_y"],
            blocked_target["approach_z"],
        ],
    )

    plotter = pv.Plotter(window_size=[1400, 850])
    plotter.set_background("#0F172A")

    plotter.add_mesh(
        load_mesh("gearbox_housing.stl"),
        color=COLORS["housing"],
        opacity=0.30,
        show_edges=True,
        label="Gearbox Housing",
    )

    plotter.add_mesh(
        load_mesh("front_cover.stl"),
        color=COLORS["cover"],
        opacity=0.45,
        show_edges=True,
        label="Front Cover",
    )

    plotter.add_mesh(
        load_mesh("bolt_open.stl"),
        color=COLORS["open_bolt"],
        label="B001 — Accessible",
    )

    plotter.add_mesh(
        load_mesh("bolt_blocked.stl"),
        color=COLORS["blocked_bolt"],
        label="B002 — Blocked",
    )

    plotter.add_mesh(
        load_mesh("blocking_rib.stl"),
        color=COLORS["blocking_rib"],
        opacity=0.85,
        label="Blocking Rib",
    )

    plotter.add_mesh(
        tool,
        color=COLORS["tool"],
        opacity=0.45,
        show_edges=True,
        label="10 mm Socket Tool Envelope",
    )

    plotter.add_text(
        "ServiSight — Tool Access Analysis",
        position="upper_left",
        font_size=16,
        color="white",
    )

    plotter.add_text(
        "Green: accessible   Red: blocked   Orange: obstruction   Blue: tool envelope",
        position="lower_left",
        font_size=10,
        color="#CBD5E1",
    )

    plotter.add_legend(
        face="circle",
        size=(0.22, 0.22),
        bcolor="#1E293B",
    )

    plotter.add_axes(
        color="white",
        xlabel="X",
        ylabel="Y",
        zlabel="Z",
    )

    plotter.view_isometric()
    plotter.show()


if __name__ == "__main__":
    main()