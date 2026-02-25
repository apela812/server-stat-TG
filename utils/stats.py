"""
Модуль сбора статистики сервера.
"""
import psutil
import platform
import socket
from datetime import timedelta


def get_cpu_stats() -> dict:
    """Получить статистику CPU."""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)

    return {
        "percent": cpu_percent,
        "freq_current": f"{cpu_freq.current:.0f}" if cpu_freq else "N/A",
        "freq_max": f"{cpu_freq.max:.0f}" if cpu_freq else "N/A",
        "cores_logical": cpu_count,
        "cores_physical": cpu_count_physical,
    }


def get_ram_stats() -> dict:
    """Получить статистику оперативной памяти."""
    ram = psutil.virtual_memory()

    return {
        "total": ram.total / (1024**3),  # GB
        "available": ram.available / (1024**3),  # GB
        "used": ram.used / (1024**3),  # GB
        "percent": ram.percent,
    }


def get_disk_stats() -> list:
    """Получить статистику дисков."""
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total / (1024**3),  # GB
                "used": usage.used / (1024**3),  # GB
                "free": usage.free / (1024**3),  # GB
                "percent": usage.percent,
            })
        except PermissionError:
            continue
    return disks


def get_network_stats() -> dict:
    """Получить статистику сети."""
    net_io = psutil.net_io_counters()
    net_if_addrs = psutil.net_if_addrs()

    # Получаем IP адреса
    ip_addresses = []
    for iface, addrs in net_if_addrs.items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK and addr.address:
                ip_addresses.append(f"{iface}: {addr.address}")

    return {
        "bytes_sent": net_io.bytes_sent / (1024**2),  # MB
        "bytes_recv": net_io.bytes_recv / (1024**2),  # MB
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
        "ip_addresses": ip_addresses,
    }


def get_system_info() -> dict:
    """Получить общую информацию о системе."""
    boot_time = psutil.boot_time()
    uptime = timedelta(seconds=int(psutil.time.time() - boot_time))

    # Форматируем uptime
    uptime_str = str(uptime)

    # Температура (если доступна)
    temp = None
    try:
        sensors = psutil.sensors_temperatures()
        if sensors:
            for name, entries in sensors.items():
                for entry in entries:
                    if entry.current:
                        temp = entry.current
                        break
                if temp:
                    break
    except (AttributeError, KeyError):
        pass

    return {
        "platform": platform.system(),
        "hostname": socket.gethostname(),
        "uptime": uptime_str,
        "boot_time": psutil.boot_time(),
        "temperature": temp,
        "cpu_count": psutil.cpu_count(logical=False),
    }


def get_top_processes(limit: int = 5) -> list:
    """Получить топ процессов по использованию CPU."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            pinfo = proc.info
            if pinfo["cpu_percent"] is not None and pinfo["memory_percent"] is not None:
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Сортируем по CPU
    processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)

    return processes[:limit]


def get_all_running_processes(sort_by: str = "memory", limit: int = 15) -> list:
    """Получить список запущенных процессов, отсортированных по CPU или памяти."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            pinfo = proc.info
            if pinfo["status"] == psutil.STATUS_RUNNING:
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Сортируем по выбранному параметру
    if sort_by == "cpu":
        processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
    else:  # memory (по умолчанию)
        processes.sort(key=lambda x: x["memory_percent"] or 0, reverse=True)

    return processes[:limit]


def get_process_info(pid: int) -> dict:
    """Получить подробную информацию о процессе по PID."""
    try:
        proc = psutil.Process(pid)
        return {
            "pid": proc.pid,
            "name": proc.name(),
            "status": proc.status(),
            "cpu_percent": proc.cpu_percent(interval=0.1),
            "memory_percent": proc.memory_percent(),
            "memory_info": proc.memory_info().rss / (1024**2),  # MB
            "num_threads": proc.num_threads(),
            "create_time": proc.create_time(),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None
