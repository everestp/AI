from dotenv import load_dotenv

from .server import app

load_dotenv()
def main():

    import uvicorn

    uvicorn.run(app=app , host="0.0.0.0",port=8001)


main()

