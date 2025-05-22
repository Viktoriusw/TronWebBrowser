import string
import random
import psutil
import time
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PasswordGenerator:
    def __init__(self):
        self.last_generation_time = 0
        self.last_cpu_usage = 0
        self.last_ram_usage = 0

    def generate_password(self, length=60, include_numbers=True, include_uppercase=True, 
                         include_lowercase=True, include_special=True):
        """Genera una contraseña segura con las características especificadas"""
        try:
            # Validar longitud
            if length > 10_000_000:
                raise ValueError("Maximum allowed length is 10 million characters.")

            # Construcción del conjunto de caracteres
            characters = ""
            if include_numbers:
                characters += string.digits
            if include_uppercase:
                characters += string.ascii_uppercase
            if include_lowercase:
                characters += string.ascii_lowercase
            if include_special:
                characters += string.punctuation

            if not characters:
                raise ValueError("Select at least one type of character.")

            # Medir tiempo de inicio
            start_time = time.time()

            # Generación de contraseña
            password = ''.join(random.SystemRandom().choice(characters) for _ in range(length))

            # Medir tiempo y recursos
            self.last_generation_time = time.time() - start_time
            self.last_cpu_usage = psutil.cpu_percent(interval=0.1)
            self.last_ram_usage = psutil.virtual_memory().percent

            # Logging
            logger.info(f'Tiempo para generar contraseña: {self.last_generation_time:.6f} segundos')
            logger.info(f'Uso de CPU: {self.last_cpu_usage}%')
            logger.info(f'Uso de RAM: {self.last_ram_usage}%')

            return {
                "password": password,
                "time": f"{self.last_generation_time:.6f} seconds",
                "cpu_usage": f"{self.last_cpu_usage}%",
                "ram_usage": f"{self.last_ram_usage}%"
            }

        except Exception as e:
            logger.error(f"Error generando contraseña: {str(e)}")
            raise

    def get_generation_stats(self):
        """Retorna las estadísticas de la última generación"""
        return {
            "time": self.last_generation_time,
            "cpu_usage": self.last_cpu_usage,
            "ram_usage": self.last_ram_usage
        } 