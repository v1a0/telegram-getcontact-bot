"""
Telegram GetContact Bot v0.1

phone_check module by SERJ.WS. and _Skill_
Telegram bot realization by V1A0
"""

import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import base64
import time
import hmac
import hashlib
import binascii
import json
from Crypto.Cipher import AES

"""
AES_KEY and TOKEN you have to take from

/data/data/app.source.getcontact/shared_prefs/GetContactSettingsPref.xml

API_TOKEN from Telegram BotFather bot

@BotFather
"""

'     C H A N G E    T H E S E    L I N E S    B E F O R E    R U N !       '
'=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V=V='

API_TOKEN = '1234567890:AAAABBCCDDEEEFFFGgGHhHJjJKkKLlLMMmf'                 # TG BOT's TOKEN
AES_KEY = '123a1234bb66660000d00ff0f00000f0ff00000f000f000ff9ff9990000fffаf' # FINAL_KEY from GetContactSettingsPref.xml
TOKEN = 'fsffFFFFFlj888s3ffmka234DDdfomIOMNOIJOIfjidjfnu87syfy73hfhkf'       # TOKEn from GetContactSettingsPref.xml
TG_ID = 123456789                                                            # Your telegram id

'=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^=^='


key = b'2Wq7)qkX~cp7)H|n_tc&o+:G_USN3/-uIi~>M+c ;Oq]E{t9)RC_5|lhAA_Qq%_4'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Authorization decorator
def auth(func):
    async def firewall(message):

        # Easy user filter
        if message['from']['id'] != TG_ID:
            return await message.reply("Access Denied", reply=False)

        return await func(message)

    return firewall


# /start and /help echos
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Alive")


# Got any message script
@dp.message_handler()
@auth
async def main(message: types.Message):

    async def phone_check(message: types.Message):
        '''
        by  SERJ.WS. Modded for python by _Skill_
        '''

        class AESCipher(object):

            def __init__(self, AES_KEY):
                self.bs = AES.block_size
                self.AES_KEY = binascii.unhexlify(AES_KEY)

            def encrypt(self, raw):
                raw = self._pad(raw)
                cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
                return base64.b64encode(cipher.encrypt(raw.encode()))

            def decrypt(self, enc):
                enc = base64.b64decode(enc)
                cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
                return self._unpad(cipher.decrypt(enc)).decode('utf-8')

            def _pad(self, s):
                return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

            @staticmethod
            def _unpad(s):
                return s[:-ord(s[len(s) - 1:])]

        aes = AESCipher(AES_KEY)

        def sendPost(url, data, sig, ts):
            headers = {'X-App-Version': '4.9.1',
                       'X-Token': TOKEN,
                       'X-Os': 'android 5.0',
                       'X-Client-Device-Id': '14130e29cebe9c39',
                       'Content-Type': 'application/json; charset=utf-8',
                       'Accept-Encoding': 'deflate',
                       'X-Req-Timestamp': ts,
                       'X-Req-Signature': sig,
                       'X-Encrypted': '1'}
            r = requests.post(url, data=data, headers=headers, verify=True)
            return json.loads(aes.decrypt(r.json()['data']))

        def getByPhone(phone):
            ts = str(int(time.time()))
            req = f'"countryCode":"RU","source":"search","token":"{TOKEN}","phoneNumber":"{phone}"'
            req = '{' + req + '}'
            string = str(ts) + '-' + req
            sig = base64.b64encode(hmac.new(key, string.encode(), hashlib.sha256).digest()).decode()
            crypt_data = aes.encrypt(req)
            return sendPost('https://pbssrv-centralevents.com/v2.5/search',
                            b'{"data":"' + crypt_data + b'"}', sig, ts)

        def getByPhoneTags(phone):
            ts = str(int(time.time()))
            req = f'"countryCode":"RU","source":"details","token":"{TOKEN}","phoneNumber":"{phone}"'
            req = '{' + req + '}'
            string = str(ts) + '-' + req
            sig = base64.b64encode(hmac.new(key, string.encode(), hashlib.sha256).digest()).decode()
            crypt_data = aes.encrypt(req)
            return sendPost('https://pbssrv-centralevents.com/v2.5/number-detail',
                            b'{"data":"' + crypt_data + b'"}', sig, ts)

        def main__(phone):
        
            if '+7' not in phone:
                if '7' not in phone[0:2]:
                    phone = '7' + phone
                if '+' not in phone[0:2]:
                    phone = '+' + phone

            answer = f"======================\n{phone}\n"

            finfo = getByPhone(phone)
            if finfo['result']['profile']['displayName']:
                answer += str(finfo['result']['profile']['displayName']) + '\n' + 'Тегов найдено: ' + str(finfo['result']['profile']['tagCount']) + '\n'
                try:
                    answer += '\n'.join([i['tag'] for i in getByPhoneTags(phone)['result']['tags']]) + '\n'
                except KeyError:
                    if finfo['result']['profile']['tagCount'] > 0:
                        answer += 'Теги найдены, но для просморта нужен премиум' + '\n'
                    else:
                        answer += 'Тегов не найдено!'+ '\n'
            else:
                answer += 'Не найдено!' + '\n'

            answer += 'Осталось обычных поисков: ' + str(
                finfo['result']['subscriptionInfo']['usage']['search']['remainingCount']) + '/' + str(
                finfo['result']['subscriptionInfo']['usage']['search']['limit']) + '\n'

            answer += 'С тегами: ' + str(
                finfo['result']['subscriptionInfo']['usage']['numberDetail']['remainingCount']) + '/' + str(
                finfo['result']['subscriptionInfo']['usage']['numberDetail']['limit']) + '\n'
            answer += '======================'

            return answer

        try:
            await message.reply(f" {main__(message.text)}", reply=False)

        except:
            await message.reply(f"Something is wrong...", reply=True)


    await phone_check(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
