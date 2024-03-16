import base64
import json
import os
import pathlib
import random
import urllib.request
import uuid
from enum import Enum
from time import time
from typing import Union
import urllib.parse

import aiohttp
import binascii
import asyncio

_DEBUG = False

_PROXY = urllib.request.getproxies().get("https")

_BASE_OPTION_SETS = [
    "fluxsydney",
	"nojbf", # no jailbreak filter
	"iyxapbing",
	"iycapbing",
	"dgencontentv3",
	"nointernalsugg",
	"disable_telemetry",
	"machine_affinity",
	"streamf",
	"langdtwb",
	"fdwtlst",
	"fluxprod",
	"eredirecturl",
	"gptvnodesc",  # may related to image search
	"gptvnoex",    # may related to image search
	"codeintfile", # code interpreter + file uploader
	"sdretrieval", # retrieve upload file
	"gamaxinvoc",  # file reader invocation
	"ldsummary",   # our guess: long document summary
	"ldqa",        # our guess: long document quality assurance
    "gpt4tmncnp"
]



class _OptionSets(Enum):
    CREATIVE = _BASE_OPTION_SETS + ["h3imaginative"]
    CREATIVECLASSIC = _BASE_OPTION_SETS 
    BALANCED = _BASE_OPTION_SETS + ["galileo"] + ["gldcl1p"]
    PRECISE = _BASE_OPTION_SETS + ["h3precise"]
    


_SLICE_IDS = [
    "schurmsg",
    "ntbkcf",
    "rankcf",
    "bgstreamcf",
    "cmcallapptf",
    "vnextvoicecf",
    "tts5cf",
    "abv2mobcf",
    "ctvismctrl",
    "suppsm240rev10-t",
    "suppsm240-t",
    "translrefctrl",
    "1215perscs0",
    "0212bops0",
    "116langwb",
    "0112wtlsts0",
    "118wcsmw",
    "1201reasons0",
    "0116trimgd",
    "cacfastapis"
]


