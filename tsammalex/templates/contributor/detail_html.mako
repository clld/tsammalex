<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>


<h2>${ctx.last_first()}</h2>

% if ctx.sections:
    <p>${ctx.sections}</p>
% endif

% if ctx.description:
    <p>${ctx.description}</p>
% endif

<dl>
    % if ctx.address:
        <dt>${_('Address')}:</dt>
        <dd>
            <address>
                ${h.text2html(ctx.address)|n}
            </address>
        </dd>
    % endif
    % if ctx.url:
        <dt>${_('Web:')}</dt>
        <dd>${h.external_link(ctx.url)}</dd>
    % endif
    % if ctx.email:
        <dt>${_('Mail:')}</dt>
        <dd>${ctx.email.replace('@', '[at]')}</dd>
    % endif
    ${util.data(ctx, with_dl=False)}
</dl>

<h3>${_('Contributions')}</h3>
<ul>
    % for c in ctx.contribution_assocs:
        <li>${h.link(request, c.contribution.language)}</li>
    % endfor
</ul>
