print('1.1')
import threading
import time

def download_simulation(file_name: str, size_mb: float) -> dict:
    """Імітація завантаження файлу."""

    thread_name = threading.current_thread().name

    print(
        f"[{thread_name}] Початок завантаження "
        f"'{file_name}' ({size_mb} MB)..."
    )

    time.sleep(size_mb * 0.5)

    print(
        f"[{thread_name}] Завантаження "
        f"'{file_name}' завершено"
    )

    return {
        "file": file_name,
        "size": size_mb,
        "thread": thread_name
    }

class MonitorThread(threading.Thread):
    """Потік-монітор."""

    def __init__(self, interval: float = 1.0):
        super().__init__(
            name="Monitor",
            daemon=True
        )

        self.interval = interval
        self.active_downloads = 0
        self._stop_event = threading.Event()

    def run(self):

        while not self._stop_event.is_set():

            print(
                f"[MONITOR] Активних потоків: "
                f"{threading.active_count()}"
            )

            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()

def main():

    files = [
        ("data.csv", 2.5),
        ("report.pdf", 1.0),
        ("image.png", 0.5),
        ("archive.zip", 4.0),
        ("log.txt", 0.3),
    ]

    monitor = MonitorThread(0.5)
    monitor.start()

    threads = []

    start = time.perf_counter()

    for file_name, size in files:

        t = threading.Thread(
            target=download_simulation,
            args=(file_name, size),
            name=f"Downloader-{file_name}"
        )

        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    elapsed = time.perf_counter() - start

    monitor.stop()

    print(
        f"\nУсі файли завантажено за "
        f"{elapsed:.2f} сек"
    )

    sequential_start = time.perf_counter()

    for file_name, size in files:
        download_simulation(
            file_name,
            size
        )

    sequential_time = (
        time.perf_counter()
        - sequential_start
    )

    print(
        f"\nПослідовне виконання: "
        f"{sequential_time:.2f} сек"
    )

    print(
        f"Паралельне виконання: "
        f"{elapsed:.2f} сек"
    )

    print(
        f"Прискорення: "
        f"{sequential_time / elapsed:.2f}x"
    )


if __name__ == "__main__":
    main()

print('\n1.2')
"""Паралельне обчислення з multiprocessing."""

import multiprocessing
import time
import os


def is_prime(n: int) -> bool:
    """Перевірка числа на простоту."""

    if n < 2:
        return False

    if n < 4:
        return True

    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5

    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False

        i += 6

    return True


def sum_primes_in_range(start: int, end: int) -> tuple[int, int, int]:
    """Обчислює суму та кількість простих чисел у діапазоні."""

    pid = os.getpid()

    total_sum = 0
    count = 0

    for number in range(start, end):

        if is_prime(number):
            total_sum += number
            count += 1

    return total_sum, count, pid


def main():

    total_range = 1_000_000
    num_workers = 4

    chunk_size = total_range // num_workers

    ranges = []

    for i in range(num_workers):

        start = i * chunk_size if i > 0 else 2

        if i == num_workers - 1:
            end = total_range
        else:
            end = (i + 1) * chunk_size

        ranges.append((start, end))

    print("Діапазони для обробки:")

    for start, end in ranges:
        print(f"[{start:,} ; {end:,})")

    # ==================================
    # Послідовне виконання
    # ==================================

    print("\n=== Послідовне виконання ===")

    start_time = time.perf_counter()

    sequential_results = []

    for start, end in ranges:
        sequential_results.append(
            sum_primes_in_range(start, end)
        )

    seq_time = (
        time.perf_counter()
        - start_time
    )

    seq_sum = sum(
        result[0]
        for result in sequential_results
    )

    seq_count = sum(
        result[1]
        for result in sequential_results
    )

    print(f"Кількість простих чисел: {seq_count}")
    print(f"Сума простих чисел: {seq_sum}")

    # ==================================
    # Паралельне виконання
    # ==================================

    print("\n=== Паралельне виконання ===")

    start_time = time.perf_counter()

    with multiprocessing.Pool(
        processes=num_workers
    ) as pool:

        parallel_results = pool.starmap(
            sum_primes_in_range,
            ranges
        )

    par_time = (
        time.perf_counter()
        - start_time
    )

    par_sum = sum(
        result[0]
        for result in parallel_results
    )

    par_count = sum(
        result[1]
        for result in parallel_results
    )

    print(f"Кількість простих чисел: {par_count}")
    print(f"Сума простих чисел: {par_sum}")

    print("\nPID робочих процесів:")

    for index, result in enumerate(
        parallel_results,
        start=1
    ):
        print(
            f"Процес {index}: "
            f"PID={result[2]}"
        )

    print("\n=== Порівняння ===")

    print(
        f"Послідовно: "
        f"{seq_time:.3f} сек"
    )

    print(
        f"Паралельно "
        f"({num_workers} процеси): "
        f"{par_time:.3f} сек"
    )

    print(
        f"Прискорення: "
        f"{seq_time / par_time:.2f}x"
    )

    print(
        f"\nРезультати збігаються: "
        f"{seq_sum == par_sum and seq_count == par_count}"
    )


