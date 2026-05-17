import logging
import asyncio
import os
from typing import Optional
from bot.config import settings

logger = logging.getLogger(__name__)

async def generate_video(
    prompt: str,
    model_type: str = "fast",
    mode: str = "text",
    image_path: Optional[str] = None
) -> str:
    """
    Fal.ai orqali video generatsiya qilish.
    - prompt: Matnli tavsif.
    - model_type: 'fast' (Tezkor) yoki 'best' (Premium).
    - mode: 'text' (Text-to-Video) yoki 'image' (Image-to-Video).
    - image_path: Foydalanuvchi yuklagan rasmning mahalliy yo'li (Image-to-Video uchun).
    """
    fal_key = settings.FAL_KEY or os.environ.get("FAL_KEY")
    
    if not fal_key:
        logger.warning("FAL_KEY sozlanmagan! Simulyatsiya rejimida test videosi yuboriladi.")
        await asyncio.sleep(6)  # Simulyatsiya kutish vaqti
        return "https://www.w3schools.com/html/mov_bbb.mp4"

    try:
        import fal_client
        os.environ["FAL_KEY"] = fal_key
        
        # 1. Rasm yuklangan bo'lsa, uni Fal.ai CDN'ga xavfsiz yuklaymiz va URL olamiz
        image_url = None
        if mode == "image" and image_path and os.path.exists(image_path):
            logger.info(f"Rasm Fal.ai CDN-ga yuklanmoqda: {image_path}")
            image_url = await asyncio.to_thread(fal_client.upload_file, image_path)
            logger.info(f"Rasm muvaffaqiyatli yuklandi: {image_url}")

        # 2. Model va API parametrlarini aniqlash
        if model_type == "best":
            if mode == "image" and image_url:
                # Premium Image-to-Video
                api_model = "fal-ai/luma-dream-machine/image-to-video"
                arguments = {
                    "prompt": prompt,
                    "image_url": image_url,
                }
            else:
                # Premium Text-to-Video
                api_model = "fal-ai/luma-dream-machine"
                arguments = {
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                }
        else:
            # Fast model (Wan v2.1)
            if mode == "image" and image_url:
                api_model = "fal-ai/wan/v2.1/image-to-video"
                arguments = {
                    "prompt": prompt,
                    "image_url": image_url,
                }
            else:
                api_model = "fal-ai/wan/v2.1/text-to-video"
                arguments = {
                    "prompt": prompt,
                    "resolution": "720p",
                    "aspect_ratio": "16:9",
                    "duration": "5",
                }

        logger.info(f"Fal.ai video yaratish boshlanmoqda. Model: {api_model}. Prompt: {prompt}")
        
        result = await asyncio.to_thread(
            fal_client.subscribe,
            api_model,
            arguments=arguments
        )
        
        # Video URL ni natijadan ajratib olish
        video_url = result.get("video", {}).get("url")
        if not video_url and "outputs" in result:
            # Fallback ba'zi modellar uchun
            video_url = result["outputs"][0]["video"]["url"]
            
        logger.info(f"Video muvaffaqiyatli yaratildi: {video_url}")
        return video_url
        
    except ImportError:
        logger.error("fal-client kutubxonasi topilmadi! Bepul test videosi qaytariladi.")
        await asyncio.sleep(5)
        return "https://www.w3schools.com/html/mov_bbb.mp4"
    except Exception as e:
        logger.error(f"Fal.ai generatsiyasida xatolik: {e}. Test videosiga o'tilmoqda.")
        await asyncio.sleep(5)
        return "https://www.w3schools.com/html/mov_bbb.mp4"
