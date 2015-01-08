<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${ctx.name} (${ctx.english_name})</%block>

<% dt = request.get_datatable('values', h.models.Value, parameter=ctx) %>
<div style="float: right; margin-top: 10px;">
    ${h.alt_representations(request, ctx, doc_position='left', exclude=['md.html'])}
</div>

<h2>${ctx.description or ctx.name}</h2>

<div class="row-fluid">
    <div class="span6">
<ul class="nav nav-pills">
    <li class="active"><a href="#map-container"><span class="icon-globe"> </span> Map</a></li>
    % if ctx._files:
        <li class="active"><a href="#images"><span class="icon-camera"> </span> Pictures</a></li>
    % endif
    <li class="active"><a href="#names"><span class="icon-list"> </span> Names</a></li>
</ul>
<table class="table table-condensed table-nonfluid">
    <tbody>
        <tr>
            <td>Biological classification:</td>
            <td>${u.format_classification(ctx, with_species=True, with_rank=True)|n}</td>
        </tr>
        ${u.tr_attr(ctx, 'characteristics')}
        ${u.tr_rel(ctx, 'countries', dt='id', dd='name')}
        ${u.tr_rel(ctx, 'ecoregions', dt='id', dd='name')}
        <tr>
            <td>Links:</td>
            <td>
                <ul class="inline">
                    % for url, label, title in ctx.link_specs:
                        <li>
                            <span class="large label label-info">
                                ${h.external_link(url, label, title=title, inverted=True, style="color: white;",)}
                            </span>
                        </li>
                    % endfor
                </ul>
            </td>
        </tr>
        ${u.tr_attr(ctx, 'references', content=h.linked_references(request, ctx))}
    </tbody>
</table>
    </div>
    <div class="span6">
        ${request.get_map('parameter', col='lineage', dt=dt).render()}
    </div>
</div>

% for chunk in [ctx._files[i:i + 3] for i in range(0, len(ctx._files), 3)]:
<div class="row-fluid" id="images">
    % for f in chunk:
        <div class="span4">
            <div class="well">
                <a href="${f.jsondatadict.get('url')}" title="view image">
                    <img src="${f.jsondatadict.get('web')}" class="image"/>
                </a>
            </div>
            <table class="table table-condensed">
                <tbody>
                    % for attr in 'source date place author permission comments'.split():
                        % if f.jsondata.get(attr):
                            <% value = f.jsondata[attr] %>
                            <tr>
                                <td>${attr.capitalize()}:</td>
                                <td>
                                    % if attr == 'permission':
                                        % if value.get('license'):
                                        ${h.external_link(value['license'][0], value['license'][1])}
                                        % endif
                                    % elif attr == 'source':
                                        ${value|n}
                                    % else:
                                        ${value}
                                    % endif
                                </td>
                            </tr>
                        % endif
                    % endfor
                </tbody>
            </table>
        </div>
    % endfor
</div>
    <hr/>
% endfor

<div id="names">
${dt.render()}
</div>