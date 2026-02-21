"""
============================================================
COTRUST PLC — Modbus Driver for Hospital Monitor
============================================================
Compatible with: COTRUST CT Series PLC (CT200/CT300)
Protocol: Modbus RTU over RS485 OR Modbus TCP over Ethernet
HMI: FATEK FBTNxx (communicates via same Modbus registers)

REGISTER MAP (configure in COTRUST PLC program):
-------------------------------------------------
D0  → Temperature (°C × 10)     e.g. 1215 = 121.5°C
D1  → Pressure (bar × 100)      e.g. 152  = 1.52 bar
D2  → Steam Flow (kg/h × 10)    e.g. 82   = 8.2 kg/h
D3  → Water Level (%)           e.g. 74   = 74%
D4  → Power (kW × 10)           e.g. 148  = 14.8 kW
D5  → Cycle Status              0=Idle 1=Heating 2=Sterilizing 3=Cooling 4=Complete 5=Error
D6  → Door Status               0=Open 1=Closed/Locked
D7  → Heater Status             0=Off 1=On
D8  → Pump Status               0=Off 1=On
D9  → Current Cycle Number
D10 → Total Cycles (lifetime)
D11 → Alarm Code                0=Normal, see ALARM_CODES below

COIL MAP:
M0  → Remote Start Cycle
M1  → Remote Stop/Abort
M2  → Remote Door Lock Command
M3  → Alarm Reset
"""

import struct
import logging
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================
# ALARM CODES
# ============================================================
ALARM_CODES = {
    0:  None,
    1:  ("دمای بیش از حد", "critical"),
    2:  ("فشار بیش از حد", "critical"),
    3:  ("فشار کمتر از حد", "warning"),
    4:  ("دمای کمتر از حد", "warning"),
    5:  ("خطای سنسور دما", "critical"),
    6:  ("خطای سنسور فشار", "critical"),
    7:  ("در قفل نشده", "warning"),
    8:  ("سطح آب پایین", "warning"),
    9:  ("اتصال کوتاه پمپ", "critical"),
    10: ("اتصال کوتاه المنت", "critical"),
    11: ("خطای ارتباطی HMI", "warning"),
    99: ("خطای ناشناخته", "critical"),
}

# ============================================================
# CYCLE STATUS MAP
# ============================================================
CYCLE_STATUS = {
    0: "idle",
    1: "heating",
    2: "sterilizing",
    3: "cooling",
    4: "complete",
    5: "error",
}


