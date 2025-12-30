use regex::Regex;
use std::sync::OnceLock;

// 基本的なプロンプトインジェクションや不適切な入力を検知するためのガードレール
// 1. システム命令の乗っ取り ("Ignore previous instructions", "System Prompt"など)
// 2. HTML/Scriptインジェクション ("<script>", "javascript:"など)
// 3. 過度に長い入力

static INJECTION_PATTERNS: OnceLock<Vec<Regex>> = OnceLock::new();

fn get_patterns() -> &'static Vec<Regex> {
    INJECTION_PATTERNS.get_or_init(|| {
        vec![
            // プロンプトインジェクション系
            Regex::new(r"(?i)ignore previous instructions").unwrap(),
            Regex::new(r"(?i)system prompt").unwrap(),
            Regex::new(r"(?i)you are an ai").unwrap(), // AIの再定義を試みるもの
            
            // XSS / インジェクション系
            Regex::new(r"(?i)<script").unwrap(),
            Regex::new(r"(?i)javascript:").unwrap(),
            Regex::new(r"(?i)vbscript:").unwrap(),
            Regex::new(r"(?i)data:text/html").unwrap(),
            Regex::new(r"(?i)alert\(").unwrap(),
        ]
    })
}

#[derive(Debug)]
pub enum ValidationResult {
    Valid,
    Blocked(String), // ブロック理由
}

pub fn validate_input(input: &str) -> ValidationResult {
    // 1. 長さチェック (極端に長い入力はDoSの可能性があるため制限)
    if input.len() > 1000 {
        return ValidationResult::Blocked("Input too long (max 1000 chars)".to_string());
    }

    // 2. パターンマッチング
    let patterns = get_patterns();
    for re in patterns {
        if re.is_match(input) {
            return ValidationResult::Blocked("Potential injection detected".to_string());
        }
    }

    ValidationResult::Valid
}
