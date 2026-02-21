"""CLI entry point for Vision Agent.

Usage:
    python -m vision_agent <image_path> [--provider mock|sealion] [--json]

Examples:
    python -m vision_agent meal.jpg
    python -m vision_agent prescription.png --provider sealion
    python -m vision_agent report.jpg --json
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from src.vision_agent.config import VLMProvider, get_settings
from src.vision_agent.graph import build_graph
from src.vision_agent.llm.base import VLMError
from src.vision_agent.llm.mock import MockVLM
from src.vision_agent.llm.sealion import SeaLionVLM
from src.vision_agent.logging_config import configure_logging


def _build_vlm(provider: VLMProvider):
    if provider == VLMProvider.SEALION:
        return SeaLionVLM()
    return MockVLM()


def _print_result(result: dict, as_json: bool) -> None:
    output = result.get("structured_output", {})
    scene = output.get("scene_type", "UNKNOWN")

    if as_json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # ── Human-readable output ──────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"  Scene: {scene}  |  Confidence: {output.get('confidence', 0):.0%}")
    print(f"{'='*50}")

    if scene == "FOOD":
        items = output.get("items", [])
        for item in items:
            n = item.get("nutrition", {})
            print(f"  {item['name']} ({item.get('quantity', '?')})")
            print(f"    Calories: {n.get('calories_kcal', '?')} kcal"
                  f"  |  Carbs: {n.get('carbs_g', '?')}g"
                  f"  |  Protein: {n.get('protein_g', '?')}g"
                  f"  |  Fat: {n.get('fat_g', '?')}g")
        print(f"\n  Total calories: {output.get('total_calories_kcal', '?')} kcal")
        if output.get("notes"):
            print(f"  Note: {output['notes']}")

    elif scene == "MEDICATION":
        print(f"  Drug    : {output.get('drug_name', '?')}")
        print(f"  Dosage  : {output.get('dosage', '?')}")
        print(f"  Freq    : {output.get('frequency', '?')}")
        if output.get("route"):
            print(f"  Route   : {output['route']}")
        if output.get("warnings"):
            print("  Warnings:")
            for w in output["warnings"]:
                print(f"    ⚠ {w}")

    elif scene == "REPORT":
        print(f"  Type: {output.get('report_type', '?')}")
        if output.get("report_date"):
            print(f"  Date: {output['report_date']}")
        print("\n  Indicators:")
        for ind in output.get("indicators", []):
            flag = "⚠ ABNORMAL" if ind.get("is_abnormal") else "  normal  "
            ref = f"  (ref: {ind['reference_range']})" if ind.get("reference_range") else ""
            print(f"    [{flag}] {ind['name']}: {ind['value']} {ind.get('unit', '')}{ref}")

    elif scene == "UNKNOWN":
        print(f"  Rejected: {output.get('reason', 'Unknown reason')}")

    elif scene == "ERROR":
        print(f"  Error: {output.get('error', 'Unknown error')}")

    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Vision Agent - analyze medical images (food, medication, reports)"
    )
    parser.add_argument("image_path", help="Path to the image file to analyze")
    parser.add_argument(
        "--provider",
        choices=["mock", "sealion"],
        default=None,
        help="VLM provider to use (default: from .env or 'mock')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output raw JSON instead of human-readable format",
    )
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    # CLI --provider flag overrides env setting
    provider = VLMProvider(args.provider) if args.provider else settings.vlm_provider

    try:
        vlm = _build_vlm(provider)
    except VLMError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    graph = build_graph(
        vlm=vlm,
        max_retries=settings.vlm_max_retries,
        retry_delay_s=settings.vlm_retry_delay_s,
    )

    initial_state = {
        "image_path": str(Path(args.image_path).resolve()),
        "image_base64": "",
        "scene_type": "",
        "confidence": 0.0,
        "raw_response": "",
        "structured_output": {},
        "error": None,
    }

    if not args.as_json:
        print(f"Analyzing: {args.image_path}  (provider: {provider.value})")

    result = graph.invoke(initial_state)
    _print_result(result, args.as_json)

    # Exit code 1 if error
    if result.get("structured_output", {}).get("scene_type") == "ERROR":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
