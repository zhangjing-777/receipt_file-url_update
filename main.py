import os
import re
import base64
import hashlib
import logging
import unicodedata
from datetime import datetime
from dotenv import load_dotenv
from fastapi import UploadFile
from pypinyin import lazy_pinyin
from supabase import create_client, Client



load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or ""
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "receipt_items_cleaned"


logger = logging.getLogger(__name__)



def make_safe_storage_path(filename: str, prefix: str = "") -> str:
    logger.info(f"Sanitizing filename: {filename}")
    # 1. 去除不可见字符 + 正规化为 NFC
    filename = unicodedata.normalize("NFKC", filename)

    # 2. 中文转拼音（只保留文件主名，后缀不处理）
    if "." in filename:
        name_part, ext = filename.rsplit(".", 1)
    else:
        name_part, ext = filename, ""

    # 转为拼音（如：'天翔迪晟（深圳）发票' → 'tianxiangdisheng_shenzhen_fapiao'）
    pinyin_name = "_".join(lazy_pinyin(name_part))

    # 3. 保留英文、数字、下划线、短横线和点，移除非法字符
    pinyin_name = re.sub(r"[^\w.-]", "_", pinyin_name)
    ext = re.sub(r"[^\w]", "", ext)

    # 4. 限长 + 防重复 hash
    if len(pinyin_name) > 80:
        hash_suffix = hashlib.md5(filename.encode()).hexdigest()[:8]
        pinyin_name = pinyin_name[:70] + "_" + hash_suffix

    # 5. 组装最终文件名
    final_filename = f"{pinyin_name}.{ext}" if ext else pinyin_name

    # 6. 可选前缀路径（如 '2025-06-23'）
    if prefix:
        result = f"{prefix}/{final_filename}"
    else:
        result = final_filename
    logger.info(f"Sanitized filename result: {result}")
    return result



def upload_file_to_storage(file: UploadFile, bucket="lazy-receipt"):
    filename = file.filename
    safe_filename = make_safe_storage_path(filename)
    logger.info(f"Safe filename generated: {safe_filename}")

    binary = file.file.read()  # 使用 file.file.read() 读取 UploadFile
    content_type = file.content_type or "application/octet-stream"
    logger.info(f"Detected content type: {content_type}")

    # 构建路径
    date_url = datetime.utcnow().date().isoformat()
    timestamp = datetime.utcnow().isoformat()
    storage_path = f"{date_url}/{timestamp}_{safe_filename}"
    logger.info(f"Uploading {filename} to storage at {storage_path}")

    # 上传
    supabase.storage.from_(bucket).upload(
        path=storage_path,
        file=binary,
        file_options={"content-type": content_type}
    )

    # 返回公开 URL（去除尾部?token）
    public_url = supabase.storage.from_(bucket).get_public_url(storage_path).rstrip('?')
    logger.info(f"Public URL: {public_url}")
    return public_url





def update_file_url(user_id: str, old_file_url: str, new_file_url: str):
    logger.info(f"Updating file_url for user_id={user_id}, old_file_url={old_file_url}, new_file_url={new_file_url}")
    try:
        # Step 1: 查询要更新的记录
        result = supabase.table(TABLE) \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("file_url", old_file_url) \
            .execute()
        
        if len(result.data) == 0:
            logger.warning(f"No record found for user_id={user_id}, old_file_url={old_file_url}")
            return

        row_id = result.data[0]["id"]

        # Step 2: 更新 file_url
        update_result = supabase.table(TABLE) \
            .update({"file_url": new_file_url}) \
            .eq("id", row_id) \
            .execute()

        logger.info(f"Update complete for row_id={row_id}, update_result={update_result.data}")
    except Exception as e:
        logger.exception(f"Exception in update_file_url: {e}")
