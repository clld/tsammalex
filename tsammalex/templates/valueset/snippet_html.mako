<p style="padding-bottom: -2mm;">
<strong><i>${ctx.parameter.name}</i></strong>
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
    % if 'thumbnail' in ctx.parameter._files[0].name:
        % for tag in ['thumbnail' + str(j + 1) for j in range(3)]:
            <% image = ctx.parameter.image(tag=tag) %>
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
        % endfor
    % else:
        % for i in range(3):
            <% image = ctx.parameter.image(index=i) %>
            % if image_url:
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
        % endfor
    % endif
    </tr></table>
% endif
