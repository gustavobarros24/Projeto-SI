import logging

from typing import Optional

from pydantic import BaseModel, Field

from domains.anamnesis.router import RouteDecision
from domains.anamnesis.state import AnamnesisSessionState, Diagnosis, AnamnesisFinalReport, AnamnesisFeedback, Symptom
from domains.anamnesis.prompts.evaluator.evaluate_question import create_evaluate_question_system_prompt, create_evaluate_question_user_prompt
from domains.anamnesis.prompts.evaluator.final_report import create_final_report_system_prompt, create_final_report_user_prompt
from domains.anamnesis.prompts.evaluator.evaluate_diagnosis import create_evaluate_diagnosis_system_prompt, create_evaluate_diagnosis_user_prompt
from core.evaluator import IEvaluator, InputEvaluation, get_grade, MAX_POINTS
from llm.translator import Language, translate_model
from utils.messages import get_last_human_message
from utils.helpers import node, MAX_IRRELEVANT_MSGS
from domains.anamnesis.scoring import (
    DiagnosisAccuracy,
    get_diagnosis_points,
    get_symptom_match_pts,
    get_tries_pts,
)
from llm.models import create_llm
from llm.config import Config
from rag.integration import augment_with_rag
from rag.query import build_anamnesis_final_report_query


log = logging.getLogger(__name__)

class QuestionEvaluation(InputEvaluation):
    symptom_targeted: Optional[str] = Field(None, description="The single symptom from all possible symptoms that this question targets, if applicable.")

class DiagnosisAttempt(BaseModel):
    diagnosis: str = Field(..., description="The concrete diagnosis targeted.")
    accuracy: DiagnosisAccuracy = Field(..., description="Level of accuracy of the proposed diagnostic hypothesis.")

class TranslatedReportFields(BaseModel):
    feedback: AnamnesisFeedback
    all_symptoms: list[str] 
    hidden_diagnosis: str 
    covered_symptoms: list[str]

class AnamnesisEvaluator(IEvaluator[AnamnesisSessionState]):
    @node(AnamnesisSessionState)
    def evaluate_input(self, state: AnamnesisSessionState) -> AnamnesisSessionState:
        log.info("Evaluating anamnesis question...")
        last_question = get_last_human_message(state.messages)
        system_prompt = create_evaluate_question_system_prompt(state)
        user_prompt = create_evaluate_question_user_prompt(state)

        medical_llm = create_llm(Config.MEDICAL_MODEL)
        scorer = medical_llm.with_structured_output(QuestionEvaluation)
        evaluation: QuestionEvaluation = scorer.invoke(
            [system_prompt, user_prompt]
        )

        log.info(f"Question evaluation anamnesis: {evaluation}...")
        if evaluation.is_relevant:
            log.info("Relevant question...")
            state.consecutive_irrelevant_count = 0
            if evaluation.symptom_targeted:
                log.info(f"Found symptom: {evaluation.symptom_targeted}...")
                if not state.evaluation_sheet.already_covered(evaluation.symptom_targeted):
                    symptom = Symptom(question_id=last_question.id, symptom=evaluation.symptom_targeted)
                    state.evaluation_sheet.covered_symptoms.append(symptom)
                else:
                    log.info(f"Symptom already covered: {evaluation.symptom_targeted}...")
            else:
                log.info("No symptom targeted...")
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
                state.route_decision = RouteDecision.PATIENT
    
        return state

    @node(AnamnesisSessionState)
    def evaluate_diagnosis_attempt(self, state: AnamnesisSessionState) -> AnamnesisSessionState:
        log.info("Evaluating diagnosis attempt...")
        last_attempt = get_last_human_message(state.diagnosis_attempts)
        system_prompt = create_evaluate_diagnosis_system_prompt(state)
        user_prompt = create_evaluate_diagnosis_user_prompt(state)

        medical_llm = create_llm(Config.MEDICAL_MODEL)
        scorer = medical_llm.with_structured_output(DiagnosisAttempt)
        diagnosis: DiagnosisAttempt = scorer.invoke(
            [system_prompt, user_prompt]
        )
        log.info(f"Diagnosis evaluation: {diagnosis}...")

        state.evaluation_sheet.diagnosis.append(Diagnosis(
            diagnosis_id=last_attempt.id,
            diagnosis=diagnosis.diagnosis,
            accuracy=diagnosis.accuracy,
        ))
        state.last_input_was_attempt = False

        if diagnosis.accuracy == DiagnosisAccuracy.EXACT:
            log.info(f"Correct diagnosis: {last_attempt.content}...")
            state.route_decision = RouteDecision.FINAL_REPORT
        elif state.diagnosis_attempts_num >= state.max_attempts:
            log.info("MAX diagnosis attempts reached: routing to final report...")
            state.route_decision = RouteDecision.FINAL_REPORT
        else:
            log.info(f"Diagnosis attempt {state.diagnosis_attempts_num}/{state.max_attempts}: continuing...")
            state.route_decision = RouteDecision.TUTOR_WRONG_DIAGNOSIS

        return state

    @node(AnamnesisSessionState)
    def generate_final_report(
        self, state: AnamnesisSessionState
    ) -> AnamnesisSessionState:
        log.info("Generating anamnesis final report...")
        evaluation = state.evaluation_sheet
        diagnosis = [diag.accuracy for diag in evaluation.diagnosis]
        best_diagnosis = DiagnosisAccuracy.most_accurate(diagnosis)
        diagnosis_points = get_diagnosis_points(best_diagnosis)
        tries_points = get_tries_pts(state.diagnosis_attempts_num)
        symptoms_num = len(state.all_symptoms)
        covered_num = state.evaluation_sheet.covered_symptoms_num
        symptom_points = get_symptom_match_pts(covered_num, symptoms_num)

        total_points = diagnosis_points + tries_points + symptom_points
        grade = get_grade(total_points)
        log.info(f"Total points: {total_points} (grade: {grade}, diagnosis_points: {diagnosis_points}, tries_points: {tries_points}, symptom_points: {symptom_points})")

        system_prompt = create_final_report_system_prompt(state, total_points, grade)
        user_prompt = create_final_report_user_prompt(state)

        system_prompt, sources = augment_with_rag(
            system_prompt, build_anamnesis_final_report_query(state)
        )

        log.info("Creating feedback for anamnesis...")
        medical_llm = create_llm(Config.MEDICAL_MODEL)
        reporter = medical_llm.with_structured_output(AnamnesisFeedback)
        feedback: AnamnesisFeedback = reporter.invoke(
            [system_prompt, user_prompt]
        )
        fields = TranslatedReportFields(
            feedback=feedback,
            hidden_diagnosis=state.hidden_diagnosis, 
            all_symptoms=state.all_symptoms, 
            covered_symptoms=state.student_covered_symptoms
        )
        if state.language != Language.EN:
            try:
                log.info(f"Normalizing fields: {fields}...")
                fields = translate_model(fields, state.language, llm=medical_llm)
                log.info(f"Translated fields: {fields}...")
            except Exception as e:
                log.info(f"Translation failed, back to english: {e}...")

        final_report = AnamnesisFinalReport(
            feedback=fields.feedback,
            total_points=total_points,
            max_points=MAX_POINTS,
            grade=grade,
            hidden_diagnosis=fields.hidden_diagnosis,
            all_symptoms=fields.all_symptoms,
            covered_symptoms_num=covered_num,
            all_symptoms_num=symptoms_num,
            covered_symptoms=fields.covered_symptoms,
            source_documents=sources,
        )

        log.info(f"Final report: {final_report}...")
        state.final_report = final_report
        state.session_summary = "ended"
        return state
