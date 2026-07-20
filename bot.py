import asyncio
import io
import re
import json
import html
import os
import httpx
import random
import string
import time
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.request import HTTPXRequest

# ওটিপি কোড সরাসরি ওয়ান-ক্লিক কপি করার লাইব্রেরি ইম্পোর্ট
try:
    from telegram import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# ==================== CONFIG SECTION ====================

BOT_TOKEN = "8684206089:AAH-FHX-izBpEIIrLDDyA2hTPt6h4R3CXdE"
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SETTINGS_FILE = "settings.json"

BOT_USERNAME = None  # রান-টাইমে অটোমেটিক আপডেট হবে

# ==================== PREMIUM EMOJI MAPPING SECTION ====================

EMOJI_ID_MAP = {
    "telegram": "5271801931814165886",
    "instagram": "5269682734820777950",
    "facebook": "5269427536453984598",
    "tiktok": "5271527792641595125",
    "x": "5269500885905468781",
    "whatsapp": "5271536803482981220",
    "up": "5244837092042750681",
    "down": "5246762912428603768",
    "add": "5397916757333654639",
    "setting": "5341715473882955310",
    "1st": "5440539497383087970",
    "2st": "5447203607294265305",
    "3rd": "5453902265922376865",
    "free": "5406756500108501710",
    "msg": "5253742260054409879",
    "link": "5271604874419647061",
    "status": "5193063022226086560",
    "home": "5416041192905265756",
    "gift_box": "5970074171449808121",
    "delete": "5422557736330106570",
    "number_change": "5267295703666824255",
    "refer_btn": "5420396762189831222",
    "get_number_btn": "5861680977994060034",
    "cross": "5420130255174145507",
    "stop": "5956074558044770726",
    "ban": "5420323339723881652",
    "loading": "5386367538735104399",
    "profile": "5382164415019768638",
    "done": "6298670698948724690",
    "otp_success": "6237550015791765281",
    "nagad": "5352985330628730418",
    "bkash": "5348469219761626211",
    "rocket": "5346042941196507141",
    "binance": "5348212415077064131",
    "live": "5355102594886833928",
    "developer": "5267294466716244344",
    "channel": "6215074610845585917",
    "copy": "5429483843541284898",
    "admin": "5350396951407895212",
    "waiting": "6217721388736712699",
    "back": "5267490665117275176",
    "leader_board": "5280769763398671636",
    "money": "6233367447789899509",
    "discord": "5807892405306791778",
    "custom_range": "5231012545799666522",
    "paypal": "5107533253946901363",
    "imo": "5337155807752524558",
    "hi": "5353027129250453493",
    "off": "5352974971167611327",
    "diamond": "5251562950698759162",
    "broadcast": "5251671501702196837",
    "key": "5296369303661067030",
    "bot_logo": "4943094697238201446",
    "tk": "5201873447554145566",
    "roket": "5188481279963715781",
    "all_done": "5859265295113261399",
    "yes": "5875017993909440887",
    "no": "5875005555684152921",
    "fire_love": "5864093929275658617"
}

FALLBACK_EMOJI_MAP = {
    "telegram": "✈️", "instagram": "📷", "facebook": "🔵", "tiktok": "🎵", "x": "❌",
    "whatsapp": "💬", "up": "📈", "down": "📉", "add": "➕", "setting": "⚙️",
    "1st": "🥇", "2st": "🥈", "3rd": "🥉", "free": "🆓", "msg": "💬", "link": "🔗",
    "status": "📊", "home": "🏠", "gift_box": "🎁", "delete": "🗑️", "number_change": "🔄",
    "get_number_btn": "📞", "cross": "❌", "stop": "🛑", "ban": "🚫", "loading": "⏳",
    "profile": "👤", "done": "✅", "otp_success": "⭐", "nagad": "🟠", "bkash": "💖",
    "rocket": "🚀", "binance": "🟡", "live": "🟢", "developer": "👨‍💻", "channel": "📢",
    "copy": "📋", "admin": "👑", "waiting": "⏳", "back": "🔙", "leader_board": "🏆",
    "custom_range": "🎯", "refer_btn": "🔗",
    "paypal": "💳", "imo": "💬", "hi": "👋", "off": "🛑", "diamond": "💎",
    "broadcast": "📢", "key": "🔑", "tk": "৳", "roket": "🚀", "all_done": "✅",
    "yes": "✔️", "no": "❌", "fire_love": "❤️"
}

PREMIUM_FLAGS = {
    "🇺🇸": "5913463998522592692",
    "🇺🇦": "5911406692007941050",
    "🇵🇱": "5913550391789752571",
    "🇰🇿": "5913724621433082323",
    "🇨🇳": "5913779335021466780",
    "🇦🇿": "5911197578640233518",
    "🇪🇺": "5911106310585193018",
    "🇦🇲": "5913272455866093666",
    "🇷🇺": "5913274246867456342",
    "🇺🇿": "5911051846104912282",
    "🇩🇪": "5911096835887337583",
    "🇯🇵": "5913293711659241040",
    "🇹🇷": "5910995113881901195",
    "🇧🇾": "5911011185649521599",
    "🇬🇧": "5913443365499703513",
    "🇮🇳": "5913754823643107921",
    "🇧🇷": "5911148568768418614",
    "🇿🇲": "5913564754160389778",
    "🇾🇪": "591334642189831222",
    "225": "5911106310585193018",
    "237": "5911106310585193018",
    "261": "5911106310585193018",
    "Egypt": "EG",
    "South Africa": "ZA",
    "Nigeria": "NG",
    "Kenya": "KE",
    "Ghana": "GH",
    "Morocco": "MA",
    "Algeria": "DZ",
    "Tunisia": "TN",
    "Libya": "LY",
    "Sudan": "SD",
    "Ethiopia": "ET",
    "Somalia": "SO",
    "Djibouti": "DJ",
    "Tanzania": "TZ",
    "Uganda": "UG",
    "Burundi": "BI",
    "Mozambique": "MZ",
    "Zambia": "ZM",
    "Zimbabwe": "ZW",
    "Namibia": "NA",
    "Malawi": "MW",
    "Lesotho": "LS",
    "Botswana": "BW",
    "Eswatini": "SZ",
    "Comoros": "KM",
    "Gambia": "GM",
    "Senegal": "SN",
    "Mauritania": "MR",
    "Mali": "ML",
    "Guinea": "GN",
    "Burkina Faso": "BF",
    "Niger": "NE",
    "Togo": "TG",
    "Benin": "BJ",
    "Mauritius": "MU",
    "Liberia": "LR",
    "Sierra Leone": "SL",
    "Chad": "TD",
    "Central African Republic": "CF",
    "Cape Verde": "CV",
    "Sao Tome and Principe": "ST",
    "Equatorial Guinea": "GQ",
    "Gabon": "GA",
    "Congo": "CG",
    "DR Congo": "CD",
    "Angola": "AO",
    "Guinea-Bissau": "GW",
    "Rwanda": "RW",
    "Eritrea": "ER",
    "United Kingdom": "GB",
    "France": "FR",
    "Germany": "DE",
    "Italy": "IT",
    "Spain": "ES",
    "Netherlands": "NL",
    "Belgium": "BE",
    "Switzerland": "CH",
    "Austria": "AT",
    "Sweden": "SE",
    "Norway": "NO",
    "Denmark": "DK",
    "Finland": "FI",
    "Portugal": "PT",
    "Ireland": "IE",
    "Hungary": "HU",
    "Poland": "PL",
    "Ukraine": "UA",
    "Lithuania": "LT",
    "Latvia": "LV",
    "Estonia": "EE",
    "Moldova": "MD",
    "Armenia": "AM",
    "Belarus": "BY",
    "Andorra": "AD",
    "Monaco": "MC",
    "San Marino": "SM",
    "Vatican City": "VA",
    "Serbia": "RS",
    "Montenegro": "ME",
    "Kosovo": "XK",
    "Croatia": "HR",
    "Slovenia": "SI",
    "Bosnia and Herzegovina": "BA",
    "North Macedonia": "MK",
    "Gibraltar": "GI",
    "Luxembourg": "LU",
    "Iceland": "IS",
    "Albania": "AL",
    "Malta": "MT",
    "Cyprus": "CY",
    "Bulgaria": "BG",
    "Slovakia": "SK",
    "Czech Republic": "CZ",
    "United States / Canada": "US",
    "Russia / Kazakhstan": "RU",
    "Bangladesh": "BD",
    "China": "CN",
    "Japan": "JP",
    "South Korea": "KR",
    "Vietnam": "VN",
    "Thailand": "TH",
    "Indonesia": "ID",
    "Malaysia": "MY",
    "Singapore": "SG",
    "Philippines": "PH",
    "Myanmar": "MM",
    "Sri Lanka": "LK",
    "Nepal": "NP",
    "Afghanistan": "AF",
    "Iran": "IR",
    "Turkey": "TR",
    "Iraq": "IQ",
    "Syria": "SY",
    "Lebanon": "LB",
    "Jordan": "JO",
    "Kuwait": "KW",
    "Saudi Arabia": "SA",
    "Yemen": "YE",
    "Oman": "OM",
    "United Arab Emirates": "AE",
    "Israel": "IL",
    "Bahrain": "BH",
    "Qatar": "QA",
    "Azerbaijan": "AZ",
    "Georgia": "GE",
    "Kyrgyzstan": "KG",
    "Tajikistan": "TJ",
    "Turkmenistan": "TM",
    "Uzbekistan": "UZ",
    "Cambodia": "KH",
    "Laos": "LA",
    "Mongolia": "MN",
    "North Korea": "KP",
    "Brazil": "BR",
    "Mexico": "MX",
    "Argentina": "AR",
    "Colombia": "CO",
    "Peru": "PE",
    "Venezuela": "VE",
    "Chile": "CL",
    "Ecuador": "EC",
    "Bolivia": "BO",
    "Paraguay": "PY",
    "Uruguay": "UY",
    "Guatemala": "GT",
    "El Salvador": "SV",
    "Honduras": "HN",
    "Nicaragua": "NI",
    "Costa Rica": "CR",
    "Panama": "PA",
    "Haiti": "HT",
    "Belize": "BZ",
    "Australia": "AU",
    "New Zealand": "NZ",
    "Papua New Guinea": "PG",
    "Fiji": "FJ",
    "Samoa": "WS",
    "Kiribati": "KI",
    "Micronesia": "FM",
    "Marshall Islands": "MH",
    "🇺🇲": "5913463998522592692",
    "🇨🇲": "5911172109484167745",
    "🇨🇮": "5222233374948602940",
    "🇲🇬": "5913766918271012920",
    "🇷🇴": "5913460373570195273",
    "🇨🇫": "5913443245240619222",
    "🇹🇬": "5913423260757790970",
    "🇧🇯": "5913735869952430547",
    "🇸🇱": "5911210450657218661",
    "🇧🇩": "5911365056594973179",
    "🇰🇷": "5913371673905598425",
    "🇬🇶": "5911306279967529251",
    "🇬🇱": "5292014752283774878",
    "🇫🇴": "5296469342039327674",
    "🇧🇳": "5911336409163109113",
    "🇧🇬": "5294329219965272288",
    "🇧🇫": "5913407764515786948",
    "🇪🇷": "5433723401464198287",
    "🇲🇼": "5433968339154122439",
    "🇲🇷": "5433859405898594234",
    "🇳🇷": "5434131139889478358",
    "🇸🇦": "4985897134424328239",
    "🇹?...": "5433640100573491806",
    "🇹🇻": "5433684690923961019",
    "🇹🇼": "5366187256937726720",
    "🇭🇰": "5292166459118606932",
    "🇲🇴": "6323557758096377611",
    "🇨🇺": "5431551436502611633",
    "🇰🇵": "5434142701941437163",
    "🇻🇪": "5434009132753499322",
    "🇸🇾": "5433910876786670092",
    "🇲🇲": "5433666360003540231",
    "🇳🇮": "5334807849418003620",
    "🇬🇳": "5913471858312744319",
    "🇰🇪": "5222279743415531561",
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿": "5911460091336331851",
    "🏴󠁧󠁢󠁷󠁬󠁳󠁿": "5911297801702084799",
    "🇻🇦": "5911211932420938860",
    "🇻🇺": "5913511535220625585",
    "🇺🇾": "5913623088406204470",
    "🇦🇪": "5913726554168365343",
    "🇺🇬": "5913488939397681980",
    "🇹🇲": "5913315521503170180",
    "🇹🇳": "5911332947419468671",
    "🇹🇹": "5911228635548750294",
    "🇹🇭": "5913617968805187987",
    "🇹🇿": "5911418949844603556",
    "🇹🇯": "5911287639809463107",
    "🇨🇭": "5913271227505448072",
    "🇸🇪": "5911156510162949403",
    "🇸🇿": "5913374525763883286",
    "🇸🇷": "5913275539652611719",
    "🇸🇩": "5911387497799094470",
    "🇪🇸": "5911193287967904547",
    "🇱🇰": "5911293163137406640",
    "🇸🇸": "5911406262511211744",
    "🇿🇦": "5911203119148044594",
    "🇸🇴": "5911397852965244436",
    "🇸🇧": "5911482712929080608",
    "🇸🇮": "5913431983836368644",
    "🇸🇰": "5913751666842145020",
    "🇸🇬": "5911531460808051849",
    "🇸🇨": "5911185183364616913",
    "🇷🇸": "5913592598433369871",
    "🇸🇳": "5910995302860461643",
    "🇸🇹": "5913574331937462345",
    "🇸🇲": "5913587968458625465",
    "🇼🇸": "5913325971158602854",
    "🇰🇳": "5913691898077253637",
    "🇻🇨": "5911318941531116255",
    "🇱🇨": "5911243659344351824",
    "🇵🇸": "5913684768431541668",
    "🇷🇼": "5911455229433352234",
    "🇶🇦": "5911260864983339619",
    "🇵🇷": "5911504350974317480",
    "🇵🇹": "5911023653939581472",
    "🇵🇭": "5911268638874145162",
    "🇵🇪": "5911207993935925780",
    "🇵🇾": "5911014265141072316",
    "🇵🇬": "5911107251183030903",
    "🇵🇦": "5913428968769327174",
    "🇵🇼": "5911283903187915549",
    "🇵🇰": "5913705895375672082",
    "🇴🇲": "5913570801474343473",
    "🇳🇴": "5913617397574537046",
    "🇳🇬": "5911143844304393105",
    "🇳🇪": "5911270086278124251",
    "🇳🇿": "5913640044937089340",
    "🇳🇱": "5913367645226275100",
    "🇳🇵": "5913496520014958723",
    "🇳🇦": "5911108535378252443",
    "🇲🇿": "5911333419865871464",
    "🇲🇦": "5911482111633658301",
    "🇲🇪": "5913239436157522151",
    "🇲🇳": "5911041383564580038",
    "🇲🇨": "5911245347266500057",
    "🇲🇩": "5913456847402045950",
    "🇲🇻": "5913501399097806832",
    "🇲🇱": "5911305266355245916",
    "🇲🇹": "5911023714069123567",
    "🇧🇲": "5913680005312811090",
    "🇲🇶": "5911378005921370347",
    "🇲🇭": "5913235935759175692",
    "🇲🇺": "5913291113204027321",
    "🇲🇽": "5913687302462246518",
    "🇫🇲": "5911271104185373336",
    "🇲🇾": "5913654360063087453",
    "🇲🇰": "5913394029210374721",
    "🇱🇺": "5913390842344640293",
    "🇱🇹": "5911172315642597775",
    "🇱🇮": "5911166650580734660",
    "🇱🇾": "5911236989260140996",
    "🇱🇷": "5913324167272337727",
    "🇰🇮": "591334642189831222",
    "🇽🇰": "5911433681582429010",
    "🇰🇼": "5913290705182134003",
    "🇰🇬": "5911202161370337549",
    "🇱🇦": "5913718526874489279",
    "🇱🇻": "5913738489882480243",
    "🇱🇧": "5911504273664905447",
    "🇱🇸": "5911059881988723711",
    "🇮🇩": "5913479361620611038",
    "🇮🇷": "5911308891307643032",
    "🇮🇶": "5911382442622587735",
    "🇮🇪": "5913440715504881532",
    "🇮🇱": "5911471936856134692",
    "🇮🇹": "5913688444923547525",
    "🇯🇲": "5913232280742006526",
    "🇯🇴": "5913234136167878475",
    "🇮🇸": "5911047899029967246",
    "🇭🇺": "5913767635530551104",
    "🇭🇳": "5911406889576436289",
    "🇭🇹": "5913459789454643194",
    "🇬🇾": "5913579412883771480",
    "🇬🇼": "5911398694778836149",
    "🇬🇹": "5913324858762072330",
    "🇬🇩": "5913228063084121946",
    "🇬🇷": "5911210399117611448",
    "🇬🇭": "5913391155877252952",
    "🇬🇪": "5913434771270144023",
    "🇬🇲": "5913657267755945883",
    "🇬🇦": "5911037896051137264",
    "🇫🇷": "5913605586414473124",
    "🇫🇮": "5911041344909873378",
    "🇫🇯": "5911393832875856716",
    "🇪🇹": "5911078333168227043",
    "🇩🇴": "5911152099231536123",
    "🇹🇱": "5911141915864076479",
    "🇪🇨": "5911273865849347408",
    "🇪🇬": "5913694831539916769",
    "🇸🇻": "5913238624408703010",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿": "5913475719488344315",
    "🇪🇪": "5910986042910969906",
    "🇩🇲": "5911377121158107430",
    "🇩🇯": "5911407709915190157",
    "🇩🇰": "5911206009661034712",
    "🇨🇾": "5911023550860366409",
    "🇭🇷🇨🇷": "5913692684056269311",
    "🇨🇷": "5911261745451635030",
    "🇨🇬": "5911338788574990168",
    "🇨🇩": "5913770362834783827",
    "🇨🇦": "5913623736946265914",
    "🇨🇻": "5913571501554012193",
    "🇹🇩": "5913299849167507310",
    "🇨🇿": "5911198691036764307",
    "🇨🇱": "5911470957603592832",
    "🇨🇴": "5913773060074246009",
    "🇧🇮": "5913766441529642752",
    "🇧🇼": "5911513782722499475",
    "🇧🇦": "5913700002680541032",
    "🇧🇴": "5913638795101606133",
    "🇧🇹": "5913236734623093021",
    "🇦🇷": "5913573356979884082",
    "🇦🇺": "5913632326880858455",
    "🇦🇹": "5911338831524664592",
    "🇧🇸": "5911451643135660214",
    "🇧🇭": "5913581774391214080",
    "Qatar": "5913437190007823331",
    "Azerbaijan": "5913401540871300096",
    "Georgia": "5913215284428801024",
    "Kyrgyzstan": "5911202161370337549",
    "Laos": "5913718526874489279",
    "Latvia": "5913738489882480243",
    "Lebanon": "5911504273664905447",
    "Lesotho": "5911059881988723711",
    "Indonesia": "5913479361620611038",
    "Iran": "5911308891307643032",
    "Iraq": "5911382442622587735",
    "Ireland": "5913440715504881532",
    "Israel": "5911471936856134692",
    "Italy": "5913688444923547525",
    "Jamaica": "5913232280742006526",
    "Jordan": "5913234136167878475",
    "Iceland": "5911047899029967246",
    "Hungary": "5913767635530551104",
    "Honduras": "5911406889576436289",
    "Haiti": "5913459789454643194",
    "Guyana": "5913579412883771480",
    "Guinea-Bissau": "5911398694778836149",
    "Guatemala": "5913324858762072330",
    "Grenada": "5913228063084121946",
    "Greece": "5911210399117611448",
    "Ghana": "5913391155877252952",
    "Georgia": "5913434771270144023",
    "Gambia": "5913657267755945883",
    "Gabon": "5911037896051137264",
    "France": "5913605586414473124",
    "Finland": "5911041344909873378",
    "Fiji": "5911393832875856716",
    "Ethiopia": "5911078333168227043",
    "Dominican Republic": "5911152099231536123",
    "Timor-Leste": "5911141915864076479",
    "Ecuador": "5911273865849347408",
    "Egypt": "5913694831539916769",
    "El Salvador": "5913238624408703010",
    "England": "5913475719488344315",
    "Estonia": "5910986042910969906",
    "Dominica": "5911377121158107430",
    "Djibouti": "5911407709915190157",
    "Denmark": "5911206009661034712",
    "Cyprus": "5911023550860366409",
    "Croatia": "5913692684056269311",
    "Costa Rica": "5911261745451635030",
    "Congo": "5911338788574990168",
    "DR Congo": "5913770362834783827",
    "Canada": "5913623736946265914",
    "Cabo Verde": "5913571501554012193",
    "Chad": "5913299849167507310",
    "Czechia": "5911198691036764307",
    "Chile": "5911470957603592832",
    "Colombia": "5913773060074246009",
    "Burundi": "5913766441529642752",
    "Botswana": "5911513782722499475",
    "Bosnia and Herzegovina": "5913700002680541032",
    "Bolivia": "5913638795101606133",
    "Bhutan": "5913236734623093021",
    "Argentina": "5913573356979884082",
    "Australia": "5913632326880858455",
    "Austria": "5911338831524664592",
    "Bahamas": "5911451643135660214",
    "Bahrain": "5913581663446634403",
    "Barbados": "5911016996740272263",
    "Belgium": "5913529642802745141",
    "Belize": "5913355005137522807",
    "Antigua and Barbuda": "5913389025573475085",
    "Angola": "5913753316109586411",
    "Andorra": "5911314702398396902",
    "Algeria": "5913782968563800236",
    "Albania": "5911357458797826163",
    "Afghanistan": "5913492040364068694",
    "Zimbabwe": "5911092502265336396"
}

