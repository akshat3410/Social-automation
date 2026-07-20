# social-engine: Context and Design Decisions

This document explains the *why* behind every major decision in the `social-engine` project. It serves as both a technical design document and an engineering philosophy guide. If you are developing on this platform, read this to understand the problem space deeply and why we approach it differently.

## 1. The Problem We're Solving

Social media automation is broken. The internet is flooded with tools that promise to "put your social media on autopilot," but they fundamentally misunderstand the goal. 

**Why social media automation tools fail:** They generate garbage content. Most tools simply hook up an LLM API to a scheduling queue. They prompt the model with "write a tweet about X," schedule the output, and call it a day. 
The result is bland, generic, and immediately recognizable as AI-generated. 

**Post scheduler vs. Content operating system:** A post scheduler simply moves text from a database to an API at a specific time. A content operating system handles the entire lifecycle: ideation, research, drafting, editing, quality assurance, publishing, and learning from performance. `social-engine` is the latter.

**The generic content trap:** Most AI writing tools produce spammy content because they lack context and memory. They don't know what you posted yesterday, they don't know what's trending right now, and they default to safe, generic language.

**The engagement problem:** AI-detected or generic content gets buried by platform algorithms. High engagement comes from novel insights, distinct voice, and relevance to current conversations.

**Why human-in-the-loop matters:** Even with advanced AI, humans provide the final check for authenticity, brand alignment, and nuance. `social-engine` is designed to do 95% of the heavy lifting, serving up high-quality drafts for human approval, not to completely remove the human from the equation.

## 2. Why This Exists

**Solo founders and small teams** spend countless hours managing social media—time they should spend building their product. Conversely, ignoring social media incurs a massive opportunity cost and algorithm penalties for inconsistent posting.

The opportunity lies in symbiosis: AI can do the grueling grunt work (researching trends, generating multiple variations, drafting outlines), while humans add the final layer of authenticity and insight.

**Why open source matters here:** Social media is an essential growth channel. Relying on a proprietary, closed-source SaaS means vendor lock-in, loss of control over your data (and memory), and an inability to customize the core AI prompts. By being open source, `social-engine` gives you full ownership of your content pipeline and the freedom to tweak the engine to your exact needs.

## 3. Design Philosophy

**Think like a content strategist, not a bot.** A bot just posts. A strategist researches, plans, writes, edits, reviews, and learns. 

Our architecture mirrors this with **The Pipeline Philosophy**:
Research → Plan → Write → Edit → Quality → Approve → Publish → Learn

**Every stage matters.** Skipping research results in generic content. Skipping quality checks risks algorithmic penalties. Skipping learning means you never improve. 

**Content feedback loops:** Publishing is not the end of the pipeline. `social-engine` analyzes the engagement metrics of published content to inform future generation, learning which hooks and topics resonate with your audience.

**Why memory is critical:** Without memory, an AI will repeat itself infinitely. A content system must remember what it has published, what performed well, and what topics have been exhausted recently. Memory ensures continuity and variety.

## 4. Why Clean Architecture?

The AI space is moving incredibly fast. Tightly coupling your application logic, database, and LLM providers is a recipe for legacy code within months.

**The cost of tightly coupled AI systems:** Everyone starts by building a monolith where an API endpoint directly queries OpenAI and saves to a database. When you need to swap to Claude, change your database schema, or add a background worker, the entire system breaks.

**Strict Boundaries:**
- **Agents must NOT touch the database directly.** They interact with Repositories.
- **The API must NOT call AI directly.** It delegates to the Agent layer.
- **What happens when you swap LLM providers?** Nothing should break. The domain logic remains untouched.

**Real-world example:** If DeepSeek releases a new model that is 10x cheaper and better for research, you should be able to swap it in for the Research Agent with a single configuration change, without touching the prompt logic or API endpoints.

## 5. Technology Choices (and Why)

### Python 3.13
- **Async-first:** AI workloads are extremely I/O heavy (waiting for network requests to LLM APIs). Python's `asyncio` is perfect for this.
- **Ecosystem:** Python is the undisputed king of the AI/ML ecosystem.
- **Type hints:** Python 3.13 offers mature, robust type hinting, allowing us to build reliable systems.

