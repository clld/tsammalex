from __future__ import unicode_literals, print_function, absolute_import, division

from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    ForeignKey,
    Float,
    Boolean,
    true,
    false,
)
from sqlalchemy.orm import relationship, backref, joinedload_all
from sqlalchemy.ext.declarative import declared_attr
from pyramid.decorator import reify

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Parameter, IdNameDescriptionMixin, Value, Language, ValueSet, Source, Editor,
    ValueSetReference, Unit, HasSourceMixin, Contributor,
)

from tsammalex.interfaces import IEcoregion


ICON_MAP = {
    'Bantu': 'ffff00',
    'Khoe': '00ffff',
    'Tuu': '66ff33',
    "Kx'a": '990099',
    'Germanic': 'dd0000',
}


# -----------------------------------------------------------------------------
# specialized common mapper classes
# -----------------------------------------------------------------------------
class TsammalexContributor(CustomModelMixin, Contributor):
    __csv_name__ = 'contributors'
    # -> id
    # names, sections, affiliation -> address, research_project, homepage -> url,
    # notes -> description
    pk = Column(Integer, ForeignKey('contributor.pk'), primary_key=True)
    sections = Column(Unicode)
    research_project = Column(Unicode)

    def csv_head(self):
        return 'id,name,sections,address,research_project,url,description'.split(',')


class TsammalexEditor(CustomModelMixin, Editor):
    __csv_name__ = 'editors'
    pk = Column(Integer, ForeignKey('editor.pk'), primary_key=True)
    sections = Column(Unicode)

    def csv_head(self):
        return ['ord', 'contributor__id', 'sections']

    def to_csv(self, ctx=None, req=None, cols=None):
        return [self.ord, self.contributor.id, self.sections]

    @classmethod
    def from_csv(cls, row, data=None):
        return cls(
            ord=int(row[0] or 1),
            dataset=list(data['Dataset'].values())[0],
            contributor=data['TsammalexContributor'][row[1]])


@implementer(interfaces.ILanguage)
class Languoid(CustomModelMixin, Language):
    __csv_name__ = 'languages'
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    lineage = Column(Unicode)
    is_english = Column(Boolean, default=False)

    def csv_head(self):
        return [
            'id',
            'name',
            'lineage',
            'description',
            'latitude',
            'longitude']


@implementer(interfaces.ISource)
class Bibrec(CustomModelMixin, Source):
    __csv_name__ = 'sources'
    pk = Column(Integer, ForeignKey('source.pk'), primary_key=True)

    def csv_head(self):
        return ['id', 'name', 'description']


@implementer(interfaces.IValue)
class Word(CustomModelMixin, Value):
    """
    name: the word form
    description: the generic term.
    """
    __csv_name__ = 'words'
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    plural_form = Column(Unicode)
    stem = Column(Unicode)
    root = Column(Unicode)
    meaning = Column(Unicode)
    phonetic = Column(Unicode)
    grammatical_info = Column(Unicode)
    notes = Column(Unicode)
    comment = Column(Unicode)

    def csv_head(self):
        return [
            'id',
            'name',
            'generic_term',
            'plural_form',
            'stem',
            'root',
            'meaning',
            'phonetic',
            'grammatical_info',
            'notes',
            'comment',
            'language__id',  # 11
            'species__id',  # 12
            'refs__ids',  # 13
            'source__id',  # 14
            'categories__ids',  # 15
        ]

    @classmethod
    def csv_query(cls, session):
        return session.query(cls)\
            .join(ValueSet).join(Language).order_by(Language.id, cls.name, cls.id)\
            .options(
                joinedload_all(cls.valueset, ValueSet.language),
                joinedload_all(cls.valueset, ValueSet.parameter, Species.categories))

    def to_csv(self, ctx=None, req=None, cols=None):
        row = [
            self.id,
            self.name,
            self.description,
            self.plural_form,
            self.stem,
            self.root,
            self.meaning,
            self.phonetic,
            self.grammatical_info,
            self.notes,
            self.comment,
            self.valueset.language.id,
            self.valueset.parameter.id,
            ';'.join(
                '%s[%s]' % (r.source.id, r.description or '')
                for r in self.valueset.references),
            self.valueset.source or '',
            ';'.join(cat.id for cat in self.valueset.parameter.categories
                     if cat.language == self.valueset.language),
        ]
        assert len(row) == len(self.csv_head())
        return row

    @classmethod
    def from_csv(cls, row, data=None, description=None):
        obj = cls(
            id=row[0],
            name=row[1],
            description=row[2],
            plural_form=row[3],
            stem=row[4],
            root=row[5],
            meaning=row[6],
            phonetic=row[7],
            grammatical_info=row[8],
            notes=row[9],
            comment=row[10],
        )
        sid = row[12]
        lid = row[11]
        vsid = '%s-%s' % (sid, lid)
        if vsid in data['ValueSet']:
            vs = data['ValueSet'][vsid]
        else:
            # Note: source and references are dumped redundantly with each word, so we
            # only have to recreate these if a new ValueSet had to be created.
            try:
                vs = data.add(
                    ValueSet, vsid,
                    id=vsid,
                    source=row[14] or None,
                    parameter=data['Species'][sid],
                    language=data['Languoid'][lid],
                    contribution=data['Contribution']['tsammalex'])
            except KeyError:
                print(sid)
                print(lid)
                return
            if row[13]:
                for i, ref in enumerate(row[13].split(';')):
                    if '[' in ref:
                        rid, pages = ref.split('[', 1)
                        try:
                            assert pages.endswith(']')
                        except:  # pragma: no cover
                            print(row[13])
                            raise
                        pages = pages[:-1]
                    else:
                        rid, pages = ref, None
                    data.add(
                        ValueSetReference, '%s-%s' % (obj.id, i),
                        valueset=vs,
                        source=data['Bibrec'][rid],
                        description=pages or None)
        obj.valueset = vs
        if row[15]:
            cats = [cat.id for cat in vs.parameter.categories]
            for catid in set(row[15].split(';')):
                if catid not in cats:
                    vs.parameter.categories.append(data['Category'][catid])
        return obj


