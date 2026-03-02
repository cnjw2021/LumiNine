from typing import List, Dict, Any, Optional


class AppError(Exception):
    """애플리케이션 공통 베이스 예외"""

    def __init__(self, message: str, *, code: str = "APP_ERROR", status: int = 500, fields: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.status = status
        self.fields = fields or []
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"code": self.code, "message": str(self)}
        if self.fields:
            data["fields"] = self.fields
        if self.details:
            data["details"] = self.details
        return data


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", *, fields: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message, code="VALIDATION_ERROR", status=400, fields=fields, details=details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found", *, details: Optional[str] = None):
        super().__init__(message, code="NOT_FOUND", status=404, details=details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", *, details: Optional[str] = None):
        super().__init__(message, code="UNAUTHORIZED", status=401, details=details)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", *, details: Optional[str] = None):
        super().__init__(message, code="FORBIDDEN", status=403, details=details)


class DomainRuleViolation(AppError):
    def __init__(self, message: str = "Domain rule violated", *, details: Optional[str] = None):
        super().__init__(message, code="DOMAIN_RULE_VIOLATION", status=422, details=details)


class ExternalServiceError(AppError):
    def __init__(self, message: str = "External service error", *, details: Optional[str] = None):
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", status=502, details=details)


