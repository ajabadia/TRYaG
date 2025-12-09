# path: src/core/logger_config.py
import logging
import sys

def setup_logger(name: str = "tryag_app", level: int = logging.INFO) -> logging.Logger:
    """
    Configura y devuelve un logger estandarizado.
    
    Args:
        name: Nombre del logger
        level: Nivel de log (default INFO)
        
    Returns:
        logging.Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Si ya tiene handlers, no añadir más (evita duplicados en reload)
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    # Crear formatter compatible con consola
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handler de archivo (append mode)
    file_handler = logging.FileHandler("app.log", mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Instancia root por defecto para importaciones rápidas
logger = setup_logger()
