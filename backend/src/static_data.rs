use std::collections::HashMap;

pub fn get_law_alias_map() -> HashMap<&'static str, Vec<&'static str>> {
    let mut m = HashMap::new();
    // 1. Specific
    m.insert(
        "高齢者虐待",
        vec!["高齢者虐待の防止、高齢者の養護者に対する支援等に関する法律"],
    );
    m.insert(
        "障害者虐待",
        vec!["障害者虐待の防止、障害者の養護者に対する支援等に関する法律"],
    );
    m.insert("児童虐待", vec!["児童虐待の防止等に関する法律"]);
    m.insert(
        "配偶者暴力",
        vec!["配偶者からの暴力の防止及び被害者の保護等に関する法律"],
    );
    m.insert("生活困窮", vec!["生活困窮者自立支援法"]);
    m.insert("身体障害", vec!["身体障害者福祉法"]);
    m.insert(
        "自立支援",
        vec![
            "生活困窮者自立支援法",
            "障害者の日常生活及び社会生活を総合的に支援するための法律",
        ],
    );
    m.insert("精神障害", vec!["精神保健及び精神障害者福祉に関する法律"]);
    m.insert("知的障害", vec!["知的障害者福祉法"]);
    // 2. Broad
    m.insert(
        "虐待",
        vec![
            "児童虐待の防止等に関する法律",
            "高齢者虐待の防止、高齢者の養護者に対する支援等に関する法律",
            "障害者虐待の防止、障害者の養護者に対する支援等に関する法律",
            "配偶者からの暴力の防止及び被害者の保護等に関する法律",
        ],
    );
    m.insert(
        "高齢",
        vec![
            "老人福祉法",
            "介護保険法",
            "高齢者虐待の防止、高齢者の養護者に対する支援等に関する法律",
        ],
    );
    m.insert("介護", vec!["介護保険法", "老人福祉法"]);
    m.insert(
        "障害",
        vec![
            "障害者の日常生活及び社会生活を総合的に支援するための法律",
            "身体障害者福祉法",
            "知的障害者福祉法",
            "精神保健及び精神障害者福祉に関する法律",
            "障害者虐待の防止、障害者の養護者に対する支援等に関する法律",
            "児童福祉法",
        ],
    );
    m.insert("児童", vec!["児童福祉法", "児童虐待の防止等に関する法律"]);
    m.insert("子供", vec!["児童福祉法", "児童虐待の防止等に関する法律"]);
    m.insert(
        "DV",
        vec!["配偶者からの暴力の防止及び被害者の保護等に関する法律"],
    );
    m.insert("生活保護", vec!["生活保護法"]);
    m.insert("生保", vec!["生活保護法"]);

    // Explicit names (simplified, assume key phrases work)
    m.insert("生活保護法", vec!["生活保護法"]);
    m.insert("児童福祉法", vec!["児童福祉法"]);

    m
}

pub fn get_child_keywords() -> Vec<&'static str> {
    vec![
        "子供",
        "児童",
        "保育",
        "幼",
        "児",
        "母子",
        "虐待",
        "障蓋児",
        "未成年",
    ]
}

pub fn get_penalty_keywords() -> Vec<&'static str> {
    vec!["罰金", "懲役", "処する", "過料", "併科"]
}

pub fn get_user_penalty_request_keywords() -> Vec<&'static str> {
    vec!["罰", "罪", "違反", "ペナルティ"]
}

pub fn get_boost_articles() -> Vec<&'static str> {
    vec![
        "第一条",
        "第二条",
        "第三条",
        "１条",
        "２条",
        "３条",
        "目的",
        "定義",
    ]
}
