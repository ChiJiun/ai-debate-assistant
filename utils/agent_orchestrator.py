from __future__ import annotations

from collections.abc import Callable, Iterable

from skills.closing import analyze_closing, generate_closing
from skills.constructive import analyze_constructive, generate_constructive
from skills.defense import generate_defense
from skills.questioning import generate_questioning
from skills.research import run_research_workflow
from utils.debate_memory import DebateMemory
from utils.openai_client import LLMConfig
from utils.trace import TraceEvent, make_trace


WorkflowLogger = Callable[[TraceEvent], None]


STEP_LABELS = {
    "research": "查詢資料",
    "constructive": "生成申論",
    "constructive_analysis": "分析申論",
    "questioning": "生成質詢",
    "defense": "生成答辯",
    "closing": "生成結辯",
    "closing_analysis": "分析結辯",
}


DEFAULT_WORKFLOW_STEPS = [
    "research",
    "constructive",
    "constructive_analysis",
    "questioning",
    "defense",
    "closing",
    "closing_analysis",
]


def run_debate_workflow(
    memory: DebateMemory,
    selected_steps: Iterable[str],
    llm_config: LLMConfig,
    tavily_key: str,
    time_range: str,
    search_depth: str,
    logger: WorkflowLogger | None = None,
) -> DebateMemory:
    for step in selected_steps:
        label = STEP_LABELS.get(step, step)
        _log(logger, label, "running", "開始執行")
        try:
            if step == "research":
                queries, search_material, sources_text, summary = run_research_workflow(
                    memory.motion,
                    memory.side,
                    memory.manual_material,
                    llm_config,
                    tavily_key,
                    time_range=time_range,
                    search_depth=search_depth,
                )
                memory.search_queries = queries
                memory.search_material = search_material
                memory.sources_text = sources_text
                memory.research_summary = summary
                _log(logger, label, "done", "已完成搜尋與資料整理")
            elif step == "constructive":
                memory.constructive = generate_constructive(
                    memory.motion,
                    memory.side,
                    memory.time_limit,
                    memory.research_material(),
                    llm_config,
                )
                _log(logger, label, "done", "已產生我方申論稿")
            elif step == "constructive_analysis":
                memory.constructive_analysis = analyze_constructive(
                    memory.motion,
                    memory.side,
                    memory.constructive,
                    memory.research_material(),
                    llm_config,
                )
                _log(logger, label, "done", "已完成申論分析")
            elif step == "questioning":
                memory.questioning = generate_questioning(
                    memory.motion,
                    memory.side,
                    memory.opponent_constructive,
                    memory.all_materials(),
                    llm_config,
                )
                _log(logger, label, "done", "已產生質詢問題")
            elif step == "defense":
                defense_question = _default_defense_question(memory)
                memory.defense = generate_defense(
                    memory.motion,
                    memory.side,
                    defense_question,
                    memory.all_materials(),
                    memory.defense_dialogue,
                    llm_config,
                )
                _log(logger, label, "done", "已產生答辯素材")
            elif step == "closing":
                memory.closing = generate_closing(
                    memory.motion,
                    memory.side,
                    memory.time_limit,
                    memory.all_materials(),
                    llm_config,
                )
                _log(logger, label, "done", "已產生結辯稿")
            elif step == "closing_analysis":
                memory.closing_analysis = analyze_closing(
                    memory.motion,
                    memory.side,
                    memory.closing,
                    memory.all_materials(),
                    llm_config,
                )
                _log(logger, label, "done", "已完成結辯分析")
            else:
                _log(logger, label, "skipped", "未知步驟，已略過")
        except Exception as exc:
            _log(logger, label, "failed", str(exc))
            raise
    return memory


def _default_defense_question(memory: DebateMemory) -> str:
    if memory.questioning.strip():
        first_question = next((line.strip("- ").strip() for line in memory.questioning.splitlines() if line.strip()), "")
        if first_question:
            return first_question
    return f"請針對辯題「{memory.motion}」模擬對方最可能提出的一個質詢問題。"


def _log(logger: WorkflowLogger | None, step: str, status: str, message: str) -> None:
    if logger:
        logger(make_trace(step, status, message))
