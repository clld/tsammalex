from clld.web.assets import environment
from path import path

import tsammalex


environment.append_path(
    path(tsammalex.__file__).dirname().joinpath('static'), url='/tsammalex:static/')
environment.load_path = list(reversed(environment.load_path))
