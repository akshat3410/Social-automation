# WHAT WE BUILD: The Social Engine Product & Technical Vision

Welcome to the `social-engine` project. This document serves as the complete product and technical vision for the project. Whether you are a new contributor, a prospective user, or a maintainer, this guide explains exactly what exists, what it does, and where it is going.

---

## 1. Vision Statement

**social-engine** is an autonomous, AI-powered content operating system designed to build and maintain high-signal audiences on autopilot. Unlike traditional schedulers that just push what you write, social-engine acts as a complete marketing team in a box: researching trends, planning strategies, drafting variations, reviewing quality, publishing, and learning from analytics. We aim to create the most extensible, self-hosted framework for technical creators to codify their unique voice, allowing them to scale their digital presence without scaling their screen time.

**The North Star Metric**: *High-Signal Engagement Rate* (the ratio of meaningful interactions—comments, retweets, bookmarks—to total impressions over time, indicating we are generating valuable content, not spam).

**Ideal Customer Profile (ICP)**: 
- Indie Developers and Solopreneurs who need a marketing presence but lack the time.
- Dev-tool Founders looking to maintain a steady cadence of thought leadership and product updates.
- Technical Marketers who want complete control over their automation pipelines and AI prompts.

---

## 2. What It Is (and Isn't)

To maintain focus, it is critical to understand the boundaries of this project.

### What It IS
- **An AI-powered content operating system**: A cohesive system of agents working together, not just a single LLM call.
- **A self-hosted, open-source pipeline**: You own your data, your API keys, and your database. Deploy it on your own VPS.
- **A framework for building on top of**: Designed with interfaces (`LLMProvider`, `SocialProvider`, `ResearchPlugin`) that make adding new models or platforms trivial.
- **A feedback loop**: A system that reads its own analytics to improve future generations.

### What It IS NOT
- **A simple post scheduler**: We don't just schedule tweets. If you only want a queue, use Buffer or Hypefury.
- **A SaaS (Software as a Service)**: This is infrastructure. We are not hosting a multi-tenant platform for end-users.
- **A replacement for human creativity**: The system amplifies human intent. It relies on the user's initial configuration, prompts, and (optional) approval to maintain high quality.
- **A spam bot**: Built-in quality gates actively reject low-effort or highly generic AI outputs.

---

## 3. The Full Pipeline (Explained)

The core of `social-engine` is a 9-step pipeline. Each step is handled by a specialized agent or service with clear inputs and outputs.

### Step 1: Research
- **What happens**: The system actively scans the internet for relevant topics, news, and discussions.
- **Who does it**: `ResearchAgent` orchestrating various `ResearchPlugin` instances (HackerNews, Reddit, RSS, GitHub Trending).
- **Inputs**: User's configured interests, target audience definitions, and recent trending keywords.
- **Process**:
  1. Fetches raw data from plugins.
  2. The LLM synthesizes this raw data to extract trending topics, key insights, and suggested angles.
  3. Memory search via `pgvector` checks if we have covered this recently to avoid repetition.
- **Output**: `ResearchResult`
  ```json
  {
    "summary": "String",
    "key_points": ["Point 1", "Point 2"],
    "trending_topics": ["AI Agents", "Rust"],
    "suggested_angles": ["Contrarian", "Tutorial"]
  }
  ```

### Step 2: Planning
- **What happens**: Deciding *what* to write about based on the research.
- **Who does it**: `PlanningAgent`.
- **Inputs**: `ResearchResult`.
- **Process**: The agent evaluates the research against the user's overarching goals (awareness, engagement, traffic, conversion). It selects the best topic, target audience, platform, and tone.
- **Output**: `ContentPlan`
  ```json
  {
    "topic": "Building scalable AI agents",
    "target_audience": "Senior Backend Engineers",
    "platform": "twitter",
    "tone": "technical, authoritative",
    "goal": "engagement"
  }
  ```

