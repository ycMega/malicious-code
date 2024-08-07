import asyncio
import traceback

from aiologger import Logger

# 配置日志


# 异步日志记录函数
# 被标记为 async 的函数在调用时不会立即执行，而是返回一个协程对象，只有在被 await 调用或作为任务调度后，才会真正执行
GLOBAL_LOGGER = Logger.with_default_handlers(level="DEBUG")
# 通过 await，可以在协程中等待其他协程完成，而不会阻塞事件循环。这使得可以同时处理多个 I/O 操作


def print_logger_info(logger: Logger):
    print(f"Logger is None: {logger is None}")
    print(f"Logger level: {logger.level}")
    print(f"Logger handlers: {logger.handlers}")

    for handler in logger.handlers:
        print(f"Handler: {handler}, Formatter: {handler.formatter}")

    if hasattr(logger, "closed"):
        print(f"Logger is closed: {logger.closed}")

    print(f"Logger name: {logger.name}")


def catch_exceptions(coro):
    async def wrapper(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except Exception as e:
            print(f"Caught exception in {coro.__name__}: {e}")
            print("Traceback:")
            traceback.print_exc()  # 打印完整的堆栈跟踪

    return wrapper


# 原实现: 使用 asyncio.get_event_loop() 和 run_in_executor 来在线程池中阻塞地运行日志记录。这会导致创建线程，从而增加开销。
# 新实现: 直接使用 await logger.info(message)，使日志记录完全异步，避免了线程的上下文切换。