COUNTRY_CODES = {
    "Cameroon": "CM", "Ivory Coast": "CI", "Madagascar": "MG", "Romania": "RO",
    "UK (Virtual)": "GB", "USA (Virtual)": "US", "Egypt": "EG", "South Africa": "ZA",
    "Nigeria": "NG", "Kenya": "KE", "Ghana": "GH", "Morocco": "MA", "Algeria": "DZ",
    "Tunisia": "TN", "Libya": "LY", "Sudan": "SD", "Ethiopia": "ET", "Somalia": "SO",
    "Djibouti": "DJ", "Tanzania": "TZ", "Uganda": "UG", "Burundi": "BI", "Mozambique": "MZ",
    "Zambia": "ZM", "Zimbabwe": "ZW", "Namibia": "NA", "Malawi": "MW", "Lesotho": "LS",
    "Botswana": "BW", "Eswatini": "SZ", "Comoros": "KM", "Gambia": "GM", "Senegal": "SN",
    "Mauritania": "MR", "Mali": "ML", "Guinea": "GN", "Burkina Faso": "BF", "Niger": "NE",
    "Togo": "TG", "Benin": "BJ", "Mauritius": "MU", "Liberia": "LR", "Sierra Leone": "SL",
    "Chad": "TD", "Central African Republic": "CF", "Cape Verde": "CV", "Sao Tome and Principe": "ST",
    "Equatorial Guinea": "GQ", "Gabon": "GA", "Congo": "CG", "DR Congo": "CD", "Angola": "AO",
    "Guinea-Bissau": "GW", "Rwanda": "RW", "Eritrea": "ER", "United Kingdom": "GB", "France": "FR",
    "Germany": "DE", "Italy": "IT", "Spain": "ES", "Netherlands": "NL", "Belgium": "BE",
    "Switzerland": "CH", "Austria": "AT", "Sweden": "SE", "Norway": "NO", "Denmark": "DK",
    "Finland": "FI", "Portugal": "PT", "Ireland": "IE", "Hungary": "HU", "Poland": "PL",
    "Ukraine": "UA", "Lithuania": "LT", "Latvia": "LV", "Estonia": "EE", "Moldova": "MD",
    "Armenia": "AM", "Belarus": "BY", "Andorra": "AD", "Monaco": "MC", "San Marino": "SM",
    "Vatican City": "VA", "Serbia": "RS", "Montenegro": "ME", "Kosovo": "XK", "Croatia": "HR",
    "Slovenia": "SI", "Bosnia and Herzegovina": "BA", "North Macedonia": "MK", "Gibraltar": "GI",
    "Luxembourg": "LU", "Iceland": "IS", "Albania": "AL", "Malta": "MT", "Cyprus": "CY",
    "Bulgaria": "BG", "Slovakia": "SK", "Czech Republic": "CZ", "United States / Canada": "US",
    "Russia / Kazakhstan": "RU", "Bangladesh": "BD", "China": "CN", "Japan": "JP",
    "South Korea": "KR", "Vietnam": "VN", "Thailand": "TH", "Indonesia": "ID", "Malaysia": "MY",
    "Singapore": "SG", "Philippines": "PH", "Myanmar": "MM", "Sri Lanka": "LK", "Nepal": "NP",
    "Afghanistan": "AF", "Iran": "IR", "Turkey": "TR", "Iraq": "IQ", "Syria": "SY",
    "Lebanon": "LB", "Jordan": "JO", "Kuwait": "KW", "Saudi Arabia": "SA", "Yemen": "YE",
    "Oman": "OM", "United Arab Emirates": "AE", "Israel": "IL", "Bahrain": "BH", "Qatar": "QA",
    "Azerbaijan": "AZ", "Georgia": "GE", "Kyrgyzstan": "KG", "Tajikistan": "TJ", "Turkmenistan": "TM",
    "Uzbekistan": "UZ", "Cambodia": "KH", "Laos": "LA", "Mongolia": "MN", "North Korea": "KP",
    "Brazil": "BR", "Mexico": "MX", "Argentina": "AR", "Colombia": "CO", "Peru": "PE",
    "Venezuela": "VE", "Chile": "CL", "Ecuador": "EC", "Bolivia": "BO", "Paraguay": "PY",
    "Uruguay": "UY", "Guatemala": "GT", "El Salvador": "SV", "Honduras": "HN", "Nicaragua": "NI",
    "Costa Rica": "CR", "Panama": "PA", "Haiti": "HT", "Belize": "BZ", "Australia": "AU",
    "New Zealand": "NZ", "Papua New Guinea": "PG", "Fiji": "FJ", "Samoa": "WS", "Kiribati": "KI",
    "Micronesia": "FM", "Marshall Islands": "MH"
}

# ==================== DYNAMIC MULTILINGUAL BROADCAST EMOJI FORMATTING ====================

EMOJI_KEYWORDS_DYNAMIC = [
    (r"\b(telegram|টেলিগ্রাম)\b", "telegram"),
    (r"\b(instagram|ইনস্টাগ্রাম|ইন্সটাগ্রাম|insta)\b", "instagram"),
    (r"\b(facebook|ফেসবুক|fb)\b", "facebook"),
    (r"\b(tiktok|টিকটক)\b", "tiktok"),
    (r"\b(whatsapp|হোয়াটসঅ্যাপ|হোয়াটসএপ|ওয়াটসঅ্যাপ)\b", "whatsapp"),
    (r"\b(paypal|পেপাল)\b", "paypal"),
    (r"\b(imo|ইমো)\b", "imo"),
    (r"\b(x)\b", "x"),
    (r"\b(hi|hello|হাই|হ্যালো|আসসালামু আলাইকুম|আসসালামু)\b", "hi"),
    (r"\b(off|বন্ধ|অফ)\b", "off"),
    (r"\b(diamond|ডায়মন্ড|হীরা)\b", "diamond"),
    (r"\b(broadcast|ব্রডকাস্ট|notice|নোটিশ|বিজ্ঞপ্তি|ঘোষণা)\b", "broadcast"),
    (r"\b(key|চাবি|এপিআই)\b", "key"),
    (r"\b(tk|টাকা|ব্যালেন্স|balance|টাকার)\b", "tk"),
    (r"\b(roket|rocket|রকেট)\b", "roket"),
    (r"\b(all done|done|সম্পন্ন|সফল|কমপ্লিট|সফলভাবে)\b", "all_done"),
    (r"\b(yes|হ্যাঁ|জি)\b", "yes"),
    (r"\b(no|না|ভুল)\b", "no"),
    (r"\b(fire love|fire|love|আগুন|ভালোবাসা)\b", "fire_love"),
    (r"\b(admin|এডমিন)\b", "admin"),
    (r"\b(developer|ডেভলপার)\b", "developer"),
    (r"\b(channel|চ্যানেল)\b", "channel"),
    (r"\b(gift|bonus|বোনাস|উপহার)\b", "gift_box"),
    (r"\b(number|নাম্বার|নম্বর)\b", "get_number_btn"),
    (r"\b(waiting|অপেক্ষা|অপেক্ষা করুন)\b", "waiting"),
    (r"\b(maintenance|মেনটেনেন্স|কাজ)\b", "stop")
]

def auto_premium_emoji_formatter(text: str) -> str:
    if not text:
        return ""
    formatted = text
    for pattern, emoji_key in EMOJI_KEYWORDS_DYNAMIC:
        emoji_html = get_tg_emoji(emoji_key)
        formatted = re.sub(pattern, lambda m: f"{emoji_html} {m.group(0)}", formatted, flags=re.IGNORECASE)
    return formatted

# মেমোরি ডেটাবেজ ক্যাশ গতি বৃদ্ধি করার জন্য (Optimized Cache and Save Logic)
_global_db_cache = {}
_dirty_files = set()

def load_data(filename=USER_DATA_FILE):
    if filename in _global_db_cache:
        return _global_db_cache[filename]
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
        _global_db_cache[filename] = {}
        return {}
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            _global_db_cache[filename] = data
            return data
    except:
        _global_db_cache[filename] = {}
        return {}

def save_data(data, filename=USER_DATA_FILE):
    _global_db_cache[filename] = data
    _dirty_files.add(filename)

def _save_data_immediate_sync(filename, data):
    try:
        temp_file = f"{filename}.tmp"
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, filename)
    except Exception:
        pass

async def _bg_disk_persistence():
    while True:
        try:
            await asyncio.sleep(1.5)
            if _dirty_files:
                to_save = list(_dirty_files)
                _dirty_files.clear()
                for filename in to_save:
                    data = _global_db_cache.get(filename)
                    if data is not None:
                        await asyncio.to_thread(_save_data_immediate_sync, filename, data)
        except Exception:
            pass

def preload_all_databases():
    for filename in [USER_DATA_FILE, PAID_SMS_FILE, STATS_FILE, BANNED_USERS_FILE, WITHDRAW_DATA_FILE, ACTIVITY_LOGS_FILE, DATA_RANGE_FILE, SETTINGS_FILE]:
        load_data(filename)

def load_stats():
    return load_data(STATS_FILE)

def save_stats(stats):
    save_data(stats, STATS_FILE)

def get_tg_emoji(key, default_char=""):
    emoji_id = EMOJI_ID_MAP.get(key)
    fallback = default_char or FALLBACK_EMOJI_MAP.get(key, "⭐")
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

def get_country_tg_flag(flag_emoji):
    emoji_id = PREMIUM_FLAGS.get(flag_emoji)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{flag_emoji}</tg-emoji>'
    return f'<tg-emoji emoji-id="5911106310585193018">{flag_emoji}</tg-emoji>'

# ==================== SYSTEM DYNAMIC SETTINGS ====================

WELCOME_MESSAGE = f'{get_tg_emoji("gift_box")} <b>WELCOME TO MULTI-PANEL OTP BOT</b> {get_tg_emoji("gift_box")}\n━━━━━━━━━━━━━━━━━━━━━━\n{get_tg_emoji("live")} <b>START INSTANT OTP RECEPTION NOW!</b> {get_tg_emoji("live")}'

_settings_cache = None

def load_settings():
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache

    default = {
        "active_panel": "zenex",
        "zenex_api_key": "ZNX_IQ52ED851U09ZAZL062U26GL",
        "zenex_base_url": "https://api.zenexnetwork.com",
        "voltx_sms_api_key": "M9JBBKWUL33",
        "voltx_sms_base_url": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api",
        "stex_sms_api_key": "MWF1Z0QG1DJ",
        "stex_sms_base_url": "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api",
        "fastxotp_api_key": "MURAD_920E47039411AB1DD899DC2D",
        "fastxotp_base_url": "https://fastxotp.com",
        "panel_url": "https://t.me/MrCodePanleBot?start=ref_8214164198",
        "allowed_services": ["Instagram", "Facebook", "WhatsApp", "TikTok", "Telegram", "Discord", "PayPal", "Imo"],
        "max_numbers_per_user": 10000,
        "welcome_message": WELCOME_MESSAGE,
        "otp_group_url": "https://t.me/+31eV11IT7WQzMjI9",
        "channel_url": "https://t.me/MrCodeUpdates",
        "support_username": "@Iklash24x7",
        "maintenance_mode": False,
        "cooldown_time": 1.0,
        "force_join_enabled": False,
        "force_join_channels": ["@MrCodeUpdates"],
        "join_alert_enabled": True,
        "numbers_per_request": 3,
        "min_withdraw": 5.0,
        "otp_bonus": 0.0012,
        "referral_bonus": 0.004,
        "admins": [8214164198]
    }

    data = load_data(SETTINGS_FILE)
    if not data:
        _global_db_cache[SETTINGS_FILE] = default
        _dirty_files.add(SETTINGS_FILE)
        _settings_cache = default
        return default

    updated = False
    for k, v in default.items():
        if k not in data:
            data[k] = v
            updated = True
    if updated:
        save_data(data, SETTINGS_FILE)
    _settings_cache = data
    return data

def save_settings(settings):
    global _settings_cache
    _settings_cache = settings
    save_data(settings, SETTINGS_FILE)

def clean_base_url(url, panel):
    url = str(url).strip().rstrip('/')
    if panel == "zenex":
        url = re.sub(r'(/v1|/api|/api/v1)$', '', url)
    elif panel == "fastxotp":
        url = re.sub(r'(/api|/api/v1)$', '', url)
    return url.rstrip('/')

def clean_range_for_rid(range_str):
    return str(range_str).strip().replace("+", "")

def get_api_credentials():
    settings = load_settings()
    panel = settings.get("active_panel", "zenex")
    
    if panel == "voltx_sms":
        raw_key = settings.get("voltx_sms_api_key", "M9JBBKWUL33")
        raw_url = settings.get("voltx_sms_base_url", "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api")
    elif panel == "stex_sms":
        raw_key = settings.get("stex_sms_api_key", "MWF1Z0QG1DJ")
        raw_url = settings.get("stex_sms_base_url", "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api")
    elif panel == "fastxotp":
        raw_key = settings.get("fastxotp_api_key", "MURAD_920E47039411AB1DD899DC2D")
        raw_url = settings.get("fastxotp_base_url", "https://fastxotp.com")
    else: # zenex
        raw_key = settings.get("zenex_api_key", "ZNX_IQ52ED851U09ZAZL062U26GL")
        raw_url = settings.get("zenex_base_url", "https://api.zenexnetwork.com")
        
    cleaned_url = clean_base_url(raw_url, panel)
    return str(raw_key).strip(), cleaned_url

def get_api_urls(panel, base_url):
    base_url = str(base_url).strip().rstrip('/')
    if panel == "zenex":
        return {
            "getnum": f"{base_url}/v1/getnum",
            "liveaccess": f"{base_url}/v1/active-ranges",
            "otp": f"{base_url}/v1/numsuccess/info"
        }
    elif panel == "fastxotp":
        return {
            "getnum": f"{base_url}/api/getnum",
            "liveaccess": f"{base_url}/api/liveaccess",
            "otp": f"{base_url}/api/otps"
        }
    elif panel == "stex_sms":
        return {
            "getnum": f"{base_url}/getnum",
            "liveaccess": f"{base_url}/liveaccess",
            "otp": f"{base_url}/success-otp"
        }
    else: # voltx_sms
        return {
            "getnum": f"{base_url}/getnum",
            "liveaccess": f"{base_url}/liveaccess",
            "otp": f"{base_url}/success-otp"
        }

def get_api_headers(panel, api_key):
    if panel == "zenex":
        return {"mapikey": api_key}
    elif panel == "fastxotp":
        return {"X-API-Key": api_key}
    elif panel == "stex_sms":
        return {"mauthapi": api_key}
    else: # voltx_sms
        return {"mauthapi": api_key}

def is_under_maintenance(uid):
    settings = load_settings()
    return settings.get("maintenance_mode", False) and not is_admin(uid)

# ==================== MULTIPLE ADMINS CONFIGURATION ====================

def get_admins():
    settings = load_settings()
    admin_list = settings.get("admins", [8214164198])
    if 8214164198 not in admin_list:
        admin_list.append(8214164198)
    return admin_list

def is_admin(user_id):
    return user_id in get_admins()

OTP_GROUP_ID = -1003963274594

request_queue = asyncio.Queue() 

# সংযোগ এবং গতি বহুগুণ বৃদ্ধি করার জন্য সুপার অপ্টিমাইজড ক্লায়েন্ট
client_async = httpx.AsyncClient(
    http2=True,
    timeout=httpx.Timeout(4.0, connect=0.8, read=3.2),
    limits=httpx.Limits(max_connections=5000, max_keepalive_connections=2500),
    trust_env=False
)

active_numbers = {}
last_range = {}
last_selected_app = {} # সেশন ট্র্যাক করে লোগো ঠিক রাখার গ্লোবাল ডিকশনারি
last_request_time = {} 
CHECK_INTERVAL = 0.5  

# ==================== GLOBAL RANGES CACHE ====================
_ranges_cache = {"data": None, "updated_at": 0.0, "fetching": False}

def get_app_emoji_id(app_name: str) -> str:
    name_lower = app_name.lower()
    if "telegram" in name_lower or name_lower == "tg":
        return "5271801931814165886"
    if "instagram" in name_lower or "insta" in name_lower:
        return "5269682734820777950"
    if "facebook" in name_lower or name_lower == "fb":
        return "5269427536453984598"
    if "tiktok" in name_lower:
        return "5271527792641595125"
    if "whatsapp" in name_lower:
        return "5271536803482981220"
    if "x" in name_lower or "twitter" in name_lower:
        return "5269500885905468781"
    if "discord" in name_lower:
        return "5807892405306791778"
    if "paypal" in name_lower:
        return "5107533253946901363"
    if "imo" in name_lower:
        return "5337155807752524558"
    return "5861680977994060034"

def get_platform_icon(platform_name: str) -> str:
    emoji_id = get_app_emoji_id(platform_name)
    return f'<tg-emoji emoji-id="{emoji_id}">📞</tg-emoji>'

def make_bold_text(text: str) -> str:
    out = []
    for char in str(text):
        o = ord(char)
        if 65 <= o <= 90:
            out.append(chr(o - 65 + 0x1D5D4))
        elif 97 <= o <= 122:
            out.append(chr(o - 97 + 0x1D5EE))
        elif 48 <= o <= 57:
            out.append(chr(o - 48 + 0x1D7EC))
        else:
            out.append(char)
    return "".join(out)

async def _bg_refresh_ranges():
    global _ranges_cache
    while True:
        try:
            if not _ranges_cache["fetching"]:
                _ranges_cache["fetching"] = True
                try:
                    data, err = await fetch_top55_ranges_by_app()
                    if data:
                        _ranges_cache["data"] = data
                        _ranges_cache["updated_at"] = time.monotonic()
                except Exception:
                    pass
                finally:
                    _ranges_cache["fetching"] = False
        except Exception:
            pass
        await asyncio.sleep(200)

# ==================== LEADERBOARD SYSTEM ====================

def get_leaderboard_text():
    stats = load_data(STATS_FILE)
    users_db = load_data(USER_DATA_FILE)
    
    sorted_users = []
    for uid, u_stats in stats.items():
        otps = u_stats.get("otps_received", [])
        sorted_users.append((uid, len(otps)))
    
    sorted_users.sort(key=lambda x: x[1], reverse=True)
    top_10 = sorted_users[:10]
    
    leaderboard_emoji = get_tg_emoji("leader_board")
    text = f"{leaderboard_emoji} <b>TOP 10 LEADERBOARD</b> {leaderboard_emoji}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if not top_10:
        text += "<i>No activity yet! Be the first on the leaderboard!</i>"
        return text
        
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for idx, (uid, otp_count) in enumerate(top_10):
        medal = medals[idx] if idx < len(medals) else "👤"
        u_info = users_db.get(str(uid), {})
        name = u_info.get("full_name") or "User"
        username = u_info.get("username")
        
        if username:
            display_name = f"@{username[:3]}***"
        else:
            display_name = f"{name[:4]}***"
            
        text += f"{medal} <b>{display_name}</b> — {otp_count} OTPs\n"
    text += f"\n━━━━━━━━━━━━━━━━━━━━━━"
    return text

# ==================== WITHDRAW DATA FUNCTIONS ====================

def load_withdraw_requests():
    return load_data(WITHDRAW_DATA_FILE)

def save_withdraw_requests(data):
    save_data(data, WITHDRAW_DATA_FILE)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

# ==================== BANNED USERS FUNCTIONS ====================

def load_banned_users():
    data = load_data(BANNED_USERS_FILE)
    if isinstance(data, dict) and not data:
        _global_db_cache[BANNED_USERS_FILE] = []
        return []
    if not isinstance(data, list):
        return []
    return data

def save_banned_users(banned_list):
    save_data(banned_list, BANNED_USERS_FILE)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ==================== DATA RANGE FILE ====================

def load_range_db():
    return load_data(DATA_RANGE_FILE)

def save_range_db(data):
    save_data(data, DATA_RANGE_FILE)

def save_number_range_info(uid, number, range_text):
    db = load_range_db()
    flag, name = get_country_info(number)
    db[normalize_number(number)] = {
        "user_id": str(uid),
        "number": f"+{normalize_number(number)}",
        "range": range_text,
        "country": f"{flag} {name}"
    }
    save_range_db(db)

# ==================== COUNTRY MAPPING SECTION ====================

