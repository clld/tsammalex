from __future__ import unicode_literals
import sys
import json
import re
from collections import defaultdict

from path import path
from clld.util import slug
from clld.scripts.util import initializedb, Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common

import tsammalex
from tsammalex import models
from tsammalex.scripts import wiki
from tsammalex.scripts.refs import get_refs
from tsammalex.scripts.word_data import parsed_word


files_dir = path('/home/robert/venvs/clld/tsammalex/data/files')
year_pages = re.compile('\([0-9]{4}:(?P<pages>[0-9]+)\)')

#
# TODO: fix plantzafrica links! they only go to the frameset!
#


def main(args):
    wiki.get_categories(args)
    #return
    data = Data()

    refs = wiki.get_refs(args)
    for rec in refs.records:
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

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

    genus_names = defaultdict(list)

    for i, spec in enumerate(species.values()):
        if spec['genus']:
            gid = 'g:' + spec['genus']
            if gid not in data['Species']:
                g = data.add(
                    models.Species, gid,
                    id='g' + str(i),
                    name=spec['genus'],
                    is_genus=True,
                    family=spec['family'])
                DBSession.flush()
            else:
                g = data['Species'][gid]
        else:
            g = None

        s = data.add(
            models.Species, spec['name'],
            id=str(i),
            genus_pk=g.pk if g else None,
            name=spec['name'],
            description=spec['description'],
            family=spec['family'],
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
                    ref = list(get_refs(spec['references'][refs[0]]))
                    for k, ref_ in enumerate(ref):
                        if isinstance(ref_, basestring):
                            vs.source = ref_
                        else:
                            ref_, pages = ref_
                            source = data['Source'][ref_]
                            DBSession.add(common.ValueSetReference(
                                valueset=vs, source=source, description=pages))
            for k, word in enumerate(words):
                word, ref = word
                genus = None
                # TODO: add words for genera!
                if ':' in word:
                    genus, word = [t.strip() for t in word.split(':', 1)]

                id_ = '%s-%s-%s' % (s.id, lang.id, k)
                if len(refs) >= 2:
                    vs = common.ValueSet(
                        id=id_,
                        parameter=s,
                        language=lang)
                if genus:
                    if not g:
                        print 'no english genus name:', s.name, s.description
                    else:
                        if genus not in genus_names['%s-%s' % (lang.id, g.id)]:
                            gvs = common.ValueSet(
                                id='g-' + id_,
                                parameter=g,
                                language=lang)
                            DBSession.add(common.Value(valueset=gvs, id='g-' + id_, name=genus))
                            genus_names['%s-%s' % (lang.id, g.id)].append(genus)
                    # TODO: add refs here!
                word, desc, classes = parsed_word(word)
                DBSession.add(common.Value(valueset=vs, id=id_, name=word, description=desc, jsondata=classes))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
