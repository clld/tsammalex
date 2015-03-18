<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "images" %>
<%block name="title">Image ${ctx.id}</%block>

<h2>Image ${ctx.id}</h2>

<div class="row-fluid" id="images">
    <div class="span6">
        <div class="well" style="text-align: center;">
            <a href="${ctx.jsondata.get('url')}" title="view image">
                <img src="${ctx.jsondata.get('web')}" class="image"/>
            </a>
        </div>
    </div>
    <div class="span6">
        <table class="table table-condensed">
            <tbody>
                <tr>
                    <td>Taxon:</td>
                    <td>${h.link(request, ctx.object)}</td>
                </tr>
                % for attr in 'source date place creator permission comments'.split():
                    <% value = ctx.get_data(attr) %>
                    % if value:
                        <tr>
                            <td>${attr.capitalize()}:</td>
                            <td>
                                    % if attr == 'permission':
                                      ${h.maybe_license_link(request, value, button='small')}
                                    % elif attr == 'source':
                                      ${h.maybe_external_link(value)}
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
