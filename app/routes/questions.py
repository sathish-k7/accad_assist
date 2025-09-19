from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import time
import uuid
import asyncio
import logging
from datetime import datetime

from app.schemas.questions import (
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    CourseListResponse,
    ExamTypesResponse,
    QuestionHistoryResponse,
    CourseStatsResponse,
    CourseInfo,
    GeneratedQuestion,
    QuestionHistoryItem,
    QuestionType,
    ExamType,
    DifficultyLevel
)
from app.schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/questions", tags=["❓ Question Generator"])

courses_db = [
    CourseInfo(course_code="CS101", title="Introduction to Computer Science", credits=3, semester=1, level="undergraduate"),
    CourseInfo(course_code="CS201", title="Data Structures and Algorithms", credits=4, semester=3, level="undergraduate"),
    CourseInfo(course_code="CS301", title="Database Management Systems", credits=3, semester=5, level="undergraduate"),
    CourseInfo(course_code="MA101", title="Engineering Mathematics I", credits=4, semester=1, level="undergraduate"),
    CourseInfo(course_code="MA201", title="Engineering Mathematics II", credits=4, semester=2, level="undergraduate"),
    CourseInfo(course_code="PH101", title="Engineering Physics", credits=3, semester=1, level="undergraduate"),
    CourseInfo(course_code="EE101", title="Basic Electrical Engineering", credits=3, semester=2, level="undergraduate"),
    CourseInfo(course_code="ME101", title="Engineering Mechanics", credits=3, semester=2, level="undergraduate"),
]

question_history_db: List[QuestionHistoryItem] = []

@router.post("/generate", response_model=QuestionGenerationResponse)
async def generate_questions(request: QuestionGenerationRequest):
    start_time = time.time()
    
    try:
        logger.info(f"Generating {request.question_count} questions for {request.course_code} ({request.exam_type})")
        
        course = next((c for c in courses_db if c.course_code == request.course_code), None)
        if not course:
            raise HTTPException(
                status_code=404,
                detail=f"Course {request.course_code} not found in database"
            )
        
        questions = await _generate_questions_from_database(request, course)
        
        total_points = sum(q.points for q in questions)
        
        processing_time = time.time() - start_time
        
        history_item = QuestionHistoryItem(
            id=str(uuid.uuid4()),
            course_code=request.course_code,
            course_title=course.title,
            exam_type=request.exam_type,
            question_count=len(questions),
            created_at=datetime.now(),
            total_points=total_points
        )
        question_history_db.append(history_item)
        
        logger.info(f"Generated {len(questions)} questions in {processing_time:.2f}s")
        
        return QuestionGenerationResponse(
            success=True,
            message=f"Generated {len(questions)} questions successfully",
            data=questions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate questions: {str(e)}"
        )

