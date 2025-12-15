# Usage Guide

## CLI Options

The `ex.py` entry point supports several flags:

-   `--config PATH`: Load a specific .yaml or .json configuration file.
    ```bash
    python ex.py --config configs/lava_custom.yaml
    ```
-   `--resume`: Resume from the last saved session (`.last_session.json`).
    ```bash
    python ex.py --resume
    ```
-   `--reset`: Ignore last session and load built-in defaults.
    ```bash
    python ex.py --reset
    ```
-   `--headless`: Run in headless mode (no UI) for testing.
    ```bash
    python ex.py --headless
    ```

## Configuration

You can create custom configuration files. See `mazespace/config/defaults.yaml` for the reference schema.

### Example: Changing Agent Color
```yaml
agents:
  - key: "my_custom_agent"
    name: "Golden Bot"
    color: [1.0, 0.8, 0.0]
    shape: "sphere"
    scale: 2.0
```

## Menu Navigation

-   **Arrow Keys**: Navigate options.
-   **Enter**: Select option.
-   **Escape**: Go Back to previous menu.
-   **Type "return"**: Go Back.
-   **Type "exit"**: Exit the application.
