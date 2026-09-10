"""Application entry point."""

from .app import VibrationPlayerGUI


def main() -> int:
    app = VibrationPlayerGUI()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
