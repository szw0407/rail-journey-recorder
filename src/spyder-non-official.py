import httpx
import json
import asyncio
import multiprocessing

BASE_URL = "http://cnrail.geogv.org/api/v1/"

def get_route_data(i, url, char):
    while True:
        try:
            a = httpx.get(
                url+ char + str(i).zfill(4) + "?locale=zhcn&query-override=&requestGeom=true"
            )
        except Exception as e:
            pass
        else:
            break
    if a.status_code == 200:
        print(char, i)
        s = json.dumps(a.json(), ensure_ascii=False, indent=4)
        with open("data.json", "a", encoding='UTF-8') as f:
            f.write(s+",\n")
        # print("Data length: ", len(data))


# async def get_route():
#     chars = (
#         'K', 'T', 'Z', 'D', 'G', 'C', '', 'S', 'Y'
#     )
#     url = BASE_URL + "route/CN~"
#     for char in chars:
#         url += char
#         async with httpx.AsyncClient() as client:
#             # for i in range(10000):
#             # response = httpx.get(url+str(i).zfill(4) + '?locale=zhcn&query-override=&requestGeom=true')
#             # use asyicio for httpx
#                 # response = await client.get(url+str(i).zfill(4) + '?locale=zhcn&query-override=&requestGeom=true')
#                 # if response.status_code == 200:
#                 #     print(response.json())
#                 #     data.append(response.json())
#                 # make the above faster with multi-threading
#                 tasks = []
#                 async def get_data(i):
#                     a = await client.get(url+str(i).zfill(4) + '?locale=zhcn&query-override=&requestGeom=true')
#                     if a.status_code == 200:
#                         print(a.json())
#                         data.append(a.json())
#                 for i in range(1,10000):
#                     tasks.append(get_data(i))
#                 await asyncio.gather(*tasks)
#                 # async for response in responses:
#                 #     if response.status_code == 200:
#                 #         print(response.json())
#                 #         data.append(response.json())


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    chars = ("K", "T", "Z", "D", "G", "C", "", "S", "Y")
    url = BASE_URL + "route/CN~"

    with open("data.json", "w") as f:
        f.write("[\n")
    for char in chars:
        tasks = []
        for i in range(1, 10000):
            tasks.append(multiprocessing.Process(target=get_route_data, args=(i, url, char)))
        k = 0
        for task in tasks:
            k += 1
            # print("Starting task ", k)
            task.start()
        for task in tasks:
            task.join()
            k -= 1
            print("Remaining tasks ", k)
    with open("data.json", "a") as f:
        f.write("]\n")
