#!/usr/bin/env python3
"""
Comprehensive Dataset Filler for Authenticator.ai
Finds working datasets online and creates synthetic data to fill all gaps
"""

import os
import json
import requests
import zipfile
import tarfile
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import shutil
import urllib.request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveDatasetFiller:
    def __init__(self, base_dir: str = "/Users/prathamsaurabh/Authenticator.ai/data/training_data"):
        self.base_dir = Path(base_dir)
        self.raw_datasets_dir = self.base_dir / "raw_datasets"
        
        # Working dataset sources found online
        self.working_datasets = {
            "general_document_classification": {
                "tobacco3482": {
                    "url": "https://www.kaggle.com/datasets/patrickaudriaz/tobacco3482jpg",
                    "description": "Tobacco document classification",
                    "type": "kaggle"
                },
                "arxiv_papers": {
                    "hf_name": "scientific_papers",
                    "description": "Scientific paper classification",
                    "type": "huggingface"
                },
                "wikipedia": {
                    "hf_name": "wikipedia",
                    "config": "20220301.en",
                    "description": "Wikipedia articles for classification",
                    "type": "huggingface"
                },
                "news_category": {
                    "hf_name": "ag_news",
                    "description": "News category classification",
                    "type": "huggingface"
                }
            },
            "k12_education": {
                "math_word_problems": {
                    "hf_name": "gsm8k",
                    "description": "Grade school math problems",
                    "type": "huggingface"
                },
                "elementary_science": {
                    "hf_name": "ai2_arc",
                    "config": "ARC-Easy",
                    "description": "Elementary science questions",
                    "type": "huggingface"
                },
                "reading_comp_race": {
                    "hf_name": "race",
                    "config": "middle",
                    "description": "Reading comprehension for middle school",
                    "type": "huggingface"
                }
            },
            "vision_datasets": {
                "mnist_docs": {
                    "hf_name": "mnist",
                    "description": "Handwritten digits for OCR",
                    "type": "huggingface"
                },
                "fashion_mnist": {
                    "hf_name": "fashion_mnist",
                    "description": "Fashion item classification",
                    "type": "huggingface"
                },
                "street_view_house_numbers": {
                    "hf_name": "svhn",
                    "config": "cropped_digits",
                    "description": "Street view house numbers",
                    "type": "huggingface"
                }
            },
            "forgery_vlm": {
                "fake_news": {
                    "hf_name": "fake_news",
                    "description": "Fake news detection dataset",
                    "type": "huggingface"
                }
            }
        }
    
    def download_huggingface_dataset(self, dataset_name: str, save_path: Path, config: str = None) -> bool:
        """Download dataset from HuggingFace"""
        try:
            from datasets import load_dataset
            logger.info(f"Downloading HuggingFace dataset: {dataset_name}")
            
            if config:
                dataset = load_dataset(dataset_name, config)
            else:
                dataset = load_dataset(dataset_name)
            
            save_path.mkdir(parents=True, exist_ok=True)
            dataset.save_to_disk(str(save_path))
            logger.info(f"✅ Successfully downloaded {dataset_name} to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {dataset_name}: {e}")
            return False
    
    def create_synthetic_document_data(self, save_path: Path, num_samples: int = 1000) -> bool:
        """Create synthetic document classification data"""
        try:
            save_path.mkdir(parents=True, exist_ok=True)
            
            # Document types for classification
            doc_types = ["invoice", "letter", "form", "report", "email", "memo", "contract", "resume"]
            
            data = []
            for i in range(num_samples):
                doc_type = random.choice(doc_types)
                
                # Generate synthetic text based on document type
                if doc_type == "invoice":
                    text = self.generate_invoice_text()
                elif doc_type == "letter":
                    text = self.generate_letter_text()
                elif doc_type == "form":
                    text = self.generate_form_text()
                elif doc_type == "report":
                    text = self.generate_report_text()
                elif doc_type == "email":
                    text = self.generate_email_text()
                elif doc_type == "memo":
                    text = self.generate_memo_text()
                elif doc_type == "contract":
                    text = self.generate_contract_text()
                else:  # resume
                    text = self.generate_resume_text()
                
                data.append({
                    "id": f"synthetic_{i:05d}",
                    "text": text,
                    "label": doc_type,
                    "synthetic": True
                })
            
            # Save as JSON
            with open(save_path / "synthetic_documents.json", "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Created {num_samples} synthetic documents at {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create synthetic documents: {e}")
            return False
    
    def create_synthetic_k12_data(self, save_path: Path, subject: str, num_samples: int = 500) -> bool:
        """Create synthetic K12 educational data"""
        try:
            save_path.mkdir(parents=True, exist_ok=True)
            
            data = []
            for i in range(num_samples):
                if subject == "math":
                    question, answer = self.generate_math_problem()
                elif subject == "science":
                    question, answer = self.generate_science_question()
                elif subject == "social_studies":
                    question, answer = self.generate_social_studies_question()
                elif subject == "reading":
                    question, answer = self.generate_reading_question()
                else:
                    question, answer = self.generate_writing_prompt()
                
                data.append({
                    "id": f"k12_{subject}_{i:05d}",
                    "question": question,
                    "answer": answer,
                    "subject": subject,
                    "grade_level": random.choice(["elementary", "middle", "high"]),
                    "synthetic": True
                })
            
            # Save as JSON
            with open(save_path / f"synthetic_{subject}.json", "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Created {num_samples} synthetic {subject} questions at {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create synthetic {subject} data: {e}")
            return False
    
    def create_synthetic_images(self, save_path: Path, image_type: str, num_samples: int = 200) -> bool:
        """Create synthetic images for vision tasks"""
        try:
            save_path.mkdir(parents=True, exist_ok=True)
            images_dir = save_path / "images"
            images_dir.mkdir(exist_ok=True)
            
            data = []
            for i in range(num_samples):
                img_path = images_dir / f"synthetic_{image_type}_{i:05d}.png"
                
                if image_type == "document":
                    img, text = self.generate_synthetic_document_image()
                elif image_type == "text":
                    img, text = self.generate_synthetic_text_image()
                elif image_type == "form":
                    img, text = self.generate_synthetic_form_image()
                else:
                    img, text = self.generate_synthetic_receipt_image()
                
                # Save image
                img.save(img_path)
                
                data.append({
                    "id": f"synthetic_{image_type}_{i:05d}",
                    "image_path": str(img_path),
                    "text": text,
                    "type": image_type,
                    "synthetic": True
                })
            
            # Save metadata
            with open(save_path / f"synthetic_{image_type}_metadata.json", "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Created {num_samples} synthetic {image_type} images at {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create synthetic {image_type} images: {e}")
            return False
    
    def create_synthetic_forgery_data(self, save_path: Path, num_samples: int = 300) -> bool:
        """Create synthetic document forgery detection data"""
        try:
            save_path.mkdir(parents=True, exist_ok=True)
            
            data = []
            for i in range(num_samples):
                # Create both authentic and forged versions
                authentic_doc = self.generate_authentic_document()
                forged_doc = self.generate_forged_document(authentic_doc)
                
                data.extend([
                    {
                        "id": f"authentic_{i:05d}",
                        "text": authentic_doc,
                        "label": "authentic",
                        "forgery_indicators": [],
                        "synthetic": True
                    },
                    {
                        "id": f"forged_{i:05d}",
                        "text": forged_doc["text"],
                        "label": "forged",
                        "forgery_indicators": forged_doc["indicators"],
                        "synthetic": True
                    }
                ])
            
            # Save as JSON
            with open(save_path / "synthetic_forgery_detection.json", "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Created {len(data)} synthetic forgery detection samples at {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create synthetic forgery data: {e}")
            return False
    
    def fill_all_gaps(self):
        """Fill all empty dataset folders with real or synthetic data"""
        logger.info("🚀 Starting comprehensive dataset filling...")
        
        # First, try to download working datasets
        logger.info("📥 Downloading working datasets from online sources...")
        self.download_working_datasets()
        
        # Then create synthetic data for remaining gaps
        logger.info("🎨 Creating synthetic data for remaining gaps...")
        self.create_synthetic_data_for_gaps()
        
        # Generate final report
        self.generate_completion_report()
    
    def download_working_datasets(self):
        """Download all working datasets"""
        total_downloaded = 0
        
        for category, datasets in self.working_datasets.items():
            for dataset_name, config in datasets.items():
                save_path = self.raw_datasets_dir / category / dataset_name
                
                if config["type"] == "huggingface":
                    success = self.download_huggingface_dataset(
                        config["hf_name"], 
                        save_path, 
                        config.get("config")
                    )
                    if success:
                        total_downloaded += 1
        
        logger.info(f"📊 Downloaded {total_downloaded} working datasets")
    
    def create_synthetic_data_for_gaps(self):
        """Create synthetic data for all empty folders"""
        # Get all empty folders
        empty_folders = self.get_empty_folders()
        
        for folder_path in empty_folders:
            category = folder_path.parent.name
            dataset_name = folder_path.name
            
            if category == "general_document_classification":
                self.create_synthetic_document_data(folder_path)
            elif category == "k12_education":
                subject = self.infer_subject_from_name(dataset_name)
                self.create_synthetic_k12_data(folder_path, subject)
            elif category == "vision_datasets":
                image_type = self.infer_image_type_from_name(dataset_name)
                self.create_synthetic_images(folder_path, image_type)
            elif category == "forgery_vlm":
                self.create_synthetic_forgery_data(folder_path)
            elif category == "k12_administrative":
                self.create_synthetic_admin_documents(folder_path, dataset_name)
    
    def get_empty_folders(self) -> List[Path]:
        """Get list of all empty dataset folders"""
        empty_folders = []
        
        for category_path in self.raw_datasets_dir.iterdir():
            if category_path.is_dir():
                for dataset_path in category_path.iterdir():
                    if dataset_path.is_dir():
                        # Check if folder is empty or has no meaningful data
                        has_data = False
                        for file_path in dataset_path.rglob("*"):
                            if file_path.is_file() and not file_path.name.startswith('.'):
                                if file_path.stat().st_size > 100:  # More than 100 bytes
                                    has_data = True
                                    break
                        
                        if not has_data:
                            empty_folders.append(dataset_path)
        
        return empty_folders
    
    # Helper methods for generating synthetic content
    def generate_invoice_text(self) -> str:
        companies = ["Tech Corp", "Global Solutions", "Digital Services", "Innovation Inc"]
        items = ["Software License", "Consulting Services", "Hardware", "Support Package"]
        
        company = random.choice(companies)
        item = random.choice(items)
        amount = random.randint(100, 5000)
        
        return f"""INVOICE #{random.randint(1000, 9999)}
From: {company}
To: Client Company
Date: {datetime.now().strftime('%Y-%m-%d')}

Item: {item}
Amount: ${amount:,.2f}
Tax: ${amount * 0.1:,.2f}
Total: ${amount * 1.1:,.2f}

Payment due within 30 days."""
    
    def generate_letter_text(self) -> str:
        return f"""Dear Sir/Madam,

I am writing to inform you about the recent updates to our services. 
We appreciate your continued business and look forward to serving you better.

{' '.join([random.choice(['Furthermore', 'Additionally', 'Moreover']) + ' ' + 
                 'we have implemented new features to enhance your experience.' 
                 for _ in range(2)])}

Please don't hesitate to contact us if you have any questions.

Sincerely,
Customer Service Team"""
    
    def generate_math_problem(self) -> tuple:
        operations = [
            lambda: (f"What is {random.randint(1, 100)} + {random.randint(1, 100)}?", "addition"),
            lambda: (f"What is {random.randint(1, 20)} × {random.randint(1, 12)}?", "multiplication"),
            lambda: (f"If John has {random.randint(5, 50)} apples and gives away {random.randint(1, 10)}, how many does he have left?", "word_problem")
        ]
        
        question, answer_type = random.choice(operations)()
        
        if answer_type == "addition":
            nums = [int(x) for x in question.split() if x.isdigit()]
            answer = str(sum(nums))
        elif answer_type == "multiplication":
            nums = [int(x) for x in question.split() if x.isdigit()]
            answer = str(nums[0] * nums[1])
        else:  # word_problem
            nums = [int(x) for x in question.split() if x.isdigit()]
            answer = str(nums[0] - nums[1])
        
        return question, answer
    
    def generate_science_question(self) -> tuple:
        questions = [
            ("What is the chemical symbol for water?", "H2O"),
            ("How many planets are in our solar system?", "8"),
            ("What gas do plants absorb from the atmosphere?", "Carbon dioxide"),
            ("What is the largest organ in the human body?", "Skin"),
            ("What is the speed of light?", "299,792,458 meters per second")
        ]
        return random.choice(questions)
    
    def generate_social_studies_question(self) -> tuple:
        questions = [
            ("What year did World War II end?", "1945"),
            ("Who was the first President of the United States?", "George Washington"),
            ("What is the capital of France?", "Paris"),
            ("In what year did the Civil War begin?", "1861"),
            ("What is the largest continent?", "Asia")
        ]
        return random.choice(questions)
    
    def generate_reading_question(self) -> tuple:
        passages = [
            "The cat sat on the mat and looked out the window.",
            "Sarah walked to the store to buy groceries for dinner.",
            "The old tree in the backyard provided shade on hot summer days."
        ]
        
        passage = random.choice(passages)
        question = f"What is the main subject of this sentence: '{passage}'?"
        
        if "cat" in passage:
            answer = "A cat sitting and looking out the window"
        elif "Sarah" in passage:
            answer = "Sarah going to buy groceries"
        else:
            answer = "An old tree providing shade"
        
        return question, answer
    
    def generate_writing_prompt(self) -> tuple:
        prompts = [
            "Write about your favorite season and why you like it.",
            "Describe what you did during your last vacation.",
            "Write a story about a magical adventure.",
            "Explain how to make your favorite sandwich.",
            "Describe your dream job and why you want it."
        ]
        
        prompt = random.choice(prompts)
        sample_answer = f"This is a sample response to: {prompt}. Students would provide their own creative writing here."
        
        return prompt, sample_answer
    
    def generate_synthetic_document_image(self) -> tuple:
        # Create a simple document image
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        text_lines = [
            "DOCUMENT HEADER",
            "This is a sample document for testing purposes.",
            "Line 3: Additional information here.",
            "Date: " + datetime.now().strftime('%Y-%m-%d'),
            "Status: Active"
        ]
        
        y_pos = 50
        for line in text_lines:
            draw.text((50, y_pos), line, fill='black')
            y_pos += 40
        
        full_text = '\n'.join(text_lines)
        return img, full_text
    
    def generate_synthetic_text_image(self) -> tuple:
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        text = f"Sample Text {random.randint(1000, 9999)}"
        draw.text((100, 200), text, fill='black')
        
        return img, text
    
    def generate_synthetic_form_image(self) -> tuple:
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        form_text = [
            "APPLICATION FORM",
            "Name: ________________",
            "Address: ________________",
            "Phone: ________________",
            "Date: " + datetime.now().strftime('%Y-%m-%d')
        ]
        
        y_pos = 100
        for line in form_text:
            draw.text((100, y_pos), line, fill='black')
            y_pos += 50
        
        return img, '\n'.join(form_text)
    
    def generate_synthetic_receipt_image(self) -> tuple:
        img = Image.new('RGB', (400, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        receipt_text = [
            "RECEIPT",
            "Store Name",
            "Item 1    $10.99",
            "Item 2    $5.50",
            "Tax       $1.32",
            "Total     $17.81",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        
        y_pos = 50
        for line in receipt_text:
            draw.text((50, y_pos), line, fill='black')
            y_pos += 40
        
        return img, '\n'.join(receipt_text)
    
    def generate_authentic_document(self) -> str:
        return f"""OFFICIAL DOCUMENT #{random.randint(1000, 9999)}
Date: {datetime.now().strftime('%Y-%m-%d')}
Issued by: Government Office

This document certifies that the information contained herein is accurate and verified.

Name: John Smith
ID: {random.randint(100000, 999999)}
Valid until: {(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')}

Official Signature: _______________
Stamp: [OFFICIAL SEAL]"""
    
    def generate_forged_document(self, authentic_doc: str) -> dict:
        # Create a forged version with subtle changes
        forged = authentic_doc.replace("John Smith", "John Smyth")  # Name alteration
        forged = forged.replace("[OFFICIAL SEAL]", "[SEAL]")  # Missing official marking
        
        indicators = [
            "Name spelling alteration",
            "Missing 'OFFICIAL' in seal marking",
            "Potential tampering detected"
        ]
        
        return {"text": forged, "indicators": indicators}
    
    def create_synthetic_admin_documents(self, save_path: Path, doc_type: str):
        """Create synthetic administrative documents"""
        save_path.mkdir(parents=True, exist_ok=True)
        
        data = []
        for i in range(100):
            if doc_type == "transcripts":
                doc = self.generate_transcript()
            elif doc_type == "report_cards":
                doc = self.generate_report_card()
            elif doc_type == "certificates":
                doc = self.generate_certificate()
            else:  # forms
                doc = self.generate_admin_form()
            
            data.append({
                "id": f"{doc_type}_{i:05d}",
                "content": doc,
                "type": doc_type,
                "synthetic": True
            })
        
        with open(save_path / f"synthetic_{doc_type}.json", "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Created 100 synthetic {doc_type} at {save_path}")
    
    def generate_transcript(self) -> str:
        subjects = ["Mathematics", "English", "Science", "History", "Art"]
        grades = ["A", "B", "C", "B+", "A-"]
        
        transcript = f"""ACADEMIC TRANSCRIPT
Student: Student Name {random.randint(100, 999)}
ID: {random.randint(10000, 99999)}
Academic Year: 2023-2024

GRADES:
"""
        for subject in subjects:
            grade = random.choice(grades)
            transcript += f"{subject}: {grade}\n"
        
        transcript += f"\nGPA: {random.uniform(2.5, 4.0):.2f}\nIssued: {datetime.now().strftime('%Y-%m-%d')}"
        return transcript
    
    def generate_report_card(self) -> str:
        return f"""REPORT CARD
Student: Student {random.randint(100, 999)}
Grade: {random.choice(['3rd', '4th', '5th', '6th'])}
Term: Fall 2024

Mathematics: {random.choice(['Excellent', 'Good', 'Satisfactory'])}
Reading: {random.choice(['Excellent', 'Good', 'Satisfactory'])}
Science: {random.choice(['Excellent', 'Good', 'Satisfactory'])}

Teacher Comments: Shows good progress in all areas.
"""
    
    def generate_certificate(self) -> str:
        return f"""CERTIFICATE OF COMPLETION
This certifies that
STUDENT NAME {random.randint(100, 999)}
has successfully completed
{random.choice(['Elementary School', 'Middle School', 'High School'])}
Date: {datetime.now().strftime('%Y-%m-%d')}
Principal: _______________"""
    
    def generate_admin_form(self) -> str:
        return f"""ADMINISTRATIVE FORM
Form ID: ADM-{random.randint(1000, 9999)}
Date: {datetime.now().strftime('%Y-%m-%d')}

Student Information:
Name: ________________
Address: ________________
Parent/Guardian: ________________
Emergency Contact: ________________

Office Use Only:
Processed by: _______________
Date processed: _______________"""
    
    def infer_subject_from_name(self, name: str) -> str:
        if "math" in name.lower():
            return "math"
        elif "science" in name.lower():
            return "science"
        elif "social" in name.lower():
            return "social_studies"
        elif "reading" in name.lower():
            return "reading"
        else:
            return "writing"
    
    def infer_image_type_from_name(self, name: str) -> str:
        if "text" in name.lower():
            return "text"
        elif "form" in name.lower():
            return "form"
        elif "receipt" in name.lower():
            return "receipt"
        else:
            return "document"
    
    def generate_completion_report(self):
        """Generate a final report of dataset completion"""
        report = {
            "completion_date": datetime.now().isoformat(),
            "total_datasets": 0,
            "filled_datasets": 0,
            "categories": {}
        }
        
        for category_path in self.raw_datasets_dir.iterdir():
            if category_path.is_dir():
                category_name = category_path.name
                report["categories"][category_name] = {
                    "total": 0,
                    "filled": 0,
                    "datasets": []
                }
                
                for dataset_path in category_path.iterdir():
                    if dataset_path.is_dir():
                        report["total_datasets"] += 1
                        report["categories"][category_name]["total"] += 1
                        
                        # Check if has meaningful data
                        has_data = any(
                            f.stat().st_size > 100 
                            for f in dataset_path.rglob("*") 
                            if f.is_file() and not f.name.startswith('.')
                        )
                        
                        if has_data:
                            report["filled_datasets"] += 1
                            report["categories"][category_name]["filled"] += 1
                            status = "✅ Filled"
                        else:
                            status = "❌ Empty"
                        
                        report["categories"][category_name]["datasets"].append({
                            "name": dataset_path.name,
                            "status": status
                        })
        
        # Save report
        with open(self.base_dir / "completion_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        completion_rate = (report["filled_datasets"] / report["total_datasets"]) * 100
        logger.info(f"""
🎉 DATASET FILLING COMPLETE!
📊 Total datasets: {report['total_datasets']}
✅ Filled datasets: {report['filled_datasets']}
📈 Completion rate: {completion_rate:.1f}%
        """)
        
        return report

def main():
    filler = ComprehensiveDatasetFiller()
    filler.fill_all_gaps()

if __name__ == "__main__":
    main()
