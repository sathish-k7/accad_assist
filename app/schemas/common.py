from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    uptime: float = Field(..., description="Service uptime in seconds")
    version: str = Field(default="1.0.0", description="API version")
    services: Optional[Dict[str, str]] = Field(None, description="Status of individual services")

class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Success status")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="Error timestamp")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="Response timestamp")

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx" 
    TXT = "txt"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
