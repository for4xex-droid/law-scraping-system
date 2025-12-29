use anyhow::Context;
use axum::{
    Router,
    extract::{Json, State},
    routing::{get, post},
};
use dotenv::dotenv;
use std::env;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::fs;
use tower_http::cors::CorsLayer;

mod gemini;
mod models;
mod static_data;

use gemini::GeminiClient;
use models::{LawDocument, SearchResult, cosine_similarity};
use static_data::{
    get_boost_articles, get_child_keywords, get_law_alias_map, get_penalty_keywords,
    get_user_penalty_request_keywords,
};

#[derive(Clone)]
struct AppState {
    docs: Arc<Vec<LawDocument>>,
    gemini_client: GeminiClient,
    law_names: Arc<Vec<String>>, // For candidates
}

#[derive(serde::Deserialize)]
struct SearchRequest {
    query: String,
}

#[derive(serde::Serialize)]
struct SearchResponse {
    results: Vec<SearchResult>,
    intent: Option<String>,
    targeted_laws: Vec<String>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    dotenv().ok();

    // Load Index
    println!("Loading index from data/index.json...");
    let index_data = fs::read_to_string("data/index.json")
        .await
        .context("Could not read index.json. Did you run export?")?;
    let docs: Vec<LawDocument> =
        serde_json::from_str(&index_data).context("Failed to parse index.json")?;
    println!("Loaded {} documents.", docs.len());

    // Extract unique law names for LLM candidates
    println!("Extracting law names...");
    let mut law_names: Vec<String> = docs
        .iter()
        .filter_map(|d| d.metadata["law_full_name"].as_str().map(|s| s.to_string()))
        .collect();
    law_names.sort();
    law_names.dedup();
    println!("Extracted {} unique laws.", law_names.len());

    println!("Loading API Key...");
    match dotenv::dotenv() {
        Ok(path) => println!("Loaded .env from {:?}", path),
        Err(e) => println!("Failed to load .env: {}", e),
    }

    let api_key = match env::var("GOOGLE_API_KEY") {
        Ok(k) => k,
        Err(_) => {
            println!("GOOGLE_API_KEY not found in env!");
            // Try loading from parent .env explicitly if needed, or panic with message
            panic!("GOOGLE_API_KEY must be set");
        }
    };
    println!("API Key found (len: {})", api_key.len());

    let gemini_client = GeminiClient::new(api_key);

    let state = AppState {
        docs: Arc::new(docs),
        gemini_client,
        law_names: Arc::new(law_names),
    };

    #[derive(serde::Deserialize)]
    struct LawContentRequest {
        law_name: String,
    }

    #[derive(serde::Serialize)]
    struct LawContentResponse {
        articles: Vec<SearchResult>, // Re-using SearchResult for convenience, though distance/relevance needed dummy values
    }

    async fn list_laws_handler(State(state): State<AppState>) -> Json<Vec<String>> {
        let mut names = state.law_names.as_ref().clone();
        names.sort();
        Json(names)
    }

    async fn get_law_content_handler(
        State(state): State<AppState>,
        Json(payload): Json<LawContentRequest>,
    ) -> Json<LawContentResponse> {
        let target = payload.law_name;
        let articles: Vec<SearchResult> = state
            .docs
            .iter()
            .filter(|d| d.metadata["law_full_name"].as_str().unwrap_or("") == target)
            .map(|d| SearchResult {
                document: d.text.clone(),
                metadata: d.metadata.clone(),
                distance: 0.0,
                relevance: 1.0,
            })
            .collect();

        // Sort? Hard without parsing "Article 1" etc.
        // We assume the source DB insertion order might be somewhat chronological or
        // relying on frontend to list them.
        // Chroma returns in ID order often, if IDs are sequential.

        Json(LawContentResponse { articles })
    }

