from src.logger import get_logger
from src.custom_exception import CustomException
import sys

logger = get_logger(__name__)

def divide_numbers(num1, num2):
    try:
        logger.info(f"Dividing {num1} by {num2}")
        return num1 / num2
    except Exception as e:
        logger.error("Error occurred while dividing numbers")
        raise CustomException("Division failed", e)


if __name__ == "__main__":
    try:
        divide_numbers(10, 0)
    except CustomException as e:
        logger.error(f"{str(e)}")
