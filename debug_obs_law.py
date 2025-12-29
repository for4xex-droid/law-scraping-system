import logging
import asyncio
from src.infrastructure.egov_api import EGovAPIClient
from src.infrastructure.database import LawRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_fetch():
    target_law_id = "423AC1000000079"
    target_name = "障害者虐待防止法"

    api = EGovAPIClient()
    db = LawRepository()

    logger.info(f"Fetching {target_name} ({target_law_id})...")

    xml_content = api.fetch_law_xml(target_law_id)
    if not xml_content:
        logger.error("XML Content is None / Empty")
        return

    logger.info(f"XML Size: {len(xml_content)} bytes")

    try:
        law_data, articles = api.parse_law_xml(xml_content, target_law_id)
        logger.info(f"Parsed. Law Name: {law_data.law_full_name}")
        logger.info(f"Articles Count: {len(articles)}")

        db.save_law(law_data)
        db.save_articles(articles)
        logger.info("Saved to DB successfully.")

    except Exception as e:
        logger.error(f"Parse/Save Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_fetch())
