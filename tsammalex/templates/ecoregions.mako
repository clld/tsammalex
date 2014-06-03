<%inherit file="tsammalex.mako"/>
<%! active_menu_item = "ecoregions" %>

<h2>The ecoregions of Southern Africa (WWF)</h2>

<img src="${request.static_url('tsammalex:static/MapSouthernAfrica01.jpg')}" class="image" alt="MapSouthernAfrica01.jpg" width="1250" height="1004" />

% for description, regions in ecoregions:
    <h3>${description}</h3>
    <dl class="dl-horizontal">
    % for region in regions:
        <dt>
            % if region.species:
            <a href="${request.route_url('parameters', _query=dict(er=region.name))}" title="show related species (${len(region.species)})">${region.id}</a>
            % else:
            ${region.id}
            % endif
        </dt>
        <dd>
            ${region.name}
            ${h.external_link(region.wwf_url(), 'WWF')}
        </dd>
    % endfor
    </dl>
% endfor
