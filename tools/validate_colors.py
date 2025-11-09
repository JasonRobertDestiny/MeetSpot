"""
WCAG 2.1色彩对比度验证工具

验证所有设计token中的颜色组合是否符合WCAG标准:
- AA级 (正文): 对比度 ≥ 4.5:1
- AA级 (大文字): 对比度 ≥ 3.0:1
- AAA级 (正文): 对比度 ≥ 7.0:1

使用方法:
python tools/validate_colors.py

或集成到CI/CD:
pytest tests/test_accessibility.py::test_color_contrast
"""

import math
import sys
from pathlib import Path
from typing import Dict, Tuple

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.design_tokens import DesignTokens


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """将十六进制颜色转换为RGB"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    计算相对亮度 (WCAG公式)
    https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    r, g, b = [x / 255.0 for x in rgb]

    def adjust(channel):
        if channel <= 0.03928:
            return channel / 12.92
        return math.pow((channel + 0.055) / 1.055, 2.4)

    r, g, b = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color1: str, color2: str) -> float:
    """
    计算两个颜色之间的对比度
    https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio

    Returns:
        对比度比值 (1:1 到 21:1)
    """
    lum1 = relative_luminance(hex_to_rgb(color1))
    lum2 = relative_luminance(hex_to_rgb(color2))

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    return (lighter + 0.05) / (darker + 0.05)


def check_wcag_compliance(
    foreground: str, background: str, level: str = "AA", text_size: str = "normal"
) -> Dict[str, any]:
    """
    检查颜色组合是否符合WCAG标准

    Args:
        foreground: 前景色 (文字)
        background: 背景色
        level: WCAG级别 ("AA" 或 "AAA")
        text_size: 文字大小 ("normal" 或 "large")

    Returns:
        {
            "ratio": 对比度,
            "passes": 是否通过,
            "level": 合规级别,
            "recommendation": 建议
        }
    """
    ratio = contrast_ratio(foreground, background)

    # WCAG标准阈值
    thresholds = {
        "AA": {"normal": 4.5, "large": 3.0},
        "AAA": {"normal": 7.0, "large": 4.5},
    }

    required_ratio = thresholds[level][text_size]
    passes = ratio >= required_ratio

    result = {
        "ratio": round(ratio, 2),
        "passes": passes,
        "level": level,
        "required": required_ratio,
        "foreground": foreground,
        "background": background,
    }

    # 生成建议
    if not passes:
        if ratio < required_ratio * 0.8:
            result["recommendation"] = "对比度严重不足,需要更换颜色"
        else:
            result["recommendation"] = "对比度略低,建议微调颜色深浅"
    else:
        if ratio >= thresholds["AAA"][text_size]:
            result["recommendation"] = "优秀！符合WCAG AAA级标准"
        else:
            result["recommendation"] = "符合WCAG AA级标准"

    return result


def validate_design_tokens():
    """验证所有设计token的色彩对比度"""
    results = []

    print("=" * 80)
    print("MeetSpot Design Tokens - WCAG 2.1色彩对比度验证报告")
    print("=" * 80)
    print()

    # 1. 验证品牌色在白色背景上
    print("📊 品牌色 vs 白色背景")
    print("-" * 80)
    white_bg = DesignTokens.BACKGROUND["primary"]

    for color_name, color_value in DesignTokens.BRAND.items():
        if color_name == "gradient":
            continue  # 跳过渐变

        result = check_wcag_compliance(color_value, white_bg, "AA", "normal")
        results.append(result)

        status = "✅ PASS" if result["passes"] else "❌ FAIL"
        print(
            f"{status} | {color_name:20s} | {color_value:10s} | {result['ratio']:5.2f}:1 | {result['recommendation']}"
        )

    print()

    # 2. 验证文字色在白色背景上
    print("📊 文字色 vs 白色背景")
    print("-" * 80)

    for color_name, color_value in DesignTokens.TEXT.items():
        if color_name == "inverse":
            continue  # 跳过反转色

        result = check_wcag_compliance(color_value, white_bg, "AA", "normal")
        results.append(result)

        status = "✅ PASS" if result["passes"] else "❌ FAIL"
        print(
            f"{status} | {color_name:20s} | {color_value:10s} | {result['ratio']:5.2f}:1 | {result['recommendation']}"
        )

    print()

    # 3. 验证场所主题色
    print("📊 场所主题色验证 (主色 vs 白色背景)")
    print("-" * 80)

    for venue_name, theme in DesignTokens.VENUE_THEMES.items():
        if venue_name == "default":
            continue

        # 主色 vs 白色背景 (用于大文字/按钮)
        result = check_wcag_compliance(
            theme["theme_primary"], white_bg, "AA", "large"  # 大文字标准 (3.0:1)
        )
        results.append(result)

        status = "✅ PASS" if result["passes"] else "❌ FAIL"
        print(
            f"{status} | {venue_name:12s} | {theme['theme_primary']:10s} | {result['ratio']:5.2f}:1 | {result['recommendation']}"
        )

        # 深色 vs 浅色背景 (用于卡片内文字)
        result_card = check_wcag_compliance(
            theme["theme_dark"], theme["theme_light"], "AA", "normal"
        )
        results.append(result_card)

        status_card = "✅ PASS" if result_card["passes"] else "❌ FAIL"
        print(
            f"  └─ {status_card} | 卡片文字 | {theme['theme_dark']:10s} on {theme['theme_light']:10s} | {result_card['ratio']:5.2f}:1"
        )

    print()
    print("=" * 80)

    # 统计结果
    total = len(results)
    passed = sum(1 for r in results if r["passes"])
    failed = total - passed

    print(f"验证总数: {total}")
    print(f"✅ 通过: {passed} ({passed/total*100:.1f}%)")
    print(f"❌ 失败: {failed} ({failed/total*100:.1f}%)")
    print("=" * 80)

    # 返回是否全部通过
    return failed == 0


if __name__ == "__main__":
    all_passed = validate_design_tokens()
    sys.exit(0 if all_passed else 1)
