const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { DatabaseSync } = require('node:sqlite');

const PORT = Number(process.env.PORT || 3000);
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'phantom2026';
const ROOT = __dirname;
const PUBLIC_DIR = path.join(ROOT, 'public');
const DATA_DIR = path.join(ROOT, 'data');
const DB_PATH = path.join(DATA_DIR, 'app.db');

fs.mkdirSync(DATA_DIR, { recursive: true });

const db = new DatabaseSync(DB_PATH);
const sessions = new Map();

const TABLE_LAYOUT_72 = [
  {id:1,x:145,y:772,w:38,h:28},{id:2,x:181,y:772,w:38,h:28},{id:3,x:145,y:745,w:38,h:28},{id:4,x:181,y:745,w:38,h:28},
  {id:5,x:270,y:726,w:38,h:28},{id:6,x:270,y:700,w:38,h:28},{id:7,x:145,y:707,w:38,h:28},{id:8,x:181,y:707,w:38,h:28},
  {id:9,x:145,y:680,w:38,h:28},{id:10,x:181,y:680,w:38,h:28},{id:11,x:233,y:726,w:38,h:28},{id:12,x:233,y:700,w:38,h:28},
  {id:13,x:350,y:610,w:38,h:28},{id:14,x:350,y:637,w:38,h:28},{id:15,x:386,y:610,w:38,h:28},{id:16,x:386,y:637,w:38,h:28},
  {id:17,x:460,y:610,w:38,h:28},{id:18,x:460,y:637,w:38,h:28},{id:19,x:496,y:610,w:38,h:28},{id:20,x:496,y:637,w:38,h:28},
  {id:21,x:574,y:610,w:38,h:28},{id:22,x:574,y:637,w:38,h:28},{id:23,x:610,y:610,w:38,h:28},{id:24,x:610,y:637,w:38,h:28},
  {id:25,x:181,y:637,w:38,h:28},{id:26,x:181,y:610,w:38,h:28},{id:27,x:240,y:520,w:38,h:28},{id:28,x:240,y:548,w:38,h:28},
  {id:29,x:277,y:520,w:38,h:28},{id:30,x:277,y:548,w:38,h:28},{id:31,x:350,y:520,w:38,h:28},{id:32,x:350,y:548,w:38,h:28},
  {id:33,x:386,y:520,w:38,h:28},{id:34,x:386,y:548,w:38,h:28},{id:35,x:460,y:520,w:38,h:28},{id:36,x:460,y:548,w:38,h:28},
  {id:37,x:496,y:520,w:38,h:28},{id:38,x:496,y:548,w:38,h:28},{id:39,x:574,y:520,w:38,h:28},{id:40,x:574,y:548,w:38,h:28},
  {id:41,x:610,y:520,w:38,h:28},{id:42,x:610,y:548,w:38,h:28},{id:43,x:185,y:405,w:38,h:28},{id:44,x:185,y:432,w:38,h:28},
  {id:45,x:222,y:405,w:38,h:28},{id:46,x:222,y:432,w:38,h:28},{id:47,x:350,y:405,w:38,h:28},{id:48,x:350,y:433,w:38,h:28},
  {id:49,x:386,y:405,w:38,h:28},{id:50,x:386,y:433,w:38,h:28},{id:51,x:460,y:405,w:38,h:28},{id:52,x:460,y:433,w:38,h:28},
  {id:53,x:496,y:405,w:38,h:28},{id:54,x:496,y:433,w:38,h:28},{id:55,x:574,y:405,w:38,h:28},{id:56,x:574,y:433,w:38,h:28},
  {id:57,x:610,y:405,w:38,h:28},{id:58,x:610,y:433,w:38,h:28},{id:59,x:200,y:280,w:38,h:28},{id:60,x:200,y:310,w:38,h:28},
  {id:61,x:350,y:280,w:38,h:28},{id:62,x:350,y:312,w:38,h:28},{id:63,x:386,y:280,w:38,h:28},{id:64,x:386,y:312,w:38,h:28},
  {id:65,x:460,y:280,w:38,h:28},{id:66,x:460,y:312,w:38,h:28},{id:67,x:496,y:280,w:38,h:28},{id:68,x:496,y:312,w:38,h:28},
  {id:69,x:574,y:280,w:38,h:28},{id:70,x:574,y:312,w:38,h:28},{id:71,x:610,y:280,w:38,h:28},{id:72,x:610,y:312,w:38,h:28}
];
const TABLE_LAYOUT_84 = [
  ...TABLE_LAYOUT_72,
  {id:73,x:350,y:200,w:38,h:28},{id:74,x:350,y:231,w:38,h:28},{id:75,x:386,y:200,w:38,h:28},{id:76,x:386,y:231,w:38,h:28},
  {id:77,x:460,y:200,w:38,h:28},{id:78,x:460,y:231,w:38,h:28},{id:79,x:496,y:200,w:38,h:28},{id:80,x:496,y:231,w:38,h:28},
  {id:81,x:574,y:200,w:38,h:28},{id:82,x:574,y:231,w:38,h:28},{id:83,x:610,y:200,w:38,h:28},{id:84,x:610,y:231,w:38,h:28}
];



