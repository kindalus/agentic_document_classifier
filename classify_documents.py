#!/usr/bin/env python3

import multiprocessing
import sys
import os

from hr_classifier_agent import HrClassifierAgent
from triage_agent import TriageAgent
from customs_classifier_agent import CustomsClassifierAgent
from invoice_classifier_agent import InvoiceClassifierAgent
from taxes_classifier_agent import TaxesClassifierAgent
from banking_classifier_agent import BankingClassifierAgent
from freight_classifier_agent import FreightClassifierAgent

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
        result_text = result.model_dump_json(indent=2)

        result_json = None
        match result.grupo_documento:
            case "DOCUMENTOS_RH":
                result_json = hr_classifier_agent.run(result_text).model_dump_json(indent=2)
            case "DOCUMENTOS_ADUANEIROS":
                result_json = customs_classifier_agent.run(result_text).model_dump_json(indent=2)
            case "DOCUMENTOS_COMERCIAIS":
                result_json = invoice_classifier_agent.run(result_text).model_dump_json(indent=2)
            case "DOCUMENTOS_FISCAIS":
                result_json = taxes_classifier_agent.run(result_text).model_dump_json(indent=2)
            case "DOCUMENTOS_BANCARIOS":
                result_json = banking_classifier_agent.run(result_text).model_dump_json(indent=2)
            case "DOCUMENTOS_FRETE":
                result_json = freight_classifier_agent.run(result_text).model_dump_json(indent=2)
            case "ERROR":
                result_json = f"Error processing document: \n{result.erro}" # type: ignore
            case _:
                del result.conteudo # type: ignore
                result_json = result.model_dump_json(indent=2)

        print("-------------------------------------------------------------------------------- ")
        print(result_json)

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Usage: python document_ai_classfier.py <files>")

    files = sys.argv[1:]
    files_to_classify: list[str] = []
    for file in files:
        if os.path.isdir(file):
            raise ValueError(f"Provided file: '{file}' is a directory.")

        if file.lower().endswith(('.pdf')):
            files_to_classify.append(file)

    num_processes = 8

    print("Starting classification...")
    print(f"Processing {len(files_to_classify)} files...")

    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(classify_document, files_to_classify)

    print("-------------------------------------------------------------------------------- ")
    print("Done: ", len(files_to_classify), "files processed.")