@router.get("/courses", response_model=CourseListResponse)
async def get_available_courses():
    try:
        return CourseListResponse(
            success=True,
            message=f"Retrieved {len(courses_db)} available courses",
            courses=courses_db,
            total_count=len(courses_db)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving courses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve courses")

@router.get("/exam-types", response_model=ExamTypesResponse)
async def get_exam_types():
    return ExamTypesResponse(
        exam_types=[
            {"value": "cat1", "label": "CAT 1", "description": "Continuous Assessment Test 1"},
            {"value": "cat2", "label": "CAT 2", "description": "Continuous Assessment Test 2"},
            {"value": "fat", "label": "FAT", "description": "Final Assessment Test"}
        ],
        question_types=[
            {"value": "mcq", "label": "MCQ", "description": "Multiple choice (4 options)"},
            {"value": "short", "label": "Short", "description": "Short descriptive answer"},
            {"value": "long", "label": "Long", "description": "Extended detailed answer"}
        ]
    )

@router.get("/history", response_model=QuestionHistoryResponse)
async def get_question_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    course_filter: Optional[str] = Query(None, description="Filter by course code"),
    exam_type_filter: Optional[ExamType] = Query(None, description="Filter by exam type")
):
    try:
        filtered_papers = question_history_db
        
        if course_filter:
            filtered_papers = [q for q in filtered_papers if q.course_code == course_filter.upper()]
        
        if exam_type_filter:
            filtered_papers = [q for q in filtered_papers if q.exam_type == exam_type_filter]
        
        filtered_papers.sort(key=lambda x: x.created_at, reverse=True)
        
        paginated_papers = filtered_papers[offset:offset + limit]
        
        return QuestionHistoryResponse(
            success=True,
            message=f"Retrieved {len(paginated_papers)} question papers from history",
            question_papers=paginated_papers,
            total_count=len(filtered_papers)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving question history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve question history")

@router.get("/courses/{course_code}/stats", response_model=CourseStatsResponse)
async def get_course_stats(course_code: str):
    try:
        course_code = course_code.upper()
        
        course = next((c for c in courses_db if c.course_code == course_code), None)
        if not course:
            raise HTTPException(status_code=404, detail=f"Course {course_code} not found")
        
        stats = {
            "course_code": course_code,
            "total_questions_available": 150,
            "question_types_breakdown": {
                "mcq": 60,
                "short": 50, 
                "long": 40
            },
            "exam_types_breakdown": {
                "cat1": 50,
                "cat2": 50,
                "fat": 50
            },
            "years_available": [2020, 2021, 2022, 2023, 2024]
        }
        
        return CourseStatsResponse(
            success=True,
            message=f"Retrieved statistics for {course_code}",
            **stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving course stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve course statistics")

@router.delete("/history/{paper_id}")
async def delete_question_paper(paper_id: str):
    try:
        paper = next((q for q in question_history_db if q.id == paper_id), None)
        if not paper:
            raise HTTPException(status_code=404, detail="Question paper not found")
        
        question_history_db.remove(paper)
        
        logger.info(f"Deleted question paper: {paper_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Question paper deleted successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question paper: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete question paper")

async def _generate_questions_from_database(
    request: QuestionGenerationRequest, 
    course: CourseInfo
) -> List[GeneratedQuestion]:
    await asyncio.sleep(1.5)
    
    questions = []
    
    # Normalize request types to expected set
    question_types = request.question_types or [QuestionType.MCQ, QuestionType.SHORT, QuestionType.LONG]
    
    questions_per_type = request.question_count // len(question_types)
    remainder = request.question_count % len(question_types)
    
    question_id_counter = 1
    
    for i, q_type in enumerate(question_types):
        count_for_type = questions_per_type + (1 if i < remainder else 0)
        
        for j in range(count_for_type):
            question = _generate_mock_question(
                question_id_counter,
                q_type,
                course,
                request.exam_type,
                request.include_answers
            )
            questions.append(question)
            question_id_counter += 1
    
    return questions

def _generate_mock_question(
    question_id: int,
    question_type: QuestionType,
    course: CourseInfo,
    exam_type: ExamType,
    include_answers: bool
) -> GeneratedQuestion:
    
    if question_type == QuestionType.MCQ:
        question_text = f"Which of the following is a fundamental concept in {course.title}?"
        options = [
            "Option A: First fundamental concept",
            "Option B: Second fundamental concept", 
            "Option C: Third fundamental concept",
            "Option D: Fourth fundamental concept"
        ]
        correct_answer = "Option A: First fundamental concept" if include_answers else None
        points = 2
    elif question_type == QuestionType.SHORT:
        question_text = f"Briefly explain a key principle of {course.title} and its practical applications."
        options = None
        correct_answer = f"Key principles include fundamental concepts with practical applications in real-world scenarios." if include_answers else None
        points = 5
    else:  # LONG
        question_text = f"Analyze and discuss the comprehensive framework of {course.title}. Provide detailed examples, compare different approaches, and evaluate their effectiveness in solving real-world problems."
        options = None
        correct_answer = f"Comprehensive analysis should cover theoretical foundations, practical applications, comparative evaluation, and real-world examples." if include_answers else None
        points = 10
    
    years = ["2021", "2022", "2023", "2024"]
    source = f"{exam_type.upper()} - {years[question_id % len(years)]}"
    
    return GeneratedQuestion(
        id=str(uuid.uuid4()),
        question_type=question_type,
        question_text=question_text,
        options=options,
        correct_answer=correct_answer,
        points=points,
        source=source,
        difficulty="medium",
        topic=f"{course.title} - Module {(question_id % 4) + 1}"
    )
