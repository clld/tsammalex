from functools import partial

from six.moves.urllib.request import urlretrieve
from purl import URL

from clld.scripts.util import create_downloads, parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Language

from tsammalex.adapters import Pdf


def cached_path(args, url, rel):
    if url.startswith('/'):
        return url
    url_ = URL(url)
    cached = args.data_file('edmond', url_.path_segments()[-1])
    if not cached.exists():
        fname, headers = urlretrieve(url, '%s' % cached)
    return str(cached)


def main(args):
    for lang in DBSession.query(Language):
        print(lang.name)
        Pdf(None, 'tsammalex').create(
            args.env['request'], filename='test.pdf', link_callback=partial(cached_path, args), lang=lang)


if __name__ == '__main__':
    main(parsed_args(bootstrap=True))