# ============================================================
# DATA CLASS
# ============================================================
@dataclass
class AutoclaveReading:
    temperature_c: float
    pressure_bar: float
    steam_flow_kg_h: float
    water_level_pct: float
    power_consumption_kw: float
    cycle_status: str
    door_locked: bool
    heater_on: bool
    pump_on: bool
    cycle_number: int
    total_cycles: int
    alarm_code: int
    alarm_message: Optional[str]
    alarm_severity: Optional[str]
    timestamp: datetime
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature_c,
            "pressure": self.pressure_bar,
            "steam_flow": self.steam_flow_kg_h,
            "water_level": self.water_level_pct,
            "power": self.power_consumption_kw,
            "status": self.cycle_status,
            "door_locked": self.door_locked,
            "heater_on": self.heater_on,
            "pump_on": self.pump_on,
            "cycle_number": self.cycle_number,
            "total_cycles": self.total_cycles,
            "alarm_code": self.alarm_code,
            "alarm_message": self.alarm_message,
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================
# MODBUS RTU DRIVER (RS485)
# ============================================================
class CotrustModbusRTU:
    """
    ارتباط با PLC COTRUST از طریق RS485
    
    سخت‌افزار مورد نیاز:
    - کابل RS485 (2 سیم: A+ و B-)
    - مبدل USB به RS485 (مثلاً CH340 یا FTDI)
    - یا کارت RS485 روی سرور
    
    تنظیمات پیش‌فرض COTRUST:
    - Baud Rate: 9600
    - Data Bits: 8
    - Parity: None (E/O/N)
    - Stop Bits: 1
    - Slave ID: 1
    """

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        slave_id: int = 1,
        baudrate: int = 9600,
        timeout: float = 2.0,
    ):
        self.port = port
        self.slave_id = slave_id
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None
        self._lock = threading.Lock()

    def connect(self) -> bool:
        try:
            import serial
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
            )
            logger.info(f"RS485 متصل شد: {self.port} @ {self.baudrate} baud")
            return True
        except Exception as e:
            logger.error(f"خطا در اتصال RS485: {e}")
            return False

    def disconnect(self):
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info("RS485 قطع شد")

    @staticmethod
    def _crc16(data: bytes) -> bytes:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return struct.pack('<H', crc)

    def _read_holding_registers(self, start_addr: int, count: int) -> Optional[list]:
        """FC03 — Read Holding Registers"""
        if not self._serial or not self._serial.is_open:
            return None

        with self._lock:
            # Build request frame
            frame = struct.pack('>BBHH', self.slave_id, 0x03, start_addr, count)
            frame += self._crc16(frame)

            try:
                self._serial.reset_input_buffer()
                self._serial.write(frame)
                time.sleep(0.05)

                # Response: [slave_id, fc, byte_count, data..., crc_lo, crc_hi]
                expected_len = 5 + count * 2
                response = self._serial.read(expected_len)

                if len(response) < expected_len:
                    logger.warning(f"پاسخ ناقص: {len(response)} بایت (انتظار {expected_len})")
                    return None

                # Validate CRC
                recv_crc = response[-2:]
                calc_crc = self._crc16(response[:-2])
                if recv_crc != calc_crc:
                    logger.error("خطای CRC در پاسخ Modbus")
                    return None

                # Parse registers
                byte_count = response[2]
                registers = []
                for i in range(count):
                    reg = struct.unpack('>H', response[3 + i*2: 5 + i*2])[0]
                    registers.append(reg)

                return registers

            except Exception as e:
                logger.error(f"خطا در خواندن رجیسترها: {e}")
                return None

    def _write_coil(self, addr: int, value: bool) -> bool:
        """FC05 — Write Single Coil"""
        if not self._serial or not self._serial.is_open:
            return False

        with self._lock:
            val = 0xFF00 if value else 0x0000
            frame = struct.pack('>BBHH', self.slave_id, 0x05, addr, val)
            frame += self._crc16(frame)

            try:
                self._serial.reset_input_buffer()
                self._serial.write(frame)
                time.sleep(0.05)
                response = self._serial.read(8)
                return len(response) == 8
            except Exception as e:
                logger.error(f"خطا در نوشتن کویل: {e}")
                return False

    def read(self) -> Optional[AutoclaveReading]:
        """خواندن تمام پارامترها از D0 تا D11"""
        regs = self._read_holding_registers(start_addr=0, count=12)
        if regs is None or len(regs) < 12:
            return None

        alarm_code = regs[11]
        alarm_info = ALARM_CODES.get(alarm_code, ("خطای ناشناخته", "critical"))

        return AutoclaveReading(
            temperature_c=regs[0] / 10.0,
            pressure_bar=regs[1] / 100.0,
            steam_flow_kg_h=regs[2] / 10.0,
            water_level_pct=regs[3],
            power_consumption_kw=regs[4] / 10.0,
            cycle_status=CYCLE_STATUS.get(regs[5], "idle"),
            door_locked=bool(regs[6]),
            heater_on=bool(regs[7]),
            pump_on=bool(regs[8]),
            cycle_number=regs[9],
            total_cycles=regs[10],
            alarm_code=alarm_code,
            alarm_message=alarm_info[0] if alarm_code else None,
            alarm_severity=alarm_info[1] if alarm_code else None,
            timestamp=datetime.now(),
        )

    def remote_start(self) -> bool:
        """فرمان شروع سیکل از راه دور → M0"""
        return self._write_coil(addr=0, value=True)

    def remote_stop(self) -> bool:
        """فرمان توقف از راه دور → M1"""
        return self._write_coil(addr=1, value=True)

    def reset_alarm(self) -> bool:
        """ریست هشدار → M3"""
        return self._write_coil(addr=3, value=True)


