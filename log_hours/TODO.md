# TODO

- [x] Fix run with crontab inside docker container - Got error:
```python
Traceback (most recent call last):
  File "/app/src/loghours.py", line 7, in <module>
    from src.automated_work_logger import AutomatedWorkLogger
ModuleNotFoundError: No module named 'src'
```
**FIXED**: Changed imports from `from src.module` to `from module` since scripts are in the same directory. Updated:
  - ✅ loghours.py and automated_work_logger.py (relative imports)
  - ✅ Dockerfile health check
  - ✅ docker-entrypoint.sh test
  - ✅ GitHub Actions workflow (.github/workflows/log-hours.yml) import tests

- [ ] Send screenshot and logs to whatsapp via API
