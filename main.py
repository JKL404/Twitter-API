from fastapi import FastAPI, Request, Form, Depends
from API import streaming, search, removefiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date

app = FastAPI(dependencies=[Depends(removefiles.remove_old_files)])


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def filter_tweets(userdata: str, limit: str, stype: str, api_type=None):
    response = False
    downlink = ''
    try:
        print(f"userdata: {userdata}\n stype: {stype}")

        filename = f"{date.today()}_{str(userdata.split(' ')[0])}_tweets"
        limit = 10 if int(limit) < 1 else int(limit)

        stream = api_type.TwitterStream(limit, filename)

        if stype == '0':
            user = str(userdata.split(' ')[0])
            response = stream.search_by_user(user)
        else:
            keywords_list = userdata.split(' ')
            response = stream.search_by_keywords(keywords_list)

        print(f'{userdata}Tweets Fetching Success') if response else print(
            f'{userdata}Tweets Fetching Failed')

        downlink = f"{filename}.csv"
    except Exception as e:
        print(f'Exception Found at {e}')
    return {"downloadlink": downlink, "resflag": response}


@app.post('/fetch_tweets/', response_class=HTMLResponse)
async def fetch_tweets(request: Request, userdata: str = Form(), limit: str = Form(regex="[0-9]{1,5}"), stype: str = Form(regex="[01]{1}")):
    tweet_res: dict = filter_tweets(
        userdata=userdata, limit=limit, stype=stype, api_type=search)
    return templates.TemplateResponse("display.html", {"request": request, "dtype": "search", "func": "/fetch_tweets/", "downloadlink": tweet_res.get("downloadlink", ''), "resflag": tweet_res.get("resflag", '')})


@app.post('/stream_tweets/', response_class=HTMLResponse)
async def stream_tweets(request: Request, userdata: str = Form(), limit: str = Form(regex="[0-9]{1,5}"), stype: str = Form(regex="[01]{1}")):
    tweet_res: dict = filter_tweets(
        userdata=userdata, limit=limit, stype=stype, api_type=streaming)
    return templates.TemplateResponse("display.html", {"request": request, "dtype": "streaming", "func": "/stream_tweets/", "downloadlink": tweet_res.get("downloadlink", ''), "resflag": tweet_res.get("resflag", '')})


@app.get("/search/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("display.html", {"request": request, "dtype": "search", "func": "/fetch_tweets/"})


@app.get("/streaming/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("display.html", {"request": request, "dtype": "streaming", "func": "/stream_tweets/"})


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
