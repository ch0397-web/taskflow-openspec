from fastapi import HTTPException


def err(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"error": {"code": code, "message": message}})


# 공통 에러 인스턴스
INVALID_CREDENTIALS = lambda: err(401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 일치하지 않습니다")
TOKEN_EXPIRED = lambda: err(401, "TOKEN_EXPIRED", "인증이 만료되었습니다")
FORBIDDEN = lambda: err(403, "FORBIDDEN", "권한이 없습니다")
NOT_FOUND = lambda: err(404, "NOT_FOUND", "해당 항목을 찾을 수 없습니다")
EMAIL_TAKEN = lambda: err(409, "EMAIL_TAKEN", "이미 가입된 이메일입니다")
ALREADY_IN_TEAM = lambda: err(409, "ALREADY_IN_TEAM", "이미 팀에 소속되어 있습니다")
NOT_OWNER = lambda: err(403, "NOT_OWNER", "본인의 메시지만 삭제할 수 있습니다")
TOO_LONG = lambda actual: err(400, "TOO_LONG", f"메시지는 1000자 이내로 입력하세요 (현재 {actual}자)")
VALIDATION_ERROR = lambda msg="올바른 형식이 아닙니다": err(400, "VALIDATION_ERROR", msg)
OWNER_CANNOT_LEAVE = lambda: err(403, "FORBIDDEN", "팀 소유자는 팀을 탈퇴할 수 없습니다")
