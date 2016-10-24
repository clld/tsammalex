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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref, joinedload_all, joinedload
from sqlalchemy.ext.declarative import declared_attr
from nameparser import HumanName

from clld import interfaces
from clldutils.misc import slug
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Parameter, IdNameDescriptionMixin, Value, Language, ValueSet, Source, Editor,
    Unit, HasSourceMixin, Contributor, Parameter_files, Contribution,
    ContributionContributor,
)
from clld.web.util.htmllib import HTML

from tsammalex.interfaces import IEcoregion


ID_SEP_PATTERN = re.compile('\.|,|;')


def split_ids(s):
    if not s:
        return []
    return sorted(set(i.strip() for i in ID_SEP_PATTERN.split(s) if i.strip()))


def parse_ref_ids(s):
    for i, ref in enumerate(s.split(';')):
        rid, pages = ref, None
        if '[' in ref:
            rid, pages = ref.split('[', 1)
            try:
                assert pages.endswith(']')
                pages = pages[:-1]
            except:  # pragma: no cover
                print(s)
                #raise
        yield i, rid, pages


class ImageData(Base):
    __table_args__ = (UniqueConstraint('image_pk', 'key'),)

    image_pk = Column(Integer, ForeignKey('parameter_files.pk'))
    key = Column(Unicode)
    value = Column(Unicode)
    image = relationship(Parameter_files, uselist=False, backref='data')


def get_data(self, key):
    for d in self.data:
        if d.key == key:
            return d.value


Parameter_files.get_data = get_data


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

    def last_first(self):
        return '{0.first} {0.last}'.format(self.parsed_name)

    def csv_head(self):
        return 'id,name,sections,editor_ord,editor_sections,address,research_project,url,description'.split(',')

    @property
    def parsed_name(self):
        return HumanName(self.name)

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


class SecondLanguoid(Base):
    """Relate languoids with "Verkehrssprachen"."""
    first_pk = Column(Integer, ForeignKey('languoid.pk'))
    second_pk = Column(Integer, ForeignKey('languoid.pk'))


