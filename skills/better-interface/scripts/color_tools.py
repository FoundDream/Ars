#!/usr/bin/env python3
"""Deterministic CSS color conversion, sRGB gamut, and WCAG 2 contrast tools."""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import re
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    red: float
    green: float
    blue: float
    alpha: float = 1.0


@dataclass(frozen=True)
class Oklch:
    lightness: float
    chroma: float
    hue: float
    alpha: float = 1.0


def clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def parse_alpha(token: str) -> float:
    token = token.strip()
    value = float(token[:-1]) / 100 if token.endswith("%") else float(token)
    if not 0 <= value <= 1:
        raise ValueError("alpha must be between 0 and 1")
    return value


def parse_angle(token: str) -> float:
    token = token.strip().lower()
    if token.endswith("deg"):
        value = float(token[:-3])
    elif token.endswith("grad"):
        value = float(token[:-4]) * 0.9
    elif token.endswith("rad"):
        value = math.degrees(float(token[:-3]))
    elif token.endswith("turn"):
        value = float(token[:-4]) * 360
    else:
        value = float(token)
    return value % 360


def parse_hex(value: str) -> Color:
    digits = value.lstrip("#")
    if len(digits) in (3, 4):
        digits = "".join(char * 2 for char in digits)
    if len(digits) not in (6, 8) or not re.fullmatch(r"[0-9a-fA-F]+", digits):
        raise ValueError("hex colors must use 3, 4, 6, or 8 hexadecimal digits")
    channels = [int(digits[index : index + 2], 16) / 255 for index in range(0, len(digits), 2)]
    return Color(*channels[:3], channels[3] if len(channels) == 4 else 1.0)


