// Counts finished games per daily puzzle and returns this player's place ("Rider No.").
// Needs a D1 database bound to the Pages project as DB.
export async function onRequestPost({ request, env }) {
  if (!env.DB) return Response.json({ error: 'no database' }, { status: 503 });
  let num = 0;
  try { num = Number((await request.json()).num); } catch (e) {}
  if (!Number.isInteger(num) || num < 1 || num > 100000) return Response.json({ error: 'bad puzzle' }, { status: 400 });
  await env.DB.prepare('CREATE TABLE IF NOT EXISTS mordle_finishes (num INTEGER PRIMARY KEY, n INTEGER NOT NULL)').run();
  const row = await env.DB.prepare(
    'INSERT INTO mordle_finishes (num, n) VALUES (?1, 1) ON CONFLICT(num) DO UPDATE SET n = n + 1 RETURNING n'
  ).bind(num).first();
  return Response.json({ rider: row ? row.n : null }, { headers: { 'cache-control': 'no-store' } });
}
