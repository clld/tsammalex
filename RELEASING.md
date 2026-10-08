# Releasing the Tsammalex clld app

```shell
git clone --depth 1 https://github.com/clld/tsammalex
cd tsammalex
pip install -e .[test]
```

```shell
unzip tsammalex.sql.zip
createdb tsammalex
psql -d tsammalex -f tsammalex.sql
```

```shell
pytest
```

Store the tested requirements:
```shell
pip freeze > requirements.txt
```

Store a db dump:
```shell
pg_dump -xO tsammalex > tsammalex.sql
zip tsammalex.sql.zip tsammalex.sql
rm tsammalex.sql
```