def split_function(value: str, name_pattern: str) -> tuple[list[str], str | None]:
    match = re.fullmatch(rf"(?:{name_pattern})\((.*)\)", value.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(f"invalid {name_pattern}() color")
    body = match.group(1).strip()
    parts = body.split("/", 1)
    channels = [token for token in re.split(r"[\s,]+", parts[0].strip()) if token]
    alpha = parts[1].strip() if len(parts) == 2 else None
    return channels, alpha


def parse_rgb(value: str) -> Color:
    channels, slash_alpha = split_function(value, r"rgba?")
    if slash_alpha is None and len(channels) == 4:
        slash_alpha = channels.pop()
    if len(channels) != 3:
        raise ValueError("rgb() requires three channels")

    def channel(token: str) -> float:
        result = float(token[:-1]) / 100 if token.endswith("%") else float(token) / 255
        if not 0 <= result <= 1:
            raise ValueError("rgb channels must be within their CSS range")
        return result

    return Color(*(channel(token) for token in channels), parse_alpha(slash_alpha) if slash_alpha else 1.0)


def parse_hsl(value: str) -> Color:
    channels, slash_alpha = split_function(value, r"hsla?")
    if slash_alpha is None and len(channels) == 4:
        slash_alpha = channels.pop()
    if len(channels) != 3 or not channels[1].endswith("%") or not channels[2].endswith("%"):
        raise ValueError("hsl() requires hue plus percentage saturation and lightness")
    hue = parse_angle(channels[0]) / 360
    saturation = float(channels[1][:-1]) / 100
    lightness = float(channels[2][:-1]) / 100
    if not 0 <= saturation <= 1 or not 0 <= lightness <= 1:
        raise ValueError("hsl saturation and lightness must be between 0% and 100%")
    red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
    return Color(red, green, blue, parse_alpha(slash_alpha) if slash_alpha else 1.0)


def parse_oklch(value: str) -> Oklch:
    channels, slash_alpha = split_function(value, r"oklch")
    if len(channels) != 3:
        raise ValueError("oklch() requires lightness, chroma, and hue")
    lightness = float(channels[0][:-1]) / 100 if channels[0].endswith("%") else float(channels[0])
    chroma = float(channels[1][:-1]) * 0.004 if channels[1].endswith("%") else float(channels[1])
    hue = parse_angle(channels[2])
    if not 0 <= lightness <= 1 or chroma < 0:
        raise ValueError("oklch lightness must be 0–1 and chroma must be non-negative")
    return Oklch(lightness, chroma, hue, parse_alpha(slash_alpha) if slash_alpha else 1.0)


def srgb_to_linear(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def linear_to_srgb(channel: float) -> float:
    return 12.92 * channel if channel <= 0.0031308 else 1.055 * channel ** (1 / 2.4) - 0.055


def color_to_oklch(color: Color) -> Oklch:
    red, green, blue = (srgb_to_linear(channel) for channel in (color.red, color.green, color.blue))
    l_value = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    m_value = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    s_value = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue
    l_root, m_root, s_root = (value ** (1 / 3) for value in (l_value, m_value, s_value))
    lightness = 0.2104542553 * l_root + 0.793617785 * m_root - 0.0040720468 * s_root
    a_value = 1.9779984951 * l_root - 2.428592205 * m_root + 0.4505937099 * s_root
    b_value = 0.0259040371 * l_root + 0.7827717662 * m_root - 0.808675766 * s_root
    chroma = math.hypot(a_value, b_value)
    hue = math.degrees(math.atan2(b_value, a_value)) % 360 if chroma > 1e-12 else 0.0
    return Oklch(lightness, chroma, hue, color.alpha)


def oklch_to_unclamped_color(oklch: Oklch) -> Color:
    angle = math.radians(oklch.hue)
    a_value = oklch.chroma * math.cos(angle)
    b_value = oklch.chroma * math.sin(angle)
    l_root = oklch.lightness + 0.3963377774 * a_value + 0.2158037573 * b_value
    m_root = oklch.lightness - 0.1055613458 * a_value - 0.0638541728 * b_value
    s_root = oklch.lightness - 0.0894841775 * a_value - 1.291485548 * b_value
    l_value, m_value, s_value = l_root**3, m_root**3, s_root**3
    red_linear = 4.0767416621 * l_value - 3.3077115913 * m_value + 0.2309699292 * s_value
    green_linear = -1.2684380046 * l_value + 2.6097574011 * m_value - 0.3413193965 * s_value
    blue_linear = -0.0041960863 * l_value - 0.7034186147 * m_value + 1.707614701 * s_value
    return Color(
        linear_to_srgb(red_linear),
        linear_to_srgb(green_linear),
        linear_to_srgb(blue_linear),
        oklch.alpha,
    )


def in_srgb_gamut(color: Color, epsilon: float = 1e-7) -> bool:
    return all(-epsilon <= channel <= 1 + epsilon for channel in (color.red, color.green, color.blue))


def parse_color(value: str) -> tuple[Color, Oklch]:
    normalized = value.strip()
    if normalized.startswith("#"):
        color = parse_hex(normalized)
        return color, color_to_oklch(color)
    if re.match(r"rgba?\(", normalized, re.IGNORECASE):
        color = parse_rgb(normalized)
        return color, color_to_oklch(color)
    if re.match(r"hsla?\(", normalized, re.IGNORECASE):
        color = parse_hsl(normalized)
        return color, color_to_oklch(color)
    if re.match(r"oklch\(", normalized, re.IGNORECASE):
        oklch = parse_oklch(normalized)
        return oklch_to_unclamped_color(oklch), oklch
    raise ValueError("supported formats: #hex, rgb(), hsl(), and oklch()")


def format_number(value: float, places: int = 3) -> str:
    if abs(value) < 0.5 * 10**-places:
        value = 0.0
    return f"{value:.{places}f}".rstrip("0").rstrip(".")


def format_oklch(oklch: Oklch) -> str:
    base = f"oklch({format_number(oklch.lightness)} {format_number(oklch.chroma)} {format_number(oklch.hue)})"
    if oklch.alpha < 1:
        base = base[:-1] + f" / {format_number(oklch.alpha)})"
    return base


def format_hex(color: Color) -> str:
    channels = [round(clamp_unit(channel) * 255) for channel in (color.red, color.green, color.blue)]
    if color.alpha < 1:
        channels.append(round(color.alpha * 255))
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def relative_luminance(color: Color) -> float:
    red, green, blue = (srgb_to_linear(clamp_unit(channel)) for channel in (color.red, color.green, color.blue))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def composite(foreground: Color, background: Color) -> Color:
    if background.alpha < 1:
        raise ValueError("contrast needs an opaque rendered background; supply the underlying surface")
    alpha = foreground.alpha
    return Color(
        foreground.red * alpha + background.red * (1 - alpha),
        foreground.green * alpha + background.green * (1 - alpha),
        foreground.blue * alpha + background.blue * (1 - alpha),
    )


def contrast_ratio(foreground: Color, background: Color) -> tuple[float, Color]:
    rendered = composite(foreground, background)
    first, second = sorted((relative_luminance(rendered), relative_luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05), rendered


def clamp_oklch_to_srgb(oklch: Oklch) -> Oklch:
    if in_srgb_gamut(oklch_to_unclamped_color(oklch)):
        return oklch
    low, high = 0.0, oklch.chroma
    for _ in range(40):
        middle = (low + high) / 2
        candidate = Oklch(oklch.lightness, middle, oklch.hue, oklch.alpha)
        if in_srgb_gamut(oklch_to_unclamped_color(candidate)):
            low = middle
        else:
            high = middle
    return Oklch(oklch.lightness, low, oklch.hue, oklch.alpha)


def convert_command(value: str) -> dict[str, object]:
    color, oklch = parse_color(value)
    gamut = in_srgb_gamut(color)
    return {
        "input": value,
        "oklch": format_oklch(oklch),
        "srgb_hex": format_hex(color) if gamut else None,
        "srgb_channels": [round(channel, 6) for channel in (color.red, color.green, color.blue)],
        "alpha": round(color.alpha, 6),
        "in_srgb_gamut": gamut,
    }


def contrast_command(foreground_value: str, background_value: str) -> dict[str, object]:
    foreground, _ = parse_color(foreground_value)
    background, _ = parse_color(background_value)
    ratio, rendered = contrast_ratio(foreground, background)
    return {
        "foreground": foreground_value,
        "background": background_value,
        "rendered_foreground": format_hex(rendered),
        "wcag2_ratio": round(ratio, 3),
        "passes": {
            "normal_text_aa": ratio >= 4.5,
            "normal_text_aaa": ratio >= 7,
            "large_text_aa": ratio >= 3,
            "large_text_aaa": ratio >= 4.5,
            "ui_and_graphics_aa": ratio >= 3,
        },
        "note": "WCAG 2 ratio only; this script does not calculate APCA.",
    }


def gamut_command(value: str) -> dict[str, object]:
    color, oklch = parse_color(value)
    return {
        "input": value,
        "oklch": format_oklch(oklch),
        "in_srgb_gamut": in_srgb_gamut(color),
        "unclamped_srgb_channels": [round(channel, 6) for channel in (color.red, color.green, color.blue)],
    }


def clamp_command(value: str) -> dict[str, object]:
    _, oklch = parse_color(value)
    clamped = clamp_oklch_to_srgb(oklch)
    color = oklch_to_unclamped_color(clamped)
    return {
        "input": value,
        "original_oklch": format_oklch(oklch),
        "clamped_oklch": format_oklch(clamped),
        "srgb_hex": format_hex(color),
        "chroma_reduction": round(oklch.chroma - clamped.chroma, 6),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    convert_parser = subparsers.add_parser("convert", help="convert a CSS color to OKLCH and sRGB")
    convert_parser.add_argument("color")
    contrast_parser = subparsers.add_parser("contrast", help="calculate a rendered WCAG 2 contrast ratio")
    contrast_parser.add_argument("foreground")
    contrast_parser.add_argument("background")
    gamut_parser = subparsers.add_parser("gamut", help="check whether a color is inside sRGB")
    gamut_parser.add_argument("color")
    clamp_parser = subparsers.add_parser("clamp", help="reduce OKLCH chroma until the color is inside sRGB")
    clamp_parser.add_argument("color")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        if arguments.command == "convert":
            result = convert_command(arguments.color)
        elif arguments.command == "contrast":
            result = contrast_command(arguments.foreground, arguments.background)
        elif arguments.command == "gamut":
            result = gamut_command(arguments.color)
        else:
            result = clamp_command(arguments.color)
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
