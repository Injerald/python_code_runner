import ast
import asyncio
import websockets

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exceptions import ChannelClosedByClient


async def listen_to_rabbitmq(queue_name):
    loop = asyncio.get_running_loop()

    fut = loop.create_future()
    AsyncioConnection(
        pika.ConnectionParameters('localhost'),
        on_open_callback=lambda c: fut.set_result(c),
        on_open_error_callback=lambda c, exc: fut.set_exception(exc),
        on_close_callback=lambda c, exc: fut.set_exception(exc)
    )
    conn = await fut
    fut = loop.create_future()
    conn.channel(on_open_callback=lambda ch: fut.set_result(ch))
    channel = await fut

    fut = loop.create_future()
    channel.queue_declare(queue=queue_name, durable=True, auto_delete=True, arguments={'x-expires': 86400000},
                          callback=lambda ch: fut.set_result(ch))
    cnt = await fut

    if cnt:
        messages = asyncio.Queue()
        channel.basic_consume(
            queue_name,
            on_message_callback=lambda *args: messages.put_nowait(args[3]),
            auto_ack=True
        )

        fut = loop.create_future()

        def on_close_callback(ch, reason):
            try:
                raise reason
            except ChannelClosedByClient:
                fut.cancel()
            except:
                fut.set_exception(reason)

        channel.add_on_close_callback(on_close_callback)

        while True:
            msg = asyncio.ensure_future(messages.get())
            await asyncio.wait([msg, fut], return_when=asyncio.FIRST_COMPLETED)
            if fut.done():
                if fut.cancelled():
                    break
                raise fut.exception()
            decoded_message = msg.result().decode('utf-8').replace('null', 'None')
            decoded_message_dict = ast.literal_eval(decoded_message)
            return decoded_message_dict['result']


async def get_code_result(websocket, path):
    queue_name = await websocket.recv()
    code_result = await listen_to_rabbitmq(queue_name)
    await websocket.send(code_result)


if __name__ == '__main__':
    server = websockets.serve(get_code_result, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
