from itertools import chain

from six import BytesIO
from docx import Document
from docx.shared import Inches

from clld.web.adapters.geojson import (
    GeoJsonParameterMultipleValueSets, GeoJson, GeoJsonLanguages,
)
from clld.web.adapters.base import Representation
from clld.interfaces import IParameter, ILanguage, IIndex

from tsammalex.interfaces import IEcoregion


class GeoJsonEcoregions(GeoJson):
    def featurecollection_properties(self, ctx, req):
        return {'name': "WWF's Terrestrial Ecoregions of the Afrotropics"}

    def get_features(self, ctx, req):
        for ecoregion in ctx.get_query():
            for polygon in ecoregion.jsondatadict['polygons']:
                yield {
                    'type': 'Feature',
                    'properties': {
                        'id': ecoregion.id,
                        'label': '%s %s' % (ecoregion.id, ecoregion.name),
                        'color': ecoregion.biome.description,
                        'language': {'id': ecoregion.id},
                        'latlng': [ecoregion.latitude, ecoregion.longitude],
                    },
                    'geometry': polygon,
                }


class GeoJsonSpecies(GeoJsonParameterMultipleValueSets):
    def feature_properties(self, ctx, req, p):
        return {
            'label': ', '.join(v.name for v in chain(*[vs.values for vs in p[1]]))}


class GeoJsonLanguoids(GeoJsonLanguages):
    def feature_properties(self, ctx, req, feature):
        return {'lineage': feature.lineage}


class Docx(Representation):
    mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    extension = 'docx'

    def write(self, ctx, req, doc):
        raise NotImplemented  # pragma: no cover

    def render(self, ctx, req):
        document = Document()
        self.write(ctx, req, document)
        #
        # TODO: add tsammalex license information!
        #
        d = BytesIO()
        document.save(d)
        d.seek(0)
        return d.read()


class LanguageDocx(Docx):
    def write(self, ctx, req, document):
        document.add_heading(ctx.name, 0)
        table = document.add_table(rows=len(ctx.valuesets) + 1, cols=2)
        table.cell(0, 0).text = 'Species'
        table.cell(0, 1).text = 'Name'

        for i, vs in enumerate(ctx.valuesets):
            table.cell(i + 1, 0).text = vs.parameter.name
            table.cell(i + 1, 1).text = ', '.join(v.name for v in vs.values)


class SpeciesDocx(Docx):
    def write(self, ctx, req, document):
        document.add_heading(ctx.name, 0)
        document.add_heading('Names', 1)
        table = document.add_table(rows=len(ctx.valuesets), cols=2)

        for i, vs in enumerate(ctx.valuesets):
            table.cell(i, 0).text = vs.language.name
            table.cell(i, 1).text = ', '.join(v.name for v in vs.values)

        document.add_heading('Photos', 1)
        for f in ctx._files:
            p = req.registry.settings['clld.files'].joinpath(f.relpath)
            document.add_picture(p, width=Inches(3.5))

            table = document.add_table(rows=0, cols=2)
            for attr in 'date place author permission comments'.split():
                if f.jsondata.get(attr):
                    cells = table.add_row().cells
                    cells[0].text = attr.capitalize()
                    value = f.jsondata[attr]
                    if attr == 'permission':
                        if value.get('license'):
                            value = value['license'][1]
                    cells[1].text = '%s' % value

            # p = document.add_paragraph('A plain paragraph having some ')
            # p.add_run('bold').bold = True
            # p.add_run(' and some ')
            # p.add_run('italic.').italic = True
            #
            # document.add_heading('Heading, level 1', level=1)
            # document.add_paragraph('Intense quote', style='IntenseQuote')
            #
            # document.add_paragraph(
            #     'first item in unordered list', style='ListBullet'
            # )
            # document.add_paragraph(
            #     'first item in ordered list', style='ListNumber'
            # )
            #
            # #document.add_picture('monty-truth.png', width=Inches(1.25))
            #
            # table = document.add_table(rows=1, cols=3)
            # hdr_cells = table.rows[0].cells
            # hdr_cells[0].text = 'Qty'
            # hdr_cells[1].text = 'Id'
            # hdr_cells[2].text = 'Desc'
            # #for item in recordset:
            # #    row_cells = table.add_row().cells
            # #    row_cells[0].text = str(item.qty)
            # #    row_cells[1].text = str(item.id)
            # #    row_cells[2].text = item.desc
            #
            # document.add_page_break()


def includeme(config):
    config.register_adapter(LanguageDocx, ILanguage)
    config.register_adapter(SpeciesDocx, IParameter)
    config.register_adapter(GeoJsonEcoregions, IEcoregion, IIndex)
    config.register_adapter(GeoJsonSpecies, IParameter)
    config.register_adapter(GeoJsonLanguoids, ILanguage, IIndex)