def get_country_info(number):
    number = str(number).strip()
    
    country_map = {
        "2376": ("🇨🇲", "Cameroon"), "2250": ("🇨🇮", "Ivory Coast"), "2613": ("🇲🇬", "Madagascar"),
        "4077": ("🇷🇴", "Romania"), "447": ("🇬🇧", "UK (Virtual)"), "1201": ("🇺🇸", "USA (Virtual)"),
        "1302": ("🇺🇸", "USA (Virtual)"), "1415": ("🇺🇸", "USA (Virtual)"), "1212": ("🇺🇸", "USA (Virtual)"),
        "1917": ("🇺🇸", "USA (Virtual)"), "1646": ("🇺🇸", "USA (Virtual)"), "1347": ("🇺🇸", "USA (Virtual)"),
        "237": ("🇨🇲", "Cameroon"), "225": ("🇨🇮", "Ivory Coast"), "261": ("🇲🇬", "Madagascar"),
        "20": ("🇪🇬", "Egypt"), "27": ("🇿🇦", "South Africa"), "234": ("🇳🇬", "Nigeria"),
        "254": ("🇰🇪", "Kenya"), "233": ("🇬🇭", "Ghana"), "212": ("🇲🇦", "Morocco"),
        "213": ("🇩🇿", "Algeria"), "216": ("🇹🇳", "Tunisia"), "218": ("🇱🇾", "Libya"),
        "249": ("🇸🇩", "Sudan"), "251": ("🇪🇹", "Ethiopia"), "252": ("🇸🇴", "Somalia"),
        "253": ("🇩🇯", "Djibouti"), "255": ("🇹🇿", "Tanzania"), "256": ("🇺🇬", "Uganda"),
        "257": ("🇧🇮", "Burundi"), "258": ("🇲🇿", "Mozambique"), "260": ("🇿🇲", "Zambia"),
        "263": ("🇿🇼", "Zimbabwe"), "264": ("🇳🇦", "Namibia"), "265": ("🇲🇼", "Malawi"),
        "266": ("🇱🇸", "Lesotho"), "267": ("🇧🇼", "Botswana"), "268": ("🇸🇿", "Eswatini"),
        "269": ("🇰🇲", "Comoros"), "220": ("🇬🇲", "Gambia"), "221": ("🇸🇳", "Senegal"),
        "222": ("🇲🇷", "Mauritania"), "223": ("🇲🇱", "Mali"), "224": ("🇬🇳", "Guinea"),
        "226": ("🇧🇫", "Burkina Faso"), "227": ("🇳🇪", "Niger"), "228": ("🇹🇬", "Togo"),
        "229": ("🇧🇯", "Benin"), "230": ("🇲🇺", "Mauritius"), "231": ("🇱🇷", "Liberia"),
        "232": ("🇸🇱", "Sierra Leone"), "235": ("🇹🇩", "Chad"), "236": ("🇨🇫", "Central African Republic"),
        "238": ("🇨🇻", "Cape Verde"), "239": ("🇸🇹", "Sao Tome and Principe"), "240": ("🇬🇶", "Equatorial Guinea"),
        "241": ("🇬🇦", "Gabon"), "242": ("🇨🇬", "Congo"), "243": ("🇨🇩", "DR Congo"),
        "244": ("🇦🇴", "Angola"), "245": ("🇬🇼", "Guinea-Bissau"), "250": ("🇷🇼", "Rwanda"),
        "291": ("🇪🇷", "Eritrea"), "40": ("🇷🇴", "Romania"), "44": ("🇬🇧", "United Kingdom"),
        "33": ("🇫🇷", "France"), "49": ("🇩🇪", "Germany"), "39": ("🇮🇹", "Italy"),
        "34": ("🇪🇸", "Spain"), "31": ("🇳🇱", "Netherlands"), "32": ("🇧🇪", "Belgium"),
        "41": ("🇨🇭", "Switzerland"), "43": ("🇦🇹", "Austria"), "46": ("🇸🇪", "Sweden"),
        "47": ("🇳🇴", "Norway"), "45": ("🇩🇰", "Denmark"), "358": ("🇫🇮", "Finland"),
        "351": ("🇵🇹", "Portugal"), "353": ("🇮🇪", "Ireland"), "36": ("🇭🇺", "Hungary"),
        "48": ("🇵🇱", "Poland"), "380": ("🇺🇦", "Ukraine"), "370": ("🇱🇹", "Lithuania"),
        "371": ("🇱🇻", "Latvia"), "372": ("🇪🇪", "Estonia"), "373": ("🇲ذج", "Moldova"),
        "374": ("🇦🇲", "Armenia"), "375": ("🇧🇾", "Belarus"), "376": ("🇦🇩", "Andorra"),
        "377": ("🇲🇨", "Monaco"), "378": ("🇸🇲", "San Marino"), "379": ("🇻🇦", "Vatican City"),
        "381": ("🇷🇸", "Serbia"), "382": ("🇲🇪", "Montenegro"), "383": ("🇽🇲", "Kosovo"),
        "385": ("🇭🇷", "Croatia"), "386": ("🇸🇮", "Slovenia"), "387": ("🇧🇦", "Bosnia and Herzegovina"),
        "389": ("🇲🇰", "North Macedonia"), "350": ("🇬🇮", "Gibraltar"), "352": ("🇱🇺", "Luxembourg"),
        "354": ("🇮🇸", "Iceland"), "355": ("🇦🇱", "Albania"), "356": ("🇲🇹", "Malta"),
        "357": ("🇨🇾", "Cyprus"), "359": ("🇧🇬", "Bulgaria"), "421": ("🇸🇰", "Slovakia"),
        "420": ("🇨🇿", "Czech Republic"), "1": ("🇺🇸", "United States / Canada"),
        "7": ("🇷🇺", "Russia / Kazakhstan"), "880": ("🇧🇩", "Bangladesh"), "86": ("🇨🇳", "China"),
        "81": ("🇯🇵", "Japan"), "82": ("??🇷", "South Korea"), "84": ("🇻🇳", "Vietnam"),
        "66": ("🇹🇭", "Thailand"), "62": ("🇮🇩", "Indonesia"), "60": ("🇲🇾", "Malaysia"),
        "65": ("🇸🇬", "Singapore"), "63": ("🇵🇭", "Philippines"), "95": ("🇲🇲", "Myanmar"),
        "94": ("🇱🇰", "Sri Lanka"), "977": ("🇳🇵", "Nepal"), "93": ("🇦🇫", "Afghanistan"),
        "98": ("🇮🇷", "Iran"), "90": ("🇹🇷", "Turkey"), "964": ("🇮🇶", "Iraq"),
        "963": ("🇸🇾", "Syria"), "961": ("🇱🇧", "Lebanon"), "962": ("🇯🇴", "Jordan"),
        "965": ("🇰🇼", "Kuwait"), "966": ("🇸🇦", "Saudi Arabia"), "967": ("🇾🇪", "Yemen"),
        "968": ("🇴🇲", "Oman"), "971": ("🇦🇪", "United Arab Emirates"), "972": ("🇮🇱", "Israel"),
        "973": ("🇧🇭", "Bahrain"), "974": ("🇶🇦", "Qatar"), "994": ("🇦🇿", "Azerbaijan"),
        "995": ("🇬🇪", "Georgia"), "996": ("🇰🇬", "Kyrgyzstan"), "992": ("🇹🇯", "Tajikistan"),
        "993": ("🇹🇲", "Turkmenistan"), "998": ("🇺🇿", "Uzbekistan"), "855": ("🇰🇭", "Cambodia"),
        "856": ("🇱🇦", "Laos"), "976": ("🇲🇳", "Mongolia"), "850": ("🇰🇵", "North Korea"),
        "55": ("🇧🇷", "Brazil"), "52": ("🇲🇽", "Mexico"), "54": ("🇦𝒓", "Argentina"),
        "57": ("🇨🇴", "Colombia"), "51": ("🇵🇪", "Peru"), "58": ("🇻🇪", "Venezuela"),
        "56": ("🇨🇱", "Chile"), "593": ("🇪🇨", "Ecuador"), "591": ("🇧🇴", "Bolivia"),
        "595": ("🇵🇾", "Paraguay"), "598": ("🇺🇾", "Uruguay"), "502": ("🇬🇹", "Guatemala"),
        "503": ("🇸🇻", "El Salvador"), "504": ("🇭🇳", "Honduras"), "505": ("🇳🇮", "Nicaragua"),
        "506": ("🇨🇷", "Costa Rica"), "507": ("🇵🇦", "Panama"), "509": ("🇭🇹", "Haiti"),
        "501": ("🇧🇿", "Belize"), "61": ("🇦🇺", "Australia"), "64": ("🇳🇿", "New Zealand"),
        "675": ("🇵🇬", "Papua New Guinea"), "679": ("🇫🇯", "Fiji"), "685": ("🇼🇸", "Samoa"),
        "686": ("🇰🇮", "Kiribati"), "691": ("🇫🇲", "Micronesia"), "692": ("🇲🇭", "Marshall Islands")
    }
    
    clean_num = str(number).replace('+', '').replace(' ', '').replace('-', '').strip()
    sorted_prefixes = sorted(country_map.keys(), key=len, reverse=True)
    
    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            return country_map[prefix]
    
    return ("🇨🇮", "IVORY COAST")

# ==================== SERVICE DETECTION & CLEANING ====================

def get_clean_app_name(app_name: str) -> str:
    name_lower = app_name.lower().strip()
    if "facebook" in name_lower or name_lower == "fb":
        return "Facebook"
    if "instagram" in name_lower or "instragram" in name_lower or name_lower == "insta":
        return "Instagram"
    if "whatsapp" in name_lower or "whats app" in name_lower:
        return "WhatsApp"
    if "tiktok" in name_lower:
        return "TikTok"
    if "paypal" in name_lower:
        return "PayPal"
    if "telegram" in name_lower or name_lower == "tg":
        return "Telegram"
    if "discord" in name_lower:
        return "Discord"
    if "imo" in name_lower:
        return "Imo"
    if "1xbet" in name_lower:
        return "1xBet"
    return app_name.capitalize()

def detect_service(full_sms):
    if not full_sms:
        return "SMS SERVICE"
    
    sms_lower = full_sms.lower()
    service_keywords = {
        "facebook": "FACEBOOK", "fb": "FACEBOOK", "instagram": "INSTAGRAM", "insta": "INSTAGRAM",
        "tiktok": "TIKTOK", "twitter": "TWITTER", "x.com": "TWITTER", "snapchat": "SNAPCHAT",
        "snap": "SNAPCHAT", "whatsapp": "WHATSAPP", "whats app": "WHATSAPP", "telegram": "TELEGRAM",
        "tg": "TELEGRAM", "discord": "DISCORD", "messenger": "MESSENGER", "linkedin": "LINKEDIN",
        "pinterest": "PINTEREST", "reddit": "REDDIT", "youtube": "YOUTUBE", "google": "GOOGLE",
        "gmail": "GOOGLE", "line": "LINE", "wechat": "WECHAT", "viber": "VIBER", "skype": "SKYPE",
        "signal": "SIGNAL", "imo": "IMO", "tumblr": "TUMBLR", "flickr": "FLICKR", "quora": "QUORA",
        "vk": "VK", "ok.ru": "OK", "odnoklassniki": "OK", "pubg": "PUBG", "free fire": "FREE FIRE",
        "freefire": "FREE FIRE", "call of duty": "CALL OF DUTY", "cod": "CALL OF DUTY",
        "fortnite": "FORTNITE", "minecraft": "MINECRAFT", "roblox": "ROBLOX", "genshin": "GENSHIN IMPACT",
        "clash of clans": "CLASH OF CLANS", "clash royale": "CLASH ROYALE", "brawl stars": "BRAWL STARS",
        "among us": "AMONG US", "valorant": "VALORANT", "apex legends": "APEX LEGENDS",
        "league of legends": "LEAGUE OF LEGENDS", "lol": "LEAGUE OF LEGENDS", "dota": "DOTA",
        "csgo": "CSGO", "counter strike": "CSGO", "apple": "APPLE", "icloud": "APPLE",
        "samsung": "SAMSUNG", "xiaomi": "XIAOMI", "huawei": "HUAWEI", "oppo": "OPPO",
        "vivo": "VIVO", "oneplus": "ONEPLUS", "realme": "REALME", "nokia": "NOKIA",
        "motorola": "MOTOROLA", "sony": "SONY", "lg": "LG", "amazon": "AMAZON",
        "microsoft": "MICROSOFT", "outlook": "MICROSOFT", "hotmail": "MICROSOFT", "yahoo": "YAHOO",
        "dropbox": "DROPBOX", "spotify": "SPOTIFY", "netflix": "NETFLIX", "zoom": "ZOOM",
        "slack": "SLACK", "trello": "TRELLO", "github": "GITHUB", "gitlab": "GITLAB",
        "bitbucket": "BITBUCKET", "docker": "DOCKER", "paypal": "PAYPAL", "payoneer": "PAYONEER",
        "wise": "WISE", "transferwise": "WISE", "skrill": "SKRILL", "neteller": "NETELLER",
        "binance": "BINANCE", "coinbase": "COINBASE", "blockchain": "BLOCKCHAIN", "bkash": "BKASH",
        "nagad": "NAGAD", "rocket": "ROCKET", "upay": "UPAY", "visa": "VISA", "mastercard": "MASTERCARD",
        "stripe": "STRIPE", "uber": "UBER", "pathao": "PATHAO", "foodpanda": "FOODPANDA",
        "hungrynaki": "HUNGRYNAKI", "daraz": "DARAZ", "aliexpress": "ALIEXPRESS", "ebay": "EBAY",
        "shopify": "SHOPIFY", "airbnb": "AIRBNB", "booking.com": "BOOKING", "booking": "BOOKING",
        "agoda": "AGODA", "expedia": "EXPEDIA", "tinder": "TINDER", "badoo": "BADOO",
        "bumble": "BUMBLE", "happn": "HAPPN", "duolingo": "DUOLINGO", "canva": "CANVA",
        "adobe": "ADOBE", "wordpress": "WORDPRESS", "wix": "WIX", "godaddy": "GODADDY",
        "namecheap": "NAMECHEAP", "cloudflare": "CLOUDFLARE", "digitalocean": "DIGITALOCEAN",
        "heroku": "HEROKU", "firebase": "FIREBASE", "aws": "AWS", "azure": "AZURE",
    }
    
    for keyword, service_name in sorted(service_keywords.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in sms_lower:
            return service_name
    
    return "SMS SERVICE"

# ==================== ADVANCED DYNAMIC KEYBOARD BUILDER ====================

def make_inline_btn(text, callback_data=None, url=None, emoji_id=None, style=None):
    api_kwargs = {}
    if emoji_id:
        api_kwargs['icon_custom_emoji_id'] = str(emoji_id)
    if style:
        api_kwargs['style'] = style
    
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data,
        url=url,
        api_kwargs=api_kwargs if api_kwargs else None
    )

def make_reply_btn(text, request_contact=False, emoji_id=None, style=None):
    api_kwargs = {}
    if emoji_id:
        api_kwargs['icon_custom_emoji_id'] = str(emoji_id)
    if style:
        api_kwargs['style'] = style
    return KeyboardButton(
        text=text,
        request_contact=request_contact,
        api_kwargs=api_kwargs if api_kwargs else None
    )

