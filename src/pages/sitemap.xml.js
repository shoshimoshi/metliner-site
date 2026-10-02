// Sitemap with language alternates and one map image per city page.
import geo from '../data/geo.json';
import cities from '../data/cities.json';

const SITE = 'https://www.metliner.com';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function GET() {
  const paths = [{ p: '/' }, { p: '/maps/' }, { p: '/about-us/' }, { p: '/contact-us/' }];
  for (const [ck, c] of Object.entries(geo)) {
    paths.push({ p: `/maps/${ck}/` });
    for (const [nk, n] of Object.entries(c.countries || {})) {
      paths.push({ p: `/maps/${ck}/${nk}/` });
      for (const slug of n.cities || []) {
        const city = cities[slug];
        if (!city) continue;
        paths.push({ p: `/maps/${ck}/${nk}/${slug}/`, city });
      }
    }
  }
  const langs = [['english', 'en'], ['zh', 'zh-Hant']];
  let out = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n';
  for (const { p, city } of paths) {
    for (const [dir] of langs) {
      out += `  <url>\n    <loc>${SITE}/${dir}${p}</loc>\n`;
      for (const [d2, code] of langs) out += `    <xhtml:link rel="alternate" hreflang="${code}" href="${SITE}/${d2}${p}"/>\n`;
      out += `    <xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/english${p}"/>\n`;
      if (city) out += `    <image:image><image:loc>${esc(SITE + (city.map.hero || city.map.thumb))}</image:loc></image:image>\n`;
      out += '  </url>\n';
    }
  }
  out += '</urlset>\n';
  return new Response(out, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
