# Railway'ga deploy qilish

Loyiha Railway uchun tayyor. Baza (SQLite) va yuklangan rasmlar **Volume**
ichida saqlanadi — shuning uchun deploy qilinganda ma'lumotlar yo'qolmaydi.

Bu qo'llanma bitta Railway akkaunti ichida ikkinchi loyihani (parda shop yonida)
ishga tushirish uchun yozilgan.

---

## 1. Project yaratish

Railway dashboard → **New Project**. Parda shop project'i ichiga qo'shmang:
alohida project bo'lgani ma'qul, shunda domen, o'zgaruvchilar va deploy tarixi
mustaqil bo'ladi.

Kodni yuborishning ikki yo'li bor:

- **GitHub orqali** (tavsiya): repozitoriyani GitHub'ga push qiling, so'ng
  Railway'da *Deploy from GitHub repo*. Keyin har `git push` avtomatik deploy
  bo'ladi.
- **CLI orqali**: `npm i -g @railway/cli`, so'ng `railway login`,
  `railway link`, `railway up`.

## 2. Volume qo'shish (eng muhim qadam)

Service → **Settings → Volumes → New Volume**

- Mount path: `/app/data`

Bu papkada `db.sqlite3` va `media/` yashaydi. Volume'siz deploy qilsangiz,
admin orqali kiritgan hamma narsa keyingi deployda o'chib ketadi.

## 3. Variables

Service → **Variables** bo'limiga quyidagilarni qo'ying:

| Nomi | Qiymati | Izoh |
|---|---|---|
| `SECRET_KEY` | (pastdagi buyruq bilan yarating) | 50+ belgi, majburiy |
| `DEBUG` | `False` | |
| `DATA_DIR` | `/app/data` | Volume mount path bilan bir xil |
| `TRUST_PROXY_IP` | `True` | Railway proxy ortida turadi |
| `SITE_DOMAIN` | `xxx.up.railway.app` | domen olingandan keyin |
| `DEFAULT_FROM_EMAIL` | masalan `portfolio@nurjahon.uz` | |
| `TELEGRAM_BOT_TOKEN` | @BotFather bergan token | kontakt formasi xabari Telegram'ga tushadi |
| `TELEGRAM_CHAT_ID` | raqamli ID (`python manage.py telegram_chat_id`) | `@username` emas, aynan raqam |
| `CONTACT_NOTIFY_EMAIL` | o'z pochtangiz | kontakt formasi xabarlari |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Gmail App Password | bo'sh qolsa xat yuborilmaydi, sayt ishlayveradi |
| `DJANGO_SUPERUSER_USERNAME` | masalan `nurjahon` | birinchi deployda admin yaratiladi |
| `DJANGO_SUPERUSER_PASSWORD` | kuchli parol | admin yaratilgach o'chirib tashlasa ham bo'ladi |
| `DJANGO_SUPERUSER_EMAIL` | pochtangiz | ixtiyoriy |

Kalit yaratish:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k()+k())"
```

`ALLOWED_HOSTS` va `CSRF_TRUSTED_ORIGINS` ni yozish shart emas: Railway bergan
domen kodda avtomatik qo'shiladi (`config/settings.py`). O'z domeningizni
(masalan `nurjahon.uz`) ulasangiz — o'shanda bu ikkovini qo'shasiz:

```
ALLOWED_HOSTS=nurjahon.uz,www.nurjahon.uz
CSRF_TRUSTED_ORIGINS=https://nurjahon.uz,https://www.nurjahon.uz
```

## 4. Domen olish

Service → **Settings → Networking → Generate Domain**.
Port so'rasa `8080` bering (Railway `PORT` o'zgaruvchisini o'zi uzatadi).

## 5. Birinchi ishga tushish — avtomatik

Har deployda `Procfile` quyidagilarni ketma-ket bajaradi:

```
migrate  ->  bootstrap  ->  collectstatic  ->  gunicorn
```

`bootstrap` komandasi (`core/management/commands/bootstrap.py`) faqat birinchi
marta ish qiladi, keyin o'zini o'tkazib yuboradi:

1. `DJANGO_SUPERUSER_*` o'zgaruvchilardan admin yaratadi (agar bazada superuser
   bo'lmasa).
2. `deploy_seed/` papkasidagi kontentni — profil, ko'nikmalar, loyihalar va
   ularning rasmlari/CV faylini — bo'sh bazaga yuklaydi.

Ya'ni deploy tugashi bilan sayt to'ldirilgan holda ochiladi va
`https://<domeningiz>/admin/` ga darrov kira olasiz.

Ish bajarilgani `DATA_DIR/.bootstrapped` fayli bilan belgilanadi. Kontentni
ataylab qayta yuklamoqchi bo'lsangiz — o'sha faylni o'chirasiz yoki
`python manage.py bootstrap --force` chaqirasiz.

### `deploy_seed/` ni yangilash

Lokal bazangizni serverga qayta ko'chirmoqchi bo'lsangiz:

```bash
python manage.py dumpdata core projects blog --exclude core.contactmessage   --indent 2 --natural-foreign --natural-primary -o deploy_seed/data.json
cp -r media/* deploy_seed/media/
```

Diqqat: bu papka **boshlang'ich** kontent uchun. Sayt ishga tushgach, kontentni
serverdagi admin panel orqali tahrirlaysiz — `deploy_seed/` endi tegmaydi.

## 6. Qayta deploy qilish

Kod o'zgargandan keyin:

```bash
git add -A && git commit -m "..." && git push
RAILWAY_TOKEN=<project token> railway up -s portfolio --ci
```

GitHub'ni Railway'ga ulasangiz (dashboard → service → Settings → Source →
Connect Repo), `railway up` ham kerak bo'lmaydi: har `git push` o'zi deploy
bo'ladi. Buni project token bilan qilib bo'lmaydi, dashboarddan bosasiz.

## 7. Xarajatni kamaytirish

Portfolio saytiga tashrif kam bo'ladi, shuning uchun
Service → **Settings → Serverless (App Sleeping)** ni yoqing. Hech kim
kirmaganda service uxlaydi va $5 lik kreditdan deyarli yemaydi.

---

## Nima o'zgargani (kod tomoni)

- `config/settings.py` — `DATA_DIR` o'zgaruvchisi: baza va media doimiy diskka
  ko'chdi; Railway domeni `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` ga avtomatik
  qo'shiladi.
- `config/urls.py` — yuklangan rasmlar produksiyada ham beriladi.
- `Procfile` — deployda `migrate` + `collectstatic`, so'ng gunicorn.
- `.python-version` — Python 3.13 (Django 6 uchun kerak).
- `.railwayignore` — serverga yuborilmaydigan fayllar (`.env`, lokal baza, `media/`).
- `core/management/commands/bootstrap.py` — birinchi ishga tushishda admin va
  boshlang'ich kontentni tayyorlaydi.
- `deploy_seed/` — lokal bazadan olingan boshlang'ich kontent va media fayllar.

Lokal ishlash o'zgarmadi: `.env` da `DATA_DIR` bo'sh bo'lsa, baza va media
avvalgidek loyiha papkasida qoladi.
