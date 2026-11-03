# Releasing the Tsammalex clld app

```shell
git clone --depth 1 https://github.com/clld/tsammalex
cd tsammalex
pip install -e .[test]
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
pg_dump -xO --compress gzip:9 tsammalex > tsammalex.sql.gz
```

