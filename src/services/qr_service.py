import urllib.parse
from typing import Optional

def generate_qr_url(data: str, size: str = "150x150", ecc: str = "L", format: str = "png") -> str:
    """
    Genera una URL para obtener un código QR conteniendo los datos especificados.
    Actualmente utiliza la API pública de qrserver.com.
    
    Args:
        data: El contenido de texto/JSON a codificar.
        size: Dimensiones "ancho x alto" (default "150x150").
        ecc: Nivel de corrección de errores (L, M, Q, H).
        format: Formato de imagen (png, gif, jpeg, svg).
        
    Returns:
        str: URL pública de la imagen del QR.
    """
    
    # 1. Validaciones básicas
    if not data:
        return ""
        
    # 2. Encoding seguro de URL
    quoted_data = urllib.parse.quote(data)
    
    # 3. Construcción de URL (Provider Agnostic wrapper)
    # En el futuro podríamos cambiar esto por una librería local (ej: qrcode) que devuelva 
    # una ruta a un archivo temporal o un base64 string, manteniendo la firma.
    base_url = "https://api.qrserver.com/v1/create-qr-code/"
    query_params = f"?size={size}&data={quoted_data}&ecc={ecc}&format={format}"
    
    return f"{base_url}{query_params}"

def get_qr_base64(data: str) -> Optional[str]:
    """
    (Futuro) Generar QR localmente y devolver base64 para offline total.
    Por ahora devuelve None o usa lógica placeholder.
    """
    # TODO: Implementar con librería 'qrcode' y 'io.BytesIO' si se requiere offline estricto
    pass
