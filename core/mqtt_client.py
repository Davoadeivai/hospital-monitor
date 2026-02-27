"""
MQTT Client - ارتباط با سنسورهای IoT
"""
import json
import logging
import threading
import django
import os

logger = logging.getLogger(__name__)

# ============================================================
# محدوده‌های قابل‌قبول سنسور (مقادیر خارج این محدوده نادیده گرفته می‌شوند)
# ============================================================
SENSOR_BOUNDS = {
    # اتوکلاو
    'temp_c':            (0,    200),    # درجه سانتیگراد
    'pressure':          (0,    10),     # بار
    'power_kw':          (0,    500),    # کیلووات
    'voltage':           (0,    1000),   # ولت
    'current':           (0,    1000),   # آمپر
    'steam_flow':        (0,    100),    # kg/h
    'water_level':       (0,    100),    # درصد
    # زباله‌سوز
    'combustion_temp':   (0,    1600),   # درجه سانتیگراد
    'post_combustion_temp': (0, 1600),
    'exhaust_temp':      (0,    600),
    'co2':               (0,    100000), # ppm
    'co':                (0,    10000),  # ppm
    'nox':               (0,    5000),   # ppm
    'so2':               (0,    5000),   # ppm
    'fuel_flow':         (0,    200),    # L/h
}


