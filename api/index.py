from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import imagehash
from PIL import Image
import requests
from io import BytesIO

app = FastAPI(
    title="Image Hashing Service",
    docs_url="/api/docs", 
    openapi_url="/api/openapi.json"
)

class ImageRequest(BaseModel):
    image_url: str

@app.post("/api/v1/hash")
async def get_image_hash(request: ImageRequest):
    try:
        # Ngụy trang thành trình duyệt thực để vượt qua tường lửa của MinIO/S3
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Referer": "https://lms-frontend-dev.izone.edu.vn/"
        }
        
        response = requests.get(request.image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        hash_value = str(imagehash.dhash(img))
        
        return {"status": "success", "hash_value": hash_value}
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi tải ảnh: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý ảnh: {str(e)}")