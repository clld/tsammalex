from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref, joinedload_all
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from pyramid.decorator import reify

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Parameter, IdNameDescriptionMixin, Value, Language, ValueSet, Source, Dataset, Editor,
)


def to_csv(obj, attr):
    rel = None
    if attr.endswith('__ids') or attr.endswith('__id'):
        attr = attr.split('__')
        rel = attr[-1]
        attr = '__'.join(attr[:-1])
    prop = getattr(obj, attr, '')
    if rel == 'id':
        return prop.id
    elif rel == 'ids':
        return ','.join(o.id for o in prop)
    return prop


class CsvMixin(object):
    __csv_head__ = ['id', 'name', 'description']

    def to_csv(self):
        return [to_csv(self, attr) for attr in self.__csv_head__]

    @classmethod
    def from_csv(cls, row):
        props = {k: row[i] for i, k in enumerate(cls.__csv_head__)
                 if not (k.endswith('__id') or k.endswith('__ids'))}
        return cls(**props)

    @classmethod
    def csv_query(cls, session):
        return session.query(cls).order_by(getattr(cls, 'id', getattr(cls, 'pk', None)))


class WordVariety(Base):
    word_pk = Column(Integer, ForeignKey('word.pk'))
    variety_pk = Column(Integer, ForeignKey('variety.pk'))


class Variety(Base, IdNameDescriptionMixin, CsvMixin):
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language, backref='varieties')


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
class TsammalexEditor(Editor, CustomModelMixin, CsvMixin):
    __csv_head__ = ['ord', 'name']

    pk = Column(Integer, ForeignKey('editor.pk'), primary_key=True)

    def to_csv(self):
        return [self.ord, self.contributor.name]


@implementer(interfaces.ILanguage)
class Languoid(Language, CustomModelMixin, CsvMixin):
    __csv_head__ = ['id', 'name', 'latitude', 'longitude', 'varieties__ids']

    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)


@implementer(interfaces.ISource)
class Bibrec(Source, CustomModelMixin, CsvMixin):
    pk = Column(Integer, ForeignKey('source.pk'), primary_key=True)


@implementer(interfaces.IValue)
class Word(Value, CustomModelMixin, CsvMixin):
    __csv_head__ = [
        'id', 'name', 'description', 'phonetic', 'grammatical_info', 'comment', 'source',
        'language__id',
        'varieties__ids',
        'species__id',
        'refs']

    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    phonetic = Column(Unicode)
    grammatical_info = Column(Unicode)
    comment = Column(Unicode)
    varieties = relationship(Variety, secondary=WordVariety.__table__)

    @classmethod
    def csv_query(cls, session):
        return session.query(cls)\
            .join(ValueSet).join(Language).order_by(Language.id, cls.name)\
            .options(joinedload_all(cls.valueset, ValueSet.language))

    def to_csv(self):
        return [
            self.id,
            self.name,
            self.description,
            self.phonetic,
            self.grammatical_info,
            self.comment,
            self.valueset.source or '',
            self.valueset.language.id,
            to_csv(self, 'varieties_ids'),
            self.valueset.parameter.id,
            ', '.join('%s[%s]' % (r.source.id, r.description or '') for r in self.valueset.references),
        ]


@implementer(interfaces.IParameter)
class Species(Parameter, CustomModelMixin, CsvMixin):
    __csv_head__ = [
        'id', 'name', 'description', 'family', 'genus', 'wikipedia_url', 'eol_id',
        'countries__ids', 'categories__ids', 'ecoregions__ids']

    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    family = Column(Unicode)
    genus = Column(Unicode)
    eol_id = Column(String)
    wikipedia_url = Column(String)

    @reify
    def thumbnail(self):
        for f in self._files:
            if f.name.startswith('thumbnail'):
                return f

    @property
    def eol_url(self):
        if self.eol_id:
            return 'http://eol.org/%s' % self.eol_id


class SpeciesCountry(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    country_pk = Column(Integer, ForeignKey('country.pk'))


class Country(Base, IdNameDescriptionMixin, CsvMixin):
    species = relationship(
        Species, secondary=SpeciesCountry.__table__, backref='countries')


class SpeciesEcoregion(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    ecoregion_pk = Column(Integer, ForeignKey('ecoregion.pk'))


class Ecoregion(Base, IdNameDescriptionMixin, CsvMixin):
    species = relationship(
        Species, secondary=SpeciesEcoregion.__table__, backref='ecoregions')


class SpeciesCategory(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    category_pk = Column(Integer, ForeignKey('category.pk'))


class Category(Base, IdNameDescriptionMixin, CsvMixin):
    species = relationship(
        Species, secondary=SpeciesCategory.__table__, backref='categories')