db.exec(`
  CREATE TABLE IF NOT EXISTS concerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    artist TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    poster TEXT,
    desc TEXT,
    tag TEXT,
    layout TEXT NOT NULL DEFAULT 'medium',
    price INTEGER NOT NULL DEFAULT 0,
    priceRules TEXT,
    kaspiNum TEXT,
    kaspiLink TEXT,
    waNum TEXT,
    visible INTEGER NOT NULL DEFAULT 1,
    createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE IF NOT EXISTS seats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concertId INTEGER NOT NULL,
    seatId TEXT NOT NULL,
    price INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'free',
    isVIP INTEGER NOT NULL DEFAULT 0,
    UNIQUE(concertId, seatId),
    FOREIGN KEY(concertId) REFERENCES concerts(id) ON DELETE CASCADE
  );
`);

function parsePriceRules(text) {
  const rules = [];
  String(text || '').split(/\n|;/).forEach(line => {
    const clean = line.trim();
    if (!clean) return;
    const range = clean.match(/(\d+)\s*(?:-|–|—)\s*(\d+)/) || clean.match(/\b(\d+)\b/);
    const numbers = clean.match(/\d[\d\s]*/g) || [];
    if (!range || !numbers.length) return;
    const start = Number(range[1]);
    const end = Number(range[2] || range[1]);
    let priceNumber = null;
    if (/[:=]/.test(clean)) {
      const after = clean.split(/[:=]/).slice(1).join(':');
      const priceMatch = after.match(/\d[\d\s]*/);
      if (priceMatch) priceNumber = Number(priceMatch[0].replace(/\s/g, ''));
    }
    if (start && end && priceNumber) rules.push({ start: Math.min(start, end), end: Math.max(start, end), price: priceNumber });
  });
  return rules;
}

function priceForSeatId(id, basePrice, priceRules) {
  const rule = parsePriceRules(priceRules).find(r => Number(id) >= r.start && Number(id) <= r.end);
  return rule ? rule.price : Number(basePrice || 0);
}

function getLayoutTable(layout) {
  return layout === 'large84' ? TABLE_LAYOUT_84 : TABLE_LAYOUT_72;
}

function createSeats(concertId, layout, price, priceRules) {
  const insertSeat = db.prepare('INSERT INTO seats (concertId, seatId, price, status, isVIP) VALUES (?, ?, ?, ?, ?)');
  for (const item of getLayoutTable(layout)) {
    insertSeat.run(concertId, String(item.id), priceForSeatId(item.id, price, priceRules), 'free', 0);
  }
}

function ensureSeedData() {
  const count = db.prepare('SELECT COUNT(*) AS count FROM concerts').get().count;
  if (count) return;
  const insert = db.prepare(`
    INSERT INTO concerts (name, artist, date, time, poster, desc, tag, layout, price, priceRules, kaspiNum, kaspiLink, waNum, visible)
    VALUES (@name, @artist, @date, @time, @poster, @desc, @tag, @layout, @price, @priceRules, @kaspiNum, @kaspiLink, @waNum, @visible)
  `);
  for (const concert of DEFAULT_CONCERTS) {
    const result = insert.run(concert);
    createSeats(Number(result.lastInsertRowid), concert.layout, concert.price, concert.priceRules);
  }
}
const DEFAULT_CONCERTS = [
  {id:1,name:'Dimash Qudaibergen - Live',artist:'Dimash Qudaibergen',date:'2026-08-15',time:'20:00',poster:'',desc:'Әлемге танымал қазақстандық әнші Димаш Құдайбергеннің Алматыдағы концерт кеші.',tag:'Хит',layout:'large',price:8000,vipPrice:25000,kaspiNum:'+7 707 000 00 01',kaspiLink:'',waNum:'77070000001',visible:true,seats:[]},
  {id:2,name:'Jazz Night - Phantom Sessions',artist:'Phantom Lounge All-Stars',date:'2026-07-20',time:'21:00',poster:'',desc:'Phantom Lounge атмосферасындағы тірі джаз кеші.',tag:'Жаңа',layout:'medium',price:5000,vipPrice:12000,kaspiNum:'+7 707 000 00 01',kaspiLink:'',waNum:'77070000001',visible:true,seats:[]},
  {id:3,name:'Deep House Party',artist:'DJ Resident + Guest',date:'2026-07-06',time:'23:00',poster:'',desc:'Deep house және tech house кеші.',tag:'',layout:'small',price:3500,vipPrice:8000,kaspiNum:'+7 707 000 00 01',kaspiLink:'',waNum:'77070000001',visible:true,seats:[]}
];

