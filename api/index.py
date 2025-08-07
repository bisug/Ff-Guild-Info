from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import asyncio
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json

import data_pb2
import encode_id_clan_pb2

app = FastAPI()

freefire_version = "ob50"

key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

jwt_token = None  # Global token variable

async def get_jwt_token():
    global jwt_token
    url = "https://free-fire-jwt-sumi.vercel.app/token?uid=3824584609&password=0290B4F2D8AB870BD11A845B214D9BEC9883C573877A9F4D43B47199672404BD"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "token" in data:
                    jwt_token = data["token"]
                    print("JWT Token updated successfully")
                else:
                    print("JWT token fetch failed or invalid status")
            else:
                print(f"JWT token fetch HTTP error: {response.status_code}")
        except Exception as e:
            print(f"Exception fetching JWT token: {e}")

async def token_refresher():
    while True:
        await get_jwt_token()
        await asyncio.sleep(8 * 3600)  # Refresh every 8 hours

@app.on_event("startup")
async def startup_event():
    await get_jwt_token()
    asyncio.create_task(token_refresher())

@app.get("/get_clan_info")
async def get_clan_info(clan_id: int):
    global jwt_token
    if not jwt_token:
        raise HTTPException(status_code=500, detail="JWT token is missing or invalid")

    # Prepare protobuf data
    my_data = encode_id_clan_pb2.MyData()
    my_data.field1 = clan_id
    my_data.field2 = 1
    data_bytes = my_data.SerializeToString()
    padded_data = pad(data_bytes, AES.block_size)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(padded_data)

    url = "https://clientbp.ggblueshark.com/GetClanInfoByClanID"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": freefire_version,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
        "Host": "clientbp.ggblueshark.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, data=encrypted_data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch data")

    # Parse protobuf response
    response_message = data_pb2.response()
    response_message.ParseFromString(response.content)

    def ts_to_str(ts):
        return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None

    return {
        "id": response_message.id,
        "clan_name": response_message.special_code,
        "timestamp1": ts_to_str(response_message.timestamp1),
        "timestamp2": ts_to_str(response_message.timestamp2),
        "last_active": ts_to_str(response_message.last_active),
        "score": response_message.score,
        "xp": response_message.xp,
        "rank": response_message.rank,
        # Add more fields as needed
    }

# To run, use: uvicorn yourfilename:app --host 0.0.0.0 --port 8000
