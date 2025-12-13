"""短信验证码(Mock版)。"""

from typing import Dict


MOCK_CODE = "123456"
_code_store: Dict[str, str] = {}


async def send_login_code(phone: str) -> str:
    """Mock发送验证码，固定返回`123456`。

    - 真实环境可替换为短信网关调用
    - 这里简单记忆最后一次下发的验证码，便于后续校验扩展
    """

    _code_store[phone] = MOCK_CODE
    return MOCK_CODE


def validate_code(phone: str, code: str) -> bool:
    """校验验证码，MVP阶段固定匹配Mock值。"""
    return code == MOCK_CODE

