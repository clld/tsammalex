<%def name="td_image(image)">
    % if image:
        <% license = u.license_name(image.get_data('permission') or '') %>
        <td width="33%"><br/>
            <img class="image" src="${image.jsondatadict.get('web')}" />&nbsp;
            <br/>
                <span style="font-size: 2.5mm;">
                    ${license}
                    ${'&copy;' if license != 'Public Domain' else 'by'|n}
                    ${image.get_data('creator') or ''}
                </span>
        </td>
    % endif
</%def>
<p style="padding-bottom: -2mm;">
<strong><i><a href="${request.resource_url(ctx.parameter)}">${ctx.parameter.name}</a></i></strong>
% if ctx.parameter.description:
<span style="color: #666;">${ctx.parameter.description}</span>
% endif
${u.names_in_2nd_languages(ctx)|n}.
% if ctx.parameter.characteristics:
    <span>Characteristics: ${ctx.parameter.characteristics}.</span>
% endif
% if ctx.parameter.biotope:
    <span>Biotope: ${ctx.parameter.biotope}.</span>
% endif
% if ctx.parameter.references:
    <span>(${ctx.parameter.formatted_refs(request)|n})</span>
% endif
</p>
<ul style="padding-top: -1mm;">
% for name in ctx.values:
    <li>
    <strong>${name.name}</strong>
    % if name.ipa:
    [${name.ipa}]
    % endif
.
% if name.grammatical_info:
<i>${name.grammatical_info}</i>.
% endif
% if name.meaning:
"${name.meaning}".
% endif
% if name.literal_translation:
Lit. "${name.literal_translation}".
% endif
% if name.usage:
[name.usage].
% endif
% if name.plural_form:
Plural <i>${name.plural_form}</i>.
% endif
% if name.source_language:
From ${name.source_language}
% if name.source_form:
<i>${name.source_form}</i>
% endif
.
% endif
% if name.linguistic_notes:
${name.linguistic_notes}.
% endif
% if name.related_lexemes:
Related words: ${name.related_lexemes}.
% endif
% if name.categories:
Categories: <i>${', '.join(use.name for use in name.categories)}</i>.
% endif
% if name.habitats:
Habitats: <i>${', '.join(use.name for use in name.habitats)}</i>.
% endif
% if name.introduced:
${name.introduced}.
% endif
% if name.uses:
Uses: ${', '.join(use.name for use in name.uses)}.
% endif
% if name.importance:
${name.importance}.
% endif
% if name.associations:
${name.associations}.
% endif
% if name.ethnobiological_notes:
${name.ethnobiological_notes}.
% endif
    </li>
% endfor
</ul>
% if ctx.parameter._files:
    <table width="100%" style="padding-top: -2mm;"><tr>
    % if 'thumbnail' in ''.join(f.name or '' for f in ctx.parameter._files):
        % for tag in ['thumbnail' + str(j + 1) for j in range(3)]:
            ${td_image(ctx.parameter.image(tag=tag))}
        % endfor
    % else:
        % for i in range(3):
            ${td_image(ctx.parameter.image(index=1))}
        % endfor
    % endif
    </tr></table>
% endif
