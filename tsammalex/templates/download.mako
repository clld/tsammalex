<%inherit file="home_comp.mako"/>


<h2>Downloads</h2>
<div class="span5 well well-small">
    <dl>
    % for model, dls in h.get_downloads(request):
        <dt>${_(model)}</dt>
        % for dl in dls:
        <dd>
            <a href="${dl.url(request)}">${dl.label(req)}</a>
        </dd>
        % endfor
    % endfor
    </dl>
</div>
<div class="span6">
    <p>
        Downloads are provided as
        ${h.external_link("http://en.wikipedia.org/wiki/Zip_%28file_format%29", label="zip archives")}
        bundling the data and a
        ${h.external_link("http://en.wikipedia.org/wiki/README", label="README")}
        file.
    </p>
    <p>
        The data served by this web application is curated as a set of CSV files in a
        <a href="https://github.com/clld/tsammalex-data">GitHub repository</a>. A detailed
        description of this repository is available in its
        <a href="https://github.com/clld/tsammalex-data/blob/master/README.md">README</a>.
    </p>
    <p>
        The Tsammalex application serves the
        <a href="https://github.com/clld/tsammalex-data/releases">latest release</a>
        of this data.
    </p>
</div>

