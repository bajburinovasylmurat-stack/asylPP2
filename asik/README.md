# Phantom Lounge Full-Stack

Бұл нұсқа `localStorage` емес, Node.js backend және SQLite база қолданады. Админ концертті, бағаны, афишаны немесе орын статусын өзгертсе, өзгеріс `data/app.db` файлына сақталады және сайтты ашқан барлық қолданушыға ортақ болады.

## Іске қосу

```bash
cd /Users/asylmuratbaiburinov/Desktop/pp2_asyl/asik
node server.js
```

Сайт:

```text
http://localhost:3000
```

Админ панель:

```text
http://localhost:3000/#admin
```

Әдепкі шифр:

```text
phantom2026
```

Шифрды ауыстыру:

```bash
ADMIN_PASSWORD="new-password" node server.js
```

База файлы:

```text
data/app.db
```
