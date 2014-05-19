from clld.scripts.util import parsed_args
from clld.lib.dsv import UnicodeCsvWriter
from clld.db.meta import DBSession
from clld.db.models.common import Parameter_files

from tsammalex.models import Languoid, Word, Species, Variety, Country, Ecoregion, Category, Bibrec, TsammalexEditor


def main(args):
    for name, model in [
        ('editors', TsammalexEditor),
        ('images', Parameter_files),
        ('countries', Country),
        ('ecoregions', Ecoregion),
        ('categories', Category),
        ('varieties', Variety),
        ('languages', Languoid),
        ('species', Species),
        ('words', Word),
        ('sources', Bibrec),
    ]:
        with open(args.data_file('dump', name + '.csv'), 'w') as fp:
            writer = UnicodeCsvWriter(fp)
            if name == 'images':
                cols = ['id', 'species_id', 'name', 'mime_type', 'src',
                        'width', 'height', 'author', 'date', 'place', 'comments', 'keywords', 'permission']
                writer.writerow(cols)
                for obj in DBSession.query(Parameter_files).order_by(Parameter_files.object_pk):
                    writer.writerow(
                        [obj.id, obj.object.id, obj.name, obj.mime_type, 'https://lingweb.eva.mpg.de' + obj.jsondatadict['src']]
                        + [obj.jsondatadict.get(c, '') for c in cols[5:]])
            else:
                writer.writerow(model.__csv_head__)
                for obj in model.csv_query(DBSession):
                    writer.writerow(obj.to_csv())


if __name__ == '__main__':
    main(parsed_args())
