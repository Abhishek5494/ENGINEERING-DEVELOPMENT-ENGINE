"""Engineering-tool integrations (MASTER §17/§18, Phases 8–12).

Each integration detects its external tool via PEM, drives it through a
CLI/API when present, and records outputs as labelled evidence. When a
tool is absent the capability reports UNAVAILABLE and its integration
tests SKIP — a tool is never assumed available.
"""

from src.integrations.freecad import (
    FREECAD_TOOLS,
    FreeCADRun,
    FreeCADUnavailable,
    FreeCadError,
    build_box_macro,
    cad_evidence,
    freecad_available,
    run_macro,
    verify_outputs as verify_cad_outputs,
    write_script,
)
from src.integrations.blender import (
    BLENDER_TOOLS,
    BlenderError,
    BlenderRun,
    BlenderUnavailable,
    blender_cli,
    blender_evidence,
    run_background,
    verify_outputs as verify_blender_outputs,
    write_script as write_blender_script,
)
from src.integrations.gazebo import (
    GAZEBO_TOOLS,
    GazeboError,
    GazeboRun,
    GazeboUnavailable,
    gazebo_cli,
    gazebo_evidence,
    run_headless,
    write_world,
)
from src.integrations.jupyter import (
    JUPYTER_TOOL,
    JupyterUnavailable,
    NotebookError,
    NotebookRun,
    build_notebook,
    execute_notebook,
    jupyter_available,
    notebook_evidence,
    validate_notebook,
    write_notebook,
)
from src.integrations.kicad import (
    KICAD_TOOLS,
    KiCadError,
    KiCadRun,
    KiCadUnavailable,
    export_gerbers,
    kicad_cli,
    kicad_evidence,
    run_drc,
    run_erc,
    verify_artifacts,
)
from src.integrations.ngspice import (
    NGSPICE_TOOLS,
    NgspiceError,
    NgspiceRun,
    NgspiceUnavailable,
    ngspice_cli,
    ngspice_evidence,
    parse_op_point,
    run_simulation,
    write_netlist,
)

# NOTE: ``freecad``, ``gazebo``, ``blender`` and ``ngspice`` each define
# ``verify_outputs`` with the same contract, and ``freecad``/``blender``
# each define ``write_script``. The package re-exports disambiguated names
# (``verify_cad_outputs`` / ``verify_blender_outputs`` /
# ``write_blender_script``); import the others from their modules directly.

__all__ = [
    "BLENDER_TOOLS",
    "BlenderError",
    "BlenderRun",
    "BlenderUnavailable",
    "FREECAD_TOOLS",
    "FreeCADRun",
    "FreeCADUnavailable",
    "FreeCadError",
    "GAZEBO_TOOLS",
    "GazeboError",
    "GazeboRun",
    "GazeboUnavailable",
    "JUPYTER_TOOL",
    "JupyterUnavailable",
    "KICAD_TOOLS",
    "KiCadError",
    "KiCadRun",
    "KiCadUnavailable",
    "NGSPICE_TOOLS",
    "NgspiceError",
    "NgspiceRun",
    "NgspiceUnavailable",
    "NotebookError",
    "NotebookRun",
    "build_box_macro",
    "build_notebook",
    "blender_cli",
    "blender_evidence",
    "cad_evidence",
    "execute_notebook",
    "export_gerbers",
    "freecad_available",
    "gazebo_cli",
    "gazebo_evidence",
    "jupyter_available",
    "kicad_cli",
    "kicad_evidence",
    "ngspice_cli",
    "ngspice_evidence",
    "notebook_evidence",
    "parse_op_point",
    "run_background",
    "run_drc",
    "run_erc",
    "run_headless",
    "run_macro",
    "run_simulation",
    "validate_notebook",
    "verify_artifacts",
    "verify_blender_outputs",
    "verify_cad_outputs",
    "write_blender_script",
    "write_netlist",
    "write_notebook",
    "write_script",
    "write_world",
]