if __name__ == "__main__":
    main()

print('\n2.1')
"""Демонстрація race condition та захист через Lock."""

import threading
import time
import random


class BankAccount:
    """Банківський рахунок без синхронізації."""

    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0

    def deposit(self, amount: float) -> None:

        current = self.balance

        time.sleep(
            random.uniform(
                0.0001,
                0.001
            )
        )

        self.balance = current + amount
        self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:

        current = self.balance

        time.sleep(
            random.uniform(
                0.0001,
                0.001
            )
        )

        if current >= amount:

            self.balance = current - amount
            self.transaction_count += 1

            return True

        return False


class SafeBankAccount:
    """Банківський рахунок із захистом через Lock."""

    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:

        with self._lock:

            current = self.balance

            time.sleep(
                random.uniform(
                    0.0001,
                    0.001
                )
            )

            self.balance = current + amount
            self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:

        with self._lock:

            current = self.balance

            time.sleep(
                random.uniform(
                    0.0001,
                    0.001
                )
            )

            if current >= amount:

                self.balance = current - amount
                self.transaction_count += 1

                return True

            return False


def deposit_worker(
    account,
    operations,
    amount
):
    for _ in range(operations):
        account.deposit(amount)


def withdraw_worker(
    account,
    operations,
    amount
):
    for _ in range(operations):
        account.withdraw(amount)


def run_transactions(
    account,
    num_deposits: int,
    num_withdrawals: int
):
    """Запуск набору потоків."""

    threads = []

    # 10 потоків поповнення

    for _ in range(10):

        t = threading.Thread(
            target=deposit_worker,
            args=(
                account,
                num_deposits // 10,
                50.0
            )
        )

        threads.append(t)

    # 10 потоків зняття

    for _ in range(10):

        t = threading.Thread(
            target=withdraw_worker,
            args=(
                account,
                num_withdrawals // 10,
                50.0
            )
        )

        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def main():

    initial_balance = 1000.0

    num_deposits = 100
    deposit_amount = 50.0

    num_withdrawals = 100
    withdraw_amount = 50.0

    expected_balance = (
        initial_balance
        + num_deposits * deposit_amount
        - num_withdrawals * withdraw_amount
    )

    # ==========================
    # Без синхронізації
    # ==========================

    print("=== Тест без синхронізації ===")

    unsafe_account = BankAccount(
        initial_balance
    )

    run_transactions(
        unsafe_account,
        num_deposits,
        num_withdrawals
    )

    print(
        f"Очікуваний баланс: "
        f"{expected_balance:.2f}"
    )

    print(
        f"Фактичний баланс: "
        f"{unsafe_account.balance:.2f}"
    )

    print(
        f"Транзакцій: "
        f"{unsafe_account.transaction_count}"
    )

    print(
        f"Баланс правильний: "
        f"{unsafe_account.balance == expected_balance}"
    )

    # ==========================
    # З синхронізацією
    # ==========================

    print(
        "\n=== Тест із синхронізацією (Lock) ==="
    )

    safe_account = SafeBankAccount(
        initial_balance
    )

    run_transactions(
        safe_account,
        num_deposits,
        num_withdrawals
    )

    print(
        f"Очікуваний баланс: "
        f"{expected_balance:.2f}"
    )

    print(
        f"Фактичний баланс: "
        f"{safe_account.balance:.2f}"
    )

    print(
        f"Транзакцій: "
        f"{safe_account.transaction_count}"
    )

    print(
        f"Баланс правильний: "
        f"{safe_account.balance == expected_balance}"
    )

    print(
        f"\nОчікуваний баланс: "
        f"{expected_balance:.2f}"
    )


