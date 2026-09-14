import logging

from typing import Optional 

from pydantic import BaseModel, Field

from core.evaluator import IEvaluator, InputEvaluation, get_grade, MAX_POINTS
from domains.xray.prompts.evaluator.evaluate_finding import create_evaluate_finding_user_prompt, create_evaluate_finding_system_prompt
from domains.xray.prompts.evaluator.evaluate_impression import create_evaluate_impression_user_prompt, create_evaluate_impression_system_prompt
from domains.xray.prompts.evaluator.final_report import create_final_report_system_prompt, create_final_report_user_prompt
from domains.xray.router import RouteDecision
from domains.xray.state import Finding, Impression, XRaySessionState, XRayFeedback, XRayFinalReport
from llm.translator import Language, translate_model
from utils.messages import get_last_human_message
from utils.helpers import MAX_IRRELEVANT_MSGS, node
from domains.xray.scoring import (
    get_tries_pts,
    get_impression_pts,
    get_findings_pts,
    get_incorrect_findings_pts,
    ImpressionAccuracy,
)
from llm.models import create_llm
from llm.config import Config
from rag.integration import augment_with_rag
from rag.query import build_xray_final_report_query


log = logging.getLogger(__name__)


class FindingEvaluation(InputEvaluation):
    is_correct: bool = Field(..., description="True if the finding matches one in the ground truth, False if it contradicts or is absent from it.")
    finding: Optional[str] = Field(None, description="The finding extracted from the student's message, normalized to a concise clinical term. None if no finding was identified.")

class ImpressionEvaluation(BaseModel):
    impression: str = Field(..., description="The concrete impression.")
    accuracy: ImpressionAccuracy = Field(..., description="Level of accuracy of the proposed impression.")

class TranslatedReportFields(BaseModel):
    feedback: XRayFeedback
    ground_truth_findings: list[str]
    correct_impression: str
    correct_findings: list[str]
    incorrect_findings: list[str]

