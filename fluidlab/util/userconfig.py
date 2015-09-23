"""User configuration (:mod:`fluidlab.util.userconfig`)
====================================================

Execute some user configuration files if they exist and gather the
configuration values as module attributes.

"""

import os as _os
from runpy import run_path as _run_path

conf_vars = {}

home = _os.path.expanduser("~")

possible_conf_files = [_os.path.join(home, '.fluidlab', 'config.py')]

conf_files = []
for _path in possible_conf_files:
    if _os.path.isfile(_path):
        conf_files.append(_path)
        conf_vars = _run_path(_path, init_globals=conf_vars)

conf_vars = {k: v for k, v in conf_vars.items() if not k.startswith('_')}

for _k, _v in conf_vars.items():
    globals()[_k] = _v
