import os
import logging
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from main import upload_file_to_storage, update_file_url



# 创建logs目录
os.makedirs('logs', exist_ok=True)

# 配置日志格式和存储
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()



@app.post("/webhook/modify_url")
async def modify_url(
    user_id: str = Form(...),
    file_url: str = Form(...),
    file: UploadFile = File(...)
):
    logger.info(f"Received modify_url request: user_id={user_id}, file_url={file_url}, filename={file.filename if file else None}")
    try:
        user_id = str(user_id)
        file_url = str(file_url)

        new_file_url = upload_file_to_storage(file)
        logger.info(f"File uploaded. user_id={user_id}, old_file_url={file_url}, new_file_url={new_file_url}")
        update_file_url(user_id, file_url, new_file_url)
        logger.info(f"File URL updated in DB for user_id={user_id}")

        return JSONResponse({
                "result": "success",
                "new_file_url": new_file_url
            })
    except Exception as e:
        logger.exception(f"Error in modify_url: {e}")
        return JSONResponse({"result": "error", "message": str(e)}, status_code=500)
