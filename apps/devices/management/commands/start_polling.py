"""
python manage.py start_polling

شروع خودکار polling برای تمام دستگاه‌های فعال
معمولاً در startup سرور اجرا می‌شه
"""
import time
import signal
import logging
from django.core.management.base import BaseCommand
from apps.devices.models import Device

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'شروع polling برای دستگاه‌های فعال'

    def add_arguments(self, parser):
        parser.add_argument('--device-id', type=int, help='فقط یک دستگاه خاص')

    def handle(self, *args, **options):
        from core.plc_driver import start_polling, stop_polling, get_all_pollers

        devices = Device.objects.filter(is_active=True)
        if options['device_id']:
            devices = devices.filter(pk=options['device_id'])

        self.stdout.write(f'\n🔌 شروع polling برای {devices.count()} دستگاه...\n')

        for device in devices:
            poller = start_polling(device)
            icon = '📡' if device.connection_type == 'rtu' else '🌐' if device.connection_type == 'tcp' else '🎮'
            self.stdout.write(
                f'  {icon} {device.name} ({device.serial_number}) — {device.get_connection_type_display()}\n'
            )

        self.stdout.write('\n✅ همه دستگاه‌ها در حال polling هستند\n')
        self.stdout.write('Ctrl+C برای توقف\n\n')

        def handle_signal(sig, frame):
            self.stdout.write('\n⏹ توقف polling...')
            for device in devices:
                stop_polling(device.pk)
            exit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        # Keep alive
        while True:
            pollers = get_all_pollers()
            active = len(pollers)
            self.stdout.write(f'\r  {active} دستگاه در حال polling  ', ending='')
            time.sleep(10)
