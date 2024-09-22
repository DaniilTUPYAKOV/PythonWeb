from typing import Callable, Awaitable, Any
from math import factorial
import json
from urllib.parse import parse_qs


async def answer(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status_code: int = 404,
    answer_body: bytes = b"Not Found",
    content_type: bytes = b"text/plain",
):
    """
    Send an HTTP response with the given status code and body.

    Args:
        send: The async function to send the response
        status_code: The HTTP status code to send (default 400)
        answer_body: The response body to send (default b"Bad Request")
        content_type: The content type of the response

    Returns:
        None
    """
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                [b"content-type", content_type],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": answer_body,
        }
    )


async def get_fibonacci(
    path: str, send: Callable[[dict[str, Any]], Awaitable[None]]
) -> None:
    """
    Send response with the nth fibonacci number if the request is correct,
    otherwise send a 422 (Unprocessable Entity)

    Args:
        path: The requested URL path,
        send: The async function to send the response

    Returns:
        None
    """
    try:
        n = int(path.split("/")[-1])
    except ValueError:
        await answer(send, 422, b"Unprocessable Entity")
        return

    if n < 0:
        await answer(send, 400, b"Invalid value for n. n must be non-negative.")
        return

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    await answer(
        send, 200, json.dumps({"result": a}).encode("utf-8"), b"application/json"
    )


async def get_mean(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    receive: Callable[[], Awaitable[dict[str, Any]]],
) -> float:
    """
    A function that receives a list of numbers from the client, and
    sends the mean of the list back to the client.

    If the list is empty, it sends a 400 (Bad Request) response.
    """
    received_list = []
    more_data = True
    while more_data:
        message = await receive()
        if message["type"] == "http.request":
            body = message["body"]
            if body == b"":
                await answer(send, 422, b"Unprocessable Entity")
                return
            received_list += json.loads(body)
            more_data = message["more_body"]

    if len(received_list) == 0:
        await answer(send, 400, b"Bad Request")
        return

    await answer(
        send,
        200,
        json.dumps({"result": sum(received_list) / len(received_list)}).encode("utf-8"),
        b"application/json",
    )


async def get_factorial(
    query: str, send: Callable[[dict[str, Any]], Awaitable[None]]
) -> int:
    """
    A function that gets a query string, parses it, and responds with the factorial
    of the value of the "n" key in the query string.
    If the value of the "n" key is not a number, or is negative, it returns an
    appropriate HTTP error.
    """
    query_args = parse_qs(query)
    if b"n" in query_args:
        try:
            n = int(query_args[b"n"][0])
        except ValueError:
            await answer(send, 422, b"Unprocessable Entity")
            return

        if n < 0:
            await answer(send, 400, b"Invalid value for n. n must be non-negative.")
            return

        await answer(
            send,
            200,
            json.dumps({"result": factorial(n)}).encode("utf-8"),
            b"application/json",
        )
        return
    await answer(send, 422, b"Unprocessable Entity")


async def application(
    scope: dict,
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    """
    The main application function that routes to the proper function based on
    the URL path.

    Args:
        scope: The scope of the request.
        receive: The function to receive the request body.
        send: The function to send the response.

    Returns:
        None
    """
    assert scope["type"] == "http"
    path = scope["path"]

    if path.startswith("/fibonacci"):
        await get_fibonacci(path, send)
    elif path == "/mean":
        await get_mean(send, receive)
    elif path == "/factorial":
        await get_factorial(scope["query_string"], send)
    else:
        await answer(send)
