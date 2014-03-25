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
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from pyramid.decorator import reify

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import Parameter, IdNameDescriptionMixin, Value, Language


class WordVariety(Base):
    word_pk = Column(Integer, ForeignKey('word.pk'))
    variety_pk = Column(Integer, ForeignKey('variety.pk'))


class Variety(Base, IdNameDescriptionMixin):
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language, backref='varieties')


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
@implementer(interfaces.IValue)
class Word(Value, CustomModelMixin):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    phonetic = Column(Unicode)
    grammatical_info = Column(Unicode)
    varieties = relationship(Variety, secondary=WordVariety.__table__)


@implementer(interfaces.IParameter)
class Species(Parameter, CustomModelMixin):
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


class Country(Base, IdNameDescriptionMixin):
    species = relationship(
        Species, secondary=SpeciesCountry.__table__, backref='countries')


class SpeciesEcoregion(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    ecoregion_pk = Column(Integer, ForeignKey('ecoregion.pk'))


class Ecoregion(Base, IdNameDescriptionMixin):
    species = relationship(
        Species, secondary=SpeciesEcoregion.__table__, backref='ecoregions')


class SpeciesCategory(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    category_pk = Column(Integer, ForeignKey('category.pk'))


class Category(Base, IdNameDescriptionMixin):
    species = relationship(
        Species, secondary=SpeciesCategory.__table__, backref='categories')