@implementer(interfaces.ILanguage)
class Languoid(CustomModelMixin, Language):
    __csv_name__ = 'languages'
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    lineage_pk = Column(Integer, ForeignKey('lineage.pk'))
    lineage = relationship(Lineage, backref='languoids')
    glottocode = Column(String)
    region = Column(Unicode)
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship(Contribution, backref=backref('language', uselist=False))

    @declared_attr
    def second_languages(cls):
        secondary = SecondLanguoid.__table__
        return relationship(
            cls,
            secondary=secondary,
            primaryjoin=cls.pk == secondary.c.first_pk,
            secondaryjoin=cls.pk == secondary.c.second_pk)

    def csv_head(self):
        return [
            'id',
            'name',
            'glottocode',
            'contributors__ids',
            'description',
            'lineages__id',
            'latitude',
            'longitude',
            'region',
            'languages__ids',
        ]

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Languoid, cls).from_csv(row)
        obj.lineage = data['Lineage'][row[5]]
        obj.contribution = Contribution(id=obj.id, name=obj.name)
        for i, cid in enumerate(split_ids(row[3])):
            ContributionContributor(
                contribution=obj.contribution,
                contributor=data['TsammalexContributor'][cid],
                ord=i)
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
    A name for a taxon in a particular language.

    name: the word form
    """
    __csv_name__ = 'names'
    __csv_head__ = [
        'id',
        'name',
        'languages__id',  # 2
        'taxa__id',  # 3
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
        sid = row['taxa__id']
        lid = row['languages__id']
        vsid = '%s-%s' % (sid, lid)
        if vsid in data['ValueSet']:
            obj.valueset = data['ValueSet'][vsid]
        else:
            # Note: source and references are dumped redundantly with each word, so we
            # only have to recreate these if a new ValueSet had to be created.
            obj.valueset = data.add(
                ValueSet, vsid,
                id=vsid,
                parameter=data['Taxon'][sid],
                language=data['Languoid'][lid],
                contribution=data['Contribution']['tsammalex'])

        if row['refs__ids']:
            for i, rid, pages in parse_ref_ids(row['refs__ids']):
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
            for id_ in split_ids(row[rel + '__ids']):
                getattr(obj, rel).append(data[cls][id_.strip()])
        return obj


class NameReference(Base, HasSourceMixin):
    name_pk = Column(Integer, ForeignKey('name.pk'))

    @declared_attr
    def name(self):
        return relationship(Name, backref='references')


@implementer(interfaces.IParameter)
class Taxon(CustomModelMixin, Parameter):
    __csv_name__ = 'taxa'
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    english_name = Column(Unicode)  # , nullable=False)
    synonyms = Column(Unicode)
    genus = Column(Unicode)
    family = Column(Unicode)
    order = Column(Unicode)
    class_ = Column(Unicode)
    phylum = Column(Unicode)
    kingdom = Column(Unicode)
    characteristics = Column(Unicode)
    biotope = Column(Unicode)
    general_uses = Column(Unicode)
    notes = Column(Unicode)
    eol_id = Column(Integer)
    gbif_id = Column(Integer)
    catalogueoflife_url = Column(String)
    ecoregions_str = Column(Unicode)
    countries_str = Column(Unicode)
    rank = Column(Unicode, default='species')

    wikipedia_url = Column(String)
    links = Column(Unicode)

    @property
    def scientific_name(self):
        return self.name

    @scientific_name.setter
    def scientific_name(self, value):
        self.name = value

    def csv_head(self):
        return [
            'id',
            'scientific_name',
            'synonyms',
            'description',
            'english_name',
            'kingdom',
            'phylum',
            'class_',
            'order',
            'family',
            'genus',
            'characteristics',
            'biotope',
            'countries__ids',  # 13
            'general_uses',  # ?
            'notes',
            'refs__ids',  # 16
            'links']

    @classmethod
    def csv_query(cls, session, type_=None):
        return Parameter.csv_query(session).options(
            joinedload(Taxon.ecoregions),
            joinedload(Taxon.countries),
            joinedload(Taxon.references),
        )

    def formatted_refs(self, req):
        res = []
        for ref in self.references:
            text = HTML.a(ref.source.name, href=req.resource_url(ref.source))
            if ref.description:
                text = '%s: %s' % (text, ref.description)
            res.append(text)
        return '; '.join(res)

    def image(self, tag=None, index=None):
        """Return the URL for the first image of a certain type.

        There are two ways to select specific images:
        - by index
        - by tag

        So the following API is supported:
        url = taxon.image_url(t, tag='thumbnail1') or taxon.image_url(t, index=0)
        """
        for i, f in enumerate(sorted(self._files, key=lambda f: f.id)):
            if index == i:
                return f
            if tag and tag in f.name:
                return f
            if tag is None and index is None:
                return f

    def image_url(self, type, tag=None, index=None):
        img = self.image(tag=tag, index=index)
        if img:
            return img.jsondata.get(type)

    @property
    def link_specs(self):
        return [
            spec[1:] for spec in [
                (
                    self.eol_id,
                    'http://eol.org/%s' % self.eol_id,
                    'eol',
                    'Encyclopedia of Life'),
                (
                    self.wikipedia_url,
                    self.wikipedia_url,
                    'wikipedia',
                    'Wikipedia'),
                (
                    self.gbif_id,
                    'http://www.gbif.org/species/%s' % self.gbif_id,
                    'GBIF',
                    'GBIF.org'),
                (
                    self.catalogueoflife_url,
                    self.catalogueoflife_url,
                    'CatalogueOfLife',
                    'The Catalogue of Life'),
                (
                    True,
                    'http://www.biodiversitylibrary.org/name/%s'
                    % self.name.capitalize().replace(' ', '_'),
                    'BHL',
                    'Biodiversity Heritage Library')] if spec[0]]

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Taxon, cls).from_csv(row)
        if row[16]:
            for i, rid, pages in parse_ref_ids(row[16]):
                data.add(
                    TaxonReference, '%s-%s' % (obj.id, i),
                    taxon=obj,
                    source=data['Bibrec'][rid],
                    description=pages or None)

        return obj


class TaxonReference(Base, HasSourceMixin):
    taxon_pk = Column(Integer, ForeignKey('taxon.pk'))
    taxon = relationship(Taxon, backref="references")


class TaxonCountry(Base):
    taxon_pk = Column(Integer, ForeignKey('taxon.pk'))
    country_pk = Column(Integer, ForeignKey('country.pk'))


class Country(Base, IdNameDescriptionMixin):
    @declared_attr
    def taxa(cls):
        return relationship(
            Taxon,
            secondary=TaxonCountry.__table__,
            backref=backref('countries', order_by=str('Country.id')))


class TaxonEcoregion(Base):
    taxon_pk = Column(Integer, ForeignKey('taxon.pk'))
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
    def taxa(cls):
        return relationship(
            Taxon,
            secondary=TaxonEcoregion.__table__,
            backref=backref('ecoregions', order_by=str('Ecoregion.id')))

    def wwf_url(self):
        return 'http://www.worldwildlife.org/ecoregions/' + self.id.lower()
