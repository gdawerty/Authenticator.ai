"""
Test script for the Context Analyzer

This script demonstrates how to use the context analyzer with sample data.
"""
import json
from uuid import uuid4
from app.models.context import ChunkInput
from app.pipeline.context import get_context_analyzer


def test_context_analyzer():
    """Test the context analyzer with sample document chunks"""

    # Sample chunks from a medical record
    sample_chunks = [
        ChunkInput(
            chunk_id="chunk_01",
            page_number=1,
            text="Patient: John Smith\nDate of Birth: January 15, 1980\nMedical Record #: 12345678\nDate of Visit: March 20, 2024"
        ),
        ChunkInput(
            chunk_id="chunk_02",
            page_number=1,
            text="Chief Complaint: Patient reports severe headache and dizziness lasting 3 days."
        ),
        ChunkInput(
            chunk_id="chunk_03",
            page_number=2,
            text="Diagnosis: Migraine with aura\nTreatment Plan: Prescribed Sumatriptan 50mg, advised rest and hydration."
        ),
        ChunkInput(
            chunk_id="chunk_04",
            page_number=2,
            text="Follow-up: Schedule appointment in 2 weeks.\nTotal Charges: $250.00"
        )
    ]

    # Create document ID
    document_id = uuid4()

    print("Testing Context Analyzer...")
    print(f"Document ID: {document_id}")
    print(f"Number of chunks: {len(sample_chunks)}\n")

    try:
        # Get analyzer instance
        analyzer = get_context_analyzer()

        # Analyze the chunks
        context = analyzer.analyze(document_id=document_id, chunks=sample_chunks)

        # Print results
        print("=" * 80)
        print("CONTEXT ANALYSIS RESULTS")
        print("=" * 80)

        print("\n--- PAGE NARRATIVES ---")
        for narrative in context.page_narratives:
            print(f"\nPage {narrative.page_number} ({narrative.page_type}):")
            print(f"  Key Takeaway: {narrative.key_takeaway}")
            print(f"  Summary: {narrative.narrative_summary}")
            print(f"  Supporting Chunks: {', '.join(narrative.supporting_chunks)}")

        print("\n--- CONTEXT ENTITIES ---")

        print("\nPrimary Actors:")
        for actor in context.context_entities.primary_actors:
            print(f"  - {actor}")

        print("\nCritical Dates:")
        for date in context.context_entities.critical_dates:
            print(f"  - {date.date} ({date.source_text}): {date.description}")

        print("\nFinancial Values:")
        for value in context.context_entities.financial_values:
            print(f"  - ${value.amount:.2f} ({value.source_text}): {value.description}")

        print("\n" + "=" * 80)
        print("Full JSON Output:")
        print("=" * 80)
        print(json.dumps(context.model_dump(), indent=2, default=str))

        return True

    except ValueError as e:
        print(f"Error: {e}")
        print("\nMake sure to set your ANTHROPIC_API_KEY in the .env file!")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    success = test_context_analyzer()
    exit(0 if success else 1)
