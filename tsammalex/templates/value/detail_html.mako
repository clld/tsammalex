<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${ctx.name}</%block>

<%def name="sidebar()">
    % if ctx.valueset.parameter.image_url('web'):
        <%util:well>
            <a href="${request.resource_url(ctx.valueset.parameter)}">
                <img src="${ctx.valueset.parameter.image_url('web')}"/>
            </a>
        </%util:well>
    % endif
</%def>

<div class="pull-right" style="margin-top: 10px">
${h.alt_representations(request, ctx)}
</div>

<h2>${ctx.name}</h2>


<table class="table-nonfluid table">
    ${u.tr_attr(ctx, 'meaning')}
    <tr>
        <td>Language:</td>
        <td>${h.link(request, ctx.valueset.language)}</td>
    </tr>
    <tr>
        <td>Species:</td>
        <td>${h.link(request, ctx.valueset.parameter)}</td>
    </tr>
    ${u.tr_rel(ctx, 'categories')}
    ${u.tr_rel(ctx, 'habitats')}
    ${u.tr_rel(ctx, 'uses', label='Usage')}
    ${u.tr_attr(ctx, 'ipa', 'IPA')}
    % for attr in 'grammatical_info plural_form stem root basic_term literal_translation usage source_language source_form linguistic_notes related_lexemes introduced importance associations ethnobiological_notes comment source original_source'.split():
        ${u.tr_attr(ctx, attr)}
    % endfor
    ${u.tr_attr(ctx, 'references', content=h.linked_references(request, ctx))}
</table>
