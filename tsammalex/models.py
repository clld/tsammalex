from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    Float,
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
    ValueSetReference,
)


class CsvMixin(object):
    #: base name of the csv file
    __csv_name__ = None

    #: list of field names for the csv file
    __csv_head__ = ['id', 'name', 'description']

    def value_to_csv(self, attr):
        """Convert one value to a representation suitable for csv writer.

        :param attr: Name of the attribute from which to convert the value.
        :return: Object suitable for serialization with csv writer.
        """
        rel = None
        if attr.endswith('__ids') or attr.endswith('__id'):
            attr = attr.split('__')
            rel = attr[-1]
            attr = '__'.join(attr[:-1])
        try:
            prop = getattr(self, attr, '')
        except:
            print self
            print attr
            raise
        if rel == 'id':
            return prop.id
        elif rel == 'ids':
            return ','.join(o.id for o in prop)
        return prop

    def to_csv(self):
        """
        :return: list of values to be passed to csv.writer.writerow
        """
        return [self.value_to_csv(attr) for attr in self.__csv_head__]

    @classmethod
    def value_from_csv(cls, attr, value):
        if not value:
            return None
        col = getattr(cls, attr)
        if isinstance(col.property.columns[0].type, Integer):
            return int(value)
        if isinstance(col.property.columns[0].type, Float):
            return float(value.replace(',', '.'))
        return value

    @classmethod
    def from_csv(cls, row, data=None):
        props = {k: cls.value_from_csv(k, row[i]) or None for i, k in enumerate(cls.__csv_head__)
                 if not (k.endswith('__id') or k.endswith('__ids'))}
        return cls(**props)

    @classmethod
    def csv_query(cls, session):
        return session.query(cls).order_by(getattr(cls, 'id', getattr(cls, 'pk', None)))


class WordVariety(Base):
    word_pk = Column(Integer, ForeignKey('word.pk'))
    variety_pk = Column(Integer, ForeignKey('variety.pk'))


class Variety(Base, IdNameDescriptionMixin, CsvMixin):
    __csv_name__ = 'varieties'
    language_pk = Column(Integer, ForeignKey('language.pk'))

    @declared_attr
    def language(cls):
        return relationship(Language, backref=backref('varieties', order_by='Variety.id'))


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
class TsammalexEditor(Editor, CustomModelMixin, CsvMixin):
    __csv_name__ = 'editors'
    __csv_head__ = ['ord', 'name']

    pk = Column(Integer, ForeignKey('editor.pk'), primary_key=True)

    def to_csv(self):
        return [self.ord, self.contributor.name]


@implementer(interfaces.ILanguage)
class Languoid(Language, CustomModelMixin, CsvMixin):
    __csv_name__ = 'languages'
    __csv_head__ = ['id', 'name', 'description', 'latitude', 'longitude', 'varieties__ids']

    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)

    @classmethod
    def from_csv(cls, row, data=None):
        lang = super(Languoid, cls).from_csv(row)
        for vid in row[5].split(','):
            if vid:
                lang.varieties.append(data['Variety'][vid])
        return lang


@implementer(interfaces.ISource)
class Bibrec(Source, CustomModelMixin, CsvMixin):
    __csv_name__ = 'sources'
    pk = Column(Integer, ForeignKey('source.pk'), primary_key=True)


@implementer(interfaces.IValue)
class Word(Value, CustomModelMixin, CsvMixin):
    __csv_name__ = 'words'
    __csv_head__ = [
        'id', 'name', 'description', 'phonetic', 'grammatical_info', 'comment',
        'source__id',
        'language__id',
        'varieties__ids',
        'species__id',
        'refs__ids']

    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    phonetic = Column(Unicode)
    grammatical_info = Column(Unicode)
    comment = Column(Unicode)
    varieties = relationship(Variety, secondary=WordVariety.__table__, order_by=Variety.id)

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
            self.value_to_csv('varieties__ids'),
            self.valueset.parameter.id,
            ';'.join('%s[%s]' % (r.source.id, r.description or '') for r in self.valueset.references),
        ]

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Word, cls).from_csv(row)
        sid = row[9]
        lid = row[7]
        vsid = '%s-%s' % (sid, lid)
        if vsid in data['ValueSet']:
            vs = data['ValueSet'][vsid]
        else:
            # Note: source and references are dumped redundantly with each word, so we
            # only have to recreate these if a new ValueSet had to be created.
            vs = data.add(
                ValueSet, vsid,
                id=vsid,
                source=row[6] or None,
                parameter=data['Species'][sid],
                language=data['Languoid'][lid],
                contribution=data['Contribution']['tsammalex'])
            if row[10]:
                for i, ref in enumerate(row[10].split(';')):
                    rid, pages = ref.split('[', 1)
                    try:
                        assert pages.endswith(']')
                    except:
                        print row[10]
                        raise
                    pages = pages[:-1]
                    data.add(
                        ValueSetReference, '%s-%s' % (obj.id, i),
                        valueset=vs, source=data['Bibrec'][rid], description=pages or None)
        obj.valueset = vs

        if row[8]:
            for i, vid in enumerate(row[8].split(',')):
                obj.varieties.append(data['Variety'][vid])

        return obj


@implementer(interfaces.IParameter)
class Species(Parameter, CustomModelMixin, CsvMixin):
    __csv_name__ = 'species'
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

    @classmethod
    def from_csv(cls, row, data=None):
        obj = super(Species, cls).from_csv(row)
        for index, model in [(7, 'Country'), (8, 'Category'), (9, 'Ecoregion')]:
            for id_ in row[index].split(','):
                if id_:
                    coll = getattr(obj, cls.__csv_head__[index].split('__')[0])
                    coll.append(data[model][id_])
        return obj


class SpeciesCountry(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    country_pk = Column(Integer, ForeignKey('country.pk'))


class Country(Base, IdNameDescriptionMixin, CsvMixin):
    __csv_name__ = 'countries'

    @declared_attr
    def species(cls):
        return relationship(
            Species,
            secondary=SpeciesCountry.__table__,
            backref=backref('countries', order_by='Country.id'))


class SpeciesEcoregion(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    ecoregion_pk = Column(Integer, ForeignKey('ecoregion.pk'))


class Ecoregion(Base, IdNameDescriptionMixin, CsvMixin):
    __csv_name__ = 'ecoregions'

    @declared_attr
    def species(cls):
        return relationship(
            Species,
            secondary=SpeciesEcoregion.__table__,
            backref=backref('ecoregions', order_by='Ecoregion.id'))


class SpeciesCategory(Base):
    species_pk = Column(Integer, ForeignKey('species.pk'))
    category_pk = Column(Integer, ForeignKey('category.pk'))


class Category(Base, IdNameDescriptionMixin, CsvMixin):
    __csv_name__ = 'categories'

    @declared_attr
    def species(cls):
        return relationship(
            Species,
            secondary=SpeciesCategory.__table__,
            backref=backref('categories', order_by='Category.id'))
