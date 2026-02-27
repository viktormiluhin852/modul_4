# test_services/service_fake_worldclockapi.py
#
# Запуск: python test_services/service_fake_worldclockapi.py
# Проверка: curl http://127.0.0.1:16001/ping
#           curl http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now

import pytz
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()

FAKE_WORLDCLOCK_PORT = 16001


@app.get("/ping")
def ping():
    return "PONG!"


# Имитация http://worldclockapi.com/api/json/utc/now
@app.get("/fake/worldclockapi/api/json/utc/now")
def get_current_utc_time():
    now = datetime.now(pytz.utc)
    response = {
        "$id": "1",
        "currentDateTime": now.strftime("%Y-%m-%dT%H:%MZ"),
        "utcOffset": "00:00:00",
        "isDayLightSavingsTime": False,
        "dayOfTheWeek": now.strftime("%A"),
        "timeZoneName": "UTC",
        "currentFileTime": int(now.timestamp() * 10**7),
        "ordinalDate": now.strftime("%Y-%j"),
        "serviceResponse": None,
    }
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=FAKE_WORLDCLOCK_PORT)
