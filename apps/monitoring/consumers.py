import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class DeviceConsumer(AsyncWebsocketConsumer):
    """WebSocket Consumer برای مانیتورینگ real-time دستگاه"""

    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.group_name = f'device_{self.device_id}'

        # بررسی احراز هویت
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # ارسال آخرین داده‌ها بلافاصله بعد از اتصال
        latest = await self.get_latest_reading()
        if latest:
            await self.send(text_data=json.dumps({'type': 'initial', 'data': latest}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """دریافت پیام از کلاینت (مثلاً تغییر وضعیت)"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'get_history':
                history = await self.get_reading_history()
                await self.send(text_data=json.dumps({'type': 'history', 'data': history}))

        except json.JSONDecodeError:
            pass

    async def sensor_update(self, event):
        """ارسال داده سنسور جدید به مرورگر"""
        await self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'data': event['data'],
        }))

    async def alert_notification(self, event):
        """ارسال هشدار جدید به مرورگر"""
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': event['data'],
        }))

    @database_sync_to_async
    def get_latest_reading(self):
        from apps.monitoring.models import SensorReading
        try:
            r = SensorReading.objects.filter(device_id=self.device_id).latest('timestamp')
            return {
                'timestamp': r.timestamp.isoformat(),
                'temperature': r.temperature_c,
                'pressure': r.pressure_bar,
                'power': r.power_consumption_kw,
                'combustion_temp': r.combustion_temp_c,
                'co_ppm': r.co_ppm,
                'status': r.device_status,
            }
        except SensorReading.DoesNotExist:
            return None

    @database_sync_to_async
    def get_reading_history(self, limit=60):
        from apps.monitoring.models import SensorReading
        readings = SensorReading.objects.filter(
            device_id=self.device_id
        ).order_by('-timestamp')[:limit]
        return [
            {
                'timestamp': r.timestamp.isoformat(),
                'temperature': r.temperature_c,
                'pressure': r.pressure_bar,
                'power': r.power_consumption_kw,
                'combustion_temp': r.combustion_temp_c,
                'co_ppm': r.co_ppm,
            }
            for r in reversed(list(readings))
        ]


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket Consumer برای داشبورد کلی بیمارستان"""

    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        self.group_name = 'dashboard_all'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def dashboard_update(self, event):
        await self.send(text_data=json.dumps({'type': 'update', 'data': event['data']}))
