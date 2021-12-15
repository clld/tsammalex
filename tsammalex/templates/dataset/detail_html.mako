<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <%util:well title="Cite">
        ${h.newline2br(h.text_citation(request, ctx))|n}
        <p>
            <a href="http://dx.doi.org/10.5281/zenodo.17571">
                <img src="https://zenodo.org/badge/doi/10.5281/zenodo.17571.svg" alt="10.5281/zenodo.17571">
            </a>
        </p>
        ${h.cite_button(request, ctx)}
    </%util:well>
    <%util:well title="Version">
        <a href="${req.resource_url(req.dataset)}" style="font-family: monospace">tsammalex.clld.org</a>
        serves the latest
        ${h.external_link('https://github.com/clld/tsammalex-data/releases', label='released version')}
        of data curated at
        ${h.external_link('https://github.com/clld/tsammalex-data', label='clld/tsammalex-data')} -
        currently
        ${h.external_link('https://github.com/clld/tsammalex-data/releases/tag/v0.3', label='v0.3')}
    </%util:well>
</%def>

<h2>Welcome to Tsammalex</h2>

<p class="lead">
Tsammalex is a multilingual lexical database on plants and animals
including linguistic, anthropological and biological information as well
as images. It has been set up as a resource for linguists,
anthropologists and other researchers, language planners and speech
communities interested in the conservation of their biological
knowledge. In the current version, it is still focused on particular
geographical regions reflecting the interests of the present
contributors (Kalahari basin in Southern Africa, Dogon languages in West
Africa).
</p>
<p class="lead">
    Lexical and biological data can be accessed directly (tabs
    <a href="${request.route_url('values')}">"Names"</a> and
    <a href="${request.route_url('parameters')}">"Taxa"</a>, respectively)
    or filtered for specific languages (<a href="${request.route_url('languages')}">"Languages"</a>)
    or geographical regions (<a href="${request.route_url('ecoregions')}">"Ecoregions"</a>
    ## and "Countries"
    ),
    with varying details. The tabs <a href="${request.route_url('sources')}">"References"</a> and
    <a href="${request.route_url('images')}">"Images"</a> include lists of sources and individual
    images.
</p>
<p>
    Tsammalex has been developed by
    ${h.external_link('https://github.com/xrotwang', label='Robert Forkel')}
    and compiled by Christfried Naumann, Lena Sell, Noémie Jaulgey
    and Kathrin Heiden. Significant amounts of data were added by
    ${h.external_link('http://dogonlanguages.org', label='Jeffrey Heath and colleagues (Dogon Languages Project)')}
    and edited by Steven Moran and Robert Forkel.
    Another bulk of data has been imported from the Reference Lexicon of the languages of Africa
    (${h.external_link('http://reflex.cnrs.fr/database/', label='RefLex')}) by  Guillaume Segerer and S. Flavier.
    Peter Fröhlich, Hans-Jörg Bibiko, Jan Klom and Stefan Koch were involved in
    former versions of the database.
</p>
<p>
    The project was funded by the Department of Linguistics of the
    ${h.external_link('http://www.eva.mpg.de/', label="Max Planck Insititute for Evolutionary Anthropology's")}
    led by Bernard Comrie. Tsammalex is published as part of the
    ${h.external_link('http://clld.org', 'Cross-Linguistic Linked Data')} project,
    led by Martin Haspelmath and maintained by the department of Cultural and Linguistic Evolution.
</p>
<p>
    The content of this web site including the downloadable database, is published under a
    ${request.dataset.jsondata['license_name']} (unless stated otherwise).
</p>
<p>
    All images and other data included in this database should be under creative commons license.
    Sensitive information that may cause conflicts in communities or harm to their environment, or
    that may threaten biological species (such as information about specific ways of killing animals
    or detailed information on medical uses) must not be included here. Cultural knowledge should
    not be published without the consent of the communities it belongs to.
</p>
