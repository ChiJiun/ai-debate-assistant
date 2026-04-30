from __future__ import annotations

import json
from typing import Mapping


DEFAULT_SKILL_TEMPLATES: dict[str, str] = {
    "motion_analysis": """
Generate a motion analysis with these sections:
1. Key term definitions
2. Affirmative burden
3. Negative burden
4. Main clash points
5. Judging criteria
""".strip(),
    "arguments": """
Generate argument materials.

For affirmative, provide 2 to 3 main arguments. For each:
- Argument name
- Reasoning
- Possible evidence direction
- Possible weakness

For negative, provide 2 to 3 main arguments. For each:
- Argument name
- Reasoning
- Possible evidence direction
- Possible weakness

If the user selected only one side, still include a concise opponent section for preparation.
""".strip(),
    "constructive": """
Generate full constructive speeches.

Include affirmative constructive and negative constructive unless the selected side is only one side;
in that case, make the selected side detailed and the other side shorter.

Each speech should include:
- Opening position
- Definitions
- Main standard
- 2 to 3 arguments
- Evidence or examples
- Impact
- Preemptive defense

Match the length to the selected time limit.
""".strip(),
    "cross_examination": """
Generate cross-examination questions.

For affirmative questioning negative:
- Attack negative assumptions
- Ask for standards
- Force concession
- Expose lack of alternative

For negative questioning affirmative:
- Attack definition
- Attack feasibility
- Attack cost
- Attack evidence
- Expose side effects

For each question include:
- Question
- Expected answer
- Follow-up question
- Purpose
""".strip(),
    "defense": """
Generate answers to likely questions for both affirmative and negative preparation.

Each answer should include:
- Question type
- Defense strategy
- 15 to 30 second answer
- Pivot sentence
""".strip(),
    "closing": """
Generate closing speeches based on the previous materials below.

Previous materials:
{previous_materials}

Closing speeches should include:
- Main clash summary
- Opponent concessions
- Why our side wins
- Best evidence or reasoning
- Final conclusion

Include affirmative and negative closings unless the selected side is only one side;
in that case, make the selected side detailed and the other side shorter.
""".strip(),
}


def get_skill_template(skill_key: str, custom_templates: Mapping[str, str] | None = None) -> str:
    if custom_templates:
        custom_template = custom_templates.get(skill_key, "").strip()
        if custom_template:
            return custom_template
    return DEFAULT_SKILL_TEMPLATES[skill_key]


def templates_to_json(templates: Mapping[str, str]) -> str:
    return json.dumps(
        {
            "version": 1,
            "type": "debate-assistant-skill-templates",
            "skills": dict(templates),
        },
        ensure_ascii=False,
        indent=2,
    )


def templates_from_json(raw_json: str) -> dict[str, str]:
    payload = json.loads(raw_json)
    skills = payload.get("skills", payload)
    if not isinstance(skills, dict):
        raise ValueError("Skill template file must contain a JSON object.")

    valid_keys = set(DEFAULT_SKILL_TEMPLATES)
    return {
        key: str(value)
        for key, value in skills.items()
        if key in valid_keys
    }
