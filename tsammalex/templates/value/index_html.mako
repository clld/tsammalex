<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "values" %>

<%block name="title">Names</%block>
<h2>${title()}</h2>
<p>
    See also
</p>
    <ol>
        <li><a href="${request.route_url('languages')}">Languages</a> > Individual languages > Names (linguistic, cultural and bilingual comparative views), and </li>
        <li><a href="${request.route_url('parameters')}">Species</a> > Individual species (multilingual comparative view)</li>
    </ol>
<div>
    ${ctx.render()}
</div>