import asyncio

from aiologger import Logger

# 配置日志
logger = Logger.with_default_handlers(level="DEBUG")


# 异步日志记录函数
# 被标记为 async 的函数在调用时不会立即执行，而是返回一个协程对象，只有在被 await 调用或作为任务调度后，才会真正执行
async def async_log(message):
    # 通过 await，可以在协程中等待其他协程完成，而不会阻塞事件循环。这使得可以同时处理多个 I/O 操作
    await logger.info(message)


# 示例使用
async def main():
    await async_log("这是一个异步日志消息")


if __name__ == "__main__":
    asyncio.run(main())


# 原实现: 使用 asyncio.get_event_loop() 和 run_in_executor 来在线程池中阻塞地运行日志记录。这会导致创建线程，从而增加开销。
# 新实现: 直接使用 await logger.info(message)，使日志记录完全异步，避免了线程的上下文切换。
