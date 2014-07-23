<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name} (${ctx.description})</%block>

##<%block name="head">
##<script src="${request.static_url('tsammalex:static/wwf_terr_ecos_at.json')}"> </script>
##</%block>

% if ctx.family or ctx.genus:
<ul class="breadcrumb">
    % if ctx.family:
    <li class="active">Family: ${ctx.family} <span class="divider">/</span></li>
    % endif
    % if ctx.genus:
    <li class="active">Genus: ${ctx.genus} <span class="divider">/</span></li>
    % endif
    <li class="active">Species: ${ctx.name}</li>
</ul>
% endif

<div style="float: right; margin-top: 10px;">
${h.alt_representations(request, ctx, doc_position='left', exclude=['md.html'])}
</div>

<h2>${ctx.description or ctx.name}</h2>

<%def name="sidebar()">
    <div style="margin-top: 5px;">
    <ul class="inline pull-right">
        % if ctx.eol_url:
            <li>
                <span class="large label label-info">
                    ${h.external_link(ctx.eol_url, 'eol', inverted=True, style="color: white;",)}
                </span>
            </li>
        % endif
        % if ctx.wikipedia_url:
        <li>
            <span class="large label label-info">
                ${h.external_link(ctx.wikipedia_url, 'wikipedia', inverted=True, style="color: white;")}
            </span>
        </li>
        % endif
    </ul>
    </div>
    <h3>Names</h3>
    <div class="well well-small">
        ${request.map.render()}
    </div>
    ${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
</%def>

% for f in filter(lambda f_: f_.name.startswith('small') or f_.name.startswith('large'), ctx._files):
<div class="fluid-row">
    <div class="span7">
    <div class="well">
        <img src="${request.file_url(f)}" class="image"/>
    </div>
        </div>
    <div class="span5">
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
</div>
    <hr/>
% endfor
