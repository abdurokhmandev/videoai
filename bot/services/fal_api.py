import logging
import asyncio
import os
from bot.config import settings

logger = logging.getLogger(__name__)

FAL_MODEL = "fal-ai/wan/v2.7/text-to-video"


async def generate_video(prompt: str) -> str:
    """
    fal.ai Wan 2.7 modelidan matn orqali video generatsiya qilish.
    Agarda settings.FAL_KEY yoki fal_client o'rnatilmagan bo'lsa, barqaror test videosini qaytaradi.
    """
    fal_key = settings.FAL_KEY or os.environ.get("FAL_KEY")
    
    if not fal_key:
        logger.warning("FAL_KEY sozlanmagan! Simulyatsiya rejimida test videosi yuboriladi.")
        await asyncio.sleep(5)  # Generatsiya simulyatsiyasi uchun kutish
        return "https://www.w3schools.com/html/mov_bbb.mp4"

    # Dinamik tarzda fal_client'ni import qilish
    try:
        import fal_client
        os.environ["FAL_KEY"] = fal_key
        
        logger.info(f"Fal.ai Wan 2.7 orqali video yaratish boshlanmoqda. Prompt: {prompt}")
        
        result = await asyncio.to_thread(
            fal_client.subscribe,
            FAL_MODEL,
            arguments={
                "prompt": prompt,
                "resolution": "720p",
                "aspect_ratio": "16:9",
                "duration": "5",
                "enable_audio": True,
            }
        )
        video_url = result["video"]["url"]
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
