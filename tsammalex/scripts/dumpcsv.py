from json import dumps

from clld.scripts.util import parsed_args
from clld.lib.dsv import UnicodeCsvWriter
from clld.db.meta import DBSession
from clld.db.models.common import Parameter_files

from tsammalex.models import Languoid, Word, Species, Variety, Country, Ecoregion, Category, Bibrec, TsammalexEditor


def main(args):
    for model in [
        TsammalexEditor,
        ('images', Parameter_files),
        Country,
        Ecoregion,
        Category,
        Variety,
        Languoid,
        Species,
        Word,
        Bibrec,
    ]:
        if isinstance(model, tuple):
            name, model = model
        else:
            name = model.__csv_name__
        with open(args.data_file('dump', name + '.csv'), 'w') as fp:
            writer = UnicodeCsvWriter(fp)

            if name == 'images':
                cols = ['id', 'species_id', 'name', 'mime_type', 'src',
                        'width', 'height', 'author', 'date', 'place', 'comments', 'keywords', 'permission']
                writer.writerow(cols)
                for obj in DBSession.query(Parameter_files).order_by(Parameter_files.pk):
                    writer.writerow(
                        [obj.id, obj.object.id, obj.name, obj.mime_type, 'https://lingweb.eva.mpg.de' + obj.jsondatadict['src']]
                        + [obj.jsondatadict.get(c, '') for c in cols[5:-1]]
                        + [dumps(obj.jsondatadict.get('permission', ''))])
            else:
                for i, obj in enumerate(model.csv_query(DBSession)):
                    if i == 0:
                        cols = obj.csv_head()
                        writer.writerow(cols)
                    writer.writerow(obj.to_csv(ctx=None, req=None, cols=cols))


if __name__ == '__main__':
    main(parsed_args())
