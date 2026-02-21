# 🏥 HospitalOS Monitor v2.0
پلتفرم مانیتورینگ Real-time اتوکلاو و زباله‌سوز بیمارستانی

**سخت‌افزار پشتیبانی شده:** PLC COTRUST CT Series + HMI FATEK FBTNxx
**پروتکل:** Modbus RTU (RS485) | Modbus TCP (Ethernet)

---

## 🚀 نصب سریع (بدون Docker)

```bash
# ۱. نصب وابستگی‌ها
pip install -r requirements.txt

# ۲. تنظیم محیط
cp .env.example .env
# فایل .env را ویرایش کنید

# ۳. دیتابیس
python manage.py migrate

# ۴. داده‌های نمونه
python manage.py setup_demo

# ۵. اجرا
python manage.py runserver
```

مرورگر: http://localhost:8000 | کاربر: admin | رمز: admin123

---

## 🐳 نصب با Docker

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py setup_demo
```

---

## 🔌 اتصال به PLC COTRUST

### روش ۱: RS485 (کابل مستقیم)

**سخت‌افزار لازم:**
- مبدل USB-RS485 (CH340 — حدود ۲۰۰ هزار تومان)
- کابل Twisted Pair شیلددار ۲ رگ

**سیم‌کشی:**
```
مبدل USB-RS485
    A+ ──────────── A+ ترمینال PLC COTRUST
    B- ──────────── B- ترمینال PLC COTRUST
   GND ──────────── GND پنل برق
```

**تنظیم در Admin پنل:**
```
/admin/devices/device/ → device → connection_type: rtu
serial_port: /dev/ttyUSB0   (Linux) یا COM3 (Windows)
baud_rate: 9600
modbus_slave_id: 1
```

### روش ۲: Ethernet TCP

```
/admin/devices/device/ → device → connection_type: tcp
plc_ip: 192.168.1.100
plc_port: 502
```

### تست اتصال

```
http://localhost:8000/devices/{id}/plc-config/
```
دکمه **"تست اتصال"** — نتیجه real-time نمایش داده می‌شه

---

## 📋 نقشه رجیسترهای Modbus (COTRUST)

در برنامه COTRUST PLC (MagicWorks) این آدرس‌ها را تنظیم کنید:

| آدرس | متغیر PLC | پارامتر | مقیاس |
|------|-----------|---------|-------|
| D0/VW0 | دما | Temperature | × 10 |
| D1/VW2 | فشار | Pressure | × 100 |
| D2/VW4 | جریان بخار | Steam Flow | × 10 |
| D3/VW6 | سطح آب | Water Level | % |
| D4/VW8 | مصرف برق | Power | × 10 |
| D5/VW10 | وضعیت سیکل | 0=Idle..5=Error | — |
| D6/VW12 | وضعیت در | 0=Open 1=Locked | — |
| D7/VW14 | المنت | 0=Off 1=On | — |
| D8/VW16 | پمپ | 0=Off 1=On | — |
| D9/VW18 | شماره سیکل | Cycle Number | — |
| D10/VW20 | کل سیکل‌ها | Total Cycles | — |
| D11/VW22 | کد خطا | Alarm Code | — |

---

## 📡 Polling خودکار

```bash
# شروع polling برای همه دستگاه‌ها
python manage.py start_polling

# فقط یک دستگاه
python manage.py start_polling --device-id 1
```

---

## 🌐 صفحات اصلی

| آدرس | توضیح |
|------|-------|
| `/` | داشبورد اصلی |
| `/monitor/{id}/` | مانیتور Real-time |
| `/devices/` | لیست دستگاه‌ها |
| `/devices/{id}/plc-config/` | تنظیم PLC |
| `/energy/` | آنالیز انرژی |
| `/costs/` | هزینه‌ها |
| `/waste/` | مدیریت زباله |
| `/alerts/` | هشدارها |
| `/reports/monthly/` | گزارش ماهانه |
| `/reports/export/` | خروجی Excel |
| `/admin/` | پنل مدیریت |

---

## 🏗️ معماری سیستم

```
سنسور → PLC COTRUST → RS485/TCP → Python Modbus
                                        ↓
                                   Django + Channels
                                        ↓
                               PostgreSQL + Redis
                                        ↓
                              مرورگر (WebSocket)
```

---

## 📦 تکنولوژی‌ها

- **Backend:** Django 4.2 + DRF + Channels + Celery
- **Database:** PostgreSQL (توسعه: SQLite)
- **Cache/Queue:** Redis
- **PLC:** pymodbus + pyserial
- **IoT:** paho-mqtt
- **Frontend:** Dark Industrial UI (CSS custom)
- **Deploy:** Docker + Nginx + Daphne
