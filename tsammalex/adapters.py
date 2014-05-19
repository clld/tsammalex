from cStringIO import StringIO
from itertools import chain, groupby

from docx import Document
from docx.shared import Inches

from sqlalchemy.orm import joinedload
from clld.db.meta import DBSession
from clld.db.models.common import Language, ValueSet
from clld.web.adapters.geojson import GeoJsonParameter
from clld.web.adapters.base import Representation
from clld.interfaces import IParameter, ILanguage


class GeoJsonSpecies(GeoJsonParameter):
    def feature_iterator(self, ctx, req):
        return groupby(
            DBSession.query(ValueSet)
            .filter(ValueSet.parameter_pk == ctx.pk)
            .order_by(ValueSet.language_pk)
            .options(joinedload(ValueSet.language)),
            lambda vs: vs.language)

    def get_language(self, ctx, req, p):
        return p[0]

    def feature_properties(self, ctx, req, p):
        return {
            'label': ', '.join(v.name for v in chain(*[vs.values for vs in p[1]]))}


class Docx(Representation):
    mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    extension = 'docx'

    def write(self, ctx, req, doc):
        return doc

    def render(self, ctx, req):
        document = Document()
        self.write(ctx, req, document)
        #
        # TODO: add tsammalex license information!
        #
        d = StringIO()
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

        #for f in filter(
        #        lambda f_: f_.name.startswith('small') or f_.name.startswith('large'),
        #        ctx._files):
        #    document.add_picture(req.file_ospath(f), width=Inches(2.5))


class SpeciesDocx(Docx):
    def write(self, ctx, req, document):
        document.add_heading(ctx.name, 0)
        document.add_heading('Names', 1)
        table = document.add_table(rows=len(ctx.valuesets), cols=2)

        for i, vs in enumerate(ctx.valuesets):
            table.cell(i, 0).text = vs.language.name
            table.cell(i, 1).text = ', '.join(v.name for v in vs.values)

        document.add_heading('Photos', 1)
        for f in filter(
                lambda f_: f_.name.startswith('small') or f_.name.startswith('large'),
                ctx._files):
            p = req.registry.settings['clld.files'].joinpath(f.relpath)
            #p = req.file_ospath(f)
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
                    cells[1].text = value

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
    config.register_adapter(GeoJsonSpecies, IParameter)