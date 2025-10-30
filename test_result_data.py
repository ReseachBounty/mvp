#!/usr/bin/env python3
"""
Test script per verificare la struttura del result_data

Questo script simula la creazione di un task e verifica che il result_data
venga salvato correttamente con la struttura prevista.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_result_data_structure():
    """Test che verifica la struttura del result_data"""

    print("=" * 80)
    print("TEST: Result Data Structure")
    print("=" * 80)

    # Simula il result_data che dovrebbe essere salvato
    expected_structure = {
        "overview": {},
        "actions": {},
        "analytics": {
            "images": []
        },
        "bytes": None
    }

    print("\n1. Struttura Attesa:")
    print(json.dumps(expected_structure, indent=2))

    # Esempio di result_data completo
    example_result_data = {
        "overview": {
            "overview": "Mock analysis demonstrates strong market positioning...",
            "key_highlights": [
                "Strong product-market fit with growing customer base",
                "Experienced leadership team with proven track record",
                "Differentiated technology platform with competitive moats"
            ],
            "overall_assessment": "The company presents a compelling investment opportunity..."
        },
        "actions": {
            "immediate_priorities": [
                "Accelerate product development on key differentiators",
                "Scale sales and marketing engine",
                "Build customer success organization"
            ],
            "medium_term_focus": [
                "Expand into adjacent markets",
                "Develop partner ecosystem",
                "Invest in brand building"
            ],
            "success_factors": [
                "Maintaining product innovation leadership",
                "Executing scalable go-to-market strategy"
            ],
            "exit_scenarios": [
                {
                    "scenario": "Strategic Acquisition",
                    "timeline": "3-5 years",
                    "probability": "Medium-High"
                }
            ]
        },
        "analytics": {
            "images": [
                "/absolute/path/to/outputs/images_20250130_120000/chart_1.jpg",
                "/absolute/path/to/outputs/images_20250130_120000/chart_2.png",
                "/absolute/path/to/outputs/images_20250130_120000/chart_3.jpg"
            ]
        },
        "bytes": "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC..." # Truncated base64
    }

    print("\n2. Esempio Result Data Completo:")
    print(json.dumps(example_result_data, indent=2))

    # Verifica chiavi principali
    print("\n3. Verifica Struttura:")
    required_keys = ["overview", "actions", "analytics", "bytes"]

    for key in required_keys:
        has_key = key in example_result_data
        status = "✓" if has_key else "✗"
        print(f"  {status} Chiave '{key}': {'Presente' if has_key else 'MANCANTE'}")

    # Verifica struttura analytics
    if "analytics" in example_result_data:
        has_images = "images" in example_result_data["analytics"]
        status = "✓" if has_images else "✗"
        print(f"  {status} analytics.images: {'Presente' if has_images else 'MANCANTE'}")

        if has_images:
            images_count = len(example_result_data["analytics"]["images"])
            print(f"    └─ Numero immagini: {images_count}")

    # Verifica presenza dati
    print("\n4. Verifica Contenuti:")

    has_overview_data = bool(example_result_data.get("overview"))
    print(f"  {'✓' if has_overview_data else '✗'} overview contiene dati")

    has_actions_data = bool(example_result_data.get("actions"))
    print(f"  {'✓' if has_actions_data else '✗'} actions contiene dati")

    has_images = len(example_result_data.get("analytics", {}).get("images", [])) > 0
    print(f"  {'✓' if has_images else '✗'} analytics.images contiene path")

    has_pdf_bytes = bool(example_result_data.get("bytes"))
    print(f"  {'✓' if has_pdf_bytes else '✗'} bytes contiene PDF base64")

    # Query SQL di esempio
    print("\n5. Query SQL per Verificare in Database:")
    print("-" * 80)

    sql_queries = """
-- Verifica struttura result_data
SELECT
  id,
  status,
  result_data->>'overview' IS NOT NULL as has_overview,
  result_data->>'actions' IS NOT NULL as has_actions,
  result_data->'analytics'->'images' IS NOT NULL as has_images,
  result_data->>'bytes' IS NOT NULL as has_pdf_bytes
FROM task
WHERE status = 'completed'
ORDER BY id DESC
LIMIT 5;

-- Conta immagini
SELECT
  id,
  jsonb_array_length(result_data->'analytics'->'images') as images_count
FROM task
WHERE status = 'completed'
  AND result_data->'analytics'->'images' IS NOT NULL;

-- Dimensione PDF base64
SELECT
  id,
  length(result_data->>'bytes') as pdf_base64_length,
  length(result_data->>'bytes') / 1024 as kb,
  length(result_data->>'bytes') / 1024 / 1024 as mb
FROM task
WHERE status = 'completed'
  AND result_data->>'bytes' IS NOT NULL;

-- Estrai overview completo
SELECT
  id,
  result_data->'overview'->>'overview' as overview_text,
  result_data->'overview'->'key_highlights' as highlights,
  result_data->'overview'->>'overall_assessment' as assessment
FROM task
WHERE status = 'completed'
LIMIT 1;

-- Lista path immagini
SELECT
  id,
  jsonb_array_elements_text(result_data->'analytics'->'images') as image_path
FROM task
WHERE status = 'completed'
  AND result_data->'analytics'->'images' IS NOT NULL
LIMIT 10;
"""

    print(sql_queries)

    print("\n" + "=" * 80)
    print("Test completato! Verifica che il result_data nel DB segua questa struttura.")
    print("=" * 80)


def test_api_response():
    """Test che mostra come il result_data appare nelle API response"""

    print("\n" + "=" * 80)
    print("API RESPONSE EXAMPLE")
    print("=" * 80)

    api_response = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "completed",
        "company_info_id": "456e7890-e89b-12d3-a456-426614174000",
        "error_message": None,
        "result_data": {
            "overview": {
                "overview": "Mock analysis demonstrates strong market positioning...",
                "key_highlights": [
                    "Strong product-market fit",
                    "Experienced leadership team",
                    "Differentiated technology"
                ],
                "overall_assessment": "Compelling investment opportunity"
            },
            "actions": {
                "immediate_priorities": [
                    "Accelerate product development",
                    "Scale sales and marketing"
                ],
                "medium_term_focus": [
                    "Expand into adjacent markets"
                ],
                "success_factors": [
                    "Maintain innovation leadership"
                ],
                "exit_scenarios": [
                    {
                        "scenario": "Strategic Acquisition",
                        "timeline": "3-5 years",
                        "probability": "Medium-High"
                    }
                ]
            },
            "analytics": {
                "images": [
                    "/path/to/chart1.jpg",
                    "/path/to/chart2.png"
                ]
            },
            "bytes": "JVBERi0xLjQKJe..." # Truncated
        }
    }

    print("\nGET /api/v1/report/task_status/{task_id}")
    print("\nResponse:")
    print(json.dumps(api_response, indent=2))

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_result_data_structure()
    test_api_response()
