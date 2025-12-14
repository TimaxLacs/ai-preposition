import uvicorn
import os
from dotenv import load_dotenv
from src.utils.logger import setup_logging

load_dotenv()

def main():
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Настройка логирования
    setup_logging(level=log_level)
    
    # Копируем конфиги если их нет
    if not os.path.exists("config/filters.yaml") and os.path.exists("config/filters.yaml.example"):
        import shutil
        shutil.copy("config/filters.yaml.example", "config/filters.yaml")
        print("Created default config/filters.yaml")
        
    if not os.path.exists("config/sources.yaml") and os.path.exists("config/sources.yaml.example"):
        import shutil
        shutil.copy("config/sources.yaml.example", "config/sources.yaml")
        print("Created default config/sources.yaml")

    print(f"Starting AI Post Filter on {host}:{port}")
    uvicorn.run("src.api.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()