if __name__ == "__main__":
    main()

print('\n2.2')
"""Семафори та Event для управління конкурентним доступом."""

import threading
import time
import random


class ConnectionPool:
    """Пул з'єднань з обмеженням через Semaphore."""

    def __init__(self, max_connections: int = 3):
        self._semaphore = threading.Semaphore(max_connections)
        self._lock = threading.Lock()

        self.max_connections = max_connections
        self.active_connections = 0
        self.total_served = 0
        self.peak_connections = 0

    def acquire_connection(self, client_name: str) -> None:

        print(f"[{client_name}] Запит на з'єднання...")

        self._semaphore.acquire()

        with self._lock:

            self.active_connections += 1

            self.peak_connections = max(
                self.peak_connections,
                self.active_connections
            )

            print(
                f"[{client_name}] Отримав з'єднання "
                f"(активних: {self.active_connections})"
            )

    def release_connection(self, client_name: str) -> None:

        with self._lock:

            self.active_connections -= 1
            self.total_served += 1

            print(
                f"[{client_name}] Повернув з'єднання "
                f"(активних: {self.active_connections})"
            )

        self._semaphore.release()

    def get_stats(self) -> dict:

        return {
            "max": self.max_connections,
            "active": self.active_connections,
            "total_served": self.total_served,
            "peak": self.peak_connections,
        }


def client_task(
    pool: ConnectionPool,
    client_name: str,
    ready_event: threading.Event
) -> None:

    ready_event.wait()

    pool.acquire_connection(client_name)

    try:

        work_time = random.uniform(
            0.5,
            2.0
        )

        print(
            f"  [{client_name}] "
            f"Працює {work_time:.1f} сек"
        )

        time.sleep(work_time)

    finally:
        pool.release_connection(client_name)


def main():

    pool = ConnectionPool(
        max_connections=3
    )

    ready_event = threading.Event()

    num_clients = 10

    threads = []

    for i in range(num_clients):

        t = threading.Thread(
            target=client_task,
            args=(
                pool,
                f"Client-{i:02d}",
                ready_event
            ),
        )

        threads.append(t)
        t.start()

    time.sleep(0.5)

    print(
        ">>> Сервер готовий! "
        "Усі клієнти починають роботу.\n"
    )

    ready_event.set()

    for t in threads:
        t.join()

    stats = pool.get_stats()

    print("\n=== Статистика пулу ===")

    print(
        f"Максимум з'єднань: "
        f"{stats['max']}"
    )

    print(
        f"Поточних з'єднань: "
        f"{stats['active']}"
    )

    print(
        f"Обслуговано клієнтів: "
        f"{stats['total_served']}"
    )

    print(
        f"Пікове навантаження: "
        f"{stats['peak']}"
    )

    if stats["peak"] <= stats["max"]:
        print(
            "Перевірка успішна: "
            "ліміт з'єднань не перевищено."
        )
    else:
        print(
            "ПОМИЛКА: перевищено "
            "максимальну кількість з'єднань!"
        )


if __name__ == "__main__":
    main()

print('\n3.1')
"""Порівняння ThreadPoolExecutor та ProcessPoolExecutor."""

from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
)
import time
import hashlib


def io_bound_task(url: str) -> dict:
    """Імітація I/O-bound задачі."""

    time.sleep(0.5)

    return {
        "url": url,
        "status": 200,
        "size": len(url) * 42
    }


def cpu_bound_task(n: int) -> dict:
    """CPU-bound задача."""

    hasher = hashlib.sha256()

    for i in range(n):
        hasher.update(str(i).encode())

    return {
        "n": n,
        "hash": hasher.hexdigest()[:16]
    }


def risky_task(value: int) -> float:
    """Задача з можливими винятками."""

    if value == 0:
        raise ZeroDivisionError(
            "Ділення на нуль!"
        )

    if value < 0:
        raise ValueError(
            f"Від'ємне значення: {value}"
        )

    return 1000.0 / value


