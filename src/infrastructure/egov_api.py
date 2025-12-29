import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from datetime import datetime
from src.core.models import Law, Article


class EGovAPIClient:
    BASE_URL = "https://elaws.e-gov.go.jp/api/1/lawdata"

    def fetch_law_xml(self, law_id: str) -> Optional[bytes]:
        """e-Gov APIからXMLデータを取得"""
        try:
            url = f"{self.BASE_URL}/{law_id}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching law {law_id}: {e}")
            return None

    def parse_law_xml(
        self, xml_content: bytes, law_id: str
    ) -> tuple[Law, List[Article]]:
        """XMLをパースしてLawとArticleのリストを返す"""
        root = ET.fromstring(xml_content)

        # Law Info
        law_num_node = root.find(".//LawNum")
        law_num = (law_num_node.text or "") if law_num_node is not None else ""

        law_title_node = root.find(".//LawBody/LawTitle")
        law_name = (
            (law_title_node.text or "Unknown")
            if law_title_node is not None
            else "Unknown"
        )

        law = Law(
            law_id=law_id,
            law_num=law_num,
            law_full_name=law_name,
            last_updated=datetime.now(),
        )

        articles = []

        # 階層構造解析のための再帰関数
        def parse_provision(element, hierarchy_stack):
            # 要素が目次や制定文でないかチェック
            if element.tag in ["TOC", "Verhulst"]:
                return

            current_hierarchy = hierarchy_stack.copy()

            # 階層名の取得 (PartTitle, ChapterTitle, etc.)
            title_node = None
            for child in element:
                if "Title" in child.tag and child.tag != "ArticleTitle":
                    title_node = child
                    break

            if title_node is not None and title_node.text:
                current_hierarchy.append(title_node.text)

            # 条文 (Article) の処理
            if element.tag == "Article":
                article_caption = element.find("ArticleCaption")
                article_title = element.find("ArticleTitle")

                caption_text = (
                    (article_caption.text or "") if article_caption is not None else ""
                )
                title_text = (
                    (article_title.text or "") if article_title is not None else ""
                )

                full_article_name = f"{title_text} {caption_text}".strip()

                # 条文本文の取得 (Paragraph/ParagraphSentence/Sentence)
                # 簡略化してテキストを結合
                content_text = ""
                for paragraph in element.findall("Paragraph"):
                    num = paragraph.find("ParagraphNum")
                    num_text = (num.text or "") if num is not None else ""

                    sentence_text = ""
                    for sent in paragraph.findall(".//Sentence"):
                        if sent.text:
                            sentence_text += sent.text

                    content_text += f"{num_text} {sentence_text}\n"

                hierarchy_str = " > ".join(current_hierarchy)
                articles.append(
                    Article(
                        law_id=law_id,
                        article_number=full_article_name,
                        hierarchy=hierarchy_str,
                        content=content_text.strip(),
                    )
                )
                return  # Article以下はもう階層構造ではないのでreturn

            # 再帰処理
            for child in element:
                parse_provision(child, current_hierarchy)

        # MainProvisionから探索開始
        main_provision = root.find(".//MainProvision")
        if main_provision is not None:
            parse_provision(main_provision, [])

        return law, articles
