# Мөлдір Өлең — Backend API

Node.js + Express + SQLite бэкенді.

---

## 🚀 Орнату

```bash
# 1. Жобаны клондаңыз немесе zip-файлды шығарыңыз
cd moldyr-backend

# 2. Тәуелділіктерді орнатыңыз
npm install

# 3. .env файлын жасаңыз
cp .env.example .env
# JWT_SECRET мәнін өзгертіңіз!

# 4. Серверді іске қосыңыз
npm start
# немесе development режимі:
npm run dev
```

Сервер http://localhost:3001 адресінде іске қосылады.

---

## 🔑 Аутентификация

Барлық admin endpoint-тары үшін `Authorization: Bearer <token>` тақырыбы қажет.

### Кіру
```http
POST /api/auth/login
Content-Type: application/json

{ "password": "admin2024" }
```
**Жауап:** `{ "token": "eyJ..." }`

### Құпия сөзді өзгерту (admin)
```http
POST /api/auth/change-password
Authorization: Bearer <token>

{ "newPassword": "жаңа_сөз" }
```

---

## 📅 Айтыстар  `/api/events`

| Метод | URL | Рұқсат | Сипаттама |
|-------|-----|---------|-----------|
| GET | `/api/events` | Жалпы | Барлық айтыстар |
| GET | `/api/events/today` | Жалпы | Бүгінгі айтыс |
| GET | `/api/events/:id` | Жалпы | Бір айтыс |
| POST | `/api/events` | Admin | Жаңа айтыс |
| PUT | `/api/events/:id` | Admin | Айтысты өңдеу |
| PATCH | `/api/events/:id/tickets` | Admin | Билет санын өзгерту |
| DELETE | `/api/events/:id` | Admin | Жою |

### POST /api/events
```json
{
  "date": "2026-05-21",
  "time": "19:00",
  "region1": "Алматы облысы",
  "region2": "Шымкент қаласы",
  "poster": "data:image/jpeg;base64,...",
  "ticketPrice": 3000,
  "totalTickets": 100,
  "remainingTickets": 100,
  "active": true
}
```

### PATCH /api/events/:id/tickets
```json
{ "delta": -1 }
```

---

## 🗳 Дауыстар  `/api/votes`

| Метод | URL | Рұқсат | Сипаттама |
|-------|-----|---------|-----------|
| POST | `/api/votes` | Жалпы | Дауыс беру |
| GET | `/api/votes` | Admin | Барлық дауыс қорытындылары |
| GET | `/api/votes/:eventId` | Admin | Бір айтыстың дауыстары |
| DELETE | `/api/votes/:eventId` | Admin | Дауыстарды тазалау |

### POST /api/votes
```json
{
  "eventId": "айтыс-id",
  "regionChoice": 1,
  "token": "уникалды-токен-200тг-төлем-соңы"
}
```
- `regionChoice`: 1 немесе 2
- `token`: бірегей токен (фронтенд жағынан генерацияланады)
- Дауыс беру тек сол күні белсенді айтыс болса ғана мүмкін
- Бір токен — бір дауыс

---

## 📷 Медиа  `/api/media`

| Метод | URL | Рұқсат |
|-------|-----|---------|
| GET | `/api/media` | Жалпы |
| POST | `/api/media` | Admin |
| PUT | `/api/media/:id` | Admin |
| DELETE | `/api/media/:id` | Admin |

### POST /api/media
```json
{
  "type": "photo",
  "image": "data:image/jpeg;base64,...",
  "caption": "Айтыс кешінен фото",
  "date": "2026-05-21"
}
```
```json
{
  "type": "video",
  "url": "https://youtube.com/watch?v=...",
  "caption": "Финал айтысы",
  "date": "2026-09-16"
}
```

---

## 🤝 Демеушілер  `/api/sponsors`

| Метод | URL | Рұқсат |
|-------|-----|---------|
| GET | `/api/sponsors` | Жалпы |
| POST | `/api/sponsors` | Admin |
| PUT | `/api/sponsors/:id` | Admin |
| DELETE | `/api/sponsors/:id` | Admin |

---

## ⚙️ Баптаулар  `/api/settings`

| Метод | URL | Рұқсат |
|-------|-----|---------|
| GET | `/api/settings/public` | Жалпы |
| GET | `/api/settings` | Admin |
| PUT | `/api/settings` | Admin |

### PUT /api/settings
```json
{
  "whatsapp": "+77016202086",
  "kaspi_link": "https://kaspi.kz/pay",
  "kaspi_merchant": "merchant_id"
}
```

---

## 🗄 Деректер базасы

SQLite (`moldyr.db`) автоматты түрде жасалады. Кестелер:

- `events` — айтыстар
- `votes` — дауыстар
- `media` — фото/видео
- `sponsors` — демеушілер
- `settings` — баптаулар

---

## 🌐 Production (VPS) орналастыру

```bash
# PM2 орнату
npm install -g pm2

# Серверді іске қосу
pm2 start server.js --name moldyr-api

# Автозапуск
pm2 startup
pm2 save
```

Nginx конфигурациясы:
```nginx
location /api {
    proxy_pass http://localhost:3001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 🔒 Қауіпсіздік ескертпелері

1. `.env` ішінде `JWT_SECRET` мәнін міндетті түрде өзгертіңіз
2. `FRONTEND_ORIGIN` мәнін нақты домен атауына қойыңыз
3. Production-да HTTPS пайдаланыңыз
