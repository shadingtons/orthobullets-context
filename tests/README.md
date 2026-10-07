# Isolated platform checks

These checks download the exact published beta.2 archive from AnkiWeb and fail if its hash or supported Anki version changes. They exercise actual Anki installation, update preservation, runtime import/menu registration, and literal deck selection using a synthetic temporary collection.

The separate session fixture tests the proposed persistent browser component on a local HTTP server, including process restart and profile isolation. This component is a personal-runtime patch under test, not a feature already included in the published beta.2 download. No real Orthobullets credentials, personal decks, clinical records or collection files are used or uploaded.

Passing these checks does not certify every clinical mapping or establish successful real-account login on each operating system. Results must be interpreted by test scope.