### Step 3: Writing
- **What happens**: Generating the actual text.
- **Who does it**: `WriterAgent`.
- **Inputs**: `ContentPlan`.
- **Process**: Generates 3-5 variations using different hooks and structures. It strictly enforces platform limits (e.g., Twitter: 280 characters, Reddit: Markdown support).
- **Output**: `list[DraftVariation]`
  ```json
  [
    {
      "content": "Most AI agents fail at scale. Here's how...",
      "hook": "Contrarian statement",
      "hashtags": ["#AI", "#Engineering"],
      "estimated_chars": 124
    }
  ]
  ```

### Step 4: Editing
- **What happens**: Refining the generated drafts to remove "AI-isms" (e.g., "In conclusion", "It's important to note").
- **Who does it**: `EditorAgent`.
- **Inputs**: `list[DraftVariation]`.
- **Process**: Improves grammar, flow, and readability. Applies user-specific style guides.
- **Output**: Edited content + a changelog explaining the edits.

### Step 5: Quality Review
- **What happens**: Automated, objective scoring of the drafts.
- **Who does it**: `QualityAgent`.
- **Inputs**: Edited drafts.
- **Process**: Scores the draft across 7 dimensions (0.0 to 1.0):
  1. Originality
  2. Hook strength
  3. Predicted engagement
  4. Spam probability (inverted: lower = better)
  5. Readability
  6. Brand consistency
  7. Human-sounding score
  *Also performs a duplicate similarity check against the semantic memory to ensure we aren't repeating ourselves.*
- **Output**: `QualityScoreResult`
  ```json
  {
    "passed": true,
    "rejection_reason": null,
    "scores": {
      "originality": 0.85,
      "human_sounding": 0.90
    }
  }
  ```
  *Drafts failing thresholds are auto-rejected.*

### Step 6: Human Approval (Optional)
- **What happens**: Manual gatekeeping.
- **Who does it**: The User (via Frontend Dashboard).
- **Inputs**: Pending drafts with quality scores.
- **Process**: User views drafts on the dashboard. They can one-click approve, edit, or reject (with a reason to train the system). This step can be bypassed in config for full automation.
- **Output**: Approved draft ready for scheduling.

### Step 7: Publishing
- **What happens**: Sending the content to the world.
- **Who does it**: `PublishingAgent` & `SocialProvider` registry.
- **Inputs**: Approved draft, scheduled time, target platform.
- **Process**: Calls the respective API (e.g., Twitter v2 POST tweets, Reddit POST to subreddit). 
- **Output**: Saves a `PublishedPost` record with the `platform_post_id`. Supports immediate, scheduled, or recurring execution.

### Step 8: Analytics Collection
- **What happens**: Gathering performance data post-publish.
- **Who does it**: `AnalyticsAgent` + Background Worker.
- **Inputs**: `platform_post_id`.
- **Process**: Re-fetches metrics at T+1h, T+24h, and T+7d.
- **Metrics Tracked**: views, likes, replies, bookmarks, reposts, CTR, follower_delta, upvotes.
- **Output**: Populates the `Analytics` table in PostgreSQL.

### Step 9: Learning
- **What happens**: Closing the loop to improve future performance.
- **Who does it**: `LearningAgent`.
- **Inputs**: Published content + Analytics data.
- **Process**: Analyzes *why* a post succeeded or failed. Did the hook work? Did the tone resonate? Did it flop completely?
- **Output**: Updates the `BrandMemory` table (via pgvector) with performance scores. These insights are embedded and fed back into future Research and Planning steps.

---

## 4. Feature Inventory (Current)

Here is exactly what is built and functional today:

### Backend
- **Core**: Full async REST API built with FastAPI.
- **Auth**: JWT authentication for API security.
- **Database**: 14-table PostgreSQL schema using SQLAlchemy 2.0.
- **Memory**: `pgvector` semantic memory integration (1536-dimensional embeddings).
- **AI Core**: 8 specialized AI agents managing the pipeline.
- **LLM Integration**: 3 LLM providers implemented (OpenRouter, OpenAI-compatible, Mock for testing).
- **Social Integration**: 2 social providers (Twitter, Reddit) + Mock provider.
- **Research**: 4 research plugins (HackerNews, Reddit, RSS, GitHub) + Mock plugin.
- **Background Jobs**: Dramatiq background task queue with 4 distinct actors.
- **Scheduling**: Cron-based scheduler for routine triggers.
- **Quality Assurance**: Automated Quality gate utilizing 7 distinct metrics.
- **Prompting**: File-based prompt versioning system.
- **Observability**: Structured logging with unique request IDs per transaction.
- **Error Handling**: Global exception handling with specific domain exceptions.
- **Data Integrity**: Soft delete support on core models and full Alembic migrations.

