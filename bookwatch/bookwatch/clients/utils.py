import asyncio

def restart_on_exception(func):
    async def wrapper(*args, **kwargs):
        self = args[0]
        try:
            response = await func(*args, **kwargs)
        except Exception as e:
            await asyncio.sleep(.5)
            self.loop.add_callback(self.restart)
            raise e
        return response
    return wrapper
