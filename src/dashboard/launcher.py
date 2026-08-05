import subprocess
import sys
from pathlib import Path

from log import log_progress


def launch_dashboard(project_root: Path, log_file: Path) -> None:
    """Start the Streamlit dashboard as a subprocess.

    Keeps the same behavior as before but extracted to a dedicated module
    to follow separation-of-concerns and improve testability.
    """
    app_path = project_root / "src" / "dashboard" / "app.py"
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)],
            check=True,
        )
    except FileNotFoundError:
        log_progress(
            "Streamlit no esta instalado. Instale streamlit y vuelva a ejecutarlo.",
            log_file,
        )
    except subprocess.CalledProcessError:
        log_progress("No se pudo iniciar el dashboard Streamlit.", log_file)
