import os
import tornado.web
import logging
import gc

TEMP_DIR = 'temp'
os.makedirs(TEMP_DIR, exist_ok=True)

# Configurar logging
logging.basicConfig(filename='server_debug.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class VideoUploadHandler(tornado.web.RequestHandler):
    def initialize(self):
        logging.info("VideoUploadHandler initialized")

    def set_default_headers(self):
        logging.info("Setting default headers")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, x-xsrftoken, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def options(self):
        logging.info("OPTIONS request received")
        self.set_status(204)
        self.finish()

    def check_xsrf_cookie(self):
        logging.info("Checking XSRF cookie - BYPASSING")
        return True

    def prepare(self):
        logging.info(f"Preparing request: {self.request.method} {self.request.uri}")
        pass

    def post(self):
        logging.info("POST request received")
        try:
            filename = self.get_argument("filename", default=None)
            if not filename:
                filename = f"video_{os.urandom(4).hex()}.webm"
            
            logging.info(f"Processing upload for filename: {filename}")
            
            file_body = self.request.body
            logging.info(f"File body size: {len(file_body)} bytes")
            
            save_path = os.path.join(TEMP_DIR, filename)
            
            with open(save_path, "wb") as f:
                f.write(file_body)
            
            logging.info(f"File saved to: {save_path}")
            
            self.write({"status": "success", "filename": filename, "path": save_path})
            
        except Exception as e:
            logging.error(f"Error in POST: {str(e)}")
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})

def mount_video_upload_route(route="/upload_video_v7"):
    """
    Monta la ruta de subida de video buscando directamente la aplicación Tornado.
    """
    try:
        logging.info(f"Attempting to mount route: {route}")
        
        tornado_app = None
        # Buscar instancia de tornado.web.Application
        for obj in gc.get_objects():
            if isinstance(obj, tornado.web.Application):
                tornado_app = obj
                break
        
        if tornado_app:
            logging.info("Found Tornado Application instance")
            tornado_app.add_handlers(r".*", [
                (route, VideoUploadHandler),
            ])
            logging.info(f"Ruta {route} montada exitosamente (v7).")
            print(f"Ruta {route} montada exitosamente (v7).")
        else:
            logging.error("Could not find Tornado Application instance via gc")
            print("Error: No se pudo obtener la instancia de la aplicación Tornado.")
            
    except Exception as e:
        logging.error(f"Error montando ruta Tornado: {e}")
        print(f"Error montando ruta Tornado: {e}")