### Frontend
- **Framework**: Next.js 14 App Router dashboard.
- **UI/UX**: Dark mode by default, responsive design.
- **Pages (9 Total)**: 
  - Dashboard (Overview)
  - Research (Trigger & view research)
  - Drafts (Approve/Reject UI)
  - Calendar (Content schedule view)
  - Analytics (Performance charts)
  - Memory (View semantic memory bank)
  - Settings (Config & API Keys)
  - Prompt Editor (Edit agent prompts & version history)
  - Logs (Live log viewer)
- **Data Viz**: Recharts integration for line, bar, and pie charts (Analytics).
- **State Management**: TanStack Query (React Query) for robust server state synchronization.
- **Language**: Strict TypeScript throughout the stack.

### DevOps
- **Orchestration**: Docker Compose setup with 6 services (`postgres`, `redis`, `backend`, `worker`, `scheduler`, `frontend`).
- **Containers**: Multi-stage Dockerfiles running as non-root users for security.
- **Database Setup**: `pgvector` extension automatically enabled in Postgres image.
- **Caching/Queue**: Redis persistence configured (appendonly).
- **CI/CD**: GitHub Actions workflow (linting, type-checking, testing).
- **Config**: Comprehensive `.env.example` defining all required keys.
- **Developer Experience**: `setup_dev.sh` for one-command local environment setup, and `seed_data.py` to generate sample data for immediate testing.

---

## 5. Configuration Reference

The system behavior is heavily customizable via environment variables and database settings:

- **AI Models**:
  - `MODEL_RESEARCH`: The model used for wide context synthesis (e.g., Claude 3.5 Sonnet, GPT-4o).
  - `MODEL_WRITING`: The model used for creative drafting.
  - `MODEL_EDITING`: The model used for strict adherence to style guides.
- **Quality Thresholds**:
  - `MIN_ENGAGEMENT_SCORE`: Float (0.0-1.0). Minimum predicted engagement to pass.
  - `MAX_SPAM_SCORE`: Float. Maximum allowed spam probability.
  - `MIN_HUMAN_SCORE`: Float. Minimum required "human-sounding" metric.
- **Feature Flags**:
  - `ENABLE_TWITTER`: Boolean.
  - `ENABLE_REDDIT`: Boolean.
  - `ENABLE_HUMAN_APPROVAL`: Boolean. If false, drafts passing quality gates are auto-scheduled.
- **Scheduling**:
  - `SCHEDULER_POLL_INTERVAL_SECONDS`: Integer. How often the scheduler checks for due posts (default: 60).
- **Memory**:
  - `MEMORY_SIMILARITY_THRESHOLD`: Float. The cosine similarity score required to flag a topic as "already covered recently".

---

## 6. API Surface

The backend exposes a comprehensive REST API:

**Auth**
- `POST /register`: Register a new admin user.
- `POST /login`: Authenticate and receive JWT.
- `GET /me`: Get current user profile.

**Content**
- `POST /ideas`: Manually inject a content idea.
- `GET /ideas`: List pending ideas.
- `GET /ideas/{id}`: Get specific idea details.
- `POST /ideas/{id}/research`: Force research execution for an idea.
- `POST /ideas/{id}/generate`: Force pipeline to generate drafts for an idea.
- `GET /drafts`: List drafts awaiting approval.
- `GET /drafts/{id}`: View specific draft variations.
- `POST /drafts/{id}/approve`: Approve a draft for scheduling.
- `POST /drafts/{id}/reject`: Reject a draft with a feedback reason.

**Publishing**
- `POST /publish`: Publish a draft immediately.
- `POST /schedule`: Schedule an approved draft.
- `DELETE /schedule/{id}`: Cancel a scheduled post.
- `GET /published`: List historical published posts.

**Analytics**
- `GET /analytics/summary`: Aggregate metrics (total views, avg engagement).
- `GET /analytics/posts`: Granular metrics per post.
- `POST /analytics/sync/{post_id}`: Force a manual metric fetch from the social platform.

