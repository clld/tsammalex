from __future__ import unicode_literals
import sys
import json

from path import path
from clld.util import slug
from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common

import tsammalex
from tsammalex import models
from tsammalex.scripts import wiki


files_dir = path('/home/robert/venvs/clld/tsammalex/data/files')


def main(args):
    #wiki.get_categories(args)
    #return
    data = Data()

    dataset = common.Dataset(
        id=tsammalex.__name__,
        name="--TODO--",
        publisher_name ="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        license="http://creativecommons.org/licenses/by/3.0/",
        domain='tsammalex.clld.org')
    DBSession.add(dataset)

    #
    # TODO: add editors!
    #

    with open(args.data_file('species.json')) as fp:
        species = json.load(fp)

    for i, spec in enumerate(species.values()):
        s = data.add(
            models.Species, spec['name'],
            id=str(i),
            name=spec['name'],
            wikipedia_url=spec['wikipedia'].get('fullurl'),
            eol_id=spec['eol'].get('id'))

        for j, img in enumerate(spec['images']):
            if not img.get('thumbnail'):
                assert img.keys() == ['metadata']
                continue

            for n in ['thumbnail', 'small', 'large']:
                if n not in img or (n == 'small' and 'large' in img):
                    continue
                jsondata = img['metadata']
                jsondata.update(img[n])
                f = common.Parameter_files(
                    object=s,
                    id='%s-%s-%s.jpg' % (s.id, j, n),
                    name='%s %s' % (n, j),
                    jsondata=jsondata,
                    mime_type='image/jpeg')
                f.create(files_dir, wiki.get(args, img[n]['src'], html=False))

        for attr, model in [
            ('categories', models.Category),
            ('countries', models.Country),
            ('ecoregions', models.Ecoregion),
        ]:
            for name in spec[attr]:
                if name in data[model.mapper_name()]:
                    o = data[model.mapper_name()][name]
                else:
                    o = data.add(model, name, id=slug(name), name=name)
                o.species.append(s)

        for lang, words in spec['names'].items():
            refs = [w[1] for w in words if w[1] is not None]
            if lang in data['Language']:
                lang = data['Language'][lang]
            else:
                lang = data.add(common.Language, lang, id=slug(lang), name=lang)
            if len(refs) < 2:
                # we use one valueset for all words!
                vs = common.ValueSet(
                    id='%s-%s' % (s.id, lang.id),
                    parameter=s,
                    language=lang)
                if refs:
                    ref = spec['references'][refs[0]]
                    if isinstance(ref, list):
                        # TODO: handle urls properly!
                        ref = ref[0]
                    for k, ref_ in enumerate(wiki.split(ref)):
                        #
                        # TODO: handle page info (2002:123)
                        #
                        if ref_ in data['Source']:
                            source = data['Source'][ref_]
                        else:
                            source = data.add(common.Source, ref_, id='%s-%s-%s' % (s.id, lang.id, k), name=ref_)
                        DBSession.add(common.ValueSetReference(valueset=vs, source=source))
            for k, word in enumerate(words):
                word, ref = word
                id_ = '%s-%s-%s' % (s.id, lang.id, k)
                if len(refs) >= 2:
                    vs = common.ValueSet(
                        id=id_,
                        parameter=s,
                        language=lang)
                    # TODO: add refs here!
                DBSession.add(common.Value(valueset=vs, id=id_, name=word))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
