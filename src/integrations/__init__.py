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
    verify_outputs,
    write_script,
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

# NOTE: both ``freecad.verify_outputs`` and ``ngspice.verify_outputs`` exist
# with the same contract; the package re-exports the FreeCAD one. Import the
# ngspice variant from its module directly when needed.

__all__ = [
    "FREECAD_TOOLS",
    "FreeCADRun",
    "FreeCADUnavailable",
    "FreeCadError",
    "JUPYTER_TOOL",
    "JupyterUnavailable",
    "KICAD_TOOLS",
    "KiCadError",
    "KiCadRun",
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
    "cad_evidence",
    "execute_notebook",
    "export_gerbers",
    "freecad_available",
    "jupyter_available",
    "kicad_cli",
    "kicad_evidence",
    "ngspice_cli",
    "ngspice_evidence",
    "notebook_evidence",
    "parse_op_point",
    "run_drc",
    "run_erc",
    "run_macro",
    "run_simulation",
    "validate_notebook",
    "verify_artifacts",
    "verify_outputs",
    "write_netlist",
    "write_notebook",
    "write_script",
]