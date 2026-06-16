from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import imagehash
from PIL import Image
import httpx
from io import BytesIO
import asyncio

app = FastAPI()

class ImageBatchRequest(BaseModel):
    image_urls: List[str]

# Hàm xử lý tải và băm 1 ảnh bất đồng bộ
async def process_single_image(client, url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = await client.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return str(imagehash.dhash(img))
    except Exception as e:
        return f"error: {str(e)}"

@app.post("/api/v1/hash-batch")
async def get_image_hash_batch(request: ImageBatchRequest):
    # Sử dụng httpx.AsyncClient để tải nhiều ảnh CÙNG LÚC
    async with httpx.AsyncClient() as client:
        tasks = [process_single_image(client, url) for url in request.image_urls]
        hash_results = await asyncio.gather(*tasks)
    
    return {
        "status": "success",
        "hashes": hash_results # Trả về mảng các mã hash theo đúng thứ tự
    }