class XRayEvaluator(IEvaluator[XRaySessionState]):
    @node(XRaySessionState)
    def evaluate_input(self, state: XRaySessionState) -> XRaySessionState:
        log.info("Evaluating xray finding...")
        last_message = get_last_human_message(state.messages)
        system_prompt = create_evaluate_finding_system_prompt(state)
        user_prompt = create_evaluate_finding_user_prompt(state)

        medical_llm = create_llm(Config.MEDICAL_MODEL)
        scorer = medical_llm.with_structured_output(FindingEvaluation)
        evaluation: FindingEvaluation = scorer.invoke(
            [system_prompt, user_prompt]
        )

        log.info(f"Input evaluation: {evaluation}...")
        if evaluation.is_relevant:
            log.info("Relevant question...")
            state.consecutive_irrelevant_count = 0
            if evaluation.finding:
                log.info(f"Found a finding evaluation xray: {evaluation}...")
                if not state.evaluation_sheet.already_found(evaluation.finding):
                    finding = Finding(message_id=last_message.id, is_correct=evaluation.is_correct, finding=evaluation.finding)
                    state.evaluation_sheet.findings.append(finding)
                    log.info(f"All correct findings: {state.student_correct_findings}...")
                    log.info(f"All incorrect findings: {state.student_incorrect_findings}...")
                else:
                    log.info(f"Finding: {evaluation.finding} already recorded, skipping...")
            else:
                log.info("Not a finding...")
        else:
            log.info("Irrelevant question...")
            state.consecutive_irrelevant_count += 1
            log.info(
                f"Consecutive irrelevant count: {state.consecutive_irrelevant_count}..."
            )

            if state.consecutive_irrelevant_count >= MAX_IRRELEVANT_MSGS:
                log.info("Too many irrelevant questions, time for tutor...")
                state.route_decision = RouteDecision.TUTOR_OFF_TRACK
            else:
                state.route_decision = RouteDecision.TUTOR_RESPONSE

        return state

    @node(XRaySessionState)
    def evaluate_impression(self, state: XRaySessionState) -> XRaySessionState:
        log.info("Evaluating impression attempt...")
        last_attempt = get_last_human_message(state.impression_attempts)
        system_prompt = create_evaluate_impression_system_prompt(state)
        user_prompt = create_evaluate_impression_user_prompt(state)

        medical_llm = create_llm(Config.MEDICAL_MODEL)
        scorer = medical_llm.with_structured_output(ImpressionEvaluation)
        impression: ImpressionEvaluation = scorer.invoke(
            [system_prompt, user_prompt]
        )
        log.info(f"Impression evaluation: {impression}...")

        state.evaluation_sheet.impressions.append(Impression(
            attempt_id=last_attempt.id,
            impression=impression.impression,
            accuracy=impression.accuracy,
        ))
        state.last_input_was_attempt = False

        if impression.accuracy == ImpressionAccuracy.EXACT_MATCH or impression.accuracy == ImpressionAccuracy.CLINICALLY_EQUIVALENT:
            log.info(f"Correct impression: {last_attempt.content}...")
            state.route_decision = RouteDecision.FINAL_REPORT
        elif state.impression_attempts_num >= state.max_attempts:
            log.info("MAX impression attempts reached: routing to final report...")
            state.route_decision = RouteDecision.FINAL_REPORT
        else:
            log.info(f"Impression attempt {state.impression_attempts_num}/{state.max_attempts}: continuing...")
            state.route_decision = RouteDecision.TUTOR_WRONG_IMPRESSION

        return state

    @node(XRaySessionState)
    def generate_final_report(
        self, state: XRaySessionState
    ) -> XRaySessionState:
        log.info("Generating xray final report...")
        evaluation = state.evaluation_sheet
        impressions = [imp.accuracy for imp in evaluation.impressions]
        best_impression = ImpressionAccuracy.most_accurate(impressions)
        impression_points = get_impression_pts(best_impression)
        tries_points = get_tries_pts(state.impression_attempts_num)
        finding_points = get_findings_pts(evaluation.correct_findings_num, state.ground_truth_findings_num)
        incorrect_finding_points = get_incorrect_findings_pts(evaluation.incorrect_findings_num)

        total_points = max(0, impression_points + tries_points + finding_points + incorrect_finding_points)
        grade = get_grade(total_points)
        log.info(f"Total points: {total_points} (grade: {grade}, impression_points: {impression_points}, tries_points: {tries_points}, finding_points: {finding_points}, incorrect_finding_points: {incorrect_finding_points})")

        system_prompt = create_final_report_system_prompt(state, total_points, grade)
        user_prompt = create_final_report_user_prompt(state)

        system_prompt, sources = augment_with_rag(
            system_prompt, build_xray_final_report_query(state)
        )

        medical_llm = create_llm(Config.MEDICAL_MODEL)
        reporter = medical_llm.with_structured_output(XRayFeedback)
        feedback: XRayFeedback = reporter.invoke(
            [system_prompt, user_prompt]
        )
        fields = TranslatedReportFields(
            feedback=feedback,
            ground_truth_findings=state.ground_truth_findings, 
            correct_impression=state.impression, 
            correct_findings=state.student_correct_findings, 
            incorrect_findings=state.student_incorrect_findings
        )
        if state.language != Language.EN:
            try:
                log.info(f"Normalizing fields: {fields}...")
                fields = translate_model(fields, state.language, llm=medical_llm)
                log.info(f"Translated fields to {state.language}: {fields}...")
            except Exception as e:
                log.info(f"Error translating, backup english: {e}...")

        final_report = XRayFinalReport(
            feedback=fields.feedback,
            total_points=total_points,
            max_points=MAX_POINTS,
            grade=grade,
            ground_truth_findings=fields.ground_truth_findings,
            ground_truth_findings_num=state.ground_truth_findings_num,
            correct_impression=fields.correct_impression,
            correct_findings=fields.correct_findings,
            incorrect_findings=fields.incorrect_findings,
            source_documents=sources,
        )

        log.info(f"Final report: {final_report}...")
        state.final_report = final_report
        state.session_summary = "ended"
        return state
