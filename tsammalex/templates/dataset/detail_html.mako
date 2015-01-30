<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <%util:well title="Cite">
        ${h.newline2br(h.text_citation(request, ctx))|n}
        ${h.cite_button(request, ctx)}
    </%util:well>
</%def>

<h2>Welcome to Tsammalex</h2>

<p class="lead">
    Tsammalex is a multilingual lexical database on plants and animals including an image repository.
    In the current preliminary version (work in progress), it is focused on the Kalahari region of
    Southern Africa. It is meant as a platform for scholars of lexicology in vernacular languages
    and other users (biologists, language planners, communities, and individual users) to share
    free images, to search for biological taxa, and to compare lexical data.


    Tsammalex is a multilingual lexical database on plants and animals including linguistic,
    anthropological and biological information as well as images. It has been set up as a
    resource for linguists, anthropologists and other researchers, language planners and
    speech communities interested in the conservation of their biological knowledge.
    In the current version, it is still focused on particular geographical regions reflecting the
    interests of the present contributors (Kalahari basin in Southern Africa, Dogon languages in West Africa).
</p>
<p class="lead">
    Lexical and biological data can be accessed directly (tabs
    "Names" and
    "Taxa", respectively)
    or filtered for specific languages ("Languages") or geographical regions ("Ecoregions" and "Countries"),
    with varying details. The tabs "References" and "Images" include lists of sources and individual
    images, while "Contribute!" provides more information, especially for potential contributors.
</p>
<p>
    Tsammalex has been developed by Robert Forkel and compiled by Christfried Naumann, Lena Sell, Noémie Jaulgey
    and Kathrin Heiden. Peter Fröhlich, Hans-Jörg Bibiko, Jan Klom and Stefan Koch were involved in
    former versions of the database. Significant amounts of data were added by
    ${h.external_link('http://dogonlanguages.org', label='Steven Moran and colleagues (Dogon languages)')}.
</p>
<p>
    The project is funded by the Max Planck Insititute for Evolutionary Anthropology's Department of Linguistics,
    led by Bernard Comrie. Tsammalex is published as part of the
    ${h.external_link('http://clld.org', 'Cross-Linguistic Linked Data')} project,
    led by Martin Haspelmath.
</p>
<p>
    The content of this web site including the downloadable database, is published under a
    ${request.dataset.jsondatadict['license_name']} (unless stated otherwise).
</p>
<p>
    Contributions and comments are highly appreciated! Read more information under "Contribute!".
</p>
<p>
    All images and other data included in this database should be under creative commons license.
    Sensitive information that may cause conflicts in communities or harm to their environment, or
    that may threaten biological species (such as information about specific ways of killing animals
    or detailed information on medical uses) must not be included here. Cultural knowledge should
    not be published without the consent of the communities it belongs to.
</p>
