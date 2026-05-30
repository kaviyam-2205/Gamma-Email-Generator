# ============================================================
# agents.py
# Gamma Email Generator — Real CrewAI Implementation
# ============================================================
# AGENT FLOW:
#   Agent 1 → Orchestrator      (analyzes & creates brief)
#   Agent 2 → Newsletter        (only if category=Newsletter)
#   Agent 3 → Promotion         (only if category=Promotion)
#   Agent 4 → Welcome           (only if category=Welcome)
#   Agent 5 → Validator         (reviews & finalizes output)
# ============================================================

from crewai import Agent, Task, Crew, Process

# ─────────────────────────────────────────
# LLM SETUP — Ollama + llama3.2
# ─────────────────────────────────────────
llm = "ollama/llama3.2"

# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────
def build_training_block(examples: list) -> str:
    if not examples:
        return "No training examples available."
    block = ""
    for i, ex in enumerate(examples, 1):
        block += f"\n--- Example {i} ---\n"
        block += f"INPUT:  {ex['input_mail'][:300]}\n"
        block += f"OUTPUT: {ex['output_mail'][:300]}\n"
    return block


# ─────────────────────────────────────────
# MAIN CREW RUNNER
# ─────────────────────────────────────────
def run_email_crew(
    input_mail: str,
    category: str,
    sub_category: str,
    training_examples: list
) -> str:

    training_block = build_training_block(training_examples)

    # ─────────────────────────────────────
    # AGENT 1 — ORCHESTRATOR
    # ─────────────────────────────────────
    orchestrator = Agent(
        role="Email Orchestrator",
        goal="Analyze the raw email and create a short brief for the specialist.",
        backstory="""You are the Lead Email Coordinator at Gamma.
You analyze raw emails and create a short 2 sentence brief.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # ─────────────────────────────────────
    # AGENT 2 — NEWSLETTER SPECIALIST
    # ─────────────────────────────────────
    newsletter_agent = Agent(
        role="Newsletter Email Specialist",
        goal="Write a short clean Gamma-branded Newsletter email.",
        backstory="""You are Gamma's Newsletter Email Specialist.
You write short, professional, brand-aligned newsletter emails.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # ─────────────────────────────────────
    # AGENT 3 — PROMOTION SPECIALIST
    # ─────────────────────────────────────
    promotion_agent = Agent(
        role="Promotion Email Specialist",
        goal="Write a short clean Gamma-branded Promotion email.",
        backstory="""You are Gamma's Promotion Email Specialist.
You write short, persuasive, brand-aligned promotional emails.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # ─────────────────────────────────────
    # AGENT 4 — WELCOME SPECIALIST
    # ─────────────────────────────────────
    welcome_agent = Agent(
        role="Welcome Email Specialist",
        goal="Write a short clean Gamma-branded Welcome email.",
        backstory="""You are Gamma's Welcome Email Specialist.
You write short, warm, brand-aligned welcome emails.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # ─────────────────────────────────────
    # AGENT 5 — VALIDATOR
    # ─────────────────────────────────────
    validator = Agent(
        role="Brand Quality Validator",
        goal="Clean and validate the generated email. Remove all extra content.",
        backstory="""You are Gamma's Brand Quality Validator.
You clean up emails — remove notes, alternatives, meta-commentary.
You return only the final clean ready-to-send email.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # ─────────────────────────────────────
    # TASK 1 — ORCHESTRATOR TASK
    # ─────────────────────────────────────
    task_orchestrate = Task(
        description=f"""
Analyze this raw email in 2 sentences only.

Category     : {category}
Sub-Category : {sub_category}
Raw Email    : {input_mail}

Return a 2 sentence brief. Nothing else.
        """,
        agent=orchestrator,
        expected_output="A 2 sentence brief describing the email intent."
    )

    # ─────────────────────────────────────
    # TASK 2 — SPECIALIST TASK
    # ─────────────────────────────────────
    specialist_map = {
        "Newsletter": (newsletter_agent, "informative, engaging, community-focused"),
        "Promotion":  (promotion_agent,  "persuasive, urgent, CTA-driven"),
        "Welcome":    (welcome_agent,    "warm, friendly, onboarding-focused")
    }

    selected_agent, tone_hint = specialist_map.get(
        category,
        (newsletter_agent, "professional and brand-aligned")
    )

    task_generate = Task(
        description=f"""
Write a short Gamma-branded {category} email.

TRAINING EXAMPLES (learn tone only — do not copy):
{training_block}

Category     : {category}
Sub-Category : {sub_category}
Tone         : {tone_hint}
Raw Email    : {input_mail}

STRICT RULES:
- Maximum 120 words
- Start with greeting: "Hi there 👋," or "Dear [Name],"
- End with: "The Gamma Team"
- No explanations or notes
- No alternative versions
- No meta-commentary
- Return ONLY the final email text
        """,
        agent=selected_agent,
        expected_output="A clean Gamma-branded email under 120 words."
    )

    # ─────────────────────────────────────
    # TASK 3 — VALIDATOR TASK
    # ─────────────────────────────────────
    task_validate = Task(
        description=f"""
Clean this {category} email strictly.

REMOVE:
- Any notes or explanations
- Any alternative versions
- Any meta-commentary
- Any text after "The Gamma Team"
- Any phrases like "Note:", "Alternatively:", "Dear Specialist"

KEEP:
- The greeting
- The main email body
- The sign-off: "The Gamma Team"

Return ONLY the final clean email. Nothing else.
        """,
        agent=validator,
        expected_output="A clean ready-to-send Gamma email with no extra content."
    )

    # ─────────────────────────────────────
    # CREW — ASSEMBLE & RUN
    # ─────────────────────────────────────
    crew = Crew(
        agents=[orchestrator, selected_agent, validator],
        tasks=[task_orchestrate, task_generate, task_validate],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return str(result)
    