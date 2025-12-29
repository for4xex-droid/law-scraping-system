use anyhow::{Context, Result, anyhow};
use reqwest::Client;

use serde_json::{Value, json};

#[derive(Clone)]
pub struct GeminiClient {
    client: Client,
    api_key: String,
}

impl GeminiClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
        }
    }

    pub async fn embed_text(&self, text: &str) -> Result<Vec<f32>> {
        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={}",
            self.api_key
        );

        // Normalize text simple cleanup (remove newlines)
        let cleaned_text = text.replace('\n', " ");

        let body = json!({
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{ "text": cleaned_text }]
            },
            "taskType": "RETRIEVAL_DOCUMENT" // Matching Python behavior
        });

        let resp = self
            .client
            .post(&url)
            .json(&body)
            .send()
            .await
            .context("Failed to send embedding request")?;

        if !resp.status().is_success() {
            let error_text = resp.text().await.unwrap_or_default();
            return Err(anyhow!("Gemini API Error: {}", error_text));
        }

        let json: Value = resp
            .json()
            .await
            .context("Failed to parse embedding response")?;

        // Extract embedding
        // Response format: { "embedding": { "values": [ ... ] } }
        let values = json["embedding"]["values"]
            .as_array()
            .context("Invalid embedding format")?;

        let vec: Vec<f32> = values
            .iter()
            .map(|v| v.as_f64().unwrap_or(0.0) as f32)
            .collect();

        Ok(vec)
    }

    pub async fn generate_intent(
        &self,
        prompt: &str,
        candidates: &[String],
    ) -> Result<Vec<String>> {
        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={}",
            self.api_key
        );

        let candidates_json = serde_json::to_string(candidates).unwrap_or_default();

        let system_prompt = format!(
            "You are a Japanese Social Welfare Law expert. \
            Select 1-3 highly relevant laws for the USER QUERY from the Candidate List. \
            Return ONLY a JSON list of strings. No markdown. \
            Candidate List: {} \
            \
            Rules: \
            - If keywords match a specific law, put it first. \
            - Return [] if no relation. \
            - EXCLUDE 'Child Welfare Law' (児童福祉法) unless query explicitly contains child/kid keywords. \
            \
            User Query: {}",
            candidates_json, prompt
        );

        let body = json!({
            "contents": [{
                "parts": [{ "text": system_prompt }]
            }]
        });

        let resp = self.client.post(&url).json(&body).send().await?;

        if !resp.status().is_success() {
            return Err(anyhow!("Gemini Gen Error: {}", resp.status()));
        }

        let json: Value = resp.json().await?;
        // Parse parts.text
        let text = json["candidates"][0]["content"]["parts"][0]["text"]
            .as_str()
            .context("No text in response")?;

        // Extract JSON
        let clean_text = text.trim();
        let clean_text = if let Some(start) = clean_text.find('[') {
            if let Some(end) = clean_text.rfind(']') {
                &clean_text[start..=end]
            } else {
                "[]"
            }
        } else {
            "[]"
        };

        let laws: Vec<String> = serde_json::from_str(clean_text).unwrap_or_default();
        Ok(laws)
    }
}
