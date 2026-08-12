# Portfolio — Django

Ikki tilli (o'zbekcha / inglizcha) shaxsiy portfolio sayt. Barcha kontent —
profil, ko'nikmalar, tajriba, loyihalar, blog — admin paneldan tahrirlanadi.

**Texnologiyalar:** Python 3.13 · Django 6.0 · SQLite · WhiteNoise · toza HTML/CSS/JS (CDN yo'q)

---

## Tez boshlash

```powershell
# 1. Virtual muhit (allaqachon yaratilgan bo'lsa, o'tkazib yuboring)
python -m venv .venv

# 2. Paketlar
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Sozlamalar
copy .env.example .env      # keyin .env ichidagi SECRET_KEY ni almashtiring

# 4. Baza
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_portfolio    # namuna ma'lumot

# 5. Admin foydalanuvchi
.\.venv\Scripts\python.exe manage.py createsuperuser

# 6. Ishga tushirish
.\.venv\Scripts\python.exe manage.py runserver
```

Sayt: <http://127.0.0.1:8000/> · Admin: <http://127.0.0.1:8000/admin/>

> Virtual muhitni aktivlashtirib olsangiz (`.\.venv\Scripts\Activate.ps1`),
> shundan keyin oddiy `python manage.py ...` deb yozish mumkin.

---

## Birinchi navbatda nima o'zgartirish kerak

1. `/admin/` ga kiring → **Profil** → ismingiz, kasbingiz, bio, email, havolalar,
   rasm va CV faylini yuklang.
2. **Ko'nikma turkumlari** va **Ko'nikmalar** — o'zingiznikini qo'ying.
3. **Loyihalar** — namuna loyihalarni o'chirib, haqiqiylarini kiriting
   (GitHub havolasi bilan). "Tanlangan" belgisi bosh sahifada ko'rsatadi.
4. **Tajriba** va **Ta'lim** bo'limlarini to'ldiring.
5. **Maqolalar** — o'rgangan mavzularingiz haqida yozing (ixtiyoriy, lekin
   ish beruvchiga juda yaxshi ta'sir qiladi).
6. `.env` dagi `SECRET_KEY` ni yangilang:
   ```powershell
   .\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
   ```

---

## Loyiha tuzilishi

```
config/         sozlamalar va asosiy URL'lar
core/           profil, ko'nikmalar, tajriba, ta'lim, kontakt, bosh sahifa
  i18n.py            ikki tilli maydonlar bilan ishlash
  translations.py    interfeys yozuvlari (uz/en lug'at)
  context_processors.py   profil va tarjimalarni har shablonga uzatadi
  templatetags/      `tr`, `url_for_lang`, `is_active` filtr/teglari
  management/commands/seed_portfolio.py   namuna ma'lumot
projects/       loyihalar va texnologiyalar
blog/           maqolalar
templates/      base.html va sahifa shablonlari
static/         css, js, svg
```

## Manzillar

| URL | Nima |
|---|---|
| `/` | bosh sahifa (o'zbekcha) |
| `/en/` | inglizcha versiya |
| `/projects/`, `/projects/<slug>/` | loyihalar (`?tech=django` bilan filtr) |
| `/blog/`, `/blog/<slug>/` | maqolalar |
| `/api/projects/` | JSON API (`?tech=`, `?featured=1`) |
| `/sitemap.xml`, `/robots.txt` | SEO |
| `/admin/` | boshqaruv paneli |

---

## Ikki tillilik qanday ishlaydi

Django'ning odatiy tarjima tizimi `.po`/`.mo` fayllarga tayanadi, ular esa GNU
gettext dasturini talab qiladi (Windows'da alohida o'rnatish kerak). Shuning
uchun bu loyihada boshqa yo'l tanlangan:

- **Baza kontenti** — har matn uchun ikkita maydon: `title_uz` va `title_en`.
  Shablonda `{{ project|tr:"title" }}` filtri joriy tilga mosini oladi
  (`core/i18n.py` dagi `translated()`).
- **Interfeys yozuvlari** — `core/translations.py` dagi `UI` lug'atida.
  Shablonda `{{ t.nav_projects }}`.
- **Til almashtirish** — `i18n_patterns` va `LocaleMiddleware`. `/` = o'zbekcha,
  `/en/` = inglizcha. Tugma `{% url_for_lang %}` tegi orqali joriy sahifaning
  boshqa tildagi manzilini beradi.

Inglizcha maydon bo'sh qolsa, sayt avtomatik o'zbekchaga qaytadi — ya'ni
hammasini birdan tarjima qilish shart emas.

---

## Testlar

```powershell
.\.venv\Scripts\python.exe manage.py test
```

29 ta test: tarjima yordamchilari, modellar, sahifalar, kontakt formasi
validatsiyasi, JSON API va `seed_portfolio` komandasi.

---

## Produksiyaga chiqarish

`.env` da:

```
DEBUG=False
SECRET_KEY=<uzun tasodifiy qiymat>
ALLOWED_HOSTS=sizningdomen.uz,www.sizningdomen.uz
CSRF_TRUSTED_ORIGINS=https://sizningdomen.uz
```

Keyin:

```bash
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi:application      # Linux hostingda
```

`manage.py check --deploy` bilan xavfsizlik sozlamalarini tekshirib oling.
`DEBUG=False` bo'lganda WhiteNoise statik fayllarni o'zi beradi va HTTPS
qat'iylashtirish sozlamalari yoqiladi (`SECURE_SSL_REDIRECT`, HSTS, secure cookie).

Bepul variantlar: **PythonAnywhere**, **Railway**, **Render**. Jiddiyroq loyiha
uchun SQLite o'rniga PostgreSQL ishlating.

---

## Keyingi qadamlar (o'rganish uchun)

- [ ] Django REST Framework bilan to'liq API + JWT
- [ ] PostgreSQL va Docker Compose
- [ ] Celery + Redis (kontakt xabarlarini fon rejimida yuborish)
- [ ] GitHub Actions'da testlarni avtomatik ishga tushirish
- [ ] `django-debug-toolbar` bilan so'rovlarni tahlil qilish
