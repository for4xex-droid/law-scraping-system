import requests
import xml.etree.ElementTree as ET


def search_law_id(keyword):
    url = "https://elaws.e-gov.go.jp/api/1/lawlists/1"
    print(f"Downloading law list to search for '{keyword}'...")
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            found = False
            with open("found_ids.txt", "a", encoding="utf-8") as f:
                for law in root.findall(".//LawNameListInfo"):
                    name = law.find("LawName").text
                    if keyword in name:
                        lid = law.find("LawId").text
                        print(f"🎯 Found: {name} -> {lid}")
                        f.write(f"{name}: {lid}\n")
                        found = True
            if not found:
                print(f"❌ No law found asking for '{keyword}'")
        else:
            print(f"❌ Error fetching list: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


# Clear file
with open("found_ids.txt", "w", encoding="utf-8") as f:
    pass

# Additional Laws
search_law_id("生活困窮者自立支援法")
search_law_id("身体障害者福祉法")
search_law_id("知的障害者福祉法")
search_law_id("精神保健及び精神障害者福祉に関する法律")
search_law_id("児童虐待の防止等に関する法律")
search_law_id("配偶者からの暴力の防止及び被害者の保護等に関する法律")
search_law_id("精神保健福祉士法")
search_law_id("精神保健福祉士法施行令")
search_law_id("精神保健福祉士法施行規則")
search_law_id("社会福祉士及び介護福祉士法")
