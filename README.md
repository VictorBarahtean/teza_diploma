##[Requirements]
After install requirements, need to modify [venv]\lib\site-packages\channels\auth.py
```
$Line 15: comment "#"
$Line 16: add "LANGUAGE_SESSION_KEY = '_language'"
```