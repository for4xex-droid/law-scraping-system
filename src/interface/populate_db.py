import logging
import asyncio
from src.infrastructure.egov_api import EGovAPIClient
from src.infrastructure.database import LawRepository

# セットアップ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    db = LawRepository()
    api = EGovAPIClient()

    # 取得したい法律のリスト (e-Gov法令APIの法令番号: 法令名)
    target_laws = {
        # 既存登録済み
        "325AC0000000144": "生活保護法",
        "322AC0000000164": "児童福祉法",
        "326AC0000000045": "社会福祉法",
        "417AC1000000124": "高齢者虐待防止法",
        "409AC0000000123": "介護保険法",
        "338AC0000000133": "老人福祉法",
        "417AC0000000123": "障害者総合支援法",
        "324AC1000000283": "身体障害者福祉法",
        "335AC0000000037": "知的障害者福祉法",
        "325AC0100000123": "精神保健福祉法",
        "412AC1000000082": "児童虐待防止法",
        "413AC0100000031": "DV防止法",
        "425AC0000000105": "生活困窮者自立支援法",
        "423AC1000000079": "障害者虐待防止法",
        "409AC0000000131": "精神保健福祉士法",
        "362AC0000000030": "社会福祉士及び介護福祉士法",
        "323AC0000000168": "少年法",
        "336AC0000000223": "災害対策基本法",
        "322AC0000000118": "災害救助法",
        "140AC0000000045": "刑法",
        "323AC0000000131": "刑事訴訟法",
    }

    logger.info(f"Target laws: {target_laws}")

    for law_id, law_name in target_laws.items():
        logger.info(f"Fetching {law_name} ({law_id})...")

        try:
            # 1. 法令本文取得 (XML)
            xml_content = api.fetch_law_xml(law_id)  # メソッド名修正
            if not xml_content:
                logger.error(f"Failed to fetch XML for {law_name}")
                continue

            # 2. パース
            law_data, articles = api.parse_law_xml(xml_content, law_id)
            logger.info(f"Parsed {law_name}: {len(articles)} articles.")

            # 3. DB保存
            db.save_law(law_data)
            db.save_articles(articles)
            logger.info(f"Saved {law_name} to DB.")

        except Exception as e:
            logger.error(f"Error processing {law_name}: {e}")

    logger.info("Database population completed.")


if __name__ == "__main__":
    asyncio.run(main())