**Prompts**
- `GET /prompts`: List all active prompts for all agents.
- `GET /prompts/{agent}`: Get the current prompt for a specific agent.
- `PUT /prompts/{agent}`: Update the prompt for an agent.
- `GET /prompts/{agent}/versions`: View history of a prompt.
- `POST /prompts/{agent}/rollback/{version}`: Revert to a previous prompt version.

---

## 7. Roadmap

### Milestone 1 — Foundation (DONE ✅)
- [x] Clean architecture scaffold
- [x] All 14 DB models
- [x] All 8 agents
- [x] 3 LLM providers
- [x] 2 social providers
- [x] Full REST API
- [x] Next.js dashboard
- [x] Docker Compose

### Milestone 2 — Quality & Testing
- [ ] Full test suite (>80% coverage via pytest)
- [ ] Integration tests using testcontainers
- [ ] Ruff linting + mypy strict type checking enforcement
- [ ] Pre-commit hooks setup
- [ ] Load testing with locust to ensure background queue stability

### Milestone 3 — Production Hardening
- [ ] Prometheus metrics endpoint (`/metrics`)
- [ ] Grafana dashboard templates for observability
- [ ] Sentry error tracking integration
- [ ] Rate limiting per user per platform to avoid API bans
- [ ] Circuit breaker pattern for external APIs (LLMs, Socials)
- [ ] Webhook support (e.g., trigger an action when a post is published)

### Milestone 4 — New Platforms
- [ ] LinkedIn provider integration
- [ ] Bluesky provider (AT Protocol integration)
- [ ] Threads provider
- [ ] Mastodon provider
- [ ] Discord webhook provider for community announcements

### Milestone 5 — Content Expansion
- [ ] Newsletter generation (Beehiiv/Substack API)
- [ ] Blog post generation (Markdown output export)
- [ ] YouTube script generation formatting
- [ ] Image prompt generation (DALL-E/Midjourney integration for social cards)
- [ ] Thread/carousel automated generation

### Milestone 6 — Intelligence
- [ ] Competitor analysis research plugin
- [ ] Trend prediction (running lightweight ML on our analytics data)
- [ ] Optimal posting time prediction based on historical engagement
- [ ] Audience persona profiling (auto-updating personas based on who engages)
- [ ] A/B test framework for hooks and images

---

## 8. How to Contribute

We designed `social-engine` to be highly extensible. Here is how you can add functionality:

- **Adding an LLM Provider**: Implement the `LLMProvider` abstract base class in `backend/agents/llm_provider.py`. Register your new provider in the configuration settings.
- **Adding a Social Platform**: Create a new class inheriting from `SocialProvider` in `backend/agents/social_provider.py`. Implement `publish()` and `fetch_analytics()`, then add it to the `SocialProviderRegistry`.
- **Adding a Research Plugin**: Implement the `ResearchPlugin` interface in the `backend/research/` directory. Define `fetch_trending()` and add it to the `ResearchPluginRegistry`.
- **Modifying Prompts**: You can edit the markdown files directly in `backend/prompts/` or use the visual Prompt Editor in the Next.js dashboard. The system tracks versions automatically on save.

For full architectural guidelines, refer to the inline docstrings in the codebase. We enforce strict Python 3.13 type hints, Pydantic v2 syntax, and SQLAlchemy 2.0 select paradigms.

---

## 9. Quick Reference Card

When navigating the repository, these are the key files and directories developers will touch most frequently:

- `backend/config/settings.py` — Central repository for all system configurations and environment variables.
- `backend/agents/llm_provider.py` — Location for adding new LLM capabilities.
- `backend/agents/social_provider.py` — Location for adding new social media endpoints.
- `backend/research/` — Directory containing all data ingestion plugins.
- `backend/prompts/*.md` — The raw instructions dictating agent behavior.
- `backend/services/content_service.py` — The core orchestrator that links the 9-step pipeline together.
- `frontend/src/app/` — Next.js App Router containing all dashboard pages and layouts.

*This document is a living artifact. Update it as new milestones are reached and the architecture evolves.*
