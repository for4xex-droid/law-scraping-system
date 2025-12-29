import requests
import xml.etree.ElementTree as ET


def check_law_id(law_id, name_hint):
    url = f"https://elaws.e-gov.go.jp/api/1/lawdata/{law_id}"
    print(f"Checking {name_hint} ({law_id})...")
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            law_title = root.find(".//LawTitle")
            if law_title is not None:
                print(f"✅ Found: {law_title.text}")
                return True
            else:
                print("⚠️ XML parsed but no LawTitle found.")
        else:
            print(f"❌ Status Code: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return False


# Candidate IDs
candidates = {
    "高齢者虐待防止法": "417AC0000000124",
    "老人福祉法": "338AC0000000133",
    "介護保険法": "409AC0000000123",
    "障害者総合支援法": "417AC0000000123",  # 障害者自立支援法から改正
}

for name, lid in candidates.items():
    check_law_id(lid, name)
