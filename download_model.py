import os
import logging
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# watt-ai/watt-tool-8B
# Qwen/Qwen2.5-14B-Instruct
# mistralai/Mistral-Small-24B-Instruct-2501
def download_model(model_id: str = "mistralai/Mistral-Small-24B-Instruct-2501", cache_dir: str = None):
    """
    Download model and tokenizer from HuggingFace Hub
    """
    try:
        
        logger.info(f"Starting download of {model_id} to {cache_dir}")
        
        # Download model files
        local_dir = snapshot_download(
            repo_id=model_id,
            cache_dir=cache_dir,
            resume_download=True,
            local_files_only=False,
            token=os.getenv("HF_TOKEN")
        )
        
        logger.info(f"Model files downloaded to {local_dir}")
        
        # Download and save tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Download and save model
        logger.info("Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype="auto"
        )
        
        # Save both tokenizer and model locally
        save_dir = os.path.join(cache_dir, f"models--{model_id.replace('/', '--')}")
        logger.info(f"Saving tokenizer and model to {save_dir}")
        
        tokenizer.save_pretrained(save_dir)
        model.save_pretrained(save_dir)
        
        logger.info("Download completed successfully!")
        return save_dir
        
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        raise

if __name__ == "__main__":
    try:
        download_model()
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"Download failed: {e}") 