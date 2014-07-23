<%inherit file="../tsammalex.mako"/>
<%! active_menu_item = "ecoregions" %>

<h2>WWF's Terrestrial Ecoregions of the Afrotropics</h2>
<p>
    Data on ecoregions is taken from the World Wildlife Fund's <i>Terrestrial Ecoregions of the World</i>
    version 2.0 from 2004. Ecoregion borders have been simplified using the modified Visvalingam
    algorithm implemented in ${h.external_link('http://mapshaper.org', label='mapshaper')},
    to allow for better rendering performance.
</p>
<blockquote>
    Olson, D.M., E. Dinerstein, E.D. Wikramanayake, N.D. Burgess, G.V.N. Powell, E.C. Underwood,
    J.A. D'Amico, I. Itoua, H.E. Strand, J.C. Morrison, C.J. Loucks, T.F. Allnutt, T.H. Ricketts,
    Y. Kura, J.F. Lamoreux, W.W. Wettengel, P. Hedao, and K.R. Kassem.
    Terrestrial Ecoregions of the World: A New Map of Life on Earth (PDF, 1.1M) BioScience 51:933-938.
</blockquote>

${request.map.render()}

${ctx.render()}
