from pydantic import BaseModel, ConfigDict

from src.core.logging import get_logger
from src.core.result import Err, Ok, Result

logger = get_logger(__name__)


class DataModel(BaseModel):
    model_config = ConfigDict(frozen=True)
    message: str


class BusinessLogic:
    @staticmethod
    def process(input_text: str) -> Result[DataModel, str]:
        logger.debug(f"Processing: {input_text}")
        if not input_text:
            return Err("Input cannot be empty")
        return Ok(DataModel(message=f"Processed: {input_text}"))
