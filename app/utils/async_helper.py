"""
异步辅助工具
"""
import asyncio
from typing import Callable, Any, Optional
from functools import wraps

from app.utils.logger import log


def async_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    异步重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍增因子
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        log.warning(
                            f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}, "
                            f"等待 {current_delay}s 后重试..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        log.error(f"{func.__name__} 达到最大重试次数，失败: {e}")
            
            raise last_exception
        
        return wrapper
    return decorator


async def run_in_threadpool(func: Callable, *args, **kwargs) -> Any:
    """
    在线程池中运行同步函数
    
    Args:
        func: 同步函数
        *args, **kwargs: 函数参数
        
    Returns:
        函数返回值
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


class TaskQueue:
    """简单的异步任务队列"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks = []
    
    async def add_task(self, coro):
        """添加任务到队列"""
        async def wrapped():
            async with self.semaphore:
                return await coro
        
        task = asyncio.create_task(wrapped())
        self.tasks.append(task)
        return task
    
    async def wait_all(self):
        """等待所有任务完成"""
        if self.tasks:
            results = await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks.clear()
            return results
        return []

