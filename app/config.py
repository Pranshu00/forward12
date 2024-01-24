import os
import sys

api_id = 24761987
api_hash = "481ad3c3c2175064a31cdcee68d29e92"
bot_token = "6920584091:AAGLqSGmhlfuGSS-qNOv_6ztGbzJtTogF_4"
# ADMINS = [5123656408]
timeout = 3

DB_URI = "mongodb+srv://NoName3:passwdmongodb@cluster1.rel9icb.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "forwardbot"

admin = os.environ.get("admins", "5123656408")

admin = admin.split(",")

ADMINS = []
for admi in admin:
    try:
        ADMINS.append(int(admi.strip()))

    except:
        print("You gave Admins in wrong format")
        sys.exit()
