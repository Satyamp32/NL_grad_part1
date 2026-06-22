# Spotify Discovery User Research Kit (Phase 2)

This kit provides the target recruitment screener, a time-boxed semi-structured interview script, empathy mapping grids, and a user journey mapping framework to conduct primary user research validating our findings from Phase 1.

---

## 📋 1. Recruitment Screener Questionnaire
**Goal:** Recruit **5–6 Spotify users** representing our prioritized segments: **Active Curators** (highly sensitive to repetition) and **Utility Listeners** (affected by context contamination).

### Section 1: Demographics & Usage Basics
1.  **Which music streaming platform do you use as your primary service?**
    *   [ ] Spotify (Proceed)
    *   [ ] Apple Music (Terminate)
    *   [ ] YouTube Music (Terminate)
    *   [ ] Other (Terminate)
2.  **How long have you been using Spotify?**
    *   [ ] Less than 6 months (Terminate - want established listeners)
    *   [ ] 6 months to 2 years (Qualifies)
    *   [ ] More than 2 years (Qualifies)
3.  **Which subscription tier do you currently use?**
    *   [ ] Free / Ad-Supported (Accept up to 2 for comparison)
    *   [ ] Premium / Paid (Target: 4-5 interviewees)

### Section 2: Behavioral Segmentation Gating
4.  **How would you describe your playlist curation habits? (Select best fit)**
    *   [ ] "I rarely make playlists; I rely on Spotify-generated mixes (Daily Mix, Discover Weekly, DJ)." -> **[Segment: Passive Lean-Back]** (Accept max 1)
    *   [ ] "I actively curate my own custom playlists, adding/removing tracks regularly." -> **[Segment: Active Curator]** (Target: 3-4)
    *   [ ] "I use Spotify to play sleep sounds, focus tracks, or children's audio for specific activities." -> **[Segment: Utility Listener]** (Target: 1-2)
5.  **How often do you use the Shuffle or Smart Shuffle features?**
    *   [ ] Daily / Almost every session (High priority)
    *   [ ] Weekly / Occasionally (Qualifies)
    *   [ ] Never (Terminate if recruiting for Shuffle research)

### Section 3: Friction Screener
6.  **How often do you feel that Spotify's recommendations or shuffles are highly repetitive (e.g. playing the same songs on loop)?**
    *   [ ] Constantly / Very Frequently (Qualifies - High Pain)
    *   [ ] Occasionally (Qualifies)
    *   [ ] Rarely / Never (Terminate - need users experiencing discovery friction)
7.  **Have you ever had utility listening sessions (e.g. lofi for work, sleep noise, kid streams) ruin or contaminate your daily recommendations?**
    *   [ ] Yes (High value for Utility Listener segment)
    *   [ ] No / Not applicable (Qualifies for other segments)

---

## 🎙️ 2. Semi-Structured Discussion Guide (30 Mins)

### Introduction & Consent (3 mins)
> *"Hi [Name], thank you for joining today. I am conducting research on how Spotify users discover new music and manage their listening routines. Our conversation will take about 30 minutes. There are no right or wrong answers; I want to understand your real day-to-day habits. May I have your permission to record this session for transcription purposes? The recording will be stored securely and used only for analysis."*

### Warm-Up: Listening Habits (5 mins)
*   Describe a typical weekday for you. When do you listen to Spotify, and on what devices (phone, laptop, car, smart speaker)?
*   What kinds of music or audio do you listen to during these different times?
*   How do you decide what to play when you open the app? (e.g. search, select a saved playlist, let the AI DJ play, hit a Daily Mix)?

### Deep-Dive: Discovery Friction & Repetition (10 mins)
*   Walk me through the last time you wanted to find something *new* or *different* to listen to. What steps did you take? How did it feel?
*   Have you noticed any repetition in the music Spotify recommends to you? Can you describe a specific time you felt frustrated by this?
*   *For Curators:* When you turn on **Smart Shuffle** in your custom playlists, what happens? How does the algorithm choose recommended tracks? Do you feel it matches your taste?
*   *For Utility Listeners:* Do you use Spotify for focus, sleep, or shared device situations? How do these sessions affect your music recommendations afterwards? How do you handle that?
*   When Spotify recommends a song you dislike, what do you do (skip, thumbs down, ignore)? What do you expect Spotify to do with that feedback? What actually happens?

### Workarounds & Alternative Platforms (7 mins)
*   When Spotify’s algorithms fail to show you fresh music, how do you find new artists? (e.g. recommendations from friends, Shazam, YouTube, TikTok, Reddit, live shows)?
*   Why do you go to those other sources instead of staying on Spotify? What do they offer that Spotify doesn't?
*   Have you tried to manually "train" or adjust Spotify's algorithms? If so, what did you do, and did it work?

