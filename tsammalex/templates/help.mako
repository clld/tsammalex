<%inherit file="${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "contribute" %>


<h2>Contribute!</h2>

<p>
    The expansion of the Tsammalex database strongly depends on researchers and communities willing
    to share their knowledge or collected data. If you are interested in a contribution and have
    questions, don't hesitate to
    <a href="${request.route_url('contact')}">contact</a> one of the editors
    (Christfried Naumann, Steven Moran or Robert Forkel).
</p>
<p>
    The structure of the database is based on
    ${h.external_link('http://en.wikipedia.org/wiki/Comma-separated_values', label='csv tables')}
    ("...csv"), i.e., a simple file format that can
    be opened and edited in editors such as Notepad, or calculation programs such as LibreOffice Calc or
    Microsoft Excel.
    ${h.external_link('https://github.com/clld/tsammalex-data/tree/master/tsammalexdata/data', label='These csv files')}
    contain all data on biological species and related linguistic or
    lexical data, as well as metadata of audio and image files, etc.
    There is
    ${h.external_link('https://github.com/clld/tsammalex-data/blob/master/tsammalexdata/data/sources.bib', label='a BibTeX')}
    file containing all
    references cited. Images of species (licensed as Creative Commons or in Public domain) might be
    uploaded to websites such as Flickr or Wikimedia Commons and linked, or sent to the editors.
    For more information on the structure of the data and on planned improvements refer to
    <a href="${request.static_url('tsammalex:static/Tsammalex-Manual.pdf')}">the manual [PDF]</a>.
</p>
##<p>
##    Here you can download the following items:
##</p>
##<ul>
##    <li>csv files including all data of the current Tsammalex version (cf. also Home/Download/GitHub repository)</li>
##    <li>a sketch manual of Tsammalex with details about layout, functions and data formats</li>
##    <li>csv table templates ready for the input of lexical ("names.csv") and biological data ("species.csv"), etc.</li>
##</ul>
<p>
    Contributions of data must be committed in the form of csv files. In a Windows environment, we recommend
    using LibreOffice Calc. Open the csv table templates, set the character encoding to UTF-8 (Unicode) and
    select comma separated table. Have a look into the sketch manual about obligatory vs. optional
    information, and start entering data. Send these files to the editors.
</p>
<p>
    Alternatively, if you feel comfortable with the
    ${h.external_link('https://help.github.com/articles/using-pull-requests/', label='GitHub collaboration model')}
    you may fork the
    ${h.external_link('https://github.com/clld/tsammalex-data', label='tsammalex-data repository')},
    add your data and submit a pull request.
</p>
<p>
    Notes:
</p>
<ul>
    <li>Lexical data in "names.csv" must be associated with one species (or another biological taxon, such as a genus).</li>
    <li>Any species (or other taxon) referred to under "names.csv" must be included previously under "species.csv".</li>
    <li>
        The consistency of the data in the tsammalex-data repository is checked by
        ${h.external_link('https://travis-ci.org/clld/tsammalex-data', label='Travis-CI')},
        so if you choose to add data using pull request, you get the added benefit of having your additions
        cross-checked while you are working on them.
    </li>
    <li>
        Further information on the rationale behind curating the data in this way are available
        in ${h.external_link('http://clld.org/2015/02/03/open-source-research-data.html', label='this post')}.
    </li>
</ul>