def benchmark_io_bound():
    """ThreadPoolExecutor для I/O-bound задач."""

    urls = [
        f"https://api.example.com/data/{i}"
        for i in range(20)
    ]

    start = time.perf_counter()

    sequential_results = []

    for url in urls:
        sequential_results.append(
            io_bound_task(url)
        )

    sequential_time = (
        time.perf_counter() - start
    )

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=5
    ) as executor:

        parallel_results = list(
            executor.map(
                io_bound_task,
                urls
            )
        )

    parallel_time = (
        time.perf_counter() - start
    )

    print(
        f"Оброблено URL: "
        f"{len(parallel_results)}"
    )

    print(
        f"Послідовно: "
        f"{sequential_time:.3f} сек"
    )

    print(
        f"ThreadPoolExecutor: "
        f"{parallel_time:.3f} сек"
    )

    print(
        f"Прискорення: "
        f"{sequential_time / parallel_time:.2f}x"
    )


def benchmark_cpu_bound():
    """ProcessPoolExecutor для CPU-bound задач."""

    tasks = [500_000] * 8

    start = time.perf_counter()

    sequential_results = [
        cpu_bound_task(task)
        for task in tasks
    ]

    sequential_time = (
        time.perf_counter() - start
    )

    start = time.perf_counter()

    with ProcessPoolExecutor(
        max_workers=4
    ) as executor:

        parallel_results = list(
            executor.map(
                cpu_bound_task,
                tasks
            )
        )

    parallel_time = (
        time.perf_counter() - start
    )

    print(
        f"Виконано задач: "
        f"{len(parallel_results)}"
    )

    print(
        f"Послідовно: "
        f"{sequential_time:.3f} сек"
    )

    print(
        f"ProcessPoolExecutor: "
        f"{parallel_time:.3f} сек"
    )

    print(
        f"Прискорення: "
        f"{sequential_time / parallel_time:.2f}x"
    )


def handle_exceptions():
    """Обробка виключень у пулах."""

    values = [10, 5, 0, -3, 8, 2]

    with ThreadPoolExecutor(
        max_workers=4
    ) as executor:

        futures = {
            executor.submit(
                risky_task,
                value
            ): value
            for value in values
        }

        for future in as_completed(
            futures
        ):
            value = futures[future]

            try:

                result = future.result()

                print(
                    f"{value} -> "
                    f"{result:.2f}"
                )

            except Exception as e:

                print(
                    f"{value} -> "
                    f"ПОМИЛКА: {e}"
                )


def main():

    print("=" * 60)
    print(
        "=== I/O-bound: "
        "ThreadPoolExecutor ==="
    )
    print("=" * 60)

    benchmark_io_bound()

    print(f"\n{'=' * 60}")

    print(
        "=== CPU-bound: "
        "ProcessPoolExecutor ==="
    )

    print("=" * 60)

    benchmark_cpu_bound()

    print(f"\n{'=' * 60}")

    print(
        "=== Обробка виключень "
        "у пулах ==="
    )

    print("=" * 60)

    handle_exceptions()


if __name__ == "__main__":
    main()

print('\n3.2')
"""Producer-Consumer з queue.Queue та демонстрація дедлоку."""

import threading
import queue
import time
import random


class Task:
    """Завдання для обробки."""

    def __init__(
        self,
        task_id: int,
        data: str,
        priority: int = 0
    ):
        self.task_id = task_id
        self.data = data
        self.priority = priority
        self.created_at = time.time()

    def __repr__(self):
        return (
            f"Task(id={self.task_id}, "
            f"data='{self.data}')"
        )


def producer(
    task_queue: queue.Queue,
    num_tasks: int,
    producer_id: int
) -> None:
    """Виробник."""

    for i in range(num_tasks):

        task = Task(
            task_id=producer_id * 100 + i,
            data=f"Дані від виробника "
                 f"{producer_id}, пакет {i}",
            priority=random.randint(1, 5),
        )

        task_queue.put(task)

        print(
            f"[Виробник-{producer_id}] "
            f"Створено {task}"
        )

        time.sleep(
            random.uniform(0.1, 0.3)
        )

    task_queue.put(None)