### Concept Validation (5 mins)
*We will pitch three conceptual AI-native features to validate their user value:*
1.  **Opportunity A (The Taste Exclusion Toggle):** *"Imagine a switch you can toggle before playing sleep sounds or lofi beats that completely hides that session from training your recommendation algorithm. How would that change your listening routines?"*
2.  **Opportunity B (The Discovery Risk Slider):** *"What if you had a slider on your mixes from 'Comfortable/Familiar' to 'Wild Exploration' where you could force the system to play 100% new, obscure music? How and when would you use this?"*
3.  **Opportunity C (Conversational PM Agent):** *"Imagine instead of typing keywords in the search bar, you could talk to an AI curator and describe a vibe (e.g. 'indie songs that feel like an autumn walk in Paris'). You could chat, refine, and save the playlist immediately. How does that compare to how you search today?"*

### Wrap-Up & Closing (2 mins)
*   Is there anything else about how you search, play, or discover music on Spotify that we didn’t cover today?
*   Thank you so much for your time and valuable insights!

---

## 🎨 3. Synthesis & Empathy Mapping templates

After conducting each interview, transfer transcript notes into this **Empathy Map** to align user observations:

```
┌───────────────────────────────────────┬───────────────────────────────────────┐
│                 SAYS                  │                THINKS                 │
│  (Direct verbatim quotes from the     │  (Beliefs, assumptions, and implicit  │
│   interviewee)                        │   thoughts they might not state)      │
│                                       │                                       │
│  - "Smart Shuffle plays the same 10   │  - "I think Spotify is pushing cheap  │
│     songs. I feel like it ignores me."│     royalty tracks to save money."    │
│  - "I have to use private session."   │  - "I'm afraid to play sleep sounds   │
│                                       │     because it will break my feed."   │
├───────────────────────────────────────┼───────────────────────────────────────┤
│                 DOES                  │                 FEELS                 │
│  (Observable behaviors, workarounds,   │  (Emotional states experienced during  │
│   and actions they take)              │   interaction)                        │
│                                       │                                       │
│  - Skips songs within 3 seconds.      │  - Bored by repetitive comfort tracks.│
│  - Uses YouTube to crawl niche lists. │  - Frustrated by lack of negative    │
│  - Manually deletes search history.   │     algorithmic controls.             │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

### Insight Log Template

| User ID | Key Quote | Pain Point Category | Validated Opportunity | Severity (1-5) |
| :---: | :--- | :--- | :--- | :---: |
| **U01** | *"If I play one focus playlist, my Discover Weekly is ruined for a month."* | Context Contamination | Taste Exclusion Toggle | 5/5 |
| **U02** | *"Smart Shuffle is a closed circle. I hear the same songs on rotation."* | Shuffle Dissatisfaction | True Random Toggle | 4/5 |

---

## 🗺️ 4. User Journey Mapping Framework: "The Discovery Loop"

Use this journey mapping outline to locate exactly where discovery breakdown happens during a listening session:

```
          1. TRIGGER ──────► 2. ENTRY ──────► 3. EXPLORE ──────► 4. EVALUATE ──────► 5. ACTION ──────► 6. RETENTION
          (User wants        (Opens app,      (Browses mixes,   (Listens to        (Saves track,      (Tracks play
           fresh music)       navigates)       shuffles list)    recommendation)    adds to queue)     in future)
```

### Journey Stages Breakdown

#### 1. Trigger (Motivation)
*   **User Goal:** Wants to change mood, find background track, or update a playlist.
*   **Friction:** High cognitive barrier to start the exploration process.
*   **User Thought:** *"I'm tired of my usual list, I need something new."*

#### 2. Entry (Navigation)
*   **User Goal:** Finds a discovery path in the UI (Search tab, Discover Weekly, Home Feed).
*   **Friction:** UI is crowded with podcasts, audiobooks, and comfort tiles.
*   **User Thought:** *"Where should I click to find actual new recommendations?"*

#### 3. Explore (Curation Selection)
*   **User Goal:** Plays a recommended playlist, turns on Smart Shuffle, or starts a Song Radio.
*   **Friction:** First few tracks are confort/liked songs; recommendations feel generic.
*   **User Thought:** *"Why is this radio station playing songs I already liked?"*

#### 4. Evaluate (Listening / Auditing)
*   **User Goal:** Evaluates recommendations; decides whether to skip or listen.
*   **Friction:** Repetition forces constant manual skipping, breaking focus.
*   **User Thought:** *"I've skipped this artist three times, why are they playing them again?"*

#### 5. Action (Curation Decision)
*   **User Goal:** Saves a discovered song or queues it.
*   **Friction:** Brittle queue management (accidental click wipes out exploration trail).
*   **User Thought:** *"Ah! I clicked the wrong track and lost my whole queue!"*

#### 6. Retention (Algorithmic Update)
*   **User Goal:** The system updates preference vectors to lock in this new taste.
*   **Friction:** Single focus sessions contaminate long-term taste profile.
*   **User Thought:** *"Now my feeds are filled with lofi focus music, I regret playing that."*
