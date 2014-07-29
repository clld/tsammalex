<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
</%block>

<%block name="title">${_('Parameters')}</%block>
<div class="pull-right well well-small">
    <form>
        <fieldset>
            <p>
                Select up to 2 languages for which to display common names of species:
            </p>
            ${select.render()}
            <button class="btn" type="submit">Submit</button>
        </fieldset>
    </form>
</div>
<h2>${title()}</h2>

<div>
    ${ctx.render()}
</div>