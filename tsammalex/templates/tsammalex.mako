<%inherit file="app.mako"/>

<%block name="brand">
    <a class="brand" href="${request.route_url('dataset')}"
       style="padding-top: 7px; padding-bottom: 2px;">
        <img src="${request.static_url('tsammalex:static/tsamma.png')}"/>
        Tsammalex
    </a>
</%block>

${next.body()}