class _LocationHint(Enum):
    USA = {
        "locale": "en-US",
        "LocationHint": [
            {
                "country": "United States",
                "state": "California",
                "city": "Los Angeles",
                "timezoneoffset": 8,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 34.0536909,
                    "Longitude": -118.242766,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }
    CHINA = {
        "locale": "zh-CN",
        "LocationHint": [
            {
                "country": "China",
                "state": "",
                "city": "Beijing",
                "timezoneoffset": 8,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 39.9042,
                    "Longitude": 116.4074,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }
    EU = {
        "locale": "en-IE",
        "LocationHint": [
            {
                "country": "Norway",
                "state": "",
                "city": "Oslo",
                "timezoneoffset": 1,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 59.9139,
                    "Longitude": 10.7522,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }
    UK = {
        "locale": "en-GB",
        "LocationHint": [
            {
                "country": "United Kingdom",
                "state": "",
                "city": "London",
                "timezoneoffset": 0,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 51.5074,
                    "Longitude": -0.1278,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }

_DELIMITER = '\x1e'
_FORWARDED_IP = f"1.0.0.{random.randint(0, 255)}"

_ALLOWED_MESSAGE_TYPES = [
    "ActionRequest",
    "Chat",
    "Context",
    "InternalSearchQuery",
    "InternalSearchResult",
    "InternalLoaderMessage",
    "Progress",
    "GenerateContentQuery",
    "SearchQuery",
    "GeneratedCode",
]
        
def sec_ms_gec():
    random_bytes = os.urandom(32)
    return binascii.hexlify(random_bytes).decode()

_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"113.0.1774.50"',
    "sec-ch-ua-full-version-list": '"Microsoft Edge";v="113.0.1774.50", "Chromium";v="113.0.5672.127", "Not-A.Brand";v="24.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-ms-gec": sec_ms_gec(),
    "sec-ms-gec-version": "1-115.0.1866.1",
    "x-ms-client-request-id": str(uuid.uuid4()),
    "x-ms-useragent": "azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.10.0 OS/Win32",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50",
    "Referer": "https://www.bing.com/search?q=Bing+AI&showconv=1",
    "Referrer-Policy": "origin-when-cross-origin",
    "x-forwarded-for": _FORWARDED_IP,
}

SYDNEY_HEADER = _HEADERS.update(
    {
        "Host": "sydney.bing.com",
        "Cache-Control": "no-cache",
        "Connection": "Upgrade",
        "Origin": "https://www.bing.com",
        "Pragma": "no-cache",
    })

_HEADERS_INIT_CONVER = {
    "accept": "application/json",
    "accept-language": "en;q=0.9,en-US;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Not A(Brand";v="99", '
                 '"Microsoft Edge";v="121", '
                 '"Chromium";v="121"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"121.0.2277.128"',
    "sec-ch-ua-full-version-list": '"Not A(Brand";v="99.0.0.0", '
                                   '"Microsoft Edge";v="121.0.2277.128", '
                                   '"Chromium";v="121.0.6167.184"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "upgrade-insecure-requests": "1",
    "x-edge-shopping-flag": "1",
    "X-Ms-Useragent": "azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.12.3 OS/Windows",
    "x-forwarded-for": _FORWARDED_IP,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36 "
                  "Edg/121.0.0.0",
}

SYDNEY_INIT_HEADER = _HEADERS_INIT_CONVER.update(
    {
        "Referer": "https://copilot.microsoft.com/",
        "X-Edge-Shopping-Flag": "0",
    })

BUNDLE_VERSION = "1.1573.4"

def _print(msg):
    if _DEBUG:
        print(msg)


def _format(msg: dict) -> str:
    return json.dumps(msg, ensure_ascii=False) + _DELIMITER


async def create_conversation(
        proxy: str | None = _PROXY,
        cookies: list[dict] | None = None,
):
    formatted_cookies = {}
    if cookies:
        for cookie in cookies:
            formatted_cookies[cookie["name"]] = cookie["value"]
    async with aiohttp.ClientSession(
            cookies=formatted_cookies,
            headers=SYDNEY_INIT_HEADER,
    ) as session:
        timeout = aiohttp.ClientTimeout(total=30)
        try:
            response = await session.get(
                url=os.environ.get("BING_PROXY_URL")
                    or f"https://edgeservices.bing.com/edgesvc/turing/conversation/create"
                       f"?bundleVersion={BUNDLE_VERSION}",
                proxy=proxy,
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            print("Request timedout, retrying...")
            response = await session.get(
                url=os.environ.get("BING_PROXY_URL")
                    or f"https://edgeservices.bing.com/edgesvc/turing/conversation/create"
                       f"?bundleVersion={BUNDLE_VERSION}",
                proxy=proxy,
                timeout=timeout,
            )
    if response.status != 200:
        text = await response.text()
        raise Exception(f"Authentication failed {text}") #todo get raised exception and return it to the bot message text
    try:
        conversation = await response.json()
    except:
        text = await response.text()
        raise Exception(text)
    if conversation["result"]["value"] != "Success":
        raise Exception("failed to create the conversation: message: " + conversation["result"]["message"])
    if 'X-Sydney-Encryptedconversationsignature' in response.headers:
        conversation['sec_access_token'] = response.headers['X-Sydney-Encryptedconversationsignature']
    
    return conversation
    #todo Iterates over "set-cookie" headers, parses values, and logs modified cookies.
    # if 'set-cookie' in response.headers:
    #     modified_cookies = {}
    #     for cookie_header in response.headers['set-cookie']:
    #         # Split by semicolon and select first part before semicolon
    #         cookie_parts = cookie_header.split(';')[0].split('=')
    #         if len(cookie_parts) == 2:
    #             cookie_name, cookie_value = cookie_parts
    #             # Parse cookies from string (assuming appropriate function exists)
    #             parsed_cookie = parse_cookie(cookie_header)
    #             if parsed_cookie:
    #                 modified_cookies[cookie_name] = parsed_cookie

    #     # Log modified cookies for further action
    #     for cookie_name, cookie_value in modified_cookies.items():
    #         print(f"Modified cookie: {cookie_name} = {cookie_value}")

    #     # Update session cookies with modified values (if applicable)
    #     # ... (update logic based on framework/library)



def _get_location_hint_from_locale(locale: str) -> Union[dict, None]:
    locale = locale.lower()
    if locale == "en-gb":
        hint = _LocationHint.UK.value
    elif locale == "en-ie":
        hint = _LocationHint.EU.value
    elif locale == "zh-cn":
        hint = _LocationHint.CHINA.value
    else:
        hint = _LocationHint.USA.value
    return hint.get("LocationHint")


async def ask_stream(
        conversation: dict,
        prompt: str,
        context: str,
        conversation_style: str = "creative",
        locale: str = "en-US",
        proxy=_PROXY,
        image_url=None,
        wss_url='wss://sydney.bing.com/sydney/ChatHub',
        cookies: list[dict] | None = None,
        no_search: bool = False,
):
    timeout = aiohttp.ClientTimeout(total=900)
    formatted_cookies = {}
    if cookies:
        for cookie in cookies:
            formatted_cookies[cookie["name"]] = cookie["value"]
    async with aiohttp.ClientSession(timeout=timeout, cookies=formatted_cookies) as session:
        conversation_id = conversation["conversationId"]
        client_id = conversation["clientId"]
        sec_access_token = conversation["sec_access_token"] if 'sec_access_token' in conversation else None
        conversation_signature = conversation["conversationSignature"] if 'conversationSignature' in conversation else None
        message_id = str(uuid.uuid4())

        async with session.ws_connect(
                # wss_url,
                wss_url + ('?sec_access_token=' + urllib.parse.quote_plus(sec_access_token) if sec_access_token else ''),
                autoping=False,
                headers=SYDNEY_HEADER,
                proxy=proxy
        ) as wss:
            await wss.send_str(_format({'protocol': 'json', 'version': 1}))
            await wss.receive(timeout=900)
            await wss.send_str(_format({"type": 6}))
            option_sets = getattr(_OptionSets, conversation_style.upper()).value.copy()
            if no_search:
                option_sets += 'nosearchall'

            struct = {
                'arguments': [
                    {
                        'optionsSets': option_sets,
                        'source': 'cib',
                        'allowedMessageTypes': _ALLOWED_MESSAGE_TYPES,
                        'sliceIds': _SLICE_IDS,
                        "verbosity": "verbose",
                        "scenario": "SERP",
                        'traceId': os.urandom(16).hex(),
                        'requestId': message_id,
                        'isStartOfSession': True, #there can be an option to have continous reply
                        'message': {
                            "locale": locale,
                            "market": locale,
                            "region": locale[-2:],  # en-US -> US
                            "locationHints": _get_location_hint_from_locale(locale),
                            "author": "user",
                            "inputMethod": "Keyboard",
                            "text": prompt,
                            "messageType": "Chat", #random.choice(["Chat", "CurrentWebpageContextRequest"]),
                            "requestId": message_id,
                            "messageId": message_id,
                            "imageUrl": image_url or None,
                        },
                        "tone": conversation_style.capitalize(),
                        'conversationSignature': conversation_signature if conversation_signature else None,
                        'participant': {
                            'id': client_id
                        },
                        "spokenTextMode": "None",
                        'conversationId': conversation_id,
                        'previousMessages': [
                            {
                                "author": "user",
                                "description": context,
                                "contextType": "WebPage",
                                "messageType": "Context",
                                "messageId": "discover-web--page-ping-mriduna-----",
                            },
                        ]
                    }
                ],
                'invocationId': '0',
                'target': 'chat',
                'type': 4
            }

            # struct = json.loads(pathlib.Path('struct.json').read_text())
            # struct['arguments'][0]['optionsSets'] = option_sets
            # struct['arguments'][0]['sliceIds'] = _SLICE_IDS
            # struct['arguments'][0]['traceId'] = struct1['arguments'][0]['traceId']
            # struct['arguments'][0]['requestId'] = message_id
            # struct['arguments'][0]['message']['requestId'] = message_id
            # struct['arguments'][0]['message']['messageId'] = message_id
            # struct['arguments'][0]['conversationSignature'] = conversation_signature
            # struct['arguments'][0]['conversationId'] = conversation_id
            # struct['arguments'][0]['previousMessages'] = struct1['arguments'][0]['previousMessages']

            await wss.send_str(_format(struct))
            _print(f'Sent:\n{json.dumps(struct)}')

            retry_count = 5
            while True:
                if wss.closed:
                    break
                msg = await wss.receive(timeout=900)

                if not msg.data:
                    retry_count -= 1
                    if retry_count == 0:
                        raise Exception("No response from server")
                    continue

                if isinstance(msg.data, str):
                    objects = msg.data.split(_DELIMITER)
                else:
                    continue

                for obj in objects:
                    if int(time()) % 6 == 0:
                        await wss.send_str(_format({"type": 6}))
                        _print(f'Sent:\n{json.dumps({"type": 6})}')
                    if not obj:
                        continue
                    response = json.loads(obj)
                    _print(f'Received:\n{obj}')
                    if response["type"] == 2:
                        if response["item"]["result"].get("error"):
                            raise Exception(
                                f"{response['item']['result']['value']}: {response['item']['result']['message']}")
                    yield response
                    if response["type"] == 2:
                        break


async def upload_image(filename=None, img_base64=None, proxy=None):
    async with aiohttp.ClientSession(
            headers={"Referer": "https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx"}
    ) as session:
        timeout = aiohttp.ClientTimeout(total=90)
        url = "https://www.bing.com/images/kblob"

        payload = {
            "imageInfo": {},
            "knowledgeRequest": {
                "invokedSkills": ["ImageById"],
                "subscriptionId": "Bing.Chat.Multimodal",
                "invokedSkillsRequestData": {"enableFaceBlur": False},
                "convoData": {
                    "convoid": "",
                    "convotone": "Creative"
                }
            }
        }

        if filename is not None:
            with open(filename, 'rb') as f:
                file_data = f.read()
                image_base64 = base64.b64encode(file_data)
        elif img_base64 is not None:
            image_base64 = img_base64
        else:
            raise Exception('no image provided')

        data = aiohttp.FormData()
        data.add_field('knowledgeRequest', json.dumps(payload), content_type="application/json")
        data.add_field('imageBase64', image_base64.decode('utf-8'), content_type="application/octet-stream")
        try:
            async with session.post(url, data=data, proxy=proxy, timeout= timeout) as resp:
                return (await resp.json())["blobId"]
        except asyncio.TimeoutError:
            raise Exception("Timedout please try again!")
