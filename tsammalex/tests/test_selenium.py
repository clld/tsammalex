from clld.tests.util import TestWithSelenium

import tsammalex


class Tests(TestWithSelenium):
    app = tsammalex.main({}, **{'sqlalchemy.url': 'postgres://robert@/tsammalex'})
