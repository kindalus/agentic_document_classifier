#!/usr/bin/env python3

import argparse
import json
import multiprocessing
import os
import sys
from pathlib import Path

from ..agents import ErrorOutput, classify_document as agent_classify
from ..pretty_print import pretty_print


def classify_document(filename: str):
    try:
        result = agent_classify(filename)

        if type(result) is ErrorOutput:
            return result

        if hasattr(result, "conteudo"):
            del result.conteudo  # pyright: ignore[reportAttributeAccessIssue]
        return result

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Classify business documents using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentic-classify document.pdf
  agentic-classify *.pdf
  agentic-classify --processes 8 documents/*.pdf
  agentic-classify --output results.json document1.pdf document2.pdf
        """,
    )

    _ = parser.add_argument("files", nargs="+", help="PDF files to classify")

    _ = parser.add_argument(
        "--processes",
        type=int,
        default=4,
        help="Number of parallel processes (default: 4)",
    )

    _ = parser.add_argument(
        "--output", type=str, help="Output file for results (JSON format)"
    )

    _ = parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate and collect files
    files_to_classify: list[str] = []
    for file_path in args.files:  # pyright: ignore[reportAny]
        path = Path(file_path)  # pyright: ignore[reportAny]

        if path.is_dir():
            if args.verbose:  # pyright: ignore[reportAny]
                print(f"Warning: Skipping directory '{file_path}'")
            continue

        if not path.exists():
            print(f"Error: File '{file_path}' not found")
            sys.exit(1)

        if not file_path.lower().endswith(".pdf"):  # pyright: ignore[reportAny]
            if args.verbose:  # pyright: ignore[reportAny]
                print(f"Warning: Skipping non-PDF file '{file_path}'")
            continue

        files_to_classify.append(file_path)  # pyright: ignore[reportAny]

    if not files_to_classify:
        print("Error: No valid PDF files found")
        sys.exit(1)

    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google AI API key:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        sys.exit(1)

    print(f"🚀 Starting classification of {len(files_to_classify)} files...")
    print(f"📊 Using {args.processes} parallel processes")  # pyright: ignore[reportAny]

    try:
        with multiprocessing.Pool(processes=args.processes) as pool:  # pyright: ignore[reportAny]
            results = pool.map(classify_document, files_to_classify)

        print(
            f"\n✅ Classification completed: {len(files_to_classify)} files processed"
        )

        # Output results
        all_results = []
        for i, result in enumerate(results):
            if args.verbose or not args.output:  # pyright: ignore[reportAny]
                print(f"\n📄 File {i + 1}: {files_to_classify[i]}")
                print("-" * 90)
                if result:
                    metadados_doc = getattr(result, "metadados_documento", None)
                    d = dict(result)
                    if metadados_doc is not None:
                        metadados_doc = dict(metadados_doc)
                        del d["metadados_documento"]
                        pretty_print([d, metadados_doc])
                    else:
                        pretty_print(d)

                else:
                    print("❌ Classification failed")

            if result:
                all_results.append(result.model_dump())  # pyright: ignore[reportUnknownMemberType]

        # Save to output file if specified
        if args.output:  # pyright: ignore[reportAny]
            output_path = Path(args.output)  # pyright: ignore[reportAny]
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {output_path}")

    except KeyboardInterrupt:
        print("\n⚠️  Classification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during classification: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
