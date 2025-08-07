import httpx
import time
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from flask import Flask, request, jsonify
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify, request
import asyncio


import data_pb2
import encode_id_clan_pb2


####################################
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
####################################
app = Flask(__name__)
###########FREE-FIRE-VERSION###########
freefire_version = "ob50"
#############KEY-AES-CBC#############
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
############ENCRYPT-UID##############
def Encrypt_ID(x):
    x = int(x)
    dec = [ '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx= [ '1','01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', 
    '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x= x/128 
    if x>128:
        x =x/128
        if x >128:
            x= x/128
            if x>128:
                x= x/128
                strx= int(x)
                y= (x-int(strx))*128
                stry =str(int(y))
                z = (y-int(stry))*128
                strz =str(int(z))
                n =(z-int(strz))*128
                strn=str(int(n))
                m=(n-int(strn))*128
                return dec[int(m)]+dec[int(n)]+dec[int(z)]+dec[int(y)]+xxx[int(x)]
            else:
                strx= int(x)
                y= (x-int(strx))*128
                stry =str(int(y))
                z = (y-int(stry))*128
                strz =str(int(z))
                n =(z-int(strz))*128
                strn=str(int(n))
                return dec[int(n)]+dec[int(z)]+dec[int(y)]+xxx[int(x)]
def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()
######ENCRYPT&DECRYPT-ID-EMOTES#######
def Encrypt_id_emote(uid):
    result = []
    while uid > 0:
        byte = uid & 0x7F
        uid >>= 7
        if uid > 0:
            byte |= 0x80
        result.append(byte)
    return bytes(result).hex()
def Decrypt_id_emote(uidd):
    bytes_value = bytes.fromhex(uidd)
    r, _ = 0, 0
    for byte in bytes_value:
        r |= (byte & 0x7F) << _
        if not (byte & 0x80):
            break
        _ += 7
    return r
############convert_timestamp##########
def convert_timestamp(release_time):
    return datetime.utcfromtimestamp(release_time).strftime('%Y-%m-%d %H:%M:%S')
##############generate_packet##########
jwt_token = None
async def get_jwt_token():
    global jwt_token
    url = "https://free-fire-jwt-sumi.vercel.app/token?uid=3824584609&password=0290B4F2D8AB870BD11A845B214D9BEC9883C573877A9F4D43B47199672404BD"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    jwt_token = data['token']
                    print("JWT Token updated successfully.")
                    print(f"Token: {token}")
                else:
                    print("Failed to get JWT token: Status is not success.")
            else:
                print(f"Failed to get JWT token: HTTP {response.status_code}")
    except httpx.RequestError as e:
        print(f"Request error: {e}")

async def token_updater():
    while True:
        await get_jwt_token()
        await asyncio.sleep(8 * 3600)

async def startup():
    await get_jwt_token()
    asyncio.create_task(token_updater())
@app.route('/get_clan_info', methods=['GET'])
async def get_clan_info():
    global jwt_token
    if not jwt_token:
        return jsonify({"error": "JWT token is missing or invalid"}), 500
    clan_id = request.args.get('clan_id')
    if not clan_id:
        return jsonify({"error": "Clan ID is required"}), 400
    json_data = '''
    {{
        "1": {},
        "2": 1
    }}
    '''.format(clan_id)
    data_dict = json.loads(json_data)
    my_data = encode_id_clan_pb2.MyData()
    my_data.field1 = data_dict["1"]
    my_data.field2 = data_dict["2"]
    print(clan_id)
    data_bytes = my_data.SerializeToString()
    padded_data = pad(data_bytes, AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(padded_data)
    formatted_encrypted_data = ' '.join([f"{byte:02X}" for byte in encrypted_data])
    url = "https://clientbp.ggblueshark.com/GetClanInfoByClanID"
    data_hex = formatted_encrypted_data
    data_bytes = bytes.fromhex(data_hex.replace(" ", ""))
    headers = {
        "Expect": "100-continue",
        "Authorization": f"Bearer {token}",
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
        response = await client.post(url, headers=headers, data=data_bytes)
    if response.status_code == 200:
        if response.content:
            response_message = data_pb2.response()
            response_message.ParseFromString(response.content)
            timestamp1_normal = datetime.fromtimestamp(response_message.timestamp1)
            timestamp2_normal = datetime.fromtimestamp(response_message.timestamp2)
            last_active_normal = datetime.fromtimestamp(response_message.last_active)
            return jsonify({
                "id": response_message.id,
                "clan_name": response_message.special_code,
                "timestamp1": timestamp1_normal.strftime("%Y-%m-%d %H:%M:%S"),
                "value_a": response_message.value_a,
                "status_code": response_message.status_code,
                "sub_type": response_message.sub_type,
                "version": response_message.version,
                "level": response_message.level,
                "flags": response_message.flags,
                "welcome_message": response_message.welcome_message,
                "region": response_message.region,
                "json_metadata": response_message.json_metadata,
                "big_numbers": response_message.big_numbers,
                "balance": response_message.balance,
                "score": response_message.score,
                "upgrades": response_message.upgrades,
                "achievements": response_message.achievements,
                "total_playtime": response_message.total_playtime,
                "energy": response_message.energy,
                "rank": response_message.rank,
                "xp": response_message.xp,
                "timestamp2": timestamp2_normal.strftime("%Y-%m-%d %H:%M:%S"),
                "error_code": response_message.error_code,
                "last_active": last_active_normal.strftime("%Y-%m-%d %H:%M:%S"),
                "guild_details": {
                    "region": response_message.guild_details.region,
                    "clan_id": response_message.guild_details.clan_id,
                    "members_online": response_message.guild_details.members_online,
                    "total_members": response_message.guild_details.total_members,
                    "regional": response_message.guild_details.regional,
                    "reward_time": response_message.guild_details.reward_time,
                    "expire_time": response_message.guild_details.expire_time
                }
            })
        else:
            return jsonify({"error": "No content in response"}), 500
    else:
        return jsonify({"error": f"Failed to fetch data: {response.status_code}"}), response.status_code




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    app.run(host='0.0.0.0', port=5000)