def main_keyboard(user_id):
    keyboard = [
        [
            make_reply_btn("GET NUMBER", emoji_id="5861680977994060034", style="success"),
            make_reply_btn("Custom Range", emoji_id="5231012545799666522", style="primary")
        ],
        [
            make_reply_btn("PROFILE", emoji_id="5382164415019768638", style="primary"),
            make_reply_btn("LEADERBOARD", emoji_id="5280769763398671636", style="primary")
        ],
        [
            make_reply_btn("SUPPORT", emoji_id="5253742260054409879", style="success")
        ]
    ]
    if is_admin(user_id):
        keyboard.append([make_reply_btn("ADMIN PANEL", emoji_id="5350396951407895212", style="danger")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    keyboard = [[make_reply_btn("CANCEL", emoji_id="5420130255174145507")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== ADMIN PANEL KEYBOARDS ====================

def admin_main_keyboard():
    keyboard = [
        [
            make_reply_btn("SYSTEM CONFIG", emoji_id="5341715473882955310", style="primary"), 
            make_reply_btn("USER CONFIG", emoji_id="5193063022226086560", style="primary")
        ],
        [
            make_reply_btn("SECURITY & JOIN", emoji_id="5420323339723881652", style="primary"), 
            make_reply_btn("NOTICE & B-CAST", emoji_id="5253742260054409879", style="primary")
        ],
        [
            make_reply_btn("API & MONITOR", emoji_id="5355102594886833928", style="primary"), 
            make_reply_btn("BACK TO MAIN", emoji_id="5267490665117275176", style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_system_config_keyboard():
    keyboard = [
        [
            make_reply_btn("GET NUMBER PER REQUEST", emoji_id="5397916757333654639", style="primary")
        ],
        [
            make_reply_btn("SET COOLDOWN", emoji_id="6217721388736712699", style="primary"), 
            make_reply_btn("EDIT ALLOWED SERVICES", emoji_id="5271604874419647061", style="primary")
        ],
        [
            make_reply_btn("SET OTP BONUS", emoji_id="6233367447789899509", style="primary"),
            make_reply_btn("SET REFERRAL BONUS", emoji_id="5970074171449808121", style="primary")
        ],
        [
            make_reply_btn("TOGGLE MAINTENANCE", emoji_id="5956074558044770726", style="danger"), 
            make_reply_btn("BACK TO ADMIN", emoji_id="5267490665117275176", style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_user_config_keyboard():
    keyboard = [
        [
            make_reply_btn("ADD BALANCE", emoji_id="5397916757333654639", style="primary"), 
            make_reply_btn("REMOVE BALANCE", emoji_id="5422557736330106570", style="primary")
        ],
        [
            make_reply_btn("USER STATUS CHECK", emoji_id="5231200819986047254", style="primary"), 
            make_reply_btn("ALL USER ID", emoji_id="5271604874419647061", style="primary")
        ],
        [
            make_reply_btn("ALL USER BALANCE", emoji_id="6233367447789899509", style="primary"), 
            make_reply_btn("BACK TO ADMIN", emoji_id="5267490665117275176", style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_security_join_keyboard():
    keyboard = [
        [
            make_reply_btn("SET FORCE JOIN", emoji_id="5271604874419647061", style="primary"), 
            make_reply_btn("TOGGLE FORCE JOIN", emoji_id="5956074558044770726", style="primary")
        ],
        [
            make_reply_btn("ADD ADMIN", emoji_id="5397916757333654639", style="primary"),
            make_reply_btn("REMOVE ADMIN", emoji_id="5422557736330106570", style="danger")
        ],
        [
            make_reply_btn("BAN USER", emoji_id="5420323339723881652", style="danger"), 
            make_reply_btn("UNBAN USER", emoji_id="6298670698948724690", style="success")
        ],
        [
            make_reply_btn("BAN USER LIST", emoji_id="5231200819986047254", style="primary"), 
            make_reply_btn("TOGGLE JOIN ALERT", emoji_id="5253742260054409879", style="primary")
        ],
        [
            make_reply_btn("BACK TO ADMIN", emoji_id="5267490665117275176", style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_notice_bcast_keyboard():
    keyboard = [
        [
            make_reply_btn("BROADCAST NOTICE", emoji_id="5253742260054409879", style="primary"), 
            make_reply_btn("B-CAST WITH BUTTON", emoji_id="5271604874419647061", style="primary")
        ],
        [
            make_reply_btn("EDIT LINKS & TEXTS", emoji_id="5341715473882955310", style="primary"), 
            make_reply_btn("BACK TO ADMIN", emoji_id="5267490665117275176", style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_api_monitor_keyboard():
    keyboard = [
        [make_reply_btn("VIEW CONFIG OVERVIEW", emoji_id="5231200819986047254", style="success")],
        [make_reply_btn("BACK TO ADMIN", emoji_id="5267490665117275176", style="danger")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

MENU_BUTTONS = {
    "GET NUMBER", "PROFILE", "SUPPORT", "ADMIN PANEL", "BACK TO MAIN", "BACK TO ADMIN", "CANCEL",
    "EDIT LINKS & TEXTS", "BAN USER", "UNBAN USER", "LEADERBOARD",
    "BAN USER LIST", "ALL USER ID", "TOGGLE MAINTENANCE", "VIEW CONFIG OVERVIEW", 
    "B-CAST WITH BUTTON", "DIRECT MSG USER", "SEARCH BY USERNAME", "SET FORCE JOIN", "TOGGLE FORCE JOIN", 
    "SET COOLDOWN", "BROADCAST NOTICE", "GET NUMBER PER REQUEST", "SYSTEM CONFIG", "USER CONFIG", 
    "SECURITY & JOIN", "NOTICE & B-CAST", "API & MONITOR", "TOGGLE JOIN ALERT", "EDIT ALLOWED SERVICES",
    "ADD BALANCE", "REMOVE BALANCE", "USER STATUS CHECK", "ALL USER BALANCE", "Custom Range",
    "ADD ADMIN", "REMOVE ADMIN", "SET OTP BONUS", "SET REFERRAL BONUS"
}

# ==================== HELPER FUNCTIONS SECTION ====================

def clean_html(text):
    if not text:
        return ""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', str(text))
    return html.unescape(text).strip()

def extract_otp(text):
    text = clean_html(text)
    if not text or text.lower() == "no content" or text.lower() == "n/a" or text.lower() == "no sms":
        return "N/A"
    
    if text.isdigit() and 3 <= len(text) <= 8:
        return text

    g_match = re.search(r'\b[Gg]-(\d{4,8})\b', text)
    if g_match:
        return g_match.group(1)

    spaced_otp = re.search(r'\b(\d{3})[\s-]?(\d{3})\b', text)
    if spaced_otp:
        return spaced_otp.group(1) + spaced_otp.group(2)

    match_3_8 = re.search(r'\b(\d{3,8})\b', text)
    if match_3_8:
        return match_3_8.group(1)

    fallback_match = re.search(r'(\d{3,8})', text)
    if fallback_match:
        return fallback_match.group(1)

    return "N/A"

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number_mino(num_str):
    num_str = str(num_str).replace('+', '').replace(' ', '').strip()
    if len(num_str) >= 8:
        return f"+{num_str[:4]}✧MINO✧{num_str[-4:]}"
    elif len(num_str) > 4:
        half = len(num_str) // 2
        return f"+{num_str[:half]}✧MINO✧{num_str[half:]}"
    return f"+{num_str}"

# ছবির মতো ডায়নামিক মাস্কিং করার জন্য নতুন ফাংশন
def mask_number_image_style(num_str):
    num_str = str(num_str).replace('+', '').replace(' ', '').strip()
    prefixes = [
        "2376", "2250", "2613", "4077", "447", "1201", "1302", "1415", "1212", "1917", 
        "1646", "1347", "237", "225", "261", "20", "27", "234", "254", "233", "212", 
        "213", "216", "218", "249", "251", "252", "253", "255", "256", "257", "258", 
        "260", "263", "264", "265", "266", "267", "268", "269", "220", "221", "222", 
        "223", "224", "226", "227", "228", "229", "230", "231", "232", "235", "236", 
        "238", "239", "240", "241", "242", "243", "244", "245", "250", "291", "40", 
        "44", "33", "49", "39", "34", "31", "32", "41", "43", "46", "47", "45", "358", 
        "351", "353", "36", "48", "380", "370", "371", "372", "373", "374", "375", 
        "376", "377", "378", "379", "381", "382", "383", "385", "386", "387", "389", 
        "350", "352", "354", "355", "356", "357", "359", "421", "420", "1", "7", 
        "880", "86", "81", "82", "84", "66", "62", "60", "65", "63", "95", "94", 
        "977", "93", "98", "90", "964", "963", "961", "962", "965", "966", "967", 
        "968", "971", "972", "973", "974", "994", "995", "996", "992", "993", "998", 
        "855", "856", "976", "850", "55", "52", "54", "57", "51", "58", "56", "593", 
        "591", "595", "598", "502", "503", "504", "505", "506", "507", "509", "501", 
        "61", "64", "675", "679", "685", "686", "691", "692"
    ]
    sorted_prefixes = sorted(prefixes, key=len, reverse=True)
    prefix = ""
    for p in sorted_prefixes:
        if num_str.startswith(p):
            prefix = p
            break
    if not prefix:
        prefix = num_str[:3] if len(num_str) > 3 else num_str
        
    last4 = num_str[-4:] if len(num_str) >= 4 else ""
    if len(num_str) <= len(prefix) + len(last4):
        return f"{num_str}"
        
    return f"{prefix}XXX{last4}"

def format_otp_display(otp):
    otp = str(otp).strip()
    if otp.isdigit() and len(otp) == 6:
        return f"{otp[:3]}-{otp[3:]}"
    return otp

def get_date_reset_time():
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return today_midnight

def is_range_request(param):
    if 'X' in param.upper():
        return True
    return False

def get_user(uid, username=None, full_name=None):
    uid_str = str(uid)
    data = load_data()
    if uid_str not in data:
        data[uid_str] = {
            "user_id": uid_str, 
            "total_numbers": 0, 
            "username": username, 
            "full_name": full_name or "N/A",
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": 0.0,
            "today_otp_earnings": 0.0,
            "total_otp_earned": 0.0,
            "today_commission": 0.0,
            "overall_commission": 0.0,
            "referred_by": None,
            "referred_count": 0
        }
        save_data(data)
    else:
        updated = False
        for key, default_val in [
            ("joined_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("balance", 0.0),
            ("today_otp_earnings", 0.0),
            ("total_otp_earned", 0.0),
            ("today_commission", 0.0),
            ("overall_commission", 0.0),
            ("referred_by", None),
            ("referred_count", 0)
        ]:
            if key not in data[uid_str]:
                data[uid_str][key] = default_val
                updated = True
        if username and data[uid_str].get("username") != username: 
            data[uid_str]["username"] = username
            updated = True
        if full_name and data[uid_str].get("full_name") != full_name: 
            data[uid_str]["full_name"] = full_name
            updated = True
        if updated:
            save_data(data)
    return data[uid_str]

async def update_db_balance(uid, amount):
    uid_str = str(uid)
    data = load_data()
    if uid_str in data:
        data[uid_str]["balance"] = round(data[uid_str].get("balance", 0.0) + amount, 5)
        save_data(data)
        return data[uid_str]["balance"]
    return 0.0

def get_all_users():
    data = load_data(USER_DATA_FILE)
    return list(data.keys()) if data else []

def user_exists(uid):
    return str(uid) in load_data(USER_DATA_FILE)

def add_number_taken(uid, count=1):
    uid_str = str(uid)
    stats = load_stats()
    if uid_str not in stats:
        stats[uid_str] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count):
        stats[uid_str]["numbers_taken"].append(now)
    log_global_activity(uid_str, "NUMBER_TAKEN", {"count": count})
    save_stats(stats)

def add_otp_received(uid):
    uid_str = str(uid)
    stats = load_stats()
    if uid_str not in stats:
        stats[uid_str] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    stats[uid_str]["otps_received"].append(now)
    save_stats(stats)

def get_user_stats(uid):
    uid_str = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid_str, {"numbers_taken": [], "otps_received": []})
    
    now = datetime.now()
    today_midnight = get_date_reset_time()
    
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])
    
    today_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight)
    today_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight)
    
    last24h_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_24h)
    last24h_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_24h)
    
    last7d_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d)
    last7d_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_7d)
    
    total_numbers = len(numbers_taken)
    total_otps = len(otps_received)
    
    return {
        "total_numbers": total_numbers,
        "total_otps": total_otps,
        "today_numbers": today_numbers,
        "today_otps": today_otps,
        "last24h_numbers": last24h_numbers,
        "last24h_otps": last24h_otps,
        "last7d_numbers": last7d_numbers,
        "last7d_otps": last7d_otps
    }

def log_global_activity(uid, action, details):
    logs = load_data(ACTIVITY_LOGS_FILE)
    if not isinstance(logs, list):
        logs = []
    now = datetime.now()
    log_entry = {
        "uid": str(uid),
        "action": action,
        "details": details,
        "timestamp": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S")
    }
    logs.append(log_entry)
    save_data(logs, ACTIVITY_LOGS_FILE)

def get_global_system_stats():
    stats = load_stats()
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_7d = now - timedelta(days=7)
    total_n, total_o = 0, 0
    today_n, today_o = 0, 0
    seven_n, seven_o = 0, 0
    for uid_str in stats:
        u_stats = stats[uid_str]
        n_list = u_stats.get("numbers_taken", [])
        o_list = u_stats.get("otps_received", [])
        total_n += len(n_list)
        total_o += len(o_list)
        for t in n_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_n += 1
            if dt >= last_7d: seven_n += 1
        for t in o_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_o += 1
            if dt >= last_7d: seven_o += 1
    return today_n, today_o, seven_n, seven_o, total_n, total_o

# ==================== DYNAMIC MULTI-PANEL ROUTING ENGINE ====================

async def fetch_top55_ranges_by_app():
    ranges_list = None
    settings = load_settings()
    panel = settings.get("active_panel", "zenex")
    api_key, base_url = get_api_credentials()
    
    allowed_services_list = settings.get("allowed_services", ["Instagram", "Facebook", "WhatsApp", "TikTok", "Telegram", "Discord", "PayPal", "Imo"])
    allowed_services_set = {s.lower() for s in allowed_services_list}
    
    urls = get_api_urls(panel, base_url)
    headers = get_api_headers(panel, api_key)
    url = urls["liveaccess"]
    
    for attempt in range(2):
        try:
            r = await client_async.get(
                url,
                headers=headers,
                timeout=httpx.Timeout(4.0, connect=1.5)
            )
            data = r.json()
            
            if panel in ["voltx_sms", "stex_sms"]:
                if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
                    ranges_list = data["data"].get("services")
            elif panel == "fastxotp":
                if isinstance(data, dict) and data.get("status") == "ok":
                    ranges_list = data.get("services")
                elif isinstance(data, dict) and "services" in data:
                    ranges_list = data.get("services")
            else: # zenex
                if isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], dict) and "active_ranges" in data["data"]:
                        ranges_list = data["data"].get("active_ranges")
                    elif data.get("success") and "data" in data:
                        ranges_list = data.get("data", {}).get("active_ranges")
                    elif "active_ranges" in data:
                        ranges_list = data.get("active_ranges")
                elif isinstance(data, list):
                    ranges_list = data
                
            if ranges_list is not None:
                break
        except Exception:
            if attempt == 0:
                await asyncio.sleep(0.1)

    if ranges_list is None:
        return None, "Server unreachable or invalid API key."

    if not ranges_list:
        return {}, None

    top_ranges_by_app = {}

    if panel in ["voltx_sms", "stex_sms", "fastxotp"]:
        for svc_obj in ranges_list:
            if not isinstance(svc_obj, dict):
                continue
            primary_raw = svc_obj.get("sid", "Unknown App")
            primary_app = get_clean_app_name(primary_raw)
            
            if primary_app.lower() not in allowed_services_set:
                continue
                
            ranges = svc_obj.get("ranges", [])
            if not primary_app or not ranges:
                continue
                
            icon = get_platform_icon(primary_app)
            if primary_app not in top_ranges_by_app:
                top_ranges_by_app[primary_app] = {"icon": icon, "ranges": [], "total_otps": 0}
                
            for rng in ranges:
                top_ranges_by_app[primary_app]["ranges"].append(rng)
                top_ranges_by_app[primary_app]["total_otps"] += 1
    else: # zenex
        for rng_obj in ranges_list:
            if not isinstance(rng_obj, dict):
                continue
            rng      = rng_obj.get("range", "")
            primary_raw = rng_obj.get("service", "Unknown App")
            primary_app = get_clean_app_name(primary_raw)
            
            if primary_app.lower() not in allowed_services_set:
                continue
                
            if not primary_app:
                continue
                
            icon = get_platform_icon(primary_app)
            if primary_app not in top_ranges_by_app:
                top_ranges_by_app[primary_app] = {"icon": icon, "ranges": [], "total_otps": 0}
            top_ranges_by_app[primary_app]["ranges"].append(rng)
            top_ranges_by_app[primary_app]["total_otps"] += 1

    top_ranges_by_app = dict(
        sorted(top_ranges_by_app.items(),
               key=lambda x: len(x[1]["ranges"]), reverse=True)
    )

    return top_ranges_by_app, None

def build_app_buttons_from_cache(top_ranges_by_app):
    buttons = []
    row = []
    for app_name, info in top_ranges_by_app.items():
        bold_name = make_bold_text(app_name)
        emoji_id = get_app_emoji_id(app_name)
        row.append(make_inline_btn(bold_name, callback_data=f"sel_app_{app_name}", emoji_id=emoji_id, style="primary"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return buttons

async def show_app_selection(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", "@MinoXSupport0")
        await update.message.reply_text(
            f"{get_tg_emoji('ban')} <b>YOU ARE BANNED</b> {get_tg_emoji('ban')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ YOU HAVE BEEN BANNED FROM USING THIS BOT.\n"
            f"📞 CONTACT SUPPORT: {support}", 
            parse_mode="HTML", 
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await update.message.reply_text(
            f"{get_tg_emoji('stop')} <b>SYSTEM UNDER MAINTENANCE</b> {get_tg_emoji('stop')}\n\n"
            f"Sorry, the bot is currently undergoing maintenance. Please try again later.", 
            parse_mode="HTML"
        )
        return

    is_joined = await is_user_joined_force_channels(uid, context)
    if not is_joined:
        await update.message.reply_text(
            f"{get_tg_emoji('channel')} <b>আপনাকে অবশ্যই আমাদের চ্যানেলগুলোতে জয়েন করতে হবে!</b>\n\n"
            f"নিচের বোতামগুলো ব্যবহার করে জয়েন করুন এবং চেক বাটনে ক্লিক করুন।",
            parse_mode="HTML",
            reply_markup=build_force_join_keyboard()
        )
        return

    context.user_data.pop("top_ranges_by_app", None)

    cache_age = time.monotonic() - _ranges_cache["updated_at"]
    if _ranges_cache["data"] and cache_age < 300:
        top_ranges_by_app = _ranges_cache["data"]
        context.user_data["top_ranges_by_app"] = top_ranges_by_app
        buttons = build_app_buttons_from_cache(top_ranges_by_app)
        keyboard = InlineKeyboardMarkup(buttons)
        msg = (
            f"{get_tg_emoji('get_number_btn')} <b>SELECT APP TO GET NUMBER</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    status = await update.message.reply_text(f"{get_tg_emoji('loading', '⏳')} <b>Loading ranges...</b>", parse_mode="HTML")

    top_ranges_by_app, err = await fetch_top55_ranges_by_app()

    if err or not top_ranges_by_app:
        top_ranges_by_app, err = await fetch_top55_ranges_by_app()

    if err:
        await status.edit_text(
            f"{get_tg_emoji('cross')} <b>Could not load ranges.</b>\n\n"
            f"<blockquote>{get_tg_emoji('stop')} {err}\n\nPlease try again in a moment.</blockquote>",
            parse_mode="HTML"
        )
        return

    if not top_ranges_by_app:
        await status.edit_text(f"{get_tg_emoji('stop')} No active ranges returned by the API.", parse_mode="HTML")
        return

    _ranges_cache["data"] = top_ranges_by_app
    _ranges_cache["updated_at"] = time.monotonic()
    context.user_data["top_ranges_by_app"] = top_ranges_by_app

    buttons = build_app_buttons_from_cache(top_ranges_by_app)
    keyboard = InlineKeyboardMarkup(buttons)
    msg = (
        f"{get_tg_emoji('get_number_btn')} <b>SELECT APP TO GET NUMBER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    await status.edit_text(msg, parse_mode="HTML", reply_markup=keyboard)

# ==================== SUPPORT CONTROLLER ====================

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = load_settings()
    support_user = settings.get("support_username", "@MinoXSupport0")
    
    emoji_msg = get_tg_emoji("msg")
    support_text = f"{emoji_msg} <b>SUPPORT & HELP CENTER</b> {get_tg_emoji('waiting')}\n\nCLICK THE BUTTON BELOW TO CONTACT SUPPORT {emoji_msg}"
    
    keyboard = InlineKeyboardMarkup([
        [make_inline_btn("SUPPORT", url=f"https://t.me/{support_user.replace('@', '')}", emoji_id="5253742260054409879", style="primary")],
        [make_inline_btn("DEVELOPER", url="https://t.me/NETBOLDNETMAIR0", emoji_id="5267294466716244344", style="primary")]
    ])
    await update.message.reply_text(support_text, reply_markup=keyboard, parse_mode="HTML")

# ==================== PROFILE DASHBOARD ====================

async def show_profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name
    
    user_info = get_user(uid, username, full_name)
    settings = load_settings()
    min_w = settings.get("min_withdraw", 5.0)
    
    profile_em = get_tg_emoji("profile")
    id_em = get_tg_emoji("status")
    calendar_em = get_tg_emoji("waiting")
    money_em = get_tg_emoji("money")
    live_em = get_tg_emoji("live")
    up_em = get_tg_emoji("up")
    trophy_em = get_tg_emoji("1st")
    
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}" if BOT_USERNAME else f"https://t.me/MrCodePanleBot?start=ref_8214164198_{uid}"
    referred_count = user_info.get("referred_count", 0)
    
    profile_text = (
        f"{profile_em} <b>My Profile</b>\n\n"
        f"{id_em} <b>User ID:</b> <code>{uid}</code>\n"
        f"{profile_em} <b>Name:</b> {html.escape(user_info.get('full_name') or 'N/A')}\n"
        f"{calendar_em} <b>Joined:</b> {user_info.get('joined_at')}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{money_em} <b>Total Balance:</b> $ {user_info.get('balance', 0.0)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{live_em} <b>OTP Earnings</b>\n"
        f"<blockquote>{up_em} Today's OTP Earnings: $ {user_info.get('today_otp_earnings', 0.0)}\n"
        f"{trophy_em} Total OTP Earned: $ {user_info.get('total_otp_earned', 0.0)}</blockquote>\n\n"
        f"{get_tg_emoji('gift_box')} <b>Commission Earnings</b>\n"
        f"<blockquote>{up_em} Today's Commission: $ {user_info.get('today_commission', 0.0)}\n"
        f"{trophy_em} Overall Commission: $ {user_info.get('overall_commission', 0.0)}</blockquote>\n\n"
        f"{get_tg_emoji('profile')} <b>Total Referred:</b> <code>{referred_count}</code>\n"
        f"{get_tg_emoji('link')} <b>Referral Link:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"{get_tg_emoji('link')} <i>Minimum withdrawal: ${min_w}</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [make_inline_btn("Withdraw", callback_data="profile_withdraw", emoji_id="6233367447789899509", style="success")]
    ])
    
    await update.message.reply_text(profile_text, reply_markup=keyboard, parse_mode="HTML")

# ==================== AUTO OTP MONITOR SECTION ====================

async def monitor_loop(app):
    while True:
        try:
            settings = load_settings()
            panel = settings.get("active_panel", "zenex")
            api_key, base_url = get_api_credentials()
            
            urls = get_api_urls(panel, base_url)
            headers = get_api_headers(panel, api_key)
            url = urls["otp"]

            r = await client_async.get(url, headers=headers)
            
            if r.status_code != 200:
                await asyncio.sleep(5)
                continue
                
            try:
                res = r.json()
            except Exception:
                await asyncio.sleep(5)
                continue
                
            otps = []
            if isinstance(res, dict):
                if "data" in res:
                    d = res["data"]
                    if isinstance(d, list):
                        otps = d
                    elif isinstance(d, dict):
                        otps = d.get("otps") or d.get("active") or []
                else:
                    otps = res.get("otps") or []
            elif isinstance(res, list):
                otps = res

            if otps:
                paid_data = load_data(PAID_SMS_FILE)
                paid_keys_set = set(paid_data.keys())
                processed_in_session = set()

                for otp in otps:
                    num = normalize_number(otp.get("number", ""))
                    
                    if panel in ["voltx_sms", "stex_sms"]:
                        full_sms = otp.get('message') or "No SMS Content"
                        otp_id = str(otp.get("otp_id") or "")
                        otp_code = extract_otp(full_sms)
                    elif panel == "fastxotp":
                        raw_otp = otp.get('otp')
                        if raw_otp and str(raw_otp).strip().isdigit() and 3 <= len(str(raw_otp).strip()) <= 8:
                            otp_code = str(raw_otp).strip()
                            full_sms = otp.get('message') or otp.get('sms') or f"OTP: {otp_code}"
                        else:
                            full_sms = otp.get('message') or otp.get('sms') or otp.get('otp') or "No SMS Content"
                            otp_code = extract_otp(full_sms)
                        otp_id = str(otp.get("otp_id") or otp.get("nid") or "")
                    else: # zenex
                        full_sms = otp.get('otp') or otp.get('sms') or otp.get('message') or "No SMS Content"
                        otp_id = str(otp.get("nid") or otp.get("otp_id", ""))
                        otp_code = extract_otp(full_sms)
                    
                    if otp_code == "N/A" or not otp_code:
                        continue
                        
                    sms_key = otp_id if otp_id else f"{num}_{full_sms}"

                    if (num in active_numbers and 
                        sms_key not in paid_keys_set and 
                        sms_key not in processed_in_session):
                        
                        details = active_numbers[num]
                        details["otp_count"] = details.get("otp_count", 0) + 1
                        
                        paid_keys_set.add(sms_key)
                        processed_in_session.add(sms_key)
                        paid_data[sms_key] = {"uid": details["uid"], "otp": otp_code}
                        
                        add_otp_received(details["uid"])
                        log_global_activity(details["uid"], "OTP_RECEIVED", {"number": num, "otp": otp_code, "sms": full_sms})

                        # ওটিপি বোনাস
                        otp_bonus_amount = settings.get("otp_bonus", 0.0012)
                        user_db = load_data(USER_DATA_FILE)
                        u_str = str(details["uid"])
                        if u_str in user_db:
                            user_db[u_str]["balance"] = round(user_db[u_str].get("balance", 0.0) + otp_bonus_amount, 5)
                            user_db[u_str]["today_otp_earnings"] = round(user_db[u_str].get("today_otp_earnings", 0.0) + otp_bonus_amount, 5)
                            user_db[u_str]["total_otp_earned"] = round(user_db[u_str].get("total_otp_earned", 0.0) + otp_bonus_amount, 5)
                            save_data(user_db, USER_DATA_FILE)

                        # --- DISTINCT LOGO SELECTION LOGIC ---
                        # ১. ইনবক্সের জন্য: ক্রয়কৃত সার্ভিস অনুযায়ী লোগো নির্বাচন
                        purchased_app = details.get("app") or "SMS SERVICE"
                        clean_user_svc = get_clean_app_name(purchased_app)
                        user_service_emoji = get_tg_emoji(clean_user_svc.lower())

                        # ২. ফরোয়ার্ডেড গ্রুপের জন্য: ওটিপি টেক্সটের প্যানেল বার্তা অনুযায়ী লোগো স্বয়ংক্রিয়ভাবে সনাক্তকরণ
                        detected_app_sms = detect_service(full_sms)
                        if detected_app_sms == "SMS SERVICE" and purchased_app:
                            detected_app_sms = purchased_app
                        clean_group_svc = get_clean_app_name(detected_app_sms)
                        group_service_emoji = get_tg_emoji(clean_group_svc.lower())

                        country_flag, country_name = get_country_info(num)
                        country_code = COUNTRY_CODES.get(country_name, "UN").upper()
                        
                        clean_num = num.replace('+', '').strip()
                        masked_num = mask_number_image_style(clean_num)
                        flag_tg = get_country_tg_flag(country_flag)
                        
                        # --- INBOX OTP DESIGN --- (ইনবক্সে মাস্কিং ছাড়া সম্পূর্ণ ফুল নাম্বারটি প্রদর্শন করার পরিবর্তন)
                        user_otp_msg = f"{flag_tg} #{country_code} {user_service_emoji} +{clean_num}"
                        
                        # Copy Button: Key Icon (Premium ID 5296369303661067030) + Copy Symbol + OTP
                        otp_btn_text = f"{otp_code}"
                        
                        if HAS_COPY_BTN:
                            try:
                                btn_copy = InlineKeyboardButton(
                                    text=otp_btn_text,
                                    copy_text=CopyTextButton(text=otp_code),
                                    api_kwargs={"icon_custom_emoji_id": "5296369303661067030"}
                                )
                            except Exception:
                                btn_copy = InlineKeyboardButton(
                                    text=otp_btn_text, 
                                    callback_data=f"copy_text_{otp_code}",
                                    api_kwargs={"icon_custom_emoji_id": "5296369303661067030"}
                                )
                        else:
                            btn_copy = InlineKeyboardButton(
                                text=otp_btn_text, 
                                callback_data=f"copy_text_{otp_code}",
                                api_kwargs={"icon_custom_emoji_id": "5296369303661067030"}
                            )
                        
                        user_otp_keyboard = InlineKeyboardMarkup([[btn_copy]])
                        
                        # --- GROUP FORWARD OTP DESIGN --- (গ্রুপে আগের মতোই মাস্কিং সক্রিয় রাখা হয়েছে)
                        group_msg = f"{flag_tg} #{country_code} {group_service_emoji} {masked_num}"
                        
                        panel_url = settings.get("panel_url", "https://t.me/MrCodePanleBot?start=ref_8214164198")
                        channel_url = settings.get("channel_url", "https://t.me/MrCodeUpdates")
                        
                        group_buttons = InlineKeyboardMarkup([
                            [btn_copy],
                            [
                                make_inline_btn(" NUMBER", url=panel_url, emoji_id="4943094697238201446", style="success"),
                                make_inline_btn(" CHANNEL", url=channel_url, emoji_id="6215074610845585917", style="danger")
                            ]
                        ])
                        
                        try:
                            await app.bot.send_message(details["uid"], user_otp_msg, parse_mode="HTML", reply_markup=user_otp_keyboard)
                        except Exception:
                            pass
                        
                        try:
                            await app.bot.send_message(OTP_GROUP_ID, group_msg, parse_mode="HTML", reply_markup=group_buttons)
                        except Exception:
                            pass
                        
                        save_data(paid_data, PAID_SMS_FILE)

                current_time = datetime.now()
                expired_nums = []
                for num_key in list(active_s.keys()):
                    if isinstance(active_s[num_key], dict) and "timestamp" in active_s[num_key]:
                        if (current_time - active_s[num_key]['timestamp']).total_seconds() > 3600:
                            expired_nums.append(num_key)
                    else:
                        if isinstance(active_numbers[num_key], dict):
                            active_numbers[num_key]['timestamp'] = current_time
                
                for num in expired_nums:
                    del active_numbers[num]
                    
        except Exception:
            pass
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== WORKER & API SECTION ====================

async def fetch_number_async(range_str):
    try:
        settings = load_settings()
        panel = settings.get("active_panel", "zenex")
        api_key, base_url = get_api_credentials()
        
        urls = get_api_urls(panel, base_url)
        headers = get_api_headers(panel, api_key)
        url = urls["getnum"]
        
        if panel in ["voltx_sms", "stex_sms"]:
            rid_val = clean_range_for_rid(range_str)
            payload = {"rid": rid_val}
        elif panel == "fastxotp":
            payload = {"range": range_str, "is_national": False}
        else: # zenex
            payload = {"range": range_str, "is_national": False, "remove_plus": False}

        r = await client_async.post(
            url,
            json=payload,
            headers=headers,
            timeout=httpx.Timeout(3.0, connect=0.8, read=2.2)
        )
        if r.status_code != 200:
            return None
            
        data = r.json()
        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict):
                ndata = data["data"]
                return ndata.get("full_number") or ndata.get("no_plus_number") or ndata.get("copy") or ndata.get("number")
            return data.get("full_number") or data.get("no_plus_number") or data.get("copy") or data.get("number") or data.get("data", {}).get("full_number")
    except Exception: 
        pass
    return None

async def worker():
    while True:
        task = await request_queue.get()
        try:
            if task['type'] == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'], task.get('edit_message'))
            elif task['type'] == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception:
            pass
        finally:
            request_queue.task_done()

# ==================== AUTO NUMBER FROM LINK SECTION ====================

async def process_auto_number(update, context, range_text):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", "@MinoXSupport0")
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"{get_tg_emoji('ban')} <b>YOU ARE BANNED</b> {get_tg_emoji('ban')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
                 f"❌ YOU HAVE BEEN BANNED FROM USING THIS BOT.\n"
                 f"📞 CONTACT SUPPORT: {support}", 
            parse_mode="HTML", 
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"{get_tg_emoji('stop')} <b>SYSTEM UNDER MAINTENANCE</b> {get_tg_emoji('stop')}\n\n"
                 f"Sorry, the bot is currently undergoing maintenance. Please try again later.", 
            parse_mode="HTML"
        )
        return

    is_joined = await is_user_joined_force_channels(uid, context)
    if not is_joined:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{get_tg_emoji('channel')} <b>আপনাকে অবশ্যই আমাদের চ্যানেলগুলোতে জয়েন করতে হবে!</b>",
            parse_mode="HTML",
            reply_markup=build_force_join_keyboard()
        )
        return

    status_msg = await context.bot.send_message(chat_id=chat_id, text=f"{get_tg_emoji('loading', '⏳')} <b>SEARCHING...</b>", parse_mode="HTML")

    try:
        result = await fetch_number_async(range_text)
        generated_num = normalize_number(result) if result else None
        
        if not generated_num:
            await status_msg.edit_text(f"{get_tg_emoji('cross')} NO NUMBERS FOUND. TRY A VALID RANGE.", parse_mode="HTML")
            return
        
        add_number_taken(uid, 1)
        last_range[str(uid)] = range_text
        
        app_name_raw = last_selected_app.get(str(uid), "Telegram")
        active_numbers[generated_num] = {"uid": uid, "range": range_text, "otp_count": 0, "app": app_name_raw}
        save_number_range_info(uid, generated_num, range_text)
        
        country_flag, country_name = get_country_info(generated_num)
        
        done_emoji = get_tg_emoji("done")
        waiting_emoji = get_tg_emoji("waiting")
        
        assign_text = (
            f"{get_country_tg_flag(country_flag)} <b>{country_name} Allocated</b> {done_emoji}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{waiting_emoji} <b>Waiting for OTP.......</b>"
        )
        
        settings = load_settings()
        
        keyboard = []
        f_emoji, f_name = get_country_info(generated_num)
        
        details = active_numbers.get(generated_num, {})
        otp_cnt = details.get("otp_count", 0)
        star_text = " ⭐" * otp_cnt if otp_cnt > 0 else ""
        
        btn_text = f" +{generated_num}{star_text}"
        
        app_emoji_key = get_clean_app_name(app_name_raw).lower()
        service_emoji_id = EMOJI_ID_MAP.get(app_emoji_key) or EMOJI_ID_MAP.get("get_number_btn")
        
        if HAS_COPY_BTN:
            num_btn = InlineKeyboardButton(text=btn_text, copy_text=CopyTextButton(text=f"+{generated_num}"), api_kwargs={"icon_custom_emoji_id": str(service_emoji_id)} if service_emoji_id else None)
        else:
            num_btn = InlineKeyboardButton(text=btn_text, callback_data=f"copy_text_{generated_num}", api_kwargs={"icon_custom_emoji_id": str(service_emoji_id)} if service_emoji_id else None)
            
        keyboard.append([num_btn])
        keyboard.append([
            make_inline_btn("Back To Country", callback_data="back_to_apps", emoji_id="5267490665117275176", style="primary"),
            make_inline_btn("VIEW OTP", url=settings.get("otp_group_url", "https://t.me/+31eV11IT7WQzMjI9"), emoji_id="5271604874419647061", style="primary")
        ])
        keyboard.append([
            make_inline_btn("Change number", callback_data="same_range", emoji_id="5267295703666824255", style="danger")
        ])
        
        await status_msg.edit_text(assign_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        await status_msg.edit_text(f"{get_tg_emoji('cross')} Error occurred: {str(e)}", parse_mode="HTML")

# ==================== USER PANEL SECTION ====================

async def process_numbers(update, context, range_text, count, edit_message=None):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", "@Iklash24x7")
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"{get_tg_emoji('ban')} <b>YOU ARE BANNED</b> {get_tg_emoji('ban')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
                 f"❌ YOU HAVE BEEN BANNED FROM USING THIS BOT.\n"
                 f"📞 CONTACT SUPPORT: {support}", 
            parse_mode="HTML", 
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"{get_tg_emoji('stop')} <b>SYSTEM UNDER MAINTENANCE</b> {get_tg_emoji('stop')}\n\n"
                 f"Sorry, the bot is currently undergoing maintenance. Please try again later.", 
            parse_mode="HTML"
        )
        return

    is_joined = await is_user_joined_force_channels(uid, context)
    if not is_joined:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{get_tg_emoji('channel')} <b>আপনাকে অবশ্যই আমাদের চ্যানেলগুলোতে জয়েন করতে হবে!</b>",
            parse_mode="HTML",
            reply_markup=build_force_join_keyboard()
        )
        return

    if not edit_message:
        status_msg = await context.bot.send_message(chat_id=chat_id, text=f"{get_tg_emoji('loading', '⏳')} <b>SEARCHING . . .</b>", parse_mode="HTML")  
    else:
        status_msg = edit_message

    try:
        add_number_taken(uid, count)
        last_range[str(uid)] = range_text   

        tasks = [fetch_number_async(range_text) for _ in range(count)]  
        results = await asyncio.gather(*tasks)  
        generated_nums = [normalize_number(n) for n in results if n]  

        if not generated_nums:  
            err_text = f"{get_tg_emoji('cross')} NO NUMBERS FOUND. TRY A VALID RANGE."
            await status_msg.edit_text(err_text, parse_mode="HTML")
            return  

        app_name_raw = last_selected_app.get(str(uid), "Telegram")
        for clean_num in generated_nums:  
            active_numbers[clean_num] = {"uid": uid, "range": range_text, "otp_count": 0, "app": app_name_raw}
            save_number_range_info(uid, clean_num, range_text)

        country_flag, country_name = get_country_info(generated_nums[0])
        
        done_emoji = get_tg_emoji("done")
        waiting_emoji = get_tg_emoji("waiting")
        
        assign_text = (
            f"{get_country_tg_flag(country_flag)} <b>{country_name} Allocated</b> {done_emoji}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{waiting_emoji} <b>Waiting for OTP.......</b>"
        )

        settings = load_settings()

        keyboard = []
        app_emoji_key = get_clean_app_name(app_name_raw).lower()
        service_emoji_id = EMOJI_ID_MAP.get(app_emoji_key) or EMOJI_ID_MAP.get("get_number_btn")

        for g_num in generated_nums:
            details = active_numbers.get(g_num, {})
            otp_cnt = details.get("otp_count", 0)
            star_text = " ⭐" * otp_cnt if otp_cnt > 0 else ""
            
            btn_text = f" +{g_num}{star_text}"
            
            if HAS_COPY_BTN:
                btn = InlineKeyboardButton(text=btn_text, copy_text=CopyTextButton(text=f"+{g_num}"), api_kwargs={"icon_custom_emoji_id": str(service_emoji_id)} if service_emoji_id else None)
            else:
                btn = InlineKeyboardButton(text=btn_text, callback_data=f"copy_text_{g_num}", api_kwargs={"icon_custom_emoji_id": str(service_emoji_id)} if service_emoji_id else None)
            keyboard.append([btn])
            
        keyboard.append([
            make_inline_btn("Back To Country", callback_data="back_to_apps", emoji_id="5267490665117275176", style="primary"),
            make_inline_btn("VIEW OTP", url=settings.get("otp_group_url", "https://t.me/+31eV11IT7WQzMjI9"), emoji_id="5271604874419647061", style="primary")
        ])
        keyboard.append([
            make_inline_btn("Change number", callback_data="same_range", emoji_id="5267295703666824255", style="danger")
        ])

        await status_msg.edit_text(assign_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        await status_msg.edit_text(f"{get_tg_emoji('cross')} System Error: {str(e)}", parse_mode="HTML")

# ==================== FORCE JOIN CHANNELS UTILS ====================

async def is_user_joined_force_channels(user_id, context):
    settings = load_settings()
    if not settings.get("force_join_enabled", False):
        return True
    if is_admin(user_id):
        return True
    channels = settings.get("force_join_channels", [])
    if not channels:
        return True
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True

def build_force_join_keyboard():
    settings = load_settings()
    channels = settings.get("force_join_channels", [])
    buttons = []
    for idx, ch in enumerate(channels, 1):
        clean_ch = ch.replace("@", "")
        buttons.append([make_inline_btn(f"Join Channel {idx}", url=f"https://t.me/{clean_ch}", emoji_id="6215074610845585917", style="primary")])
    buttons.append([make_inline_btn("Check Joined", callback_data="check_force_join", emoji_id="6298670698948724690", style="success")])
    return InlineKeyboardMarkup(buttons)

async def show_force_join_manager(update, context):
    settings = load_settings()
    channels = settings.get("force_join_channels", [])
    
    msg = f"{get_tg_emoji('link')} <b>FORCE JOIN CHANNELS MANAGER</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not channels:
        msg += "<i>No channels set yet.</i>"
    else:
        for idx, ch in enumerate(channels, 1):
            msg += f"<b>{idx}.</b> <code>{ch}</code>\n"
            
    kb = InlineKeyboardMarkup([
        [make_inline_btn("➕ Add Channel", callback_data="fj_add_start", emoji_id="5397916757333654639", style="primary")],
        [make_inline_btn("🗑️ Delete Channel", callback_data="fj_del_start", emoji_id="5422557736330106570", style="danger")],
        [make_inline_btn("🧹 Clear All", callback_data="fj_clear_all", emoji_id="5956074558044770726", style="danger")],
        [make_inline_btn("🔙 Back", callback_data="fj_back_security", emoji_id="5267490665117275176", style="danger")]
    ])
    
    if update.callback_query:
        await update.callback_query.message.edit_text(msg, parse_mode="HTML", reply_markup=kb)
    else:
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=kb)

# ==================== PARALLEL BROADCAST UTILS ====================

async def send_broadcast_task(bot, sem, target_id, is_text, msg_obj, formatted_text, kb=None):
    async with sem:
        for attempt in range(3):
            try:
                if is_text:
                    try:
                        await bot.send_message(chat_id=target_id, text=formatted_text, parse_mode="HTML", reply_markup=kb)
                    except Exception as parse_err:
                        if "parse" in str(parse_err).lower():
                            clean_text = clean_html(formatted_text)
                            await bot.send_message(chat_id=target_id, text=clean_text, reply_markup=kb)
                        else:
                            raise parse_err
                else:
                    try:
                        await bot.copy_message(chat_id=target_id, from_chat_id=msg_obj.chat_id, message_id=msg_obj.message_id, caption=formatted_text, parse_mode="HTML", reply_markup=kb)
                    except Exception as parse_err:
                        if "parse" in str(parse_err).lower():
                            clean_caption = clean_html(formatted_text)
                            await bot.copy_message(chat_id=target_id, from_chat_id=msg_obj.chat_id, message_id=msg_obj.message_id, caption=clean_caption, reply_markup=kb)
                        else:
                            raise parse_err
                return True
            except Exception as e:
                err_str = str(e).lower()
                # ইউজার বট বন্ধ অথবা ডিঅ্যাক্টিভেট করে রাখলে রিট্রাই না করে সরাসরি ফেরত যাবে
                if "forbidden" in err_str or "blocked" in err_str or "chat not found" in err_str or "user is deactivated" in err_str:
                    break
                if "retry after" in err_str:
                    wait_match = re.search(r'\b\d+\b', err_str)
                    wait_sec = int(wait_match.group(0)) if wait_match else 5
                    await asyncio.sleep(wait_sec)
                else:
                    await asyncio.sleep(0.5)
        return False

# ==================== WITHDRAWALS FLOW ====================

async def process_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    
    if text == "CANCEL":
        context.user_data.clear()
        await update.message.reply_text(f"{get_tg_emoji('cross')} WITHDRAW CANCELLED {get_tg_emoji('cross')}", reply_markup=main_keyboard(uid), parse_mode="HTML")
        return
        
    try:
        amount = float(text)
    except:
        await update.message.reply_text(f"{get_tg_emoji('stop')} PLEASE SEND A VALID AMOUNT!", reply_markup=cancel_keyboard(), parse_mode="HTML")
        return
        
    user_info = get_user(uid)
    settings = load_settings()
    min_w = settings.get("min_withdraw", 5.0)
    
    if amount < min_w:
        await update.message.reply_text(f"{get_tg_emoji('down')} MINIMUM WITHDRAW ${min_w}", reply_markup=cancel_keyboard(), parse_mode="HTML")
        return
        
    if amount > user_info.get("balance", 0):
        await update.message.reply_text(f"{get_tg_emoji('ban')} INSUFFICIENT BALANCE!", reply_markup=cancel_keyboard(), parse_mode="HTML")
        return
        
    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = "number"
    await update.message.reply_text(f"{get_tg_emoji('get_number_btn')} Enter your account number (Nagad/bKash/Rocket/Binance ID):", reply_markup=cancel_keyboard())

async def process_withdraw_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    
    if text == "CANCEL":
        context.user_data.clear()
        await update.message.reply_text(f"{get_tg_emoji('cross')} WITHDRAW CANCELLED {get_tg_emoji('cross')}", reply_markup=main_keyboard(uid), parse_mode="HTML")
        return
        
    method = context.user_data.get("withdraw_method")
    amount = context.user_data.get("withdraw_amount")
    account_number = text
    payment_id = generate_payment_id()
    
    withdraw_requests = load_withdraw_requests()
    withdraw_requests[payment_id] = {
        "user_id": uid,
        "method": method,
        "amount": amount,
        "number": account_number,
        "status": "pending",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_withdraw_requests(withdraw_requests)
    
    await update_db_balance(uid, -amount)
    
    await update.message.reply_text(
        f"{get_tg_emoji('done')} <b>WITHDRAW REQUEST SUBMITTED</b>\n\n"
        f"{get_tg_emoji('money')} <b>Amount:</b> ${amount}\n"
        f"{get_tg_emoji('setting')} <b>Method:</b> {method}\n"
        f"{get_tg_emoji('get_number_btn')} <b>Number:</b> {account_number}\n"
        f"{get_tg_emoji('status')} <b>Request ID:</b> <code>{payment_id}</code>\n\n"
        f"<i>Please wait for Admin approval.</i>",
        parse_mode="HTML",
        reply_markup=main_keyboard(uid)
    )
    
    money_em = get_tg_emoji("money")
    profile_em = get_tg_emoji("profile")
    link_em = get_tg_emoji("link")
    
    admin_msg = (
        f"{money_em} <b>NEW WITHDRAWAL REQUEST</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{profile_em} <b>User ID:</b> <code>{uid}</code>\n"
        f"{money_em} <b>Amount:</b> ${amount}\n"
        f"{link_em} <b>Method:</b> {method}\n"
        f"{get_tg_emoji('get_number_btn')} <b>Number:</b> {account_number}\n"
        f"{get_tg_emoji('status')} <b>Request ID:</b> <code>{payment_id}</code>\n"
    )
    kb = InlineKeyboardMarkup([
        [
            make_inline_btn("Reject", callback_data=f"adm_rej_{payment_id}", emoji_id="5422557736330106570", style="danger"),
            make_inline_btn("Approve", callback_data=f"adm_app_{payment_id}", emoji_id="6298670698948724690", style="success")
        ]
    ])
    for admin_id in get_admins():
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_msg, reply_markup=kb, parse_mode="HTML")
        except:
            pass

    context.user_data.clear()

# ==================== ADMIN PANEL - ACTIONS ====================

async def admin_ban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["admin_ban_mode"] = True
    context.user_data["admin_unban_mode"] = False
    await update.message.reply_text(
        f"{get_tg_emoji('ban')} <b>SEND TELEGRAM ID TO BAN USER</b> {get_tg_emoji('ban')}\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>Please send the Telegram User ID you want to ban:</blockquote>",
        parse_mode="HTML"
    )

async def admin_unban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["admin_unban_mode"] = True
    context.user_data["admin_ban_mode"] = False
    await update.message.reply_text(
        f"{get_tg_emoji('done')} <b>SEND UNBAN USER ID</b> {get_tg_emoji('done')}\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>Please send the Telegram User ID you want to unban:</blockquote>",
        parse_mode="HTML"
    )

async def show_banned_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banned = load_banned_users()
    if not banned:
        await update.message.reply_text(f"{get_tg_emoji('cross')} <b>No banned users found.</b>", parse_mode="HTML")
        return
    
    text = f"{get_tg_emoji('ban')} <b>BANNED USERS LIST</b>:\n━━━━━━━━━━━━━━━━━━\n"
    for idx, user_id in enumerate(banned, 1):
        text += f"{idx}. <code>{user_id}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def process_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["admin_ban_mode"] = False
    target = update.message.text.strip()
    if target.isdigit():
        if ban_user(target):
            await update.message.reply_text(f"{get_tg_emoji('done')} <b>User {target} has been Banned!</b>", parse_mode="HTML")
        else:
            await update.message.reply_text("User is already banned.")
    else:
        await update.message.reply_text("Invalid User ID.")

async def process_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["admin_unban_mode"] = False
    target = update.message.text.strip()
    if target.isdigit():
        if unban_user(target):
            await update.message.reply_text(f"{get_tg_emoji('done')} <b>User {target} has been Unbanned!</b>", parse_mode="HTML")
        else:
            await update.message.reply_text("User is not banned.")
    else:
        await update.message.reply_text("Invalid User ID.")

# ==================== ADMIN DYNAMIC SETTERS ====================

async def admin_set_cooldown_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid): return
    context.user_data["admin_edit_mode"] = "cooldown"
    await update.message.reply_text(
        f"{get_tg_emoji('waiting')} <b>SET COOLDOWN TIME</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>নম্বর রিকোয়েস্ট/চেঞ্জিং এর কুলডাউন সেকেন্ড সংখ্যায় পাঠান (যেমন: 4.0):</blockquote>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_set_force_join_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid): return
    context.user_data["admin_edit_mode"] = "force_join_channels"
    settings = load_settings()
    current_ch = ", ".join(settings.get("force_join_channels", []))
    await update.message.reply_text(
        f"{get_tg_emoji('link')} <b>SET FORCE JOIN CHANNELS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>Current Channels: <code>{current_ch}</code></blockquote>\n\n"
        f"<blockquote>নতুন চ্যানেল লিস্ট টাইপ করে পাঠান:</blockquote>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_edit_links_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid): return
    
    keyboard = InlineKeyboardMarkup([
        [make_inline_btn("Edit Welcome Msg", callback_data="edit_txt_welcome", emoji_id="5253742260054409879", style="primary")],
        [make_inline_btn("Edit OTP Group Link", callback_data="edit_txt_otpgroup", emoji_id="5271604874419647061", style="primary")],
        [make_inline_btn("Edit Channel Link", callback_data="edit_txt_channel", emoji_id="6215074610845585917", style="primary")],
        [make_inline_btn("Edit Panel URL Link", callback_data="edit_txt_panelurl", emoji_id="5271604874419647061", style="primary")],
        [make_inline_btn("Edit Support Username", callback_data="edit_txt_support", emoji_id="5341715473882955310", style="primary")],
        [make_inline_btn("Back", callback_data="admin_back_to_config", emoji_id="5267490665117275176", style="danger")]
    ])
    
    await update.message.reply_text(
        f"{get_tg_emoji('setting')} <b>EDIT LINKS & TEXTS SYSTEM</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"নিচের বাটনগুলো থেকে সিলেক্ট করুন আপনি কোন লেখা বা লিঙ্ক পরিবর্তন করতে চান:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# ==================== MESSAGE HANDLER SECTION ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""

    if not is_admin(uid) and is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", "@MinoXSupport0")
        await update.message.reply_text(
            f"{get_tg_emoji('ban')} <b>YOU ARE BANNED</b> {get_tg_emoji('ban')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ YOU HAVE BEEN BANNED FROM USING THIS BOT.\n"
            f"📞 CONTACT SUPPORT: {support}", 
            parse_mode="HTML", 
            reply_markup=main_keyboard(uid)
        )
        return

    # কিবোর্ড ক্লিকে ডায়নামিক স্টেট রিসেট করা
    if text in MENU_BUTTONS:
        context.user_data.pop("admin_edit_mode", None)
        context.user_data.pop("admin_ban_mode", None)
        context.user_data.pop("admin_unban_mode", None)
        context.user_data.pop("mode", None)
        context.user_data.pop("broadcast_mode", None)
        context.user_data.pop("withdraw_mode", None)

    # মাল্টিমিডিয়া ব্রডকাস্টার (সুরক্ষিত ও সুরক্ষিত ব্যাকগ্রাউন্ড সেন্ডার)
    if context.user_data.get("broadcast_mode") and is_admin(uid):
        context.user_data["broadcast_mode"] = False
        user_db = load_data(USER_DATA_FILE)
        all_uids = list(user_db.keys())
        
        if not all_uids:
            await update.message.reply_text(f"{get_tg_emoji('cross')} পাঠানোর জন্য কোনো ইউজার পাওয়া যায়নি!", parse_mode="HTML")
            return

        # অ্যাডমিনকে তাৎক্ষণিকভাবে রেসপন্স প্রদান
        await update.message.reply_text(
            f"{get_tg_emoji('broadcast')} <b>ব্রডকাস্ট ব্যাকগ্রাউন্ডে সফলভাবে শুরু হয়েছে!</b>\n"
            f"সম্পূর্ণ শেষ হলে আপনাকে ইনবক্সে রিপোর্ট পাঠানো হবে।",
            parse_mode="HTML"
        )

        orig_text = update.message.text or update.message.caption or ""
        formatted_text = auto_premium_emoji_formatter(orig_text)
        is_text_msg = bool(update.message.text)
        
        # ব্যাকগ্রাউন্ড কোরুটিন রান করা
        async def run_bg_broadcast(bot, admin_id, uids, is_txt, msg_obj, fmt_text):
            try:
                sem = asyncio.Semaphore(50)  # প্রতি সেকেন্ডে সর্বোচ্চ ৫০টি কনকারেন্ট রিকোয়েস্ট
                tasks = []
                for user_id_str in uids:
                    # শুধুমাত্র সাংখ্যিক আইডিগুলোতে পাঠানো নিশ্চিত করার নিরাপত্তা কোড
                    if str(user_id_str).isdigit():
                        tasks.append(send_broadcast_task(bot, sem, int(user_id_str), is_txt, msg_obj, fmt_text, kb=None))
                    
                if not tasks:
                    await bot.send_message(chat_id=admin_id, text="⚠️ No valid users found for broadcast.", parse_mode="HTML")
                    return

                results = await asyncio.gather(*tasks)
                success = sum(1 for r in results if r)
                fail = len(results) - success

                report_text = (
                    f"{get_tg_emoji('done')} <b>BROADCAST NOTICE COMPLETE !</b>\n\n"
                    f"{get_tg_emoji('status')} <b>REPORT:</b>\n\n"
                    f"<blockquote>✅ Succeeded: {success} Users</blockquote>\n"
                    f"<blockquote>❌ Failed: {fail} Users</blockquote>"
                )
                await bot.send_message(chat_id=admin_id, text=report_text, parse_mode="HTML")
            except Exception as e:
                try:
                    await bot.send_message(chat_id=admin_id, text=f"❌ Broadcast background error: {str(e)}")
                except:
                    pass

        asyncio.create_task(run_bg_broadcast(context.bot, uid, all_uids, is_text_msg, update.message, formatted_text))
        return

    # উইথড্রয়াল স্টেট
    withdraw_mode = context.user_data.get("withdraw_mode")
    if withdraw_mode == "amount":
        await process_withdraw_amount(update, context)
        return
    elif withdraw_mode == "number":
        await process_withdraw_number(update, context)
        return

    # এডমিন কনফিগারেশন ইনপুট
    edit_mode = context.user_data.get("admin_edit_mode")
    if edit_mode and is_admin(uid):
        context.user_data["admin_edit_mode"] = None
        settings = load_settings()
        
        if edit_mode == "welcome":
            settings["welcome_message"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} Welcome Message সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
            save_settings(settings)
        elif edit_mode == "otpgroup":
            if text.startswith("http"):
                settings["otp_group_url"] = text
                await update.message.reply_text(f"{get_tg_emoji('done')} OTP Group লিঙ্ক সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল লিঙ্ক ফরম্যাট!", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "channel":
            if text.startswith("http"):
                settings["channel_url"] = text
                await update.message.reply_text(f"{get_tg_emoji('done')} Channel লিঙ্ক সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল লিঙ্ক ফরম্যাট!", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "panelurl":
            if text.startswith("http"):
                settings["panel_url"] = text
                await update.message.reply_text(f"{get_tg_emoji('done')} Panel URL লিঙ্ক সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল লিঙ্ক ফরম্যাট!", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "support":
            if text.startswith("@"):
                settings["support_username"] = text
                await update.message.reply_text(f"{get_tg_emoji('done')} Support Username সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল ইউজারনেম ফরম্যাট!", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "cooldown":
            try:
                settings["cooldown_time"] = float(text)
                await update.message.reply_text(f"{get_tg_emoji('done')} Cooldown লিমিট সফলভাবে {text} সেকেন্ড সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "otp_bonus":
            try:
                val = float(text)
                settings["otp_bonus"] = val
                await update.message.reply_text(f"{get_tg_emoji('done')} OTP Bonus সফলভাবে ${val} সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "referral_bonus":
            try:
                val = float(text)
                settings["referral_bonus"] = val
                await update.message.reply_text(f"{get_tg_emoji('done')} Referral Bonus সফলভাবে ${val} সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "force_join_channels":
            channels_list = [ch.strip() for ch in text.split(",") if ch.strip()]
            settings["force_join_channels"] = channels_list
            await update.message.reply_text(f"{get_tg_emoji('done')} Force Join চ্যানেলসমূহ সফলভাবে সেট করা হয়েছে!", reply_markup=admin_security_join_keyboard())
            save_settings(settings)
        elif edit_mode == "add_admin":
            if text.isdigit():
                new_admin_id = int(text)
                admins_list = settings.get("admins", [8214164198])
                if new_admin_id not in admins_list:
                    admins_list.append(new_admin_id)
                    settings["admins"] = admins_list
                    save_settings(settings)
                    await update.message.reply_text(f"{get_tg_emoji('done')} User <code>{new_admin_id}</code> সফলভাবে অ্যাডমিন হিসেবে যুক্ত হয়েছে!", parse_mode="HTML", reply_markup=admin_security_join_keyboard())
                else:
                    await update.message.reply_text(f"{get_tg_emoji('cross')} ইউজার ইতিমধ্যে অ্যাডমিন তালিকায় আছেন!", reply_markup=admin_security_join_keyboard())
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল ইউজার আইডি ফরম্যাট!", reply_markup=admin_security_join_keyboard())
        elif edit_mode == "remove_admin":
            if text.isdigit():
                target_admin_id = int(text)
                if target_admin_id == 8214164198:
                    await update.message.reply_text(f"{get_tg_emoji('cross')} আপনি মূল প্রধান অ্যাডমিন রিমুভ করতে পারবেন না!", reply_markup=admin_security_join_keyboard())
                else:
                    admins_list = settings.get("admins", [8214164198])
                    if target_admin_id in admins_list:
                        admins_list.remove(target_admin_id)
                        settings["admins"] = admins_list
                        save_settings(settings)
                        await update.message.reply_text(f"{get_tg_emoji('done')} User <code>{target_admin_id}</code> সফলভাবে অ্যাডমিন তালিকা থেকে বাদ পড়েছে!", parse_mode="HTML", reply_markup=admin_security_join_keyboard())
                    else:
                        await update.message.reply_text(f"{get_tg_emoji('cross')} ইউজার অ্যাডমিন তালিকায় নেই!", reply_markup=admin_security_join_keyboard())
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল ইউজার আইডি ফরম্যাট!", reply_markup=admin_security_join_keyboard())
        elif edit_mode == "allowed_services":
            services_list = [s.strip() for s in text.split(",") if s.strip()]
            settings["allowed_services"] = services_list
            await update.message.reply_text(f"{get_tg_emoji('done')} সচল সার্ভিস ফিল্টার সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "numbers_per_request":
            try:
                val = int(text)
                if val < 1: raise ValueError
                settings["numbers_per_request"] = val
                await update.message.reply_text(f"{get_tg_emoji('done')} Numbers Per Request সফলভাবে {val} টি সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text(f"{get_tg_emoji('cross')} ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "direct_msg_uid":
            if text.isdigit():
                context.user_data["admin_direct_uid"] = text
                context.user_data["admin_edit_mode"] = "direct_msg_text"
                await update.message.reply_text(f"{get_tg_emoji('msg')} <b>Now enter the message content to send:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} Invalid User ID!", reply_markup=admin_user_config_keyboard())
        elif edit_mode == "direct_msg_text":
            target_uid = context.user_data.get("admin_direct_uid")
            try:
                formatted_text = auto_premium_emoji_formatter(text)
                await context.bot.send_message(chat_id=int(target_uid), text=f"{get_tg_emoji('msg')} <b>MESSAGE FROM ADMIN:</b>\n\n{formatted_text}", parse_mode="HTML")
                await update.message.reply_text(f"{get_tg_emoji('done')} Message sent successfully!", reply_markup=admin_user_config_keyboard())
            except Exception as e:
                await update.message.reply_text(f"{get_tg_emoji('cross')} Failed to send message: {e}", reply_markup=admin_user_config_keyboard())
        elif edit_mode == "search_username":
            uname = text.replace("@", "").strip().lower()
            users = load_data(USER_DATA_FILE)
            found = False
            for u_id, details in users.items():
                if str(details.get("username", "")).lower() == uname:
                    found = True
                    stats = get_user_stats(u_id)
                    status_msg = (
                        f"{get_tg_emoji('profile')} <b>USER FOUND CHECK</b> {get_tg_emoji('status')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🆔 <b>User ID:</b> <code>{u_id}</code>\n"
                        f"🏷️ <b>Username:</b> @{details.get('username')}\n"
                        f"👥 <b>Total Referred:</b> <code>{details.get('referred_count', 0)}</code>\n"
                        f"🔗 <b>Referred By:</b> <code>{details.get('referred_by') or 'None'}</code>\n\n"
                        f"{get_tg_emoji('up')} <b>TODAY STATUS</b>\n"
                        f"📱 NUMBERS TAKEN : {stats['today_numbers']}\n"
                        f"🔑 OTPS RECEIVED : {stats['today_otps']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━"
                    )
                    kb = InlineKeyboardMarkup([[
                        make_inline_btn("CHECK ALL DATA", callback_data=f"full_logs_{u_id}", emoji_id="6215074610845585917", style="primary")
                    ]])
                    await update.message.reply_text(status_msg, parse_mode="HTML", reply_markup=kb)
                    break
            if not found:
                await update.message.reply_text(f"{get_tg_emoji('cross')} No user found with that username.", reply_markup=admin_user_config_keyboard())
        elif edit_mode == "broadcast_btn_msg":
            context.user_data["admin_broadcast_msg_obj"] = update.message
            context.user_data["admin_edit_mode"] = "broadcast_btn_text"
            await update.message.reply_text(f"{get_tg_emoji('link')} <b>Enter the Button Text:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        elif edit_mode == "broadcast_btn_text":
            context.user_data["admin_broadcast_btn_text"] = text
            context.user_data["admin_edit_mode"] = "broadcast_btn_url"
            await update.message.reply_text(f"{get_tg_emoji('link')} <b>Enter the Button URL (https://...):</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        elif edit_mode == "broadcast_btn_url":
            if text.startswith("http"):
                msg_obj = context.user_data.get("admin_broadcast_msg_obj")
                btn_txt = context.user_data.get("admin_broadcast_btn_text")
                btn_url = text
                
                users = load_data(USER_DATA_FILE)
                kb = InlineKeyboardMarkup([[InlineKeyboardButton(btn_txt, url=btn_url)]])
                orig_text = msg_obj.text or msg_obj.caption or ""
                formatted_text = auto_premium_emoji_formatter(orig_text)

                # বাটন সহ ব্রডকাস্ট ব্যাকগ্রাউন্ড টাস্ক শুরু এবং অ্যাডমিন রেসপন্স প্রদান
                await update.message.reply_text(
                    f"{get_tg_emoji('broadcast')} <b>লিঙ্ক বাটন সহ ব্রডকাস্ট ব্যাকগ্রাউন্ডে সফলভাবে শুরু হয়েছে!</b>\n"
                    f"সম্পূর্ণ শেষ হলে আপনাকে ইনবক্সে চূড়ান্ত রিপোর্ট পাঠানো হবে।", 
                    parse_mode="HTML"
                )
                
                all_uids = list(users.keys())
                is_text_msg = bool(msg_obj.text)

                async def run_bg_btn_broadcast(bot, admin_id, uids, is_txt, m_obj, fmt_text, keyboard_layout):
                    try:
                        sem = asyncio.Semaphore(50)
                        tasks = []
                        for target_uid in uids:
                            # শুধুমাত্র সাংখ্যিক আইডিগুলোতে পাঠানো নিশ্চিত করার নিরাপত্তা কোড
                            if str(target_uid).isdigit():
                                tasks.append(send_broadcast_task(bot, sem, int(target_uid), is_txt, m_obj, fmt_text, kb=keyboard_layout))
                        
                        if not tasks:
                            await bot.send_message(chat_id=admin_id, text="⚠️ No valid users found for button broadcast.", parse_mode="HTML")
                            return

                        results = await asyncio.gather(*tasks)
                        success = sum(1 for r in results if r)
                        fail = len(results) - success
                        await bot.send_message(
                            chat_id=admin_id,
                            text=f"{get_tg_emoji('done')} <b>BUTTON BROADCAST COMPLETE!</b>\n\n"
                                 f"✅ Succeeded: {success}\n❌ Failed: {fail}",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        try:
                            await bot.send_message(chat_id=admin_id, text=f"❌ Button broadcast background error: {str(e)}")
                        except:
                            pass

                asyncio.create_task(run_bg_btn_broadcast(context.bot, uid, all_uids, is_text_msg, msg_obj, formatted_text, kb))
                context.user_data.clear()
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} Invalid URL! Must start with https://.", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "add_balance_uid":
            if text.isdigit():
                context.user_data["admin_add_uid"] = text
                context.user_data["admin_edit_mode"] = "add_balance_amount"
                await update.message.reply_text(f"{get_tg_emoji('money')} <b>Type the amount of USD to ADD to user balance:</b>", reply_markup=cancel_keyboard(), parse_mode="HTML")
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} Invalid ID!", reply_markup=admin_user_config_keyboard())
        elif edit_mode == "add_balance_amount":
            try:
                amt = float(text)
                target = context.user_data.get("admin_add_uid")
                await update_db_balance(target, amt)
                await update.message.reply_text(f"{get_tg_emoji('done')} ${amt} added to User: `{target}` successfully!", reply_markup=admin_user_config_keyboard())
            except:
                await update.message.reply_text(f"{get_tg_emoji('cross')} Invalid amount!", reply_markup=admin_user_config_keyboard())
        elif edit_mode == "rem_balance_uid":
            if text.isdigit():
                context.user_data["admin_rem_uid"] = text
                context.user_data["admin_edit_mode"] = "rem_balance_amount"
                await update.message.reply_text(f"{get_tg_emoji('money')} <b>Type the amount of USD to REMOVE from user balance:</b>", reply_markup=cancel_keyboard(), parse_mode="HTML")
            else:
                await update.message.reply_text(f"{get_tg_emoji('cross')} Invalid ID!", reply_markup=admin_user_config_keyboard())
        elif edit_mode == "rem_balance_amount":
            try:
                amt = float(text)
                target = context.user_data.get("admin_rem_uid")
                await update_db_balance(target, -amt)
                await update.message.reply_text(f"{get_tg_emoji('delete')} ${amt} removed from User: `{target}` successfully!", reply_markup=admin_user_config_keyboard())
            except:
                await update.message.reply_text(f"{get_tg_emoji('cross')} Invalid amount!", reply_markup=admin_user_config_keyboard())
        elif edit_mode == "stex_sms_api_key":
            settings["stex_sms_api_key"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} Stex SMS API Key সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "stex_sms_base_url":
            settings["stex_sms_base_url"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} Stex SMS Base URL সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "zenex_api_key":
            settings["zenex_api_key"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} Zenex API Key সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "zenex_base_url":
            settings["zenex_base_url"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} Zenex Base URL সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "voltx_sms_api_key":
            settings["voltx_sms_api_key"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} Voltx SMS API Key সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "voltx_sms_base_url":
            settings["voltx_sms_base_url"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} Voltx SMS Base URL সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "fastxotp_api_key":
            settings["fastxotp_api_key"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} FastXOTP API Key সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "fastxotp_base_url":
            settings["fastxotp_base_url"] = text
            await update.message.reply_text(f"{get_tg_emoji('done')} FastXOTP Base URL সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
            save_settings(settings)
        elif edit_mode == "fj_add_channel":
            channels = settings.get("force_join_channels", [])
            ch_name = text.strip()
            if not ch_name.startswith("@") and not ch_name.replace("-", "").isdigit():
                await update.message.reply_text("❌ Invalid format! Channel must start with @ or be a negative ID.", reply_markup=admin_security_join_keyboard())
                return
            if ch_name not in channels:
                channels.append(ch_name)
                settings["force_join_channels"] = channels
                save_settings(settings)
                await update.message.reply_text(f"✅ Channel <code>{ch_name}</code> added successfully!", parse_mode="HTML")
                await show_force_join_manager(update, context)
            else:
                await update.message.reply_text("❌ Channel already exists!", reply_markup=admin_security_join_keyboard())
        elif edit_mode == "fj_del_channel":
            channels = settings.get("force_join_channels", [])
            if text.isdigit():
                idx = int(text) - 1
                if 0 <= idx < len(channels):
                    removed = channels.pop(idx)
                    settings["force_join_channels"] = channels
                    save_settings(settings)
                    await update.message.reply_text(f"✅ Channel <code>{removed}</code> deleted successfully!", parse_mode="HTML")
                    await show_force_join_manager(update, context)
                else:
                    await update.message.reply_text("❌ Invalid index number!", reply_markup=admin_security_join_keyboard())
            else:
                await update.message.reply_text("❌ Please enter a valid number index!", reply_markup=admin_security_join_keyboard())
        return

    if context.user_data.get("admin_ban_mode") and is_admin(uid):
        await process_ban_user(update, context)
        return
    
    if context.user_data.get("admin_unban_mode") and is_admin(uid):
        await process_unban_user(update, context)
        return

    if text == "CANCEL":
        context.user_data.clear()
        await update.message.reply_text(f"{get_tg_emoji('cross')} CANCELLED", reply_markup=main_keyboard(uid), parse_mode="HTML")
        return

    # কাস্টম রেঞ্জ কাস্টমাইজেশন
    if text == "Custom Range":
        context.user_data["mode"] = "range_1"
        await update.message.reply_text("Entering Custom Range mode...", reply_markup=cancel_keyboard())
        await update.message.reply_text(
            f"{get_tg_emoji('custom_range')} <b>ENTER CUSTOM RANGE</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>Please type and send your custom range (e.g. +236X or 236):</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                make_inline_btn("View Range", url="https://t.me/voltxsmsrenge", emoji_id="5271604874419647061", style="primary")
            ]])
        )
        return

    # লিডারবোর্ড ভিউ
    if text == "LEADERBOARD":
        leaderboard_text = get_leaderboard_text()
        kb = None
        if is_admin(uid):
            kb = InlineKeyboardMarkup([[
                make_inline_btn("Reset Leaderboard", callback_data="admin_reset_leaderboard", emoji_id="5422557736330106570", style="danger")
            ]])
        await update.message.reply_text(leaderboard_text, parse_mode="HTML", reply_markup=kb)
        return

    # --- ADMIN SUB-CATEGORY REDIRECTS ---

    if text == "SYSTEM CONFIG" and is_admin(uid):
        await update.message.reply_text(f"{get_tg_emoji('setting')} <b>System Configuration Category:</b>", parse_mode="HTML", reply_markup=admin_system_config_keyboard())
        return

    if text == "USER CONFIG" and is_admin(uid):
        await update.message.reply_text(f"{get_tg_emoji('profile')} <b>User Configuration Category:</b>", parse_mode="HTML", reply_markup=admin_user_config_keyboard())
        return

    if text == "SECURITY & JOIN" and is_admin(uid):
        await update.message.reply_text(f"{get_tg_emoji('ban')} <b>Security & Force Join Category:</b>", parse_mode="HTML", reply_markup=admin_security_join_keyboard())
        return

    if text == "NOTICE & B-CAST" and is_admin(uid):
        await update.message.reply_text(f"{get_tg_emoji('msg')} <b>Notices & Broadcasting Category:</b>", parse_mode="HTML", reply_markup=admin_notice_bcast_keyboard())
        return

    if text == "API & MONITOR" and is_admin(uid):
        settings = load_settings()
        panel = settings.get("active_panel", "zenex").upper()
        keyboard = InlineKeyboardMarkup([
            [make_inline_btn(f"Active Panel: [{panel}]", callback_data="admin_select_panel", emoji_id="5355102594886833928")],
            [make_inline_btn("Zenex Config", callback_data="admin_config_zenex", emoji_id="5341715473882955310")],
            [make_inline_btn("Voltx SMS Config", callback_data="admin_config_voltx_sms", emoji_id="5341715473882955310")],
            [make_inline_btn("Stex SMS Config", callback_data="admin_config_stex_sms", emoji_id="5341715473882955310")],
            [make_inline_btn("FastXOTP Config", callback_data="admin_config_fastxotp", emoji_id="5341715473882955310")]
        ])
        await update.message.reply_text(f"{get_tg_emoji('live')} <b>API, Multi-Panel & Live Monitoring Category:</b>", parse_mode="HTML", reply_markup=admin_api_monitor_keyboard())
        await update.message.reply_text(f"{get_tg_emoji('setting')} <b>Choose API Panel operation to perform:</b>", reply_markup=keyboard, parse_mode="HTML")
        return
# ==================== MAIN SUB-MENU ACTIONS ====================

    if text == "GET NUMBER PER REQUEST" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "numbers_per_request"
        await update.message.reply_text(
            f"{get_tg_emoji('add')} <b>GET NUMBER PER REQUEST LIMIT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>ইউজার একসাথে কয়টি নাম্বার পাবে তা সংখ্যায় টাইপ করে পাঠান:</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "SET COOLDOWN" and is_admin(uid):
        await admin_set_cooldown_start(update, context)
        return

    if text == "EDIT ALLOWED SERVICES" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "allowed_services"
        await update.message.reply_text(
            f"{get_tg_emoji('setting')} <b>EDIT ALLOWED SERVICES</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>অনুমোদিত সার্ভিসগুলোর নাম কমা দিয়ে লিখে পাঠান (যেমন: Facebook, WhatsApp, Telegram):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "SET OTP BONUS" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "otp_bonus"
        await update.message.reply_text(
            f"{get_tg_emoji('money')} <b>SET OTP BONUS AMOUNT</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>প্রতিটি ওটিপি রিসিভের জন্য বোনাস এমাউন্ট টাইপ করে পাঠান (যেমন: 0.0012):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "SET REFERRAL BONUS" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "referral_bonus"
        await update.message.reply_text(
            f"{get_tg_emoji('gift_box')} <b>SET REFERRAL BONUS AMOUNT</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>সফল রেফারেলের জন্য বোনাস এমাউন্ট টাইপ করে পাঠান (যেমন: 0.004):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "TOGGLE MAINTENANCE" and is_admin(uid):
        settings = load_settings()
        settings["maintenance_mode"] = not settings.get("maintenance_mode", False)
        save_settings(settings)
        status = "ENABLED 🟢" if settings["maintenance_mode"] else "DISABLED 🔴"
        await update.message.reply_text(f"{get_tg_emoji('stop')} Maintenance Mode has been {status}!", reply_markup=admin_system_config_keyboard(), parse_mode="HTML")
        return

    if text == "DIRECT MSG USER" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "direct_msg_uid"
        await update.message.reply_text(
            f"{get_tg_emoji('msg')} <b>DIRECT MESSAGE TO USER</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>মেসেজ পাঠাতে ইউজারের Telegram ID টাইপ করে পাঠান:</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "SEARCH BY USERNAME" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "search_username"
        await update.message.reply_text(
            f"{get_tg_emoji('get_number_btn')} <b>SEARCH USER BY USERNAME</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>ইউজারের ইউজারনেম টাইপ করে পাঠান (@ ছাড়া বা @ সহ):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "EDIT LINKS & TEXTS" and is_admin(uid):
        await admin_edit_links_start(update, context)
        return

    if text == "SET FORCE JOIN" and is_admin(uid):
        await show_force_join_manager(update, context)
        return

    if text == "TOGGLE FORCE JOIN" and is_admin(uid):
        settings = load_settings()
        settings["force_join_enabled"] = not settings.get("force_join_enabled", False)
        save_settings(settings)
        status = "ENABLED 🟢" if settings["force_join_enabled"] else "DISABLED 🔴"
        await update.message.reply_text(f"{get_tg_emoji('ban')} Force Join System has been {status}!", reply_markup=admin_security_join_keyboard(), parse_mode="HTML")
        return

    if text == "TOGGLE JOIN ALERT" and is_admin(uid):
        settings = load_settings()
        settings["join_alert_enabled"] = not settings.get("join_alert_enabled", True)
        save_settings(settings)
        status = "ENABLED 🟢" if settings["join_alert_enabled"] else "DISABLED 🔴"
        await update.message.reply_text(f"{get_tg_emoji('msg')} New User Join Notification is now {status}!", reply_markup=admin_security_join_keyboard(), parse_mode="HTML")
        return

    if text == "ADD BALANCE" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "add_balance_uid"
        await update.message.reply_text(f"{get_tg_emoji('add')} <b>Send the User Telegram ID to add USD balance:</b>", reply_markup=cancel_keyboard(), parse_mode="HTML")
        return

    if text == "REMOVE BALANCE" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "rem_balance_uid"
        await update.message.reply_text(f"{get_tg_emoji('delete')} <b>Send the User Telegram ID to remove USD balance:</b>", reply_markup=cancel_keyboard(), parse_mode="HTML")
        return

    if text == "ALL USER BALANCE" and is_admin(uid):
        user_db = load_data(USER_DATA_FILE)
        if user_db:
            total_users = len(user_db)
            total_system_balance = 0.0
            balance_lines = []
            
            for i, (user_id, info) in enumerate(user_db.items(), 1):
                u_bal = info.get("balance", 0.0)
                total_system_balance += u_bal
                balance_lines.append(f"{i}. ID: {user_id} | Balance: $ {u_bal:.2f}")
            
            file_content = "💵 ALL USER BALANCE REPORT (USD) 💵\n"
            file_content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            file_content += f"👥 Total Users: {total_users}\n"
            file_content += f"💵 Total System Balance: $ {total_system_balance:.2f}\n"
            file_content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            file_content += "\n".join(balance_lines)
            
            file_io = io.BytesIO(file_content.encode("utf-8"))
            file_io.name = "balance_sheet.txt"
            
            await update.message.reply_document(
                document=file_io,
                caption=f"👥 Total Users: {total_users}\n💵 Total System Balance: $ {total_system_balance:.2f}",
                reply_markup=admin_user_config_keyboard()
            )
        return

    if text == "SUPPORT":
        await support_command(update, context)
        return

    if text == "GET NUMBER":
        await show_app_selection(update, context)
        return

    if text == "PROFILE":
        await show_profile_command(update, context)
        return

    if text == "ADD ADMIN" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "add_admin"
        await update.message.reply_text(
            f"{get_tg_emoji('add')} <b>ADD NEW *</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>নতুন এডমিনের Telegram User ID টাইপ করে পাঠান:</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "REMOVE ADMIN" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "remove_admin"
        await update.message.reply_text(
            f"{get_tg_emoji('delete')} <b>REMOVE ADMIN ID</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>যে এডমিনকে রিমুভ করতে চান তার Telegram User ID টাইপ করে পাঠান:</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if context.user_data.get("mode") in ["range_1"]:
        if "X" in text.upper() or text.isdigit():
            settings = load_settings()
            count = settings.get("numbers_per_request", 1)
            context.user_data["mode"] = None
            await request_queue.put({'type': 'process_numbers', 'update': update, 'context': context, 'range_text': text, 'count': count})
        return
    
    # ==================== ADMIN PANEL - MAIN HANDLERS ====================

    if text == "ADMIN PANEL" and is_admin(uid):
        context.user_data["admin_mode"] = "main"
        
        today_n, today_o, seven_n, seven_o, total_n, total_o = get_global_system_stats()
        users_count = len(get_all_users())
        banned_count = len(load_banned_users())
        active_numbers_count = len(active_numbers)
        settings = load_settings()
        panel = settings.get("active_panel", "zenex").upper()
        
        admin_welcome = (
            f"⌬━━━━━━━━━━━━━━━━━━━━⌬\n"
            f"       {get_tg_emoji('admin')} <b>ADVANCED ADMIN PANEL</b> {get_tg_emoji('admin')}       \n"
            f"⌬━━━━━━━━━━━━━━━━━━━━⌬\n\n"
            f"{get_tg_emoji('setting')} <b>Active Backend:</b> <code>{panel}</code>\n"
            f"{get_tg_emoji('profile')} <b>Registered Users:</b> <code>{users_count}</code>\n"
            f"{get_tg_emoji('ban')} <b>Banned Users:</b> <code>{banned_count}</code>\n"
            f"{get_tg_emoji('get_number_btn')} <b>Reserved Numbers:</b> <code>{active_numbers_count}</code>\n\n"
            f"{get_tg_emoji('status')} <b>Global Activity Stats:</b>\n"
            f"<blockquote>• Today: <code>{today_n}</code> Numbers | <code>{today_o}</code> OTPs {get_tg_emoji('live')}\n"
            f"• 7 Days: <code>{seven_n}</code> Numbers | <code>{seven_o}</code> OTPs {get_tg_emoji('up')}\n"
            f"• Lifetime: <code>{total_n}</code> Numbers | <code>{total_o}</code> OTPs {get_tg_emoji('1st')}</blockquote>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(admin_welcome, reply_markup=admin_main_keyboard(), parse_mode="HTML")
        return

    if text == "BACK TO MAIN" and context.user_data.get("admin_mode"):
        context.user_data.clear()
        await update.message.reply_text(f"{get_tg_emoji('back')} Back to main menu.", reply_markup=main_keyboard(uid), parse_mode="HTML")
        return

    if text == "BACK TO ADMIN":
        context.user_data.clear()
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text(f"{get_tg_emoji('back')} Back to admin panel.", reply_markup=admin_main_keyboard(), parse_mode="HTML")
        return

    if text == "VIEW CONFIG OVERVIEW" and is_admin(uid):
        settings = load_settings()
        api_key, base_url = get_api_credentials()
        overview = (
            f"{get_tg_emoji('status')} <b>BOT CONFIGURATION OVERVIEW</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{get_tg_emoji('setting')} <b>Active Panel:</b> <code>{settings.get('active_panel', 'zenex').upper()}</code>\n"
            f"{get_tg_emoji('link')} <b>Active API Key:</b> <code>{api_key}</code>\n"
            f"{get_tg_emoji('home')} <b>Active BASE URL:</b> <code>{base_url}</code>\n"
            f"{get_tg_emoji('up')} <b>Max Numbers Per Batch:</b> <code>{settings.get('max_numbers_per_user', 100)}</code>\n"
            f"{get_tg_emoji('get_number_btn')} <b>Numbers Per Request:</b> <code>{settings.get('numbers_per_request', 1)}</code>\n"
            f"{get_tg_emoji('money')} <b>OTP Bonus:</b> <code>$ {settings.get('otp_bonus', 0.0012)}</code>\n"
            f"{get_tg_emoji('gift_box')} <b>Referral Bonus:</b> <code>$ {settings.get('referral_bonus', 0.004)}</code>\n"
            f"{get_tg_emoji('stop')} <b>Maintenance Mode:</b> <code>{'ENABLED' if settings.get('maintenance_mode', False) else 'DISABLED'}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(overview, parse_mode="HTML", reply_markup=admin_api_monitor_keyboard())
        return

    if text == "BROADCAST NOTICE" and is_admin(uid):
        context.user_data["broadcast_mode"] = True
        await update.message.reply_text(
            f"{get_tg_emoji('msg')} <b>BROADCAST NOTICE SYSTEM</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>যে নোটিশটি ব্রডকাস্ট করতে চান তা টেক্সট, ফটো বা যেকোনো মিডিয়া ফরম্যাটে পাঠান। স্বয়ংক্রিয়ভাবে প্রিমিয়াম ইমোজিগুলো ফরম্যাট হয়ে যাবে।</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "B-CAST WITH BUTTON" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "broadcast_btn_msg"
        await update.message.reply_text(
            f"{get_tg_emoji('msg')} <b>BROADCAST WITH LINK BUTTON</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>মেসেজের কন্টেন্টটি পাঠান (ফটো, টেক্সট বা মিডিয়া):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return
    
    if text == "USER STATUS CHECK" and is_admin(uid):
        context.user_data["mode"] = "input_user_id"
        msg = (
            f"<blockquote>🔍 <b>ENTER TELEGRAM ID</b> 🔍</blockquote>\n\n"
            f"<blockquote>💬 PLEASE ENTER THE TELEGRAM ID OF THE USER YOU WANT TO SEARCH FOR :</blockquote>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("mode") == "input_user_id" and is_admin(uid):
        target_uid = text.strip()
        if not target_uid.isdigit():
            await update.message.reply_text(f"{get_tg_emoji('cross')} INVALID ID! PLEASE SEND A NUMERIC TELEGRAM ID.", parse_mode="HTML")
            return
        
        context.user_data["mode"] = None
        stats = get_user_stats(target_uid)
        target_user_info = get_user(target_uid)
        
        status_msg = (
            f"{get_tg_emoji('profile')} <b>USER STATUS CHECK</b> {get_tg_emoji('status')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 <b>User ID:</b> <code>{target_uid}</code>\n"
            f"🏷️ <b>Username:</b> @{target_user_info.get('username') or 'N/A'}\n"
            f"👥 <b>Total Referred:</b> <code>{target_user_info.get('referred_count', 0)}</code>\n"
            f"🔗 <b>Referred By:</b> <code>{target_user_info.get('referred_by') or 'None'}</code>\n\n"
            f"{get_tg_emoji('live')} <b>TODAY ({datetime.now().strftime('%d/%m/%Y')})</b>\n"
            f"{get_tg_emoji('get_number_btn')} NUMBERS TAKEN : {stats['today_numbers']}\n"
            f"{get_tg_emoji('copy')} OTPS RECEIVED : {stats['today_otps']} {get_tg_emoji('live')}\n\n"
            f"{get_tg_emoji('up')} <b>LAST 7 DAYS</b>\n"
            f"{get_tg_emoji('get_number_btn')} NUMBERS TAKEN : {stats['last7d_numbers']}\n"
            f"{get_tg_emoji('copy')} OTPS RECEIVED : {stats['last7d_otps']} {get_tg_emoji('up')}\n\n"
            f"{get_tg_emoji('link')} <b>ALL TIME RECORD</b>\n"
            f"{get_tg_emoji('get_number_btn')} TOTAL NUMBERS : {stats['total_numbers']}\n"
            f"{get_tg_emoji('copy')} TOTAL OTPS : {stats['total_otps']} {get_tg_emoji('1st')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{get_tg_emoji('setting')} <b>Bot | LIVE REAL-TIME DATA</b>"
        )
        
        keyboard = InlineKeyboardMarkup([
            [make_inline_btn("CHECK ALL DATA", callback_data=f"full_logs_{target_uid}", emoji_id="6215074610845585917", style="primary")]
        ])
        
        await update.message.reply_text(status_msg, parse_mode="HTML", reply_markup=keyboard)
        return

    if text == "ALL USER ID" and is_admin(uid):
        users = get_all_users()
        if users:
            total_users = len(users)
            file_lines = []
            for i, user_id in enumerate(users, 1):
                file_lines.append(f"{i}️⃣ {user_id}")
            
            file_content = "\n".join(file_lines)
            file = io.BytesIO(file_content.encode("utf-8"))
            file.name = f"ALL_USERS_{total_users}.txt"
            
            caption = f"{get_tg_emoji('status')} <b>ALL USER LIST</b> {get_tg_emoji('status')}\n\n{get_tg_emoji('profile')} Total Users: {total_users}"
            await update.message.reply_document(
                document=file,
                caption=caption,
                parse_mode="HTML",
                reply_markup=admin_user_config_keyboard()
            )
        else:
            await update.message.reply_text(f"{get_tg_emoji('cross')} No users found.", reply_markup=admin_user_config_keyboard(), parse_mode="HTML")
        return

    if text == "BAN USER LIST" and is_admin(uid):
        await show_banned_users_list(update, context)
        return

    if text == "BAN USER" and is_admin(uid):
        await admin_ban_user_start(update, context)
        return

    if text == "UNBAN USER" and is_admin(uid):
        await admin_unban_user_start(update, context)
        return

    else:
        await update.message.reply_text(f"{get_tg_emoji('home')} <b>PLEASE USE THE BUTTONS BELOW :</b>", parse_mode="HTML", reply_markup=main_keyboard(uid))

# ==================== COMMAND HANDLERS SECTION ====================

async def get1number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", "@MinoXSupport0")
        await update.message.reply_text(
            f"{get_tg_emoji('ban')} <b>YOU ARE BANNED</b> {get_tg_emoji('ban')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ YOU HAVE BEEN BANNED FROM USING THIS BOT.\n"
            f"📞 CONTACT SUPPORT: {support}", 
            parse_mode="HTML", 
            reply_markup=main_keyboard(uid)
        )
        return
    await show_app_selection(update, context)
    
# ==================== START & CALLBACK SECTION ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_str = str(uid)
    username = update.effective_user.username
    full_name = update.effective_user.full_name
    
    existing_data = load_data(USER_DATA_FILE)
    is_new_user = uid_str not in existing_data
    
    user_info = get_user(uid, username, full_name)
    
    args = context.args
    referrer_id = None
    if args:
        param = args[0]
        if param.startswith("ref_"):
            referrer_id = param.replace("ref_", "").strip()
        elif is_range_request(param):
            range_text = param
            await request_queue.put({
                'type': 'auto_number', 
                'update': update, 
                'context': context, 
                'range_text': range_text
            })
            return
            
    if is_new_user and referrer_id:
        if referrer_id.isdigit() and referrer_id != uid_str:
            ref_data = load_data(USER_DATA_FILE)
            if referrer_id in ref_data:
                settings = load_settings()
                ref_bonus = settings.get("referral_bonus", 0.004)
                
                ref_data[uid_str]["referred_by"] = referrer_id
                ref_data[referrer_id]["referred_count"] = ref_data[referrer_id].get("referred_count", 0) + 1
                ref_data[referrer_id]["balance"] = round(ref_data[referrer_id].get("balance", 0.0) + ref_bonus, 5)
                save_data(ref_data, USER_DATA_FILE)
                
                try:
                    await context.bot.send_message(
                        chat_id=int(referrer_id),
                        text=f"{get_tg_emoji('add')} <b>New user joined using your link!</b>\n\n"
                             f"👤 <b>Name:</b> {html.escape(full_name or 'N/A')}\n"
                             f"🆔 <b>ID:</b> <code>{uid}</code>\n"
                             f"{get_tg_emoji('money')} <b>Referral Bonus:</b> +${ref_bonus}",
                        parse_mode="HTML"
                    )
                except:
                    pass
    
    if is_new_user:
        settings = load_settings()
        if settings.get("join_alert_enabled", True):
            alert_msg = (
                f"{get_tg_emoji('channel')} <b>NEW USER JOINED!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{get_tg_emoji('status')} <b>User ID:</b> <code>{uid}</code>\n"
                f"{get_tg_emoji('profile')} <b>Name:</b> {html.escape(full_name or 'N/A')}\n"
                f"{get_tg_emoji('developer')} <b>Username:</b> @{username if username else 'N/A'}"
            )
            for admin_id in get_admins():
                try:
                    await context.bot.send_message(chat_id=admin_id, text=alert_msg, parse_mode="HTML")
                except:
                    pass
    
    context.user_data.clear()
    settings = load_settings()
    start_msg = settings.get("welcome_message", WELCOME_MESSAGE)
    
    await update.message.reply_text(start_msg, parse_mode="HTML")
    await update.message.reply_text(f"{get_tg_emoji('home')} <b>PLEASE USE THE BUTTONS BELOW :</b>", parse_mode="HTML", reply_markup=main_keyboard(uid))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    uid_str = str(uid)
    data = query.data
    await query.answer()
    
    if not is_admin(uid) and is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", "@MinoXSupport0")
        await query.edit_message_text(f"🚫 YOU ARE BANNED 🚫\n━━━━━━━━━━━━━━━━━━━━\n\n❌ YOU HAVE BEEN BANNED FROM USING THIS BOT.\n📞 CONTACT SUPPORT: {support}")
        return
    
    if is_under_maintenance(uid):
        await query.message.reply_text(f"{get_tg_emoji('stop')} <b>SYSTEM UNDER MAINTENANCE</b>", parse_mode="HTML")
        return

    if data == "check_force_join":
        is_joined = await is_user_joined_force_channels(uid, context)
        if is_joined:
            await query.message.delete()
            settings = load_settings()
            start_msg = settings.get("welcome_message", WELCOME_MESSAGE)
            await context.bot.send_message(chat_id=uid, text=start_msg, parse_mode="HTML")
            await context.bot.send_message(chat_id=uid, text=f"{get_tg_emoji('home')} <b>PLEASE USE THE BUTTONS BELOW :</b>", parse_mode="HTML", reply_markup=main_keyboard(uid))
        else:
            await query.answer("❌ আপনি এখনো সব চ্যানেলে জয়েন করেননি!", show_alert=True)
        return

    elif data == "admin_reset_leaderboard" and is_admin(uid):
        save_data({}, STATS_FILE)
        if STATS_FILE in _global_db_cache:
            _global_db_cache[STATS_FILE] = {}
        await query.answer("🏆 Leaderboard reset successfully!", show_alert=True)
        await query.message.edit_text(get_leaderboard_text(), parse_mode="HTML", reply_markup=None)
        return

    elif data == "profile_withdraw":
        user_info = get_user(uid)
        settings = load_settings()
        min_w = settings.get("min_withdraw", 5.0)
        
        if user_info.get("balance", 0.0) < min_w:
            await query.answer(f"❌ Minimum withdrawal is ${min_w}!", show_alert=True)
            return
            
        keyboard = InlineKeyboardMarkup([
            [
                make_inline_btn("bKash", callback_data="with_meth_bKash", emoji_id="5348469219761626211"),
                make_inline_btn("Nagad", callback_data="with_meth_Nagad", emoji_id="5352985330628730418")
            ],
            [
                make_inline_btn("Rocket", callback_data="with_meth_Rocket", emoji_id="5346042941196507141"),
                make_inline_btn("Binance", callback_data="with_meth_Binance", emoji_id="5348212415077064131")
            ],
            [
                make_inline_btn("« Back to Profile", callback_data="back_to_profile", emoji_id="5267490665117275176", style="danger")
            ]
        ])
        await query.message.edit_text(f"{get_tg_emoji('money')} <b>Select Withdrawal Method:</b>", reply_markup=keyboard, parse_mode="HTML")
        return

    elif data.startswith("with_meth_"):
        method = data.replace("with_meth_", "")
        context.user_data["withdraw_method"] = method
        context.user_data["withdraw_mode"] = "amount"
        await query.message.delete()
        await context.bot.send_message(
            chat_id=uid,
            text=f"{get_tg_emoji('money')} <b>Withdraw Method: {method}</b>\n\n✏️ Please type and send the USD amount you wish to withdraw:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    elif data == "back_to_profile":
        await query.message.delete()
        await show_profile_command(query, context)
        return

    elif data.startswith("adm_app_"):
        payment_id = data.replace("adm_app_", "")
        withdraw_requests = load_withdraw_requests()
        if payment_id in withdraw_requests:
            req = withdraw_requests[payment_id]
            req["status"] = "approved"
            save_withdraw_requests(withdraw_requests)
            try:
                await context.bot.send_message(
                    chat_id=req["user_id"],
                    text=f"{get_tg_emoji('done')} <b>WITHDRAWAL APPROVED!</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                         f"$ {req['amount']} has been successfully sent to your {req['method']} account: <code>{req['number']}</code>\n"
                         f"Thank you for using our service!",
                    parse_mode="HTML"
                )
            except:
                pass
            await query.message.edit_text(f"{get_tg_emoji('done')} Approved Request `{payment_id}` successfully!")
        return

    elif data.startswith("adm_rej_"):
        payment_id = data.replace("adm_rej_", "")
        withdraw_requests = load_withdraw_requests()
        if payment_id in withdraw_requests:
            req = withdraw_requests[payment_id]
            req["status"] = "rejected"
            save_withdraw_requests(withdraw_requests)
            await update_db_balance(req["user_id"], req["amount"])
            try:
                await context.bot.send_message(
                    chat_id=req["user_id"],
                    text=f"{get_tg_emoji('cross')} <b>WITHDRAWAL REQUEST REJECTED</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                         f"Your withdrawal request of $ {req['amount']} via {req['method']} has been rejected by Admin. "
                         f"Amount has been refunded to your profile balance.",
                    parse_mode="HTML"
                )
            except:
                pass
            await query.message.edit_text(f"{get_tg_emoji('cross')} Rejected and Refunded Request `{payment_id}` successfully!")
        return

    elif data == "admin_back_to_config":
        context.user_data.clear()
        context.user_data["admin_mode"] = "main"
        today_n, today_o, seven_n, seven_o, total_n, total_o = get_global_system_stats()
        users_count = len(get_all_users())
        banned_count = len(load_banned_users())
        active_numbers_count = len(active_numbers)
        settings = load_settings()
        panel = settings.get("active_panel", "zenex").upper()
        admin_welcome = (
            f"⌬━━━━━━━━━━━━━━━━━━━━⌬\n"
            f"       {get_tg_emoji('admin')} <b>ADVANCED ADMIN PANEL</b> {get_tg_emoji('admin')}       \n"
            f"⌬━━━━━━━━━━━━━━━━━━━━⌬\n\n"
            f"{get_tg_emoji('setting')} <b>Active Backend:</b> <code>{panel}</code>\n"
            f"{get_tg_emoji('profile')} <b>Registered Users:</b> <code>{users_count}</code>\n"
            f"{get_tg_emoji('ban')} <b>Banned Users:</b> <code>{banned_count}</code>\n"
            f"{get_tg_emoji('get_number_btn')} <b>Reserved Numbers:</b> <code>{active_numbers_count}</code>\n\n"
            f"{get_tg_emoji('status')} <b>Global Activity Stats:</b>\n"
            f"<blockquote>• Today: <code>{today_n}</code> Numbers | <code>{today_o}</code> OTPs {get_tg_emoji('live')}\n"
            f"• 7 Days: <code>{seven_n}</code> Numbers | <code>{seven_o}</code> OTPs {get_tg_emoji('up')}\n"
            f"• Lifetime: <code>{total_n}</code> Numbers | <code>{total_o}</code> OTPs {get_tg_emoji('1st')}</blockquote>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        await query.message.reply_text(admin_welcome, reply_markup=admin_main_keyboard(), parse_mode="HTML")
        return

    elif data == "admin_select_panel":
        settings = load_settings()
        active = settings.get("active_panel", "zenex")
        btn_zenex = "🟢 ZENEX" if active == "zenex" else "ZENEX"
        btn_voltx = "🟢 VOLTX SMS" if active == "voltx_sms" else "VOLTX SMS"
        btn_stex = "🟢 STEX SMS" if active == "stex_sms" else "STEX SMS"
        btn_fastxotp = "🟢 FASTXOTP" if active == "fastxotp" else "FASTXOTP"
        kb = InlineKeyboardMarkup([
            [make_inline_btn(btn_zenex, callback_data="change_panel_zenex")],
            [make_inline_btn(btn_voltx, callback_data="change_panel_voltx_sms")],
            [make_inline_btn(btn_stex, callback_data="change_panel_stex_sms")],
            [make_inline_btn(btn_fastxotp, callback_data="change_panel_fastxotp")],
            [make_inline_btn("🔙 Back to Config", callback_data="admin_back_to_config")]
        ])
        await query.message.edit_text(f"{get_tg_emoji('setting')} <b>SELECT ACTIVE API PANEL:</b>", reply_markup=kb, parse_mode="HTML")
        return
        
    elif data.startswith("change_panel_"):
        new_panel = data.replace("change_panel_", "")
        settings = load_settings()
        settings["active_panel"] = new_panel
        save_settings(settings)
        global _ranges_cache
        _ranges_cache["data"] = None
        _ranges_cache["updated_at"] = 0.0
        await query.answer(f"✅ Panel switched to {new_panel.upper()}!", show_alert=True)
        await query.message.delete()
        await context.bot.send_message(chat_id=uid, text=f"{get_tg_emoji('done')} <b>Bot is now using: {new_panel.upper()} API!</b>", reply_markup=admin_main_keyboard(), parse_mode="HTML")
        return

    elif data == "admin_config_zenex":
        settings = load_settings()
        kb = InlineKeyboardMarkup([
            [make_inline_btn("🔑 Edit Zenex Key", callback_data="edit_zenex_key")],
            [make_inline_btn("🌐 Edit Zenex URL", callback_data="edit_zenex_url")],
            [make_inline_btn("🔙 Back", callback_data="admin_back_to_config")]
        ])
        msg = f"{get_tg_emoji('setting')} <b>Zenex Panel Settings:</b>\n\n🔑 Key: <code>{settings.get('zenex_api_key')}</code>\n🌐 URL: <code>{settings.get('zenex_base_url')}</code>"
        await query.message.edit_text(msg, reply_markup=kb, parse_mode="HTML")
        return
        
    elif data == "admin_config_voltx_sms":
        settings = load_settings()
        kb = InlineKeyboardMarkup([
            [make_inline_btn("🔑 Edit Voltx SMS Key", callback_data="edit_voltx_sms_key")],
            [make_inline_btn("🌐 Edit Voltx SMS URL", callback_data="edit_voltx_sms_url")],
            [make_inline_btn("🔙 Back", callback_data="admin_back_to_config")]
        ])
        msg = f"{get_tg_emoji('setting')} <b>Voltx SMS Panel Settings:</b>\n\n🔑 Key: <code>{settings.get('voltx_sms_api_key')}</code>\n🌐 URL: <code>{settings.get('voltx_sms_base_url')}</code>"
        await query.message.edit_text(msg, reply_markup=kb, parse_mode="HTML")
        return

    elif data == "admin_config_stex_sms":
        settings = load_settings()
        kb = InlineKeyboardMarkup([
            [make_inline_btn("🔑 Edit Stex SMS Key", callback_data="edit_stex_sms_key")],
            [make_inline_btn("🌐 Edit Stex SMS URL", callback_data="edit_stex_url")],
            [make_inline_btn("🔙 Back", callback_data="admin_back_to_config")]
        ])
        msg = f"{get_tg_emoji('setting')} <b>Stex SMS Panel Settings:</b>\n\n🔑 Key: <code>{settings.get('stex_sms_api_key')}</code>\n🌐 URL: <code>{settings.get('stex_sms_base_url')}</code>"
        await query.message.edit_text(msg, reply_markup=kb, parse_mode="HTML")
        return

    elif data == "admin_config_fastxotp":
        settings = load_settings()
        kb = InlineKeyboardMarkup([
            [make_inline_btn("🔑 Edit FastXOTP Key", callback_data="edit_fastxotp_key")],
            [make_inline_btn("🌐 Edit FastXOTP URL", callback_data="edit_fastxotp_url")],
            [make_inline_btn("🔙 Back", callback_data="admin_back_to_config")]
        ])
        msg = f"{get_tg_emoji('setting')} <b>FastXOTP Panel Settings:</b>\n\n🔑 Key: <code>{settings.get('fastxotp_api_key')}</code>\n🌐 URL: <code>{settings.get('fastxotp_base_url')}</code>"
        await query.message.edit_text(msg, reply_markup=kb, parse_mode="HTML")
        return

    elif data == "edit_zenex_key":
        context.user_data["admin_edit_mode"] = "zenex_api_key"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new API Key for Zenex:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_zenex_url":
        context.user_data["admin_edit_mode"] = "zenex_base_url"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new BASE URL for Zenex:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "edit_voltx_sms_key":
        context.user_data["admin_edit_mode"] = "voltx_sms_api_key"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new API Key for Voltx SMS:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_voltx_sms_url":
        context.user_data["admin_edit_mode"] = "voltx_sms_base_url"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new BASE URL for Voltx SMS:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "edit_stex_sms_key":
        context.user_data["admin_edit_mode"] = "stex_sms_api_key"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new API Key for Stex SMS:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_stex_url":
        context.user_data["admin_edit_mode"] = "stex_sms_base_url"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new BASE URL for Stex SMS:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "edit_fastxotp_key":
        context.user_data["admin_edit_mode"] = "fastxotp_api_key"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new API Key for FastXOTP:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_fastxotp_url":
        context.user_data["admin_edit_mode"] = "fastxotp_base_url"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>Type and send new BASE URL for FastXOTP:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "same_range":
        settings = load_settings()
        cooldown = settings.get("cooldown_time", 4.0)
        current_time = time.time()
        time_passed = current_time - last_request_time.get(uid_str, 0.0)
        
        if time_passed < cooldown:
            wait_time = round(cooldown - time_passed, 1)
            await query.answer(f"⏳ Please wait {wait_time}s before changing number.", show_alert=True)
            return

        last_request_time[uid_str] = current_time
        r_text = last_range.get(uid_str)
        if r_text:
            await query.answer("🔄 Changing number...")
            await request_queue.put({
                'type': 'process_numbers', 
                'update': update, 
                'context': context, 
                'range_text': r_text, 
                'count': settings.get("numbers_per_request", 1),
                'edit_message': query.message
            })
        return

    elif data == "back_to_apps":
        cache_age = time.monotonic() - _ranges_cache["updated_at"]
        if _ranges_cache["data"] and cache_age < 300:
            top_ranges_by_app = _ranges_cache["data"]
            context.user_data["top_ranges_by_app"] = top_ranges_by_app
            buttons = build_app_buttons_from_cache(top_ranges_by_app)
            keyboard = InlineKeyboardMarkup(buttons)
            msg = (
                f"{get_tg_emoji('get_number_btn')} <b>SELECT APP TO GET NUMBER</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            await query.edit_message_text(msg, parse_mode="HTML", reply_markup=keyboard)
            return

        status = await query.edit_message_text(f"{get_tg_emoji('loading', '⏳')} <b>Loading ranges...</b>", parse_mode="HTML")
        top_ranges_by_app, err = await fetch_top55_ranges_by_app()
        if err or not top_ranges_by_app:
            top_ranges_by_app, err = await fetch_top55_ranges_by_app()
        if err:
            await status.edit_text(
                f"{get_tg_emoji('cross')} <b>Could not load ranges.</b>\n\n"
                f"<blockquote>{get_tg_emoji('stop')} {err}\n\nPlease try again in a moment.</blockquote>",
                parse_mode="HTML"
            )
            return

        _ranges_cache["data"] = top_ranges_by_app
        _ranges_cache["updated_at"] = time.monotonic()
        context.user_data["top_ranges_by_app"] = top_ranges_by_app
        buttons = build_app_buttons_from_cache(top_ranges_by_app)
        keyboard = InlineKeyboardMarkup(buttons)
        msg = (
            f"{get_tg_emoji('get_number_btn')} <b>SELECT APP TO GET NUMBER</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━" # উদাহরণস্বরূপ
        )
        await status.edit_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return


    elif data.startswith("sel_app_"):
        app_name = data[len("sel_app_"):]
        last_selected_app[uid_str] = app_name  
        
        cached = context.user_data.get("top_ranges_by_app") or {}
        
        if app_name in cached:
            info = cached[app_name]
            ranges = info["ranges"]
        else:
            try:
                fresh_data, fetch_err = await fetch_top55_ranges_by_app()
                if fresh_data and app_name in fresh_data:
                    info  = fresh_data[app_name]
                    ranges = info["ranges"]
                    context.user_data["top_ranges_by_app"] = fresh_data
                    _ranges_cache["data"]       = fresh_data
                    _ranges_cache["updated_at"] = time.monotonic()
                else:
                    ranges = []
            except Exception as e:
                await query.edit_message_text(f"❌ Failed to load ranges: {e}")
                return
        if not ranges:
            await query.edit_message_text(f"📱 {app_name} — No active ranges found.")
            return

        country_buttons_map = {}
        for rng in ranges:
            flag, name = get_country_info(rng)
            country_key = f"{flag} {name}"
            if country_key not in country_buttons_map:
                country_buttons_map[country_key] = []
            country_buttons_map[country_key].append(rng)

        buttons = []
        row = []
        if "country_ranges" not in context.user_data:
            context.user_data["country_ranges"] = {}

        for country_label, rng_list in country_buttons_map.items():
            idx = len(context.user_data["country_ranges"]) + 1
            idx_str = str(idx)
            context.user_data["country_ranges"][idx_str] = {
                "app": app_name,
                "label": country_label,
                "ranges": rng_list
            }
            
            flag_char = country_label.split()[0] if country_label else ""
            clean_country_name = country_label.replace(flag_char, "").strip()
            flag_emoji_id = PREMIUM_FLAGS.get(flag_char)
            
            row.append(make_inline_btn(
                clean_country_name, 
                callback_data=f"sel_cty_{idx_str}", 
                emoji_id=flag_emoji_id,
                style="danger"
            ))
            
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        
        buttons.append([make_inline_btn("« Back", callback_data="back_to_apps", emoji_id="5267490665117275176", style="primary")])
        keyboard = InlineKeyboardMarkup(buttons)
        context.user_data["selected_app"] = app_name
        msg = f"🌎 <b>Select Country for {app_name}:</b>"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    elif data.startswith("sel_cty_"):
        settings = load_settings()
        cooldown = settings.get("cooldown_time", 4.0)
        current_time = time.time()
        time_passed = current_time - last_request_time.get(uid_str, 0.0)
        
        if time_passed < cooldown:
            wait_time = round(cooldown - time_passed, 1)
            await query.answer(f"⏳ Please wait {wait_time}s before requesting.", show_alert=True)
            return

        idx_str = data[len("sel_cty_"):]
        country_ranges_dict = context.user_data.get("country_ranges") or {}
        cty_info = country_ranges_dict.get(idx_str)
        
        if not cty_info:
            await query.edit_message_text("⚠️ Session expired. Please try getting number again.")
            return
        
        app_name = cty_info["app"]
        last_selected_app[uid_str] = app_name
        country_label = cty_info["label"]
        country_ranges = cty_info["ranges"]

        available_ranges = country_ranges[:45]
        selected_range = random.choice(available_ranges)

        try:
            await query.edit_message_text(f"{get_tg_emoji('loading', '⏳')} <b>Getting Number</b>", parse_mode="HTML")
        except Exception:
            pass

        count = settings.get("numbers_per_request", 1)
        
        tasks = [fetch_number_async(selected_range) for _ in range(count)]
        results = await asyncio.gather(*tasks)
        generated_nums = [normalize_number(n) for n in results if n]

        if not generated_nums:
            kb = InlineKeyboardMarkup([[make_inline_btn("« Back", callback_data=f"sel_app_{app_name}", emoji_id="5267490665117275176", style="primary")]])
            await query.edit_message_text("❌ FAILED — No valid numbers could be fetched. Try again.", reply_markup=kb)
            return

        for g_num in generated_nums:
            active_numbers[g_num] = {"uid": uid, "range": selected_range, "otp_count": 0, "app": app_name}
            save_number_range_info(uid, g_num, selected_range)
        
        last_range[uid_str] = selected_range
        last_request_time[uid_str] = current_time
        add_number_taken(uid, len(generated_nums))
        
        country_flag, country_name_local = get_country_info(generated_nums[0])
        done_emoji = get_tg_emoji("done")
        waiting_emoji = get_tg_emoji("waiting")
        
        assign_text = (
            f"{get_country_tg_flag(country_flag)} <b>{country_name_local} Allocated</b> {done_emoji}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{waiting_emoji} <b>Waiting for OTP.......</b>"
        )
        
        keyboard = []
        app_emoji_key = get_clean_app_name(app_name).lower()
        service_emoji_id = EMOJI_ID_MAP.get(app_emoji_key) or EMOJI_ID_MAP.get("get_number_btn")

        for g_num in generated_nums:
            details = active_numbers.get(g_num, {})
            otp_cnt = details.get("otp_count", 0)
            star_text = " ⭐" * otp_cnt if otp_cnt > 0 else ""
            
            btn_text = f" +{g_num}{star_text}"
            
            if HAS_COPY_BTN:
                btn = InlineKeyboardButton(text=btn_text, copy_text=CopyTextButton(text=f"+{g_num}"), api_kwargs={"icon_custom_emoji_id": str(service_emoji_id)} if service_emoji_id else None)
            else:
                btn = InlineKeyboardButton(text=btn_text, callback_data=f"copy_text_{g_num}", api_kwargs={"icon_custom_emoji_id": str(service_emoji_id)} if service_emoji_id else None)
            keyboard.append([btn])
            
        keyboard.append([
            make_inline_btn("Back To Country", callback_data="back_to_apps", emoji_id="5267490665117275176", style="primary"),
            make_inline_btn("VIEW OTP", url=settings.get("otp_group_url", "https://t.me/+31eV11IT7WQzMjI9"), emoji_id="5271604874419647061", style="primary")
        ])
        keyboard.append([
            make_inline_btn("Change number", callback_data="same_range", emoji_id="5267295703666824255", style="danger")
        ])
        
        await query.edit_message_text(assign_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data == "view_otp":
        found_otp = False
        paid_data = load_data(PAID_SMS_FILE)
        user_active_nums = [num for num, details in active_numbers.items() if details["uid"] == uid]
        
        alerts = []
        for num in user_active_nums:
            for sms_key, info in paid_data.items():
                if info.get("uid") == uid and sms_key.startswith(num):
                    alerts.append(f"📞 +{num}: <b>{info.get('otp')}</b>")
        
        if alerts:
            alert_text = "\n".join(alerts)
            await query.answer(f"OTPs Received:\n{alert_text}", show_alert=True)
        else:
            await query.answer("⏳ No OTP received yet for your active  s.", show_alert=True)
        return

    elif data == "edit_txt_welcome":
        context.user_data["admin_edit_mode"] = "welcome"
        await context.bot.send_message(uid, f"{get_tg_emoji('msg')} <b>নতুন Welcome Message-টি টাইপ করে পাঠান:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "edit_txt_otpgroup":
        context.user_data["admin_edit_mode"] = "otpgroup"
        await context.bot.send_message(uid, f"{get_tg_emoji('link')} <b>নতুন OTP Group লিঙ্কটি পাঠান:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "edit_txt_channel":
        context.user_data["admin_edit_mode"] = "channel"
        await context.bot.send_message(uid, f"{get_tg_emoji('channel')} <b>নতুন Channel লিঙ্কটি পাঠান:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "edit_txt_panelurl":
        context.user_data["admin_edit_mode"] = "panelurl"
        await context.bot.send_message(uid, f"{get_tg_emoji('link')} <b>নতুন Panel URL লিঙ্কটি পাঠান:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "edit_txt_support":
        context.user_data["admin_edit_mode"] = "support"
        await context.bot.send_message(uid, f"{get_tg_emoji('setting')} <b>নতুন Support Username-টি পাঠান (@ সহ):</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "fj_add_start":
        context.user_data["admin_edit_mode"] = "fj_add_channel"
        await query.message.reply_text("✏️ Please send the Channel Username (e.g., <code>@MyChannel</code>) to add:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "fj_del_start":
        context.user_data["admin_edit_mode"] = "fj_del_channel"
        await query.message.reply_text("✏️ Please send the number (index) of the channel you want to delete:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "fj_clear_all":
        settings = load_settings()
        settings["force_join_channels"] = []
        save_settings(settings)
        await query.answer("🧹 All Force Join channels cleared!", show_alert=True)
        await show_force_join_manager(update, context)
        return

    elif data == "fj_back_security":
        await query.message.delete()
        await context.bot.send_message(chat_id=uid, text="🛡️ <b>Security & Force Join Category:</b>", parse_mode="HTML", reply_markup=admin_security_join_keyboard())
        return

# ==================== MAIN & POST INIT SECTION ====================

async def post_init(application): 
    global BOT_USERNAME
    try:
        bot_info = await application.bot.get_me()
        BOT_USERNAME = bot_info.username
    except Exception:
        BOT_NAME = "@MrCodePanleBot"

    preload_all_databases()
    asyncio.create_task(_bg_disk_persistence())

    for _ in range(20):
        asyncio.create_task(worker())
    asyncio.create_task(monitor_loop(application))
    asyncio.create_task(_bg_refresh_ranges())

def main():
    request_config = HTTPXRequest(connect_timeout=25.0, read_timeout=25.0)
    
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request_config)
        .concurrent_updates(True)
        .post_init(post_init)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get1number", get1number_command))
    
    app.add_handler(CallbackQueryHandler(button_callback))
    
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.AUDIO | filters.Document.ALL) & (~filters.COMMAND), 
        handle_message
    ))
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()