@implementer(interfaces.IParameter)
class Species(CustomModelMixin, Parameter):
    __csv_name__ = 'species'
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    english_name = Column(Unicode)  # , nullable=False)
    family = Column(Unicode)
    genus = Column(Unicode)
    order = Column(Unicode)
    kingdom = Column(Unicode)
    characteristics = Column(Unicode)
    biotope = Column(Unicode)
    general_uses = Column(Unicode)
    notes = Column(Unicode)
    eol_id = Column(String)
    tpl_id = Column(String)
    ecoregions_str = Column(Unicode)
    countries_str = Column(Unicode)

    wikipedia_url = Column(String)
    links = Column(Unicode)

    def csv_head(self):
        #id,scientific_name,species_description,english_name,kingdom,order,family,genus,characteristics,
        # biotope,ecoregions__ids,countries__ids,general_uses,notes,refs__ids,
        # wikipedia_url,eol_id,links

        return [
            'id',
            'name',
            'description',

            'english_name',
            'kingdom',

            'order',
            'family',
            'genus',
            'characteristics',

            'biotope',
            'ecoregions__ids',  # 10
            'countries__ids',  # 11
            'general_uses',  # ?


            'notes',
            'refs__ids',  # 14
            'wikipedia_url',
            'eol_id',
            'links']

    @reify
    def thumbnail(self):
        for f in self._files:
            if 1:  # todo: check tags!
                return f.jsondatadict['thumbnail']

    @property
    def tpl_url(self):
        if self.tpl_id:
            return 'http://www.theplantlist.org/tpl1.1/record/%s' % self.tpl_id

    @property
    def eol_url(self):
        if self.eol_id:
            return 'http://eol.org/%s' % self.eol_id

    def to_csv(self, ctx=None, req=None, cols=None):
        row = super(Species, self).to_csv(ctx=ctx, req=req, cols=cols)
        row[14] = ';'.join(
                '%s[%s]' % (r.source.id, r.description or '')
                for r in self.references)
        return row

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Species, cls).from_csv(row)
        for index, attr, model in [
            (11, 'countries', 'Country'), (10, 'ecoregions', 'Ecoregion')
        ]:
            for id_ in row[index].split(','):
                if id_:
                    if id_ in data[model]:
                        coll = getattr(obj, attr)
                        coll.append(data[model][id_])
                    else:
                        print('unknown %s: %s' % (model, id_))
        if row[14]:
            for i, ref in enumerate(row[14].split(';')):
                if '[' in ref:
                    rid, pages = ref.split('[', 1)
                    try:
                        assert pages.endswith(']')
                        pages = pages[:-1]
                    except:  # pragma: no cover
                        print(row[14])
                        #raise
                    #pages = pages[:-1]
                else:
                    rid, pages = ref, None
                data.add(
                    SpeciesReference, '%s-%s' % (obj.id, i),
                    species=obj,
                    source=data['Bibrec'][rid],
                    description=pages or None)

        return obj


