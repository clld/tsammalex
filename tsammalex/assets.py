from pathlib import Path

from clld.web.assets import environment

import tsammalex


environment.append_path(
    Path(tsammalex.__file__).parent.joinpath('static').as_posix(),
    url='/tsammalex:static/')
environment.load_path = list(reversed(environment.load_path))
