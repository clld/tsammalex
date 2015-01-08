from __future__ import unicode_literals, print_function, absolute_import, division
import re

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

from clld import interfaces
from clld.util import slug
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Parameter, IdNameDescriptionMixin, Value, Language, ValueSet, Source, Editor,
    Unit, HasSourceMixin, Contributor,
)

from tsammalex.interfaces import IEcoregion


ID_SEP_PATTERN = re.compile('\.|,|;')


# -----------------------------------------------------------------------------
# specialized common mapper classes
# -----------------------------------------------------------------------------
class Lineage(Base, IdNameDescriptionMixin):
    __csv_name__ = 'lineages'
    glottocode = Column(String)
    color = Column(String, default='ff6600')
    family = Column(Unicode)
    family_glottocode = Column(String)

    def csv_head(self):
        return [
            'id',
            'name',
            'description',
            'glottocode',
            'family',
            'family_glottocode',
            'color']


class Use(Base, IdNameDescriptionMixin):
    __csv_name__ = 'uses'

    def csv_head(self):
        return ['id', 'name', 'description']


class TsammalexContributor(CustomModelMixin, Contributor):
    __csv_name__ = 'contributors'
    # -> id
    # names, sections, affiliation -> address, research_project, homepage -> url,
    # notes -> description
    pk = Column(Integer, ForeignKey('contributor.pk'), primary_key=True)
    sections = Column(Unicode)
    research_project = Column(Unicode)

    def csv_head(self):
        return 'id,name,editor_ord,editor_sections,sections,address,research_project,url,description'.split(',')

    @property
    def notes(self):
        return self.description

    @notes.setter
    def notes(self, value):
        self.description = value

    @property
    def affiliation(self):
        return self.address

    @affiliation.setter
    def affiliation(self, value):
        self.address = value

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(TsammalexContributor, cls).from_csv(row)
        if row[3]:
            data.add(
                TsammalexEditor, row[0],
                ord=int(row[3]),
                dataset=data['Dataset']['tsammalex'],
                contributor=obj,
                sections=row[4])
        return obj


class TsammalexEditor(CustomModelMixin, Editor):
    pk = Column(Integer, ForeignKey('editor.pk'), primary_key=True)
    sections = Column(Unicode)


@implementer(interfaces.ILanguage)
class Languoid(CustomModelMixin, Language):
    __csv_name__ = 'languages'
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    lineage_pk = Column(Integer, ForeignKey('lineage.pk'))
    lineage = relationship(Lineage, backref='languoids')
    glottocode = Column(String)

    def csv_head(self):
        return [
            'id',
            'name',
            'lineage__id',
            'description',
            'latitude',
            'longitude',
            'glottocode']

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Languoid, cls).from_csv(row)
        obj.lineage = data['Lineage'][row[2]]
        return obj


@implementer(interfaces.ISource)
class Bibrec(CustomModelMixin, Source):
    __csv_name__ = 'sources'
    pk = Column(Integer, ForeignKey('source.pk'), primary_key=True)

    def csv_head(self):
        return ['id', 'name', 'description']


class NameUse(Base):
    name_pk = Column(Integer, ForeignKey('name.pk'))
    use_pk = Column(Integer, ForeignKey('use.pk'))


class NameCategory(Base):
    name_pk = Column(Integer, ForeignKey('name.pk'))
    category_pk = Column(Integer, ForeignKey('category.pk'))


class NameHabitat(Base):
    name_pk = Column(Integer, ForeignKey('name.pk'))
    category_pk = Column(Integer, ForeignKey('category.pk'))


@implementer(interfaces.IUnit)
class Category(CustomModelMixin, Unit):
    pk = Column(Integer, ForeignKey('unit.pk'), primary_key=True)
    notes = Column(Unicode)
    is_habitat = Column(Boolean, default=False)

    @property
    def meaning(self):
        return self.description

    @meaning.setter
    def meaning(self, value):
        self.description = value

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

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Category, cls).from_csv(row)
        obj.language = data['Languoid'][row[3]]
        return obj