ensureSeedData();

function allConcerts(includeHidden) {
  const concerts = db.prepare(`SELECT * FROM concerts ${includeHidden ? '' : 'WHERE visible = 1'} ORDER BY date ASC, time ASC`).all();
  const seatsStmt = db.prepare('SELECT seatId AS id, price, status, isVIP FROM seats WHERE concertId = ? ORDER BY CAST(seatId AS INTEGER)');
  return concerts.map(c => ({
    ...c,
    visible: Boolean(c.visible),
    vipPrice: c.price,
    seats: seatsStmt.all(c.id).map(s => ({ ...s, id: String(s.id), isVIP: Boolean(s.isVIP) }))
  }));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 8_000_000) {
        reject(new Error('Payload too large'));
        req.destroy();
      }
    });
    req.on('end', () => {
      if (!body) return resolve({});
      try { resolve(JSON.parse(body)); }
      catch { reject(new Error('Invalid JSON')); }
    });
    req.on('error', reject);
  });
}

function send(res, status, payload, headers = {}) {
  const data = JSON.stringify(payload);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': Buffer.byteLength(data), ...headers });
  res.end(data);
}

function sendError(res, status, message) {
  send(res, status, { error: message });
}

function requireAuth(req, res) {
  const auth = req.headers['authorization'] || '';
  const token = auth.replace('Bearer ', '').trim();
  if (!token || !sessions.has(token)) {
    sendError(res, 401, 'Unauthorized');
    return false;
  }
  return true;
}

function safePath(urlPath) {
  const requested = decodeURIComponent(urlPath === '/' ? '/index.html' : urlPath);
  const file = path.normalize(path.join(PUBLIC_DIR, requested));
  return file.startsWith(PUBLIC_DIR) ? file : null;
}

function serveStatic(req, res, pathname) {
  const file = safePath(pathname);
  if (!file || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }
  const ext = path.extname(file).toLowerCase();
  const type = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml'
  }[ext] || 'application/octet-stream';
  res.writeHead(200, { 'Content-Type': type });
  fs.createReadStream(file).pipe(res);
}

function cleanConcertPayload(body) {
  return {
    name: String(body.name || '').trim(),
    artist: String(body.artist || '').trim(),
    date: String(body.date || '').trim(),
    time: String(body.time || '20:00').trim(),
    poster: String(body.poster || '').trim(),
    desc: String(body.desc || '').trim(),
    tag: String(body.tag || '').trim(),
    layout: body.layout === 'large84' ? 'large84' : 'medium',
    price: Number(body.price || 0),
    priceRules: String(body.priceRules || '').trim(),
    kaspiNum: String(body.kaspiNum || '').trim(),
    kaspiLink: String(body.kaspiLink || '').trim(),
    waNum: String(body.waNum || body.kaspiNum || '').replace(/\D/g, ''),
    visible: body.visible === undefined ? 1 : (body.visible ? 1 : 0)
  };
}

