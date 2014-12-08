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
    free images, to search for biological species, and to compare lexical data.
</p>
<p>
    Contributors and comments are very welcome. It has been set up by Robert Forkel and compiled
    by Christfried Naumann with the support of Kathrin Heiden, Lena Sell and Noémie Jaulgey (data)
    as well as Peter Fröhlich, Hans-Jörg Bibiko, Jan Klom and Stefan Koch (former set-up).
</p>
<p>
    The project is
    funded by the Max Planck Insititute for Evolutionary Anthropology's Department of Linguistics,
    led by Bernard Comrie. Tsammalex is published as part of the
    ${h.external_link('http://clld.org', 'Cross-Linguistic Linked Data')} project,
    led by Martin Haspelmath.
</p>
<p>
    Tsammalex is a database including linguistic, anthropological and biological information
    about plant and animal species. It is a resource for linguists, anthropologists and other
    researchers as well as for speech communities interested in the conservation of their biological
    knowledge. Sensitive information that may cause harm to communities and their environment,
    or that may threaten biological species (such as information about specific ways of killing
    animals or detailed information on medical uses) should not be included here. Cultural knowledge
    should not be published without the consent of the communities it belongs to.
</p>
<p>
    The content of this web site including the downloadable database, is published under a
    ${request.dataset.jsondatadict['license_name']} License (unless stated otherwise).
</p>