@implementer(interfaces.IValue)
class Name(CustomModelMixin, Value):
    """
    A name for a species in a particular language.

    name: the word form
    """
    __csv_name__ = 'names'
    __csv_head__ = [
        'id',
        'name',
        'language__id',  # 2
        'species__id',  # 3
        'ipa',
        'audio',  # will be removed!
        'grammatical_info',
        'plural_form',
        'stem',
        'root',
        'basic_term',
        'meaning',  # -> description
        'literal_translation',
        'usage',
        'source_language',
        'source_form',
        'linguistic_notes',
        'related_lexemes',
        'categories__ids',
        'habitats__ids',
        'introduced',
        'uses__ids',
        'importance',
        'associations',
        'ethnobiological_notes',
        'comment',
        'source',
        'refs__ids',
        'original_source',
    ]

    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

    ipa = Column(Unicode)
    grammatical_info = Column(Unicode)
    plural_form = Column(Unicode)
    stem = Column(Unicode)
    root = Column(Unicode)
    basic_term = Column(Unicode)
    literal_translation = Column(Unicode)
    usage = Column(Unicode)
    source_language = Column(Unicode)
    source_form = Column(Unicode)
    linguistic_notes = Column(Unicode)
    related_lexemes = Column(Unicode)
    introduced = Column(Unicode)
    importance = Column(Unicode)
    associations = Column(Unicode)
    ethnobiological_notes = Column(Unicode)

    comment = Column(Unicode)
    source = Column(Unicode)
    original_source = Column(Unicode)

    categories = relationship(Category, secondary=NameCategory.__table__)
    habitats = relationship(Category, secondary=NameHabitat.__table__)
    uses = relationship(Use, secondary=NameUse.__table__)

    @property
    def meaning(self):
        return self.description

    @meaning.setter
    def meaning(self, value):
        self.description = value

    def csv_head(self):
        return self.__csv_head__

    @classmethod
    def csv_query(cls, session):
        return session.query(cls)\
            .join(ValueSet).join(Language).order_by(Language.id, cls.name, cls.id)\
            .options(
                joinedload_all(cls.valueset, ValueSet.language),
                joinedload_all(cls.valueset, ValueSet.parameter))

    @classmethod
    def from_csv(cls, row, data=None, description=None):
        obj = cls(**{n: row[i] for i, n in enumerate(cls.__csv_head__) if '__' not in n and n != 'audio'})
        if not slug(row[1]):
            obj.active = False
        row = dict(list(zip(cls.__csv_head__, row)))
        sid = row['species__id']
        lid = row['language__id']
        vsid = '%s-%s' % (sid, lid)
        if vsid in data['ValueSet']:
            obj.valueset = data['ValueSet'][vsid]
        else:
            # Note: source and references are dumped redundantly with each word, so we
            # only have to recreate these if a new ValueSet had to be created.
            obj.valueset = data.add(
                ValueSet, vsid,
                id=vsid,
                parameter=data['Species'][sid],
                language=data['Languoid'][lid],
                contribution=data['Contribution']['tsammalex'])

        if row['refs__ids']:
            for i, ref in enumerate(row['refs__ids'].split(';')):
                if '[' in ref:
                    rid, pages = ref.split('[', 1)
                    try:
                        assert pages.endswith(']')
                    except:  # pragma: no cover
                        print(row['refs__ids'])
                        raise
                    pages = pages[:-1]
                else:
                    rid, pages = ref, None
                data.add(
                    NameReference, '%s-%s' % (obj.id, i),
                    name=obj,
                    source=data['Bibrec'][rid],
                    description=pages or None)
        for rel, cls in [
            ('categories', 'Category'),
            ('habitats', 'Category'),
            ('uses', 'Use')
        ]:
            if row[rel + '__ids']:
                for id_ in set(ID_SEP_PATTERN.split(row[rel + '__ids'])):
                    if id_.strip():
                        getattr(obj, rel).append(data[cls][id_.strip()])
        return obj


class NameReference(Base, HasSourceMixin):
    name_pk = Column(Integer, ForeignKey('name.pk'))

    @declared_attr
    def name(self):
        return relationship(Name, backref='references')


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
    gbif_id = Column(String)
    ecoregions_str = Column(Unicode)
    countries_str = Column(Unicode)

    wikipedia_url = Column(String)
    links = Column(Unicode)

    @property
    def scientific_name(self):
        return self.name

    @scientific_name.setter
    def scientific_name(self, value):
        self.name = value

    @property
    def species_description(self):
        return self.description

    @species_description.setter
    def species_description(self, value):
        self.description = value

    def csv_head(self):
        return [
            'id',
            'scientific_name',
            'species_description',
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

    def image_url(self, type):
        """Return the URL for the first image of a certain type."""
        for f in self._files:
            if 1:  # FIXME: check tags!
                return f.jsondatadict.get(type)

    @property
    def link_specs(self):
        return [
            spec for spec in [
                (self.eol_url, 'eol', 'Encyclopedia of Life'),
                (self.wikipedia_url, 'wikipedia', 'Wikipedia'),
                (self.tpl_url, 'ThePlantList', 'ThePlantList'),
                (self.gbif_url, 'GBIF', 'GBIF.org'),
                (self.bhl_url, 'BHL', 'Biodiversity Heritage Library')] if spec[0]]

    @property
    def tpl_url(self):
        if self.tpl_id:
            return 'http://www.theplantlist.org/tpl1.1/record/%s' % self.tpl_id

    @property
    def eol_url(self):
        if self.eol_id:
            return 'http://eol.org/%s' % self.eol_id

    @property
    def gbif_url(self):
        if self.gbif_id:
            return 'http://www.gbif.org/species/%s' % self.gbif_id

    @property
    def bhl_url(self):
        return 'http://www.biodiversitylibrary.org/name/%s' \
            % self.name.capitalize().replace(' ', '_')

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Species, cls).from_csv(row)
        for index, attr, model in [
            (11, 'countries', 'Country'), (10, 'ecoregions', 'Ecoregion')
        ]:
            for id_ in ID_SEP_PATTERN.split(row[index]):
                if id_.strip():
                    if id_ in data[model]:
                        coll = getattr(obj, attr)
                        coll.append(data[model][id_.strip()])
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
