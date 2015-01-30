<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

${util.codes()}

<h2>${_('Language')} ${ctx.name}</h2>
<div style="float: right;">
${h.alt_representations(request, ctx, doc_position='left', exclude=['md.html'])}
</div>
<div class="tabbable">
    <ul class="nav nav-tabs">
        <li><a href="#description" data-toggle="tab">Description</a></li>
        <li class="active"><a href="#names" data-toggle="tab">Names (linguistic view)</a></li>
        <li><a href="#cultural" data-toggle="tab">Names (cultural view)</a></li>
        ##<li><a href="#species" data-toggle="tab">Species (bilingual comparative view)</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="description" class="tab-pane">
            <p>${ctx.description or ''}</p>
            <h4>Classification</h4>
            <dl>
                <dt>Lineage</dt>
                <dd>
                    ${ctx.lineage.name}
                    % if ctx.lineage.glottocode:
                        ${h.external_link(h.glottolog_url(ctx.lineage.glottocode),
                        label=ctx.lineage.glottocode)}
                    % endif
                </dd>
                % if ctx.lineage.family:
                    <dt>Family</dt>
                    <dd>
                        ${ctx.lineage.family}
                    % if ctx.lineage.family_glottocode:
                        ${h.external_link(h.glottolog_url(ctx.lineage.family_glottocode),
                        label=ctx.lineage.family_glottocode)}
                    % endif
                    </dd>
                % endif
            </dl>
            % if ctx.second_languages:
                <h4>Link Languages</h4>
                <ul class="unstyled">
                    % for l in ctx.second_languages:
                <li>${h.link(request, l)}</li>
                    % endfor
                </ul>
            % endif
            % if categories:
                <h4>Categories</h4>
                <dl class="dl-horizontal">
                    % for cat in categories:
                        <dt>${cat.name}</dt>
                        <dd>${cat.description or ''}</dd>
                    % endfor
                </dl>
            % endif
        </div>
        <div id="names" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, language=ctx).render()}
        </div>
        <div id="cultural" class="tab-pane">
            ${request.get_datatable('values', h.models.Value, language=ctx, type='cultural').render()}
        </div>
        ##<div id="species" class="tab-pane">
        ##    ${request.get_datatable('values', h.models.Value, language=ctx).render()}
        ##</div>
    </div>
    <script>
$(document).ready(function() {
    if (location.hash !== '') {
        $('a[href="#' + location.hash.substr(2) + '"]').tab('show');
    }
    return $('a[data-toggle="tab"]').on('shown', function(e) {
        return location.hash = 't' + $(e.target).attr('href').substr(1);
    });
});
    </script>
</div>