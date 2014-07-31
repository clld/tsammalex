<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${ctx.name}</%block>

<h2>${ctx.name}</h2>

<table class="table-nonfluid table">
    <tr>
        <td>Language:</td>
        <td>${h.link(request, ctx.valueset.language)}</td>
    </tr>
    <tr>
        <td>Species:</td>
        <td>${h.link(request, ctx.valueset.parameter)}</td>
    </tr>
    <tr>
        <td>Categories:</td>
        <td>
            <dl class="dl-horizontal">
                % for cat in ctx.valueset.parameter.categories:
                    % if cat.language == ctx.valueset.language:
                        <dt>${cat.name}</dt>
                        <dd>${cat.description or ''}</dd>
                    % endif
                % endfor
            </dl>
        </td>
    </tr>
    <tr>
        <td>References:</td>
        <td>${h.linked_references(request, ctx.valueset)}</td>
    </tr>
</table>
