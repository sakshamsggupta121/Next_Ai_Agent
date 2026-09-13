import os
from dotenv import load_dotenv
from anakin import Anakin

load_dotenv()


class DecisionAgent:

    def __init__(self):
        api_key = os.getenv("ANAKIN_API_KEY")

        if not api_key:
            raise ValueError(
                "ANAKIN_API_KEY is missing in .env file"
            )

        self.client = Anakin(api_key=api_key)

    def research(self, student):

        query = f"""
You are an academic decision research agent.

Analyze this student profile:

Education Level: {student['class_level']}
Stream: {student['stream']}
Interests: {student['interest']}
Preferred Location: {student['location']}
Annual Budget: INR {student['budget']}
Career Goal: {student['career_goal']}

Research current suitable colleges and courses for this student.

Compare:
1. Course relevance
2. Career relevance
3. Location
4. Approximate annual fees
5. Important admission considerations

Prefer official college sources when available.

If the exact budget has no suitable option, suggest nearby alternatives
and clearly mention that the student should verify current fees and admission
details from official sources.

Give a concise recommendation and include useful source links.
"""

        result = self.client.agentic_search(
            query,
            depth="standard"
        )

        return result