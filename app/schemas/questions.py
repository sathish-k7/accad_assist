from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

from .common import APIResponse, ProcessingStatus

class CourseLevel(str, Enum):
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    DOCTORATE = "doctorate"

class ExamType(str, Enum):
    CAT1 = "cat1"
    CAT2 = "cat2"
    FAT = "fat"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT = "short"
    LONG = "long"

class CourseInfo(BaseModel):
    course_code: str = Field(..., description="Course code (e.g., CS101)")
    title: str = Field(..., description="Course title")
    credits: int = Field(..., ge=1, le=6, description="Course credits")
    semester: int = Field(..., ge=1, le=8, description="Semester number")
    level: CourseLevel = Field(..., description="Course level")
    description: Optional[str] = Field(None, description="Course description")

class GeneratedQuestion(BaseModel):
    id: str = Field(..., description="Question ID")
    question_text: str = Field(..., description="Question text")
    question_type: QuestionType = Field(..., description="Type of question")
    options: Optional[List[str]] = Field(None, description="Options for MCQ")
    correct_answer: str = Field(..., description="Correct answer")
    explanation: Optional[str] = Field(None, description="Answer explanation")
    points: int = Field(default=1, ge=1, le=10, description="Points for question")
    topic: Optional[str] = Field(None, description="Question topic")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Question difficulty")

class QuestionGenerationRequest(BaseModel):
    course_code: str = Field(..., description="Course code (e.g., CS101)")
    exam_type: ExamType = Field(..., description="Type of exam")
    question_count: int = Field(default=10, ge=1, le=50, description="Number of questions to generate")
    question_types: Optional[List[QuestionType]] = Field(default=None, description="Specific question types to include (mcq/short/long)")
    difficulty_filter: Optional[str] = Field(default=None, description="Filter by difficulty level")
    include_answers: bool = Field(default=True, description="Whether to include correct answers")
    
    @field_validator('course_code')
    @classmethod
    def validate_course_code(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Course code must be at least 2 characters long')
        return v.strip().upper()

class QuestionGenerationResponse(APIResponse):
    data: Optional[List[GeneratedQuestion]] = Field(None, description="Generated questions")

class CourseListResponse(APIResponse):
    courses: List[CourseInfo] = Field(..., description="Available courses")
    total_count: int = Field(..., description="Total course count")

class ExamTypesResponse(BaseModel):
    exam_types: List[Dict[str, str]] = Field(..., description="Available exam types")
    question_types: List[Dict[str, str]] = Field(..., description="Available question types")

class QuestionHistoryItem(BaseModel):
    id: str = Field(..., description="Question paper ID")
    course_code: str = Field(..., description="Course code")
    course_title: str = Field(..., description="Course title")
    exam_type: ExamType = Field(..., description="Exam type")
    question_count: int = Field(..., description="Number of questions")
    created_at: datetime = Field(..., description="Creation timestamp")
    total_points: int = Field(..., description="Total points")

class QuestionHistoryResponse(APIResponse):
    question_papers: List[QuestionHistoryItem] = Field(..., description="Previous question papers")
    total_count: int = Field(..., description="Total count")

class CourseStatsResponse(APIResponse):
    course_code: str = Field(..., description="Course code")
    total_questions_available: int = Field(..., description="Total questions in database for this course")
    question_types_breakdown: Dict[str, int] = Field(..., description="Breakdown by question type")
    exam_types_breakdown: Dict[str, int] = Field(..., description="Breakdown by exam type")
    years_available: List[int] = Field(..., description="Years for which questions are available")
