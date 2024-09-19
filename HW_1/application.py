from typing import Callable, Awaitable, Any
from math import factorial
import json

def get_fibonacci(n: int, send: Callable[[dict[str, Any]], Awaitable[None]]) -> int:
    """
    Get the nth number in the Fibonacci sequence

    Args:
        n: A positive integer

    Returns:
        int: The nth Fibonacci number
    """

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return send(
        {
            "type": "http.response.body",
            "body": bytes(f"{b}", "utf-8"),
        }
    )

def get_mean(numbers: list[float]) -> float:
    """
    Get the mean of a list of float numbers

    Args:
        numbers: A list of float numbers

    Returns:
        float: The mean of the numbers
    """

    return sum(numbers) / len(numbers)

def get_factorial(n: int, send: Callable[[dict[str, Any]], Awaitable[None]]) -> int:
    """
    Get the factorial of a number

    Args:
        n: A positive integer

    Returns:
        int: The factorial of the number
    """

    return send(
        {
            "type": "http.response.body",
            "body": bytes(f"{factorial(n)}", "utf-8"),
        }
    )

async def application(scope, receive, send):
    assert scope["type"] == "http"
    path = scope["path"]

    if path.startswith("/fibonacci"):
        n = int(path.split("/")[-1])
        if n < 0:
            await send(
                {
                    "type": "http.response.start",
                    "status": 400,
                    "headers": [
                        [b"content-type", b"text/plain"],
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"Invalid value for n. n must be non-negative.",
                }
            )
        else:
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"content-type", b"text/plain"],
                    ],
                }
            )
            await get_fibonacci(n, send)
    elif path == "/mean":
        await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"content-type", b"text/plain"],
                    ],
                }
            )
        message = await receive()
        if message["type"] == "http.request.body":
            body = message["body"]
            list_data = json.loads(body)
            print(body)
            print(list_data)
            
            # await send(
            #     {
            #         "type": "http.response.body",
            #         "body": b"The mean is the average of a set of numbers.",
            #     }
            # )
    elif path == "/factorial":
        query_string = scope["query_string"]
        n = int(query_string)
        if n < 0:
            await send(
                {
                    "type": "http.response.start",
                    "status": 400,
                    "headers": [
                        [b"content-type", b"text/plain"],
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"Invalid value for n. n must be non-negative.",
                }
            )
        else:
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"content-type", b"text/plain"],
                    ],
                }
            )
            await get_factorial(n, send)
    else:
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [
                    [b"content-type", b"text/plain"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"Not Found",
            }
        )
