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
        <li class="active"><a href="#words" data-toggle="tab">Words</a></li>
        <li><a href="#description" data-toggle="tab">Description</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="words" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, language=ctx).render()}
        </div>
        <div id="description" class="tab-pane">
            <p>${ctx.description or ''}</p>
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