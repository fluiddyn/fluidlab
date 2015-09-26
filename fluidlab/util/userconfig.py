"""User configuration (:mod:`fluidlab.util.userconfig`)
====================================================

Execute some user configuration files if they exist and gather the
configuration values as module attributes.

"""

from fluiddyn.util.userconfig import load_user_conf_files

config = load_user_conf_files('fluidlab')
del load_user_conf_files

glob = globals()
for _k, _v in config.items():
    glob[_k] = _v
del glob