    let app = Router::new()
        .route("/health", get(|| async { "OK" }))
        .route("/search", post(search_handler))
        .route("/laws", get(list_laws_handler))
        .route("/laws/content", post(get_law_content_handler))
        .layer(CorsLayer::permissive())
        .with_state(state);

    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    println!("Listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await?, app).await?;

    Ok(())
}

async fn search_handler(
    State(state): State<AppState>,
    Json(payload): Json<SearchRequest>,
) -> Json<SearchResponse> {
    let query = payload.query;

    println!("Search Query: {}", query);

    // 1. Embedding
    let query_vec = match state.gemini_client.embed_text(&query).await {
        Ok(v) => v,
        Err(e) => {
            eprintln!("Embedding error: {}", e);
            return Json(SearchResponse {
                results: vec![],
                intent: Some("Embedding Failed".to_string()),
                targeted_laws: vec![],
            });
        }
    };

    // 2. Intent Detection
    // A. Static
    let alias_map = get_law_alias_map();
    let mut target_laws: Vec<String> = Vec::new();
    let mut intent_msg: Option<String> = None;

    // Check aliases (Longest match)
    // Keys sorted by length desc handled by loop logic if we sort keys
    let mut sorted_keys: Vec<&str> = alias_map.keys().cloned().collect();
    sorted_keys.sort_by_key(|k| k.len()); // ascending
    sorted_keys.reverse(); // descending

    for alias in sorted_keys {
        if query.contains(alias) {
            if let Some(laws) = alias_map.get(alias) {
                target_laws = laws.iter().map(|s| s.to_string()).collect();
                intent_msg = Some(format!("Static Match: {}", alias));
                break;
            }
        }
    }

    // B. AI Intent (if static failed)
    if target_laws.is_empty() {
        // Attempt LLM
        // println!("Triggering LLM Intent...");
        if let Ok(suggestions) = state
            .gemini_client
            .generate_intent(&query, &state.law_names)
            .await
        {
            if !suggestions.is_empty() {
                target_laws = suggestions;
                intent_msg = Some("AI Suggested".to_string());
            }
        }
    }

    // 3. Search & Ranking
    // We compute scores for ALL documents (in-memory is fast enough for 2000 items)
    // Then filter or rank.

    let child_keywords = get_child_keywords();
    let penalty_keywords = get_penalty_keywords();
    let user_penalty_keywords = get_user_penalty_request_keywords();
    let boost_articles = get_boost_articles();

    let user_wants_penalty = user_penalty_keywords.iter().any(|k| query.contains(k));
    let query_contains_child = child_keywords.iter().any(|k| query.contains(k));

    let mut scored_results: Vec<SearchResult> = state
        .docs
        .iter()
        .map(|doc| {
            let sim = cosine_similarity(&query_vec, &doc.embedding);
            let mut dist = 1.0 - sim;

            // Apply Logic
            let law_name = doc.metadata["law_full_name"].as_str().unwrap_or("");
            let article_num = doc.metadata["article_number"].as_str().unwrap_or("");
            let doc_text = &doc.text;

            // Logic from app.py:
            // 1. Child Welfare Law Penalty
            if law_name == "児童福祉法" && !query_contains_child {
                dist += 0.15;
            }

            // 2. Penalty Keywords (if user didn't ask)
            if !user_wants_penalty && penalty_keywords.iter().any(|k| doc_text.contains(k)) {
                dist += 0.25;
            }

            // 3. Boost (Purpose/First Articles)
            if boost_articles.iter().any(|k| article_num.contains(k))
                || doc_text
                    .chars()
                    .take(50)
                    .collect::<String>()
                    .contains("目的")
            {
                dist -= 0.15;
            }

            // If target_laws is set, we need to handle that.
            // App.py: If target_laws, fetch ONLY those laws, ensure diversity, then sort.
            // If not, fallback search (which applies above logic).
            // BUT strict filtering might hide good results if AI is wrong.
            // App.py uses strict filtering IF static/AI matched.
            // Here, let's just heavily penalize non-matching laws if target is set?
            // Or strict filter.
            // Strict filter is safer for "Intent".

            let mut final_dist = dist;
            if !target_laws.is_empty() {
                if !target_laws.contains(&law_name.to_string()) {
                    // Push it way back
                    final_dist += 10.0;
                }
            }

            SearchResult {
                document: doc_text.clone(),
                metadata: doc.metadata.clone(),
                distance: final_dist, // Modified distance
                relevance: if final_dist > 1.0 {
                    0.0
                } else {
                    1.0 - final_dist
                },
            }
        })
        .collect();

    // Sort by distance ASC
    scored_results.sort_by(|a, b| {
        a.distance
            .partial_cmp(&b.distance)
            .unwrap_or(std::cmp::Ordering::Equal)
    });

    // Filter out highly irrelevant (distance > 5.0)
    let final_results: Vec<SearchResult> = scored_results
        .into_iter()
        .filter(|r| r.distance < 2.0) // 2.0 allows for some penalties but excludes strictly filtered
        .take(15) // Top 15
        .collect();

    Json(SearchResponse {
        results: final_results,
        intent: intent_msg,
        targeted_laws: target_laws,
    })
}
