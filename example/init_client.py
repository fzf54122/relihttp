import asyncio

from relihttp import (AbstractClient,
                      ClientTypeEnum,
                      TransportError)

def client_main():
    client = AbstractClient.create_client(ClientTypeEnum.SYNC,logger=True)
    url = 'http://127.0.0.1:8000'

    try:
        resp = client.get(url, headers={"Accept": "application/json"})
        print(resp.json())
    except TransportError as e:
        print("Error: {}".format(e))

async def async_main():
    url = 'http://127.0.0.1:8000'
    # async with AbstractClient.create_client(ClientTypeEnum.ASYNC) as client:
    #     url = 'http://127.0.0.1:8000'
    #     try:
    #         resp = await client.get(url, headers={"Accept": "application/json"})
    #         print(resp.json())
    #     except TransportError as e:
    #         print("Error: {}".format(e))
    client = AbstractClient.create_client(ClientTypeEnum.ASYNC)
    try:
        resp = await client.get(url, headers={"Accept": "application/json"})
        print(resp.json())
    except TransportError as e:
        print("Error: {}".format(e))
    finally:
        await client.close()

if __name__ == "__main__":
    # asyncio.run(async_main())
    client_main()
