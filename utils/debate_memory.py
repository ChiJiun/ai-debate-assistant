from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass
class DebateMemory:
    motion: str
    side: str
    time_limit: str
    manual_material: str = ""
    search_queries: str = ""
    search_material: str = ""
    research_summary: str = ""
    sources_text: str = ""
    constructive: str = ""
    constructive_analysis: str = ""
    opponent_constructive: str = ""
    questioning: str = ""
    question_simulation: str = ""
    question_dialogue: str = ""
    defense: str = ""
    defense_dialogue: str = ""
    closing: str = ""
    closing_analysis: str = ""

    @classmethod
    def from_state(cls, state: Mapping[str, object], time_limit: str) -> "DebateMemory":
        return cls(
            motion=str(state.get("motion", "")),
            side=str(state.get("side", "")),
            time_limit=time_limit,
            manual_material=str(state.get("manual_material", "")),
            search_queries=str(state.get("search_queries", "")),
            search_material=str(state.get("search_material", "")),
            research_summary=str(state.get("research_summary", "")),
            sources_text=str(state.get("sources_text", "")),
            constructive=str(state.get("constructive", "")),
            constructive_analysis=str(state.get("constructive_analysis", "")),
            opponent_constructive=str(state.get("opponent_constructive", "")),
            questioning=str(state.get("questioning", "")),
            question_simulation=str(state.get("question_simulation", "")),
            question_dialogue=str(state.get("question_dialogue", "")),
            defense=str(state.get("defense", "")),
            defense_dialogue=str(state.get("defense_dialogue", "")),
            closing=str(state.get("closing", "")),
            closing_analysis=str(state.get("closing_analysis", "")),
        )

    def research_material(self) -> str:
        return self._join(
            self.manual_material,
            self.search_material,
            self.research_summary,
        )

    def all_materials(self) -> str:
        labeled_parts = {
            "手動輸入資料": self.manual_material,
            "查詢資料": self.search_material,
            "資料整理": self.research_summary,
            "我方申論": self.constructive,
            "申論分析": self.constructive_analysis,
            "對方申論": self.opponent_constructive,
            "質詢設計": self.questioning,
            "質詢模擬": self.question_simulation,
            "質詢多輪紀錄": self.question_dialogue,
            "答辯內容": self.defense,
            "答辯多輪紀錄": self.defense_dialogue,
            "結辯稿": self.closing,
            "結辯分析": self.closing_analysis,
        }
        return self._join(
            *(f"## {label}\n{value}" for label, value in labeled_parts.items() if value.strip())
        )

    def to_state_updates(self) -> dict[str, str]:
        return {
            "search_queries": self.search_queries,
            "search_material": self.search_material,
            "research_summary": self.research_summary,
            "sources_text": self.sources_text,
            "constructive": self.constructive,
            "constructive_analysis": self.constructive_analysis,
            "questioning": self.questioning,
            "defense": self.defense,
            "closing": self.closing,
            "closing_analysis": self.closing_analysis,
        }

    @staticmethod
    def _join(*parts: str) -> str:
        return "\n\n".join(part for part in parts if part.strip())
