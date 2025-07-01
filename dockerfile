# 使用官方 FastAPI 推荐基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 拷贝 requirements 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动 FastAPI 应用
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
