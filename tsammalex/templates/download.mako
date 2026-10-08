<%inherit file="home_comp.mako"/>

<h2>Downloads</h2>

<div class="alert alert-info">
        <a href="${req.resource_url(req.dataset)}" style="font-family: monospace">tsammalex.clld.org</a>
        serves the latest
        ${h.external_link('https://github.com/clld/tsammalex-data/releases', label='released version')}
        of data curated at
        ${h.external_link('https://github.com/clld/tsammalex-data', label='clld/tsammalex-data')} -
        currently
        ${h.external_link('https://github.com/clld/tsammalex-data/releases/tag/v0.3', label='v0.3')}
</div>

