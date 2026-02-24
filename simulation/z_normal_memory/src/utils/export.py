import stim
import cairosvg


def export_diagram(circuit: stim.Circuit, initial_basis: str):
    diagram = circuit.without_noise().diagram(
        "detslice-with-ops-svg",
        tick=range(0, 1000),
        filter_coords=["L0"],
    )
    with open(
        f"simulation/z_normal_memory/figs/circuit_detslice-with-ops_{initial_basis}.svg",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(str(diagram))


def export_diagram_full(circuit: stim.Circuit, initial_basis: str):
    diagram = circuit.without_noise().diagram(
        "detslice-with-ops-svg",
        tick=range(0, 1000),
        filter_coords=[
            # "L0",
            # "D1271",
            # "D1274",
            # "D1277",
            # "D1281",
            # "D1285",
        ],
    )
    with open(
        f"simulation/z_normal_memory/figs/circuit_detslice-with-ops_full_{initial_basis}.svg",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(str(diagram))

    # diagram1 = circuit.without_noise().diagram(
    #     "detslice-with-ops-svg",
    #     tick=range(61, 62),
    # )
    # with open("figs/circuit_detslice-with-ops1.svg", "w", encoding="utf-8") as f:
    #     f.write(str(diagram1))

    # # SVGからPDFに変換
    # cairosvg.svg2pdf(
    #     url="figs/circuit_detslice-with-ops.svg",
    #     write_to="figs/circuit_detslice-with-ops.pdf",
    # )

    # timeline = circuit.diagram('timeline-svg')
    # with open("figs/circuit_timeline.svg", "w", encoding="utf-8") as f:
    #     f.write(str(timeline))
    # cairosvg.svg2pdf(url="figs/circuit_timeline.svg", write_to="figs/circuit_timeline.pdf")
