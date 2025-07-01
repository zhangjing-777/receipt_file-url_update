# ReceiptDrop 文件上传与URL更新服务

## 项目简介
本项目基于 FastAPI，结合 Supabase 存储和数据库，实现发票/收据文件的安全上传、URL规范化与数据库自动更新。支持中文文件名转拼音、日志记录、异常处理。

## 主要功能
- 上传文件到 Supabase Storage，自动生成安全、规范的文件名和公开URL
- 数据库表（receipt_items_cleaned）中 file_url 字段的自动更新
- 全流程日志记录，便于追踪和排查

## 依赖环境
- Python 3.11+
- FastAPI
- python-dotenv
- supabase-py
- pypinyin
- 其它依赖详见 `requirements.txt`

## 环境变量
请在根目录下创建 `.env` 文件，内容示例：
```
SUPABASE_URL=你的supabase项目url
SUPABASE_SERVICE_ROLE_KEY=你的supabase service role key
```

## 主要API
### 1. 文件上传并修改数据库URL
- **POST** `/webhook/modify_url`
- **参数（form-data）**：
  - `user_id` (str): 用户ID
  - `file_url` (str): 旧文件URL（数据库中原有的）
  - `file` (file): 新上传的文件
- **返回**：
  - `result`: "success" 或 "error"
  - `new_file_url`: 新的公开URL

## 日志说明
- 日志文件每日生成，保存在 `logs/` 目录，同时输出到控制台。
- 记录请求、上传、数据库操作、异常等关键事件。

## 运行方法
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 启动服务：
   ```bash
   uvicorn app:app --reload
   ```
3. 访问API或用Postman测试。

## Docker 支持
如需容器化运行，可参考 `docker-compose.yml` 和 `dockerfile`。