class SpeciesReference(Base, HasSourceMixin):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    species = relationship(Species, backref="references")


class SpeciesCountry(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    country_pk = Column(Integer, ForeignKey('country.pk'))


class Country(Base, IdNameDescriptionMixin):
    __csv_name__ = 'countries'

    def csv_head(self):
        return ['id', 'name', 'description']

    @declared_attr
    def species(cls):
        return relationship(
            Species,
            secondary=SpeciesCountry.__table__,
            backref=backref('countries', order_by=str('Country.id')))


class SpeciesEcoregion(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    ecoregion_pk = Column(Integer, ForeignKey('ecoregion.pk'))


class Biome(Base, IdNameDescriptionMixin):
    """
    description holds a RGB color to use in maps.
    """


@implementer(IEcoregion)
class Ecoregion(Base, IdNameDescriptionMixin):
    """
    Attribute_Label: ECO_NAME -> name
    Attribute_Definition: Ecoregion Name

    Attribute_Label: BIOME

    Attribute_Label: eco_code -> id
    Attribute_Definition:
        This is an alphanumeric code that is similar to eco_ID but a little easier to
        interpret. The first 2 characters (letters) are the realm the ecoregion is in.
        The 2nd 2 characters are the biome and the last 2 characters are the ecoregion
        number.

    Attribute_Label: GBL_STAT
    Attribute_Definition: Global Status
    Attribute_Definition_Source:
        A 30-year prediction of future conservation status given current conservation
        status and trajectories.

    Attribute_Label: area_km2
    Attribute_Definition: Area of the Ecoregion (km2)

    Attribute_Label: G200_REGIO -> description
    Attribute_Definition: Global 200 Name
    """
    __csv_name__ = 'ecoregions'

    realm = Column(Unicode, doc='Biogeographical realm')
    gbl_stat = Column(
        Unicode,
        doc='A 30-year prediction of future conservation status given current '
            'conservation status and trajectories.')
    latitude = Column(Float)
    longitude = Column(Float)
    area = Column(Integer, doc='Area of the Ecoregion (km2)')
    biome_pk = Column(Integer, ForeignKey('biome.pk'))
    biome = relationship(
        Biome, backref=backref('ecoregions', order_by=str('Ecoregion.id')))

    gbl_stat_map = {
        1: 'CRITICAL OR ENDANGERED'.lower(),
        2: 'VULNERABLE'.lower(),
        3: 'RELATIVELY STABLE OR INTACT'.lower(),
    }
    realm_map = dict(
        AA='Australasia',
        AN='Antarctic',
        AT='Afrotropics',
        IM='IndoMalay',
        NA='Nearctic',
        NT='Neotropics',
        OC='Oceania',
        PA='Palearctic',
    )

    def csv_head(self):
        return ['id', 'name', 'description']

    @declared_attr
    def species(cls):
        return relationship(
            Species,
            secondary=SpeciesEcoregion.__table__,
            backref=backref('ecoregions', order_by=str('Ecoregion.id')))

    def wwf_url(self):
        return 'http://www.worldwildlife.org/ecoregions/' + self.id.lower()


class SpeciesCategory(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    category_pk = Column(Integer, ForeignKey('category.pk'))


@implementer(interfaces.IUnit)
class Category(CustomModelMixin, Unit):
    pk = Column(Integer, ForeignKey('unit.pk'), primary_key=True)
    notes = Column(Unicode)
    is_habitat = Column(Boolean, default=False)

    @classmethod
    def csv_query(cls, session, type_=None):
        query = Unit.csv_query(session)
        if type_ == 'categories':
            query = query.filter(cls.is_habitat == false())
        elif type == 'habitats':
            query = query.filter(cls.is_habitat == true())
        return query

    def csv_head(self):
        return ['id', 'name', 'description', 'language__id', 'notes']

    @declared_attr
    def species(cls):
        return relationship(
            Species,
            secondary=SpeciesCategory.__table__,
            backref=backref('categories', order_by=str('Category.id')))

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Category, cls).from_csv(row)
        obj.language = data['Languoid'][row[3]]
        return obj
