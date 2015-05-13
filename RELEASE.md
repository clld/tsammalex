## Creating a release of Tsammalex

1. Update the clone of `clld/tsammalex-data` and `git checkout` the corresponding data release.
2. Add new icons using the [make_icons.py script](https://github.com/clld/recipes/blob/master/clld/make_icons.py) with the icon specifications from
```bash
csvcut tsammalex-data/tsammalexdata/data/lineages.csv -c color
```
3. Import the data running the `initializedb.py` script.
4. Run the test suite.
5. Adapt version info on the app landing page.
6. [Create a release](https://help.github.com/articles/creating-releases/) of `clld/tsammalex`.
7. Create PDF downloads locally.
8. Update database, application and downloads on the server.
