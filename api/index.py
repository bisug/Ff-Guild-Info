from fastapi import FastAPI, Request
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

# AES keys
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

jwt_token = None

async def get_jwt_token():
    global jwt_token
    url = "https://free-fire-jwt-sumi.vercel.app/token?uid=3824584609&password=0290B4F2D8AB870BD11A845B214D9BEC9883C573877A9F4D43B47199672404BD"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            jwt_token = data.get("token")

@app.on_event("startup")
async def startup_event():
    await get_jwt_token()

@app.get("/get_clan_info")
async def get_clan_info(request: Request):
    global jwt_token
    clan_id = request.query_params.get("clan_id")
    if not clan_id:
        return JSONResponse(content={"error": "Clan ID is required"}, status_code=400)

    json_data = {
        "1": int(clan_id),
        "2": 1
    }

    my_data = encode_id_clan_pb2.MyData()
    my_data.field1 = json_data["1"]
    my_data.field2 = json_data["2"]
    data_bytes = my_data.SerializeToString()
    padded_data = pad(data_bytes, AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(padded_data)

    url = "https://clientbp.ggblueshark.com/GetClanInfoByClanID"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "ob50",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
        "Host": "clientbp.ggblueshark.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, data=encrypted_data)

    if response.status_code == 200:
        response_message = data_pb2.response()
        response_message.ParseFromString(response.content)
        return {
            "id": response_message.id,
            "clan_name": response_message.special_code,
            "timestamp1": datetime.fromtimestamp(response_message.timestamp1).strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp2": datetime.fromtimestamp(response_message.timestamp2).strftime("%Y-%m-%d %H:%M:%S"),
            "last_active": datetime.fromtimestamp(response_message.last_active).strftime("%Y-%m-%d %H:%M:%S"),
            "score": response_message.score,
            "xp": response_message.xp,
            "rank": response_message.rank
            # Add more fields as needed
        }
    else:
        return JSONResponse(content={"error": "Failed to fetch data"}, status_code=response.status_code) 
