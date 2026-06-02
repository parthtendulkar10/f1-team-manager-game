"""Prompt templates for AI-driven narrative generation."""


def personality_prompt(name: str, role: str, context: str) -> str:
    return (
        f"Create a grounded F1 personality for {name}, who is a {role}. "
        f"Use this context: {context}. Include management style, communication tone, risk profile, and hidden pressure points in 2-3 sentences."
    )


def event_prompt(state_summary: str) -> str:
    return (
        "Generate one realistic F1 internal event with tension and trade-offs. "
        "It can be driver dispute, engineering conflict, media scandal, sponsor pressure, or leak. "
        f"Base it on this state: {state_summary}. Keep it concise and actionable."
    )


def negotiation_prompt(candidate_name: str, candidate_tier: str, state_summary: str) -> str:
    return (
        f"Generate a negotiation scene with driver {candidate_name} ({candidate_tier}). "
        "Provide a short demand and concern linked to team performance and budget. "
        f"Team summary: {state_summary}."
    )


def consequence_prompt(decision: str, state_summary: str) -> str:
    return (
        f"Explain realistic immediate and medium-term consequences for this team decision: '{decision}'. "
        f"State context: {state_summary}. Respond in 3-4 short lines with balanced positive and negative effects."
    )


def race_commentary_prompt(state_summary: str, finish_position: int) -> str:
    return (
        f"Produce race commentary for a new F1 team finishing P{finish_position}. "
        f"Use this state context: {state_summary}. Include one tactical insight and one emotional beat."
    )


def sponsorship_prompt(state_summary: str) -> str:
    return (
        "Create a realistic sponsor interaction for an F1 team. "
        "Include a short sponsor demand and what they offer financially. "
        f"Context: {state_summary}."
    )