def consumer(
    task_queue: queue.Queue,
    consumer_id: int,
    results: list,
    results_lock: threading.Lock
) -> None:
    """Споживач."""

    while True:

        try:
            task = task_queue.get(
                timeout=2
            )

        except queue.Empty:

            print(
                f"[Споживач-{consumer_id}] "
                f"Черга порожня"
            )

            break

        if task is None:

            task_queue.put(None)
            task_queue.task_done()

            break

        processing_time = random.uniform(
            0.2,
            0.6
        )

        print(
            f"  [Споживач-{consumer_id}] "
            f"Обробляє {task}"
        )

        time.sleep(processing_time)

        result = {
            "task_id": task.task_id,
            "consumer": consumer_id,
            "time": processing_time
        }

        with results_lock:
            results.append(result)

        task_queue.task_done()


def producer_consumer_demo():
    """Producer-Consumer."""

    task_queue = queue.Queue(maxsize=5)

    results = []
    results_lock = threading.Lock()

    num_producers = 2
    num_consumers = 3
    tasks_per_producer = 5

    producers = []
    consumers = []

    for i in range(num_consumers):

        t = threading.Thread(
            target=consumer,
            args=(
                task_queue,
                i,
                results,
                results_lock
            ),
            name=f"Consumer-{i}"
        )

        consumers.append(t)
        t.start()

    for i in range(num_producers):

        t = threading.Thread(
            target=producer,
            args=(
                task_queue,
                tasks_per_producer,
                i
            ),
            name=f"Producer-{i}"
        )

        producers.append(t)
        t.start()

    for t in producers:
        t.join()

    task_queue.join()

    for t in consumers:
        t.join()

    avg_time = (
        sum(r["time"] for r in results)
        / len(results)
        if results
        else 0
    )

    print("\n=== Результати ===")

    print(
        f"Оброблено задач: "
        f"{len(results)}"
    )

    print(
        f"Середній час: "
        f"{avg_time:.3f} сек"
    )


def deadlock_demo():
    """Демонстрація дедлоку."""

    lock_a = threading.Lock()
    lock_b = threading.Lock()

    deadlock_detected = threading.Event()

    def worker_1():

        lock_a.acquire()

        print(
            "[Worker-1] "
            "Захопив Lock A"
        )

        time.sleep(0.1)

        acquired = lock_b.acquire(
            timeout=2
        )

        if not acquired:

            print(
                "[Worker-1] "
                "ДЕДЛОК!"
            )

            deadlock_detected.set()

            lock_a.release()
            return

        lock_b.release()
        lock_a.release()

    def worker_2():

        lock_b.acquire()

        print(
            "[Worker-2] "
            "Захопив Lock B"
        )

        time.sleep(0.1)

        acquired = lock_a.acquire(
            timeout=2
        )

        if not acquired:

            print(
                "[Worker-2] "
                "ДЕДЛОК!"
            )

            deadlock_detected.set()

            lock_b.release()
            return

        lock_a.release()
        lock_b.release()

    def safe_worker_1():

        with lock_a:

            time.sleep(0.1)

            with lock_b:
                print(
                    "[Safe-1] "
                    "Успішно виконався"
                )

    def safe_worker_2():

        with lock_a:

            time.sleep(0.1)

            with lock_b:
                print(
                    "[Safe-2] "
                    "Успішно виконався"
                )

    print(
        "=== Спроба з потенційним дедлоком ==="
    )

    t1 = threading.Thread(
        target=worker_1
    )

    t2 = threading.Thread(
        target=worker_2
    )

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    if deadlock_detected.is_set():

        print(
            ">>> Дедлок виявлено!"
        )

    else:

        print(
            ">>> Дедлок не виник."
        )

    print(
        "\n=== Безпечна версія ==="
    )

    s1 = threading.Thread(
        target=safe_worker_1
    )

    s2 = threading.Thread(
        target=safe_worker_2
    )

    s1.start()
    s2.start()

    s1.join()
    s2.join()

    print(
        "Безпечне завершення "
        "без дедлоку."
    )


def main():

    print("=" * 60)
    print(
        "=== Producer-Consumer ==="
    )
    print("=" * 60)

    producer_consumer_demo()

    print(f"\n{'=' * 60}")

    print(
        "=== Демонстрація дедлоку ==="
    )

    print("=" * 60)

    deadlock_demo()


if __name__ == "__main__":
    main()