### FastAPI + Pydantic v2
- **Auto-generated OpenAPI docs:** Essential for a clean, discoverable API.
- **Pydantic v2 performance:** Written in Rust, it is up to 10x faster than v1 for data validation.
- **Dependency injection:** Built into FastAPI, making clean architecture and testing significantly easier.
- **Why not Flask/Django:** We need async-first, modern type safety, and minimal overhead.

### PostgreSQL + pgvector
- **Why not a dedicated vector DB (Pinecone, Weaviate, Chroma):** Managing multiple databases adds immense operational overhead.
- **Single source of truth:** Relational data (users, posts, metrics) and vector data (embeddings for semantic search) live side-by-side in PostgreSQL.
- **pgvector cosine distance:** Perfect for semantic deduplication (ensuring we don't post the same idea twice).
- **Alembic:** Rock-solid reproducible database migrations.

### Redis + Dramatiq
- **Why message queues:** AI tasks are slow. A web request cannot wait 30 seconds for an LLM to generate a draft.
- **Why not Celery:** Dramatiq has a cleaner API, better type safety, and sane defaults compared to Celery's complexity.
- **Redis persistence:** Ensures no job loss on worker restart.
- **Rate limiting:** Essential for respecting social platform API limits.

### OpenRouter as AI Gateway
- **One API for 100+ models:** Instantly access OpenAI, Anthropic, Google, and open-source models through a single interface.
- **Cost optimization:** Route easy tasks (research summarization) to cheap models, and complex tasks (final drafting) to expensive, capable models.
- **Resilience:** Easy fallback if one provider experiences an outage.
- **Abstraction:** We keep the interface abstract (`social_engine.ai`) so we aren't permanently locked to OpenRouter.

### Next.js + shadcn/ui
- **Server components:** Fast initial load and excellent SEO/performance.
- **shadcn/ui:** Accessible, beautifully designed, and importantly, *not a black box*. You own the component code.
- **Recharts:** Composable and open-source for analytics visualization.
- **Why not a SaaS template:** We prioritize ownership over dependencies. You should own your UI.

## 6. The Agent Design Decisions

### Why 8 Separate Agents (not 1 mega-prompt)?
- **Single responsibility:** Each agent does one specific thing well (e.g., researching, planning, drafting).
- **Independent iteration:** You can improve the Writer Agent's prompt without breaking the Quality Gate.
- **Independent testing:** You can mock at the agent boundary, testing the Planner in isolation.
- **Cost control:** Use a cheap model like Haiku for research, and a premium model like Opus for drafting.
- **Prompt specialization:** Mega-prompts get confused. Focused prompts yield predictable, high-quality results.

### Why 3-5 Draft Variations?
- Different hooks appeal to different segments of your audience.
- It lays the foundation for automated A/B testing.
- It prevents the AI from falling into a single-path tunnel vision.
- Humans need choices to pick the best possible representation of their voice.

### Why a Quality Gate?
- **Algorithm defense:** Platforms aggressively downrank low-quality or repetitive content.
- **Spam protection:** One bad, off-brand post can ruin an account's reputation.
- **Consistency:** Automatically enforces brand voice and safety guidelines.
- **Data collection:** The Quality Gate scores content across 7 metrics, providing a learning signal for future generation.

### Why Human Approval is Optional?
- Power users want full automation (fire and forget).
- New users want strict oversight to build trust in the system.
- Regulated industries (finance, healthcare) require manual compliance review.
- Handled gracefully via the `ENABLE_HUMAN_APPROVAL` feature flag.

## 7. Memory System Rationale

Content systems fail without memory because they end up repeating the same angles forever. 

**Semantic search vs. keyword search:** A standard database query won't catch that "productivity tips" and "time management hacks" are conceptually identical. Vector embeddings do.

**0.85 cosine similarity threshold:** This is our sweet spot. Too strict (>0.95), and it blocks valid creative riffs on past themes. Too loose (<0.7), and it flags unrelated topics as duplicates.

**BrandMemory Types:** We categorize memory into distinct types: `tweet`, `reddit_post`, `hook`, `style`, `product_info`, and `feature`. This allows agents to query specific contexts (e.g., "Find successful hooks we've used for product_info X").

**Learning over time:** As posts are published and engagement data returns, the memory embeddings are updated with performance metadata, allowing the system to learn what works.

## 8. Multi-Platform Strategy

**Why Twitter and Reddit first?** They have the most developer-friendly APIs and distinct content cultures.
- **Twitter:** High-velocity, short-form, hook-driven, trend-focused.
- **Reddit:** Community-specific (subreddits), long-form acceptable, highly sensitive to authenticity and spam (karma system).

**The SocialProvider abstraction:** By abstracting the platform logic into a generic interface, we future-proof the engine for seamless addition of LinkedIn, Bluesky, Threads, or Mastodon.

**Platform-specific quality rules:** A great tweet is a terrible subreddit post. The Quality Gate dynamically loads rules based on the target platform (e.g., Twitter's 280 character limit vs. a specific subreddit's formatting rules).

## 9. Open Source Strategy

**MIT Licensed:** `social-engine` is MIT licensed, not AGPL or proprietary. We want this to be the foundational operating system for content generation that anyone can build upon or commercialize.

**What stays open:** The core infrastructure, agent pipeline, memory system, and API.

**Self-hosting:** Companies can self-host this entirely, using their own API keys, ensuring their brand data never leaves their infrastructure.

**Mock providers:** We provide mock LLM and Social providers out-of-the-box so contributors can build and test without needing real Twitter API keys or incurring OpenRouter costs.

**Contributing model:** Plugins serve as the primary extension point to keep the core clean.

## 10. What We Deliberately Left Out

- **No built-in AI API keys:** Users bring their own keys. We don't markup API costs.
- **No analytics SaaS integration:** Raw data lives in your PostgreSQL database. Query it however you want.
- **No social account marketplace:** We focus on the pipeline, not account brokering.
- **No content calendar AI:** (Coming in the roadmap) Currently, scheduling is explicit.
- **No Instagram/YouTube (yet):** The API complexity and media handling requirements outweigh the immediate value for a text-first pipeline.

## 11. Comparison with Alternatives

| Feature | social-engine | Buffer | Hootsuite | Typefully | Custom Bot |
|---|---|---|---|---|---|
| **AI content generation** | ✅ Multi-agent | ❌ | ❌ | ✅ Basic | ⚠️ DIY |
| **Open source** | ✅ MIT | ❌ | ❌ | ❌ | ✅ |
| **Self-hostable** | ✅ Docker | ❌ | ❌ | ❌ | ✅ |
| **Long-term memory** | ✅ pgvector | ❌ | ❌ | ❌ | ❌ |
| **Quality gate** | ✅ 7-metric | ❌ | ❌ | ❌ | ❌ |
| **Pluggable LLMs** | ✅ Any provider | ❌ | ❌ | ❌ | ⚠️ DIY |
| **Research pipeline** | ✅ HN/Reddit/RSS | ❌ | ❌ | ❌ | ❌ |
| **Analytics learning** | ✅ Built-in | ✅ Basic | ✅ Basic | ❌ | ❌ |

## 12. Known Tradeoffs

- **Complexity vs. Simplicity:** Clean architecture adds more files and boilerplate. The tradeoff is worth it for long-term testability and decoupled agent iteration.
- **pgvector vs. Dedicated Vector DB:** We trade the hyper-scale capabilities of Pinecone for the massive convenience of a single database. For 99% of social media use cases, pgvector is more than fast enough.
- **Dramatiq vs. Celery:** Dramatiq has a smaller ecosystem than Celery, but offers a vastly superior developer experience and type safety.
- **OpenRouter dependency:** Relying on one gateway is a single point of failure. This is mitigated by our abstract AI interface—swapping to direct OpenAI or Anthropic SDKs requires modifying only one provider class.