def validate_sensor_payload(data: dict) -> tuple[bool, list]:
    """
    بررسی اعتبار داده سنسور
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    for field, (min_val, max_val) in SENSOR_BOUNDS.items():
        value = data.get(field)
        if value is None:
            continue  # فیلد اختیاری است
        if not isinstance(value, (int, float)):
            errors.append(f"{field}: مقدار باید عدد باشد، دریافت شد: {type(value).__name__}")
            continue
        if not (min_val <= value <= max_val):
            errors.append(f"{field}: مقدار {value} خارج از محدوده [{min_val}, {max_val}]")
    return len(errors) == 0, errors


def get_mqtt_client():
    """ساخت و پیکربندی MQTT Client"""
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        logger.warning("paho-mqtt نصب نشده - MQTT غیرفعال")
        return None

    from django.conf import settings

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ به MQTT Broker متصل شد")
            topic = f"{settings.MQTT_TOPIC_PREFIX}/#"
            client.subscribe(topic)
            logger.info(f"Subscribe شد روی: {topic}")
        else:
            logger.error(f"❌ خطا در اتصال MQTT: code={rc}")

    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode('utf-8'))
            handle_sensor_data(payload, message.topic)
        except json.JSONDecodeError as e:
            logger.error(f"خطا در parse MQTT payload: {e}")
        except Exception as e:
            logger.error(f"خطا در پردازش MQTT message: {e}")

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            logger.warning(f"قطع ارتباط MQTT: code={rc}")

    client = mqtt.Client(client_id=f"hospital_monitor_{os.getpid()}")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    if settings.MQTT_USERNAME:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    return client


def handle_sensor_data(data: dict, topic: str):
    """پردازش داده سنسور و ذخیره در دیتابیس"""
    from apps.devices.models import Device, DeviceCycle
    from apps.monitoring.models import SensorReading
    from core.calculators import AlertChecker
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    try:
        device_serial = data.get('device_id') or data.get('serial_number')
        if not device_serial:
            logger.warning(f"داده بدون device_id: {data}")
            return

        # اعتبارسنجی محدوده داده‌های سنسور
        is_valid, errors = validate_sensor_payload(data)
        if not is_valid:
            logger.warning(f"داده نامعتبر از {device_serial} (topic={topic}): {errors}")
            return

        device = Device.objects.get(serial_number=device_serial, is_active=True)

        # پیدا کردن سیکل جاری
        active_cycle = DeviceCycle.objects.filter(
            device=device, status__in=['heating', 'sterilizing', 'cooling']
        ).order_by('-start_time').first()

        # ذخیره داده سنسور
        reading = SensorReading.objects.create(
            device=device,
            cycle=active_cycle,
            power_consumption_kw=data.get('power_kw', 0),
            voltage_v=data.get('voltage', 0),
            current_a=data.get('current', 0),
            # اتوکلاو
            temperature_c=data.get('temp_c'),
            pressure_bar=data.get('pressure'),
            steam_flow_kg_h=data.get('steam_flow'),
            water_level_pct=data.get('water_level'),
            door_locked=data.get('door_locked'),
            # زباله‌سوز
            combustion_temp_c=data.get('combustion_temp'),
            post_combustion_temp_c=data.get('post_combustion_temp'),
            exhaust_temp_c=data.get('exhaust_temp'),
            co2_ppm=data.get('co2'),
            co_ppm=data.get('co'),
            nox_ppm=data.get('nox'),
            so2_ppm=data.get('so2'),
            fuel_flow_lh=data.get('fuel_flow'),
            device_status=data.get('status', 'idle'),
        )

        # به‌روزرسانی وضعیت دستگاه
        device.status = 'online'
        device.save(update_fields=['status'])

        # بررسی هشدار
        AlertChecker.check_reading(reading)

        # ارسال به WebSocket (real-time dashboard)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"device_{device.pk}",
            {
                'type': 'sensor_update',
                'data': {
                    'device_id': device.pk,
                    'timestamp': reading.timestamp.isoformat(),
                    'temperature': reading.temperature_c,
                    'pressure': reading.pressure_bar,
                    'power': reading.power_consumption_kw,
                    'combustion_temp': reading.combustion_temp_c,
                    'co_ppm': reading.co_ppm,
                    'status': reading.device_status,
                }
            }
        )

    except Device.DoesNotExist:
        logger.warning(f"دستگاه با serial {data.get('device_id')} پیدا نشد")
    except Exception as e:
        logger.error(f"خطا در handle_sensor_data: {e}", exc_info=True)


def start_mqtt_listener():
    """شروع MQTT Listener در thread جداگانه"""
    from django.conf import settings

    client = get_mqtt_client()
    if not client:
        return

    try:
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        thread = threading.Thread(target=client.loop_forever, daemon=True)
        thread.start()
        logger.info(f"🚀 MQTT Listener شروع شد - {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
    except Exception as e:
        logger.error(f"خطا در شروع MQTT: {e}")


def simulate_sensor_data(device_id: int, device_type: str = 'autoclave'):
    """
    شبیه‌ساز داده سنسور برای تست (بدون نیاز به سخت‌افزار)
    """
    import random
    from django.utils import timezone

    if device_type == 'autoclave':
        return {
            'device_id': f'DEVICE_{device_id:03d}',
            'timestamp': timezone.now().isoformat(),
            'temp_c': round(121 + random.uniform(-2, 5), 1),
            'pressure': round(1.5 + random.uniform(-0.1, 0.2), 2),
            'power_kw': round(15 + random.uniform(-2, 3), 1),
            'voltage': round(380 + random.uniform(-5, 5), 0),
            'current': round(25 + random.uniform(-2, 2), 1),
            'steam_flow': round(8 + random.uniform(-1, 1), 1),
            'water_level': round(75 + random.uniform(-5, 5), 0),
            'door_locked': True,
            'status': 'sterilizing',
        }
    else:  # incinerator
        return {
            'device_id': f'DEVICE_{device_id:03d}',
            'timestamp': timezone.now().isoformat(),
            'combustion_temp': round(900 + random.uniform(-20, 50), 0),
            'post_combustion_temp': round(950 + random.uniform(-20, 30), 0),
            'exhaust_temp': round(200 + random.uniform(-10, 20), 0),
            'power_kw': round(25 + random.uniform(-3, 5), 1),
            'voltage': 380,
            'current': round(40 + random.uniform(-3, 3), 1),
            'co2': round(5000 + random.uniform(-200, 200), 0),
            'co': round(30 + random.uniform(-10, 10), 0),
            'nox': round(150 + random.uniform(-20, 30), 0),
            'so2': round(50 + random.uniform(-10, 10), 0),
            'fuel_flow': round(8 + random.uniform(-1, 1), 1),
            'status': 'burning',
        }
