#!/usr/bin/env python3

import multiprocessing
import sys
import os
import argparse
from pathlib import Path

from ..agents.base_agent import ErrorOutput
from ..agents.specialized.hr_classifier_agent import HrClassifierAgent
from ..agents.triage_agent import TriageAgent
from ..agents.specialized.customs_classifier_agent import CustomsClassifierAgent
from ..agents.specialized.invoice_classifier_agent import InvoiceClassifierAgent
from ..agents.specialized.taxes_classifier_agent import TaxesClassifierAgent
from ..agents.specialized.banking_classifier_agent import BankingClassifierAgent
from ..agents.specialized.freight_classifier_agent import FreightClassifierAgent
import json

def classify_document(filename: str):
    triage_agent = TriageAgent()
    hr_classifier_agent = HrClassifierAgent()
    customs_classifier_agent = CustomsClassifierAgent()
    invoice_classifier_agent = InvoiceClassifierAgent()
    taxes_classifier_agent = TaxesClassifierAgent()
    banking_classifier_agent = BankingClassifierAgent()
    freight_classifier_agent = FreightClassifierAgent()

    try:
        result = triage_agent.run(filename)

        if type(result) is ErrorOutput:
            return result


        result_text = result.model_dump_json(indent=2)



        match result.grupo_documento:
            case "DOCUMENTOS_RH":
                return hr_classifier_agent.run(result_text)
            case "DOCUMENTOS_ADUANEIROS":
                return customs_classifier_agent.run(result_text)
            case "DOCUMENTOS_COMERCIAIS":
                return invoice_classifier_agent.run(result_text)
            case "DOCUMENTOS_FISCAIS":
                return taxes_classifier_agent.run(result_text)
            case "DOCUMENTOS_BANCARIOS":
                return banking_classifier_agent.run(result_text)
            case "DOCUMENTOS_FRETE":
                return freight_classifier_agent.run(result_text)
            case _:
                del result.conteudo # type: ignore
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
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='PDF files to classify'
    )
    
    parser.add_argument(
        '--processes',
        type=int,
        default=4,
        help='Number of parallel processes (default: 4)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate and collect files
    files_to_classify: list[str] = []
    for file_path in args.files:
        path = Path(file_path)
        
        if path.is_dir():
            if args.verbose:
                print(f"Warning: Skipping directory '{file_path}'")
            continue
            
        if not path.exists():
            print(f"Error: File '{file_path}' not found")
            sys.exit(1)
            
        if not file_path.lower().endswith('.pdf'):
            if args.verbose:
                print(f"Warning: Skipping non-PDF file '{file_path}'")
            continue
            
        files_to_classify.append(file_path)
    
    if not files_to_classify:
        print("Error: No valid PDF files found")
        sys.exit(1)
    
    # Check API key
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print("Error: GOOGLE_AI_API_KEY environment variable not set")
        print("Please set your Google AI API key:")
        print("export GOOGLE_AI_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    print(f"🚀 Starting classification of {len(files_to_classify)} files...")
    print(f"📊 Using {args.processes} parallel processes")
    
    try:
        with multiprocessing.Pool(processes=args.processes) as pool:
            results = pool.map(classify_document, files_to_classify)
        
        print(f"\n✅ Classification completed: {len(files_to_classify)} files processed")
        
        # Output results
        all_results = []
        for i, result in enumerate(results):
            if args.verbose or not args.output:
                print(f"\n📄 File {i+1}: {files_to_classify[i]}")
                print("-" * 80)
                if result:
                    print(result.model_dump_json(indent=2))
                else:
                    print("❌ Classification failed")
            
            if result:
                all_results.append(result.model_dump())
        
        # Save to output file if specified
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
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
