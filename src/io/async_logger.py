import asyncio
import traceback

from loguru import logger as GLOBAL_LOGGER

# 文件轮换（Log Rotation）是指在日志文件达到特定条件时（如大小、时间等）自动创建新的日志文件并开始新的日志记录。
# 这样可以防止单个日志文件过大，便于管理和存档
# 每次调用 logger.add() 函数时，都会创建一个新的日志处理器，并将其添加到 logger 中


# 配置日志


# 异步日志记录函数
# 被标记为 async 的函数在调用时不会立即执行，而是返回一个协程对象，只有在被 调用或作为任务调度后，才会真正执行
# GLOBAL_LOGGER = Logger(name="global_logger")


# 通过 await，可以在协程中等待其他协程完成，而不会阻塞事件循环。这使得可以同时处理多个 I/O 操作


# def print_logger_info(logger: Logger):
#     print(f"Logger is None: {logger is None}")
#     print(f"Logger level: {logger.level}")
#     print(f"Logger handlers: {logger.handlers}")

#     for handler in logger.handlers:
#         print(f"Handler: {handler}, Formatter: {handler.formatter}")

#     if hasattr(logger, "closed"):
#         print(f"Logger is closed: {logger.closed}")

#     print(f"Logger name: {logger.name}")


def catch_exceptions(coro):
    def wrapper(*args, **kwargs):
        try:
            return coro(*args, **kwargs)
        except Exception as e:
            print(f"Caught exception in {coro.__name__}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()  # 打印完整的堆栈跟踪

    return wrapper


# 原实现: 使用 asyncio.get_event_loop() 和 run_in_executor 来在线程池中阻塞地运行日志记录。这会导致创建线程，从而增加开销。
# 新实现: 直接使用 logger.info(message)，使日志记录完全异步，避免了线程的上下文切换。