async function handleApi(req, res, pathname) {
  try {
    if (req.method === 'GET' && pathname === '/api/concerts') {
      send(res, 200, { concerts: allConcerts(false) });
      return;
    }
    if (req.method === 'GET' && pathname === '/api/admin/concerts') {
      if (!requireAuth(req, res)) return;
      send(res, 200, { concerts: allConcerts(true) });
      return;
    }
    if (req.method === 'POST' && pathname === '/api/admin/login') {
      const body = await readBody(req);
      if (String(body.password || '') !== ADMIN_PASSWORD) {
        sendError(res, 401, 'Қате пароль');
        return;
      }
      const token = crypto.randomBytes(24).toString('hex');
      sessions.set(token, Date.now());
      send(res, 200, { token });
      return;
    }
    if (req.method === 'POST' && pathname === '/api/admin/concerts') {
      if (!requireAuth(req, res)) return;
      const c = cleanConcertPayload(await readBody(req));
      if (!c.name || !c.date || !c.price) {
        sendError(res, 400, 'Name, date and price are required');
        return;
      }
      const result = db.prepare(`
        INSERT INTO concerts (name, artist, date, time, poster, desc, tag, layout, price, priceRules, kaspiNum, kaspiLink, waNum, visible, updatedAt)
        VALUES (@name, @artist, @date, @time, @poster, @desc, @tag, @layout, @price, @priceRules, @kaspiNum, @kaspiLink, @waNum, @visible, CURRENT_TIMESTAMP)
      `).run(c);
      createSeats(Number(result.lastInsertRowid), c.layout, c.price, c.priceRules);
      send(res, 201, { concerts: allConcerts(true) });
      return;
    }
    const concertMatch = pathname.match(/^\/api\/admin\/concerts\/(\d+)$/);
    if (concertMatch && req.method === 'PUT') {
      if (!requireAuth(req, res)) return;
      const id = Number(concertMatch[1]);
      const old = db.prepare('SELECT * FROM concerts WHERE id = ?').get(id);
      if (!old) return sendError(res, 404, 'Concert not found');
      const c = cleanConcertPayload({ ...old, ...(await readBody(req)) });
      db.prepare(`
        UPDATE concerts SET name=@name, artist=@artist, date=@date, time=@time, poster=@poster, desc=@desc, tag=@tag,
        layout=@layout, price=@price, priceRules=@priceRules, kaspiNum=@kaspiNum, kaspiLink=@kaspiLink, waNum=@waNum,
        visible=@visible, updatedAt=CURRENT_TIMESTAMP WHERE id=@id
      `).run({ ...c, id });
      if (old.layout !== c.layout) {
        db.prepare('DELETE FROM seats WHERE concertId = ?').run(id);
        createSeats(id, c.layout, c.price, c.priceRules);
      } else if (old.price !== c.price || old.priceRules !== c.priceRules) {
        const seats = db.prepare('SELECT seatId FROM seats WHERE concertId = ?').all(id);
        const updateSeat = db.prepare('UPDATE seats SET price = ? WHERE concertId = ? AND seatId = ?');
        seats.forEach(s => updateSeat.run(priceForSeatId(s.seatId, c.price, c.priceRules), id, s.seatId));
      }
      send(res, 200, { concerts: allConcerts(true) });
      return;
    }
    if (concertMatch && req.method === 'DELETE') {
      if (!requireAuth(req, res)) return;
      const id = Number(concertMatch[1]);
      db.prepare('DELETE FROM seats WHERE concertId = ?').run(id);
      db.prepare('DELETE FROM concerts WHERE id = ?').run(id);
      send(res, 200, { concerts: allConcerts(true) });
      return;
    }
    const visibleMatch = pathname.match(/^\/api\/admin\/concerts\/(\d+)\/visible$/);
    if (visibleMatch && req.method === 'PATCH') {
      if (!requireAuth(req, res)) return;
      const id = Number(visibleMatch[1]);
      const c = db.prepare('SELECT visible FROM concerts WHERE id = ?').get(id);
      if (!c) return sendError(res, 404, 'Concert not found');
      db.prepare('UPDATE concerts SET visible = ?, updatedAt = CURRENT_TIMESTAMP WHERE id = ?').run(c.visible ? 0 : 1, id);
      send(res, 200, { concerts: allConcerts(true) });
      return;
    }
    const seatMatch = pathname.match(/^\/api\/admin\/concerts\/(\d+)\/seats\/([^/]+)$/);
    if (seatMatch && req.method === 'PATCH') {
      if (!requireAuth(req, res)) return;
      const concertId = Number(seatMatch[1]);
      const seatId = decodeURIComponent(seatMatch[2]);
      const seat = db.prepare('SELECT status FROM seats WHERE concertId = ? AND seatId = ?').get(concertId, seatId);
      if (!seat) return sendError(res, 404, 'Seat not found');
      db.prepare('UPDATE seats SET status = ? WHERE concertId = ? AND seatId = ?').run(seat.status === 'taken' ? 'free' : 'taken', concertId, seatId);
      db.prepare('UPDATE concerts SET updatedAt = CURRENT_TIMESTAMP WHERE id = ?').run(concertId);
      send(res, 200, { concerts: allConcerts(true) });
      return;
    }
    const seatsBulkMatch = pathname.match(/^\/api\/admin\/concerts\/(\d+)\/seats$/);
    if (seatsBulkMatch && req.method === 'PUT') {
      if (!requireAuth(req, res)) return;
      const concertId = Number(seatsBulkMatch[1]);
      const body = await readBody(req);
      const status = body.status === 'taken' ? 'taken' : 'free';
      db.prepare('UPDATE seats SET status = ? WHERE concertId = ?').run(status, concertId);
      db.prepare('UPDATE concerts SET updatedAt = CURRENT_TIMESTAMP WHERE id = ?').run(concertId);
      send(res, 200, { concerts: allConcerts(true) });
      return;
    }
    sendError(res, 404, 'API route not found');
  } catch (err) {
    console.error(err);
    sendError(res, 500, err.message || 'Server error');
  }
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname.startsWith('/api/')) {
    handleApi(req, res, url.pathname);
    return;
  }
  serveStatic(req, res, url.pathname);
});

server.listen(PORT, () => {
  console.log(`Phantom Lounge server: http://localhost:${PORT}`);
  console.log(`Admin password: ${ADMIN_PASSWORD}`);
});