# ============================================================
# MODBUS TCP DRIVER (Ethernet)
# ============================================================
class CotrustModbusTCP:
    """
    ارتباط با PLC COTRUST از طریق شبکه Ethernet
    
    نیاز: ماژول Ethernet روی COTRUST PLC
    پیش‌فرض: IP=192.168.1.100, Port=502
    """

    def __init__(
        self,
        host: str = "192.168.1.100",
        port: int = 502,
        slave_id: int = 1,
        timeout: float = 3.0,
    ):
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self._transaction_id = 0
        self._sock = None
        self._lock = threading.Lock()

    def connect(self) -> bool:
        import socket
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.timeout)
            self._sock.connect((self.host, self.port))
            logger.info(f"Modbus TCP متصل شد: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"خطا در اتصال TCP: {e}")
            return False

    def disconnect(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def _next_tid(self) -> int:
        self._transaction_id = (self._transaction_id + 1) % 65536
        return self._transaction_id

    def _read_holding_registers(self, start_addr: int, count: int) -> Optional[list]:
        """Modbus TCP FC03"""
        if not self._sock:
            return None

        with self._lock:
            tid = self._next_tid()
            # MBAP Header + PDU
            pdu = struct.pack('>BHH', 0x03, start_addr, count)
            mbap = struct.pack('>HHHB', tid, 0, len(pdu) + 1, self.slave_id)
            frame = mbap + pdu

            try:
                self._sock.sendall(frame)
                response = self._sock.recv(256)

                if len(response) < 9:
                    return None

                # Parse
                byte_count = response[8]
                registers = []
                for i in range(count):
                    offset = 9 + i * 2
                    if offset + 2 <= len(response):
                        reg = struct.unpack('>H', response[offset:offset+2])[0]
                        registers.append(reg)

                return registers if len(registers) == count else None

            except Exception as e:
                logger.error(f"خطای TCP: {e}")
                self._sock = None
                return None

    def _write_coil(self, addr: int, value: bool) -> bool:
        if not self._sock:
            return False
        with self._lock:
            tid = self._next_tid()
            val = 0xFF00 if value else 0x0000
            pdu = struct.pack('>BHH', 0x05, addr, val)
            mbap = struct.pack('>HHHB', tid, 0, len(pdu) + 1, self.slave_id)
            try:
                self._sock.sendall(mbap + pdu)
                resp = self._sock.recv(12)
                return len(resp) == 12
            except Exception as e:
                logger.error(f"خطای TCP write coil: {e}")
                return False

    def read(self) -> Optional[AutoclaveReading]:
        regs = self._read_holding_registers(start_addr=0, count=12)
        if regs is None or len(regs) < 12:
            # Try reconnect
            self.connect()
            return None

        alarm_code = regs[11]
        alarm_info = ALARM_CODES.get(alarm_code, ("خطای ناشناخته", "critical"))

        return AutoclaveReading(
            temperature_c=regs[0] / 10.0,
            pressure_bar=regs[1] / 100.0,
            steam_flow_kg_h=regs[2] / 10.0,
            water_level_pct=regs[3],
            power_consumption_kw=regs[4] / 10.0,
            cycle_status=CYCLE_STATUS.get(regs[5], "idle"),
            door_locked=bool(regs[6]),
            heater_on=bool(regs[7]),
            pump_on=bool(regs[8]),
            cycle_number=regs[9],
            total_cycles=regs[10],
            alarm_code=alarm_code,
            alarm_message=alarm_info[0] if alarm_code else None,
            alarm_severity=alarm_info[1] if alarm_code else None,
            timestamp=datetime.now(),
        )

    def remote_start(self) -> bool:
        return self._write_coil(addr=0, value=True)

    def remote_stop(self) -> bool:
        return self._write_coil(addr=1, value=True)

    def reset_alarm(self) -> bool:
        return self._write_coil(addr=3, value=True)


# ============================================================
# SIMULATOR (برای تست بدون سخت‌افزار)
# ============================================================
class AutoclaveSimulator:
    """
    شبیه‌ساز واقع‌گرایانه یک سیکل اتوکلاو
    برای تست نرم‌افزار بدون اتصال به PLC واقعی
    """
    def __init__(self):
        self._phase = "idle"
        self._start_time = None
        self._temp = 25.0
        self._pressure = 0.0
        self._power = 0.0
        self._cycle_num = 0
        self._total_cycles = 142  # شروع از یه عدد واقع‌گرایانه
        self._alarm = 0
        import random
        self._random = random

    def _simulate_phase(self) -> tuple:
        """شبیه‌سازی واقع‌گرایانه مراحل سیکل"""
        rnd = self._random
        noise = lambda: rnd.uniform(-0.5, 0.5)

        if self._phase == "idle":
            self._temp = max(25.0, self._temp - 0.5) + noise()
            self._pressure = max(0.0, self._pressure - 0.01)
            self._power = 0.0
            status = 0

        elif self._phase == "heating":
            elapsed = (datetime.now() - self._start_time).seconds
            self._temp = min(121.0, 25.0 + elapsed * 0.8 + noise())
            self._pressure = min(1.0, elapsed * 0.006 + noise() * 0.01)
            self._power = 18.0 + noise()
            status = 1
            if self._temp >= 120.5:
                self._phase = "sterilizing"

        elif self._phase == "sterilizing":
            self._temp = 121.5 + noise() * 0.3
            self._pressure = 1.52 + noise() * 0.02
            self._power = 8.0 + noise()
            status = 2
            elapsed = (datetime.now() - self._start_time).seconds
            if elapsed > 30:  # 30 ثانیه برای demo
                self._phase = "cooling"

        elif self._phase == "cooling":
            self._temp = max(40.0, self._temp - 0.7 + noise())
            self._pressure = max(0.0, self._pressure - 0.05 + noise() * 0.01)
            self._power = 0.5 + noise() * 0.1
            status = 3
            if self._temp <= 42.0:
                self._phase = "complete"

        elif self._phase == "complete":
            status = 4
            self._power = 0.0

        else:
            status = 0
            self._power = 0.0

        return status

    def start_cycle(self):
        if self._phase in ("idle", "complete"):
            self._phase = "heating"
            self._start_time = datetime.now()
            self._cycle_num += 1
            self._total_cycles += 1
            logger.info(f"🔬 سیکل #{self._cycle_num} شروع شد (شبیه‌ساز)")

    def stop_cycle(self):
        self._phase = "idle"
        self._start_time = None

    def read(self) -> AutoclaveReading:
        status_code = self._simulate_phase()
        rnd = self._random
        return AutoclaveReading(
            temperature_c=round(self._temp, 1),
            pressure_bar=round(self._pressure, 2),
            steam_flow_kg_h=round(8.2 + rnd.uniform(-0.3, 0.3), 1) if self._phase == "sterilizing" else 0.0,
            water_level_pct=round(74 + rnd.uniform(-2, 2), 0),
            power_consumption_kw=round(self._power, 1),
            cycle_status=CYCLE_STATUS.get(status_code, "idle"),
            door_locked=self._phase not in ("idle", "complete"),
            heater_on=self._phase == "heating",
            pump_on=self._phase in ("heating", "sterilizing"),
            cycle_number=self._cycle_num,
            total_cycles=self._total_cycles,
            alarm_code=self._alarm,
            alarm_message=None,
            alarm_severity=None,
            timestamp=datetime.now(),
        )


# ============================================================
# POLLING SERVICE — خواندن خودکار هر N ثانیه
# ============================================================
class PLCPollingService:
    """
    سرویس polling: هر N ثانیه داده می‌خونه،
    ذخیره می‌کنه، و از طریق WebSocket ارسال می‌کنه
    """

    def __init__(self, device_id: int, driver, interval_seconds: int = 5):
        self.device_id = device_id
        self.driver = driver
        self.interval = interval_seconds
        self._thread = None
        self._running = False
        self._last_alarm_code = 0

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info(f"Polling شروع شد — دستگاه #{self.device_id} هر {self.interval}s")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        # Import داخل thread تا از circular import جلوگیری بشه
        import django
        from django.utils import timezone
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        while self._running:
            try:
                reading = self.driver.read()
                if reading and reading.is_valid:
                    self._process(reading)
                else:
                    logger.warning(f"خواندن ناموفق — دستگاه #{self.device_id}")
            except Exception as e:
                logger.error(f"خطا در polling: {e}")
            time.sleep(self.interval)

    def _process(self, reading: AutoclaveReading):
        from django.utils import timezone
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from apps.devices.models import Device, DeviceCycle
        from apps.monitoring.models import SensorReading, DeviceAlert

        try:
            device = Device.objects.get(pk=self.device_id)

            # فعال‌ترین سیکل
            active_cycle = DeviceCycle.objects.filter(
                device=device,
                status__in=["heating", "sterilizing", "cooling"]
            ).first()

            # ذخیره در دیتابیس
            SensorReading.objects.create(
                device=device,
                cycle=active_cycle,
                timestamp=timezone.now(),
                temperature_c=reading.temperature_c,
                pressure_bar=reading.pressure_bar,
                steam_flow_kg_h=reading.steam_flow_kg_h,
                water_level_pct=reading.water_level_pct,
                power_consumption_kw=reading.power_consumption_kw,
                door_locked=reading.door_locked,
                device_status=reading.cycle_status,
            )

            # آپدیت وضعیت دستگاه
            device.status = "online" if reading.cycle_status != "error" else "error"
            device.last_seen = timezone.now()
            device.save(update_fields=["status", "last_seen"])

            # بررسی هشدار جدید
            if reading.alarm_code and reading.alarm_code != self._last_alarm_code:
                DeviceAlert.objects.create(
                    device=device,
                    cycle=active_cycle,
                    alert_type="sensor",
                    severity=reading.alarm_severity or "warning",
                    message=reading.alarm_message or "هشدار دستگاه",
                    value=str(reading.alarm_code),
                )
                self._last_alarm_code = reading.alarm_code
            elif not reading.alarm_code:
                self._last_alarm_code = 0

            # ارسال به WebSocket
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"device_{self.device_id}",
                    {
                        "type": "sensor_update",
                        "data": reading.to_dict(),
                    }
                )

        except Exception as e:
            logger.error(f"خطا در پردازش داده PLC: {e}")


# ============================================================
# FACTORY — انتخاب خودکار درایور بر اساس تنظیمات
# ============================================================
def get_plc_driver(device):
    """
    بر اساس تنظیمات دستگاه، درایور مناسب رو برمی‌گردونه
    
    device.connection_type:
        'rtu'  → RS485 (مبدل USB-RS485)
        'tcp'  → Ethernet
        'sim'  → شبیه‌ساز (برای تست)
    """
    from django.conf import settings

    conn_type = getattr(device, "connection_type", "sim")

    if conn_type == "rtu":
        driver = CotrustModbusRTU(
            port=getattr(device, "serial_port", "/dev/ttyUSB0"),
            slave_id=getattr(device, "modbus_slave_id", 1),
            baudrate=getattr(device, "baud_rate", 9600),
        )
        driver.connect()
        return driver

    elif conn_type == "tcp":
        driver = CotrustModbusTCP(
            host=getattr(device, "plc_ip", "192.168.1.100"),
            port=getattr(device, "plc_port", 502),
            slave_id=getattr(device, "modbus_slave_id", 1),
        )
        driver.connect()
        return driver

    else:
        return AutoclaveSimulator()


# ============================================================
# GLOBAL POLLING REGISTRY
# ============================================================
_active_pollers: Dict[int, PLCPollingService] = {}


def start_polling(device) -> PLCPollingService:
    """شروع polling برای یک دستگاه"""
    device_id = device.pk
    if device_id in _active_pollers:
        _active_pollers[device_id].stop()

    driver = get_plc_driver(device)
    poller = PLCPollingService(
        device_id=device_id,
        driver=driver,
        interval_seconds=getattr(device, "polling_interval", 5),
    )
    poller.start()
    _active_pollers[device_id] = poller
    return poller


def stop_polling(device_id: int):
    if device_id in _active_pollers:
        _active_pollers[device_id].stop()
        del _active_pollers[device_id]


def get_all_pollers() -> Dict[int, PLCPollingService]:
    return _active_pollers
