# Release Checklist

1. Update `pyproject.toml` version.
2. Run tests:

   ```bash
   python -m pytest -q
   ```

3. Build distributions:

   ```bash
   python -m build
   ```

4. Inspect `dist/`.
5. Upload with Twine when ready:

   ```bash
   python -m twine upload dist/*
   ```

