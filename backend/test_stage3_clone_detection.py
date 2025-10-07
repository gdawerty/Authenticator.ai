"""
Test Script for Enhanced Stage 3 Clone Detection
Demonstrates SimHash & MinHash functionality for the authenticity pipeline
"""

import requests
import json
import os
from datetime import datetime


class Stage3CloneDetectionTester:
    """Test the enhanced Stage 3 clone detection pipeline"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.stage3_url = f"{base_url}/api/stage3"
        
    def test_single_document_analysis(self, file_path):
        """Test clone detection on a single document"""
        print(f"\n=== Testing Single Document Analysis ===")
        print(f"File: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found")
            return None
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'similarity_threshold': 0.85,
                    'document_type': 'test_document'
                }
                
                response = requests.post(
                    f"{self.stage3_url}/analyze",
                    files=files,
                    data=data
                )
                
            if response.status_code == 200:
                result = response.json()
                self._print_analysis_results(result)
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error testing document: {e}")
            return None
    
    def test_batch_analysis(self, documents):
        """Test batch clone detection across multiple documents"""
        print(f"\n=== Testing Batch Analysis ===")
        print(f"Documents: {len(documents)}")
        
        try:
            batch_data = {
                'documents': documents,
                'similarity_threshold': 0.85
            }
            
            response = requests.post(
                f"{self.stage3_url}/batch_analyze",
                json=batch_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self._print_batch_results(result)
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in batch testing: {e}")
            return None
    
    def test_similarity_threshold_update(self, new_threshold):
        """Test updating similarity threshold"""
        print(f"\n=== Testing Threshold Update ===")
        
        try:
            response = requests.put(
                f"{self.stage3_url}/threshold",
                json={'threshold': new_threshold}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Threshold updated: {result}")
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error updating threshold: {e}")
            return None
    
    def get_system_statistics(self):
        """Get clone detection system statistics"""
        print(f"\n=== System Statistics ===")
        
        try:
            response = requests.get(f"{self.stage3_url}/statistics")
            
            if response.status_code == 200:
                stats = response.json()
                self._print_statistics(stats)
                return stats
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return None
    
    def search_similar_documents(self, file_id):
        """Search for documents similar to a specific file ID"""
        print(f"\n=== Searching Similar Documents ===")
        print(f"File ID: {file_id}")
        
        try:
            response = requests.get(f"{self.stage3_url}/search/{file_id}")
            
            if response.status_code == 200:
                result = response.json()
                self._print_search_results(result)
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error searching similar documents: {e}")
            return None
    
    def _print_analysis_results(self, result):
        """Print formatted analysis results"""
        print(f"\nStage 3 Clone Detection Results:")
        print(f"File ID: {result.get('file_id')}")
        print(f"Filename: {result.get('filename')}")
        print(f"Similarity Score: {result.get('similarity_score', 0):.3f}")
        print(f"Duplicates Found: {result.get('duplicates_found', 0)}")
        
        fingerprint_data = result.get('fingerprint_data', {})
        print(f"\nFingerprint Data:")
        print(f"  SimHash: {fingerprint_data.get('simhash', 'N/A')[:16]}...")
        print(f"  MinHash Signature Length: {fingerprint_data.get('minhash_signature_length', 0)}")
        print(f"  Shingles Count: {fingerprint_data.get('shingles_count', 0)}")
        print(f"  Text Length: {fingerprint_data.get('text_length', 0)}")
        
        matches = result.get('similarity_matches', [])
        if matches:
            print(f"\nSimilarity Matches ({len(matches)}):")
            for i, match in enumerate(matches[:5]):  # Show top 5
                print(f"  {i+1}. File: {match.get('filename', 'Unknown')}")
                print(f"     Similarity: {match.get('similarity_score', 0):.3f}")
                print(f"     Method: {match.get('match_method', 'unknown')}")
                if match.get('hamming_distance') is not None:
                    print(f"     Hamming Distance: {match.get('hamming_distance')}")
                if match.get('jaccard_similarity') is not None:
                    print(f"     Jaccard Similarity: {match.get('jaccard_similarity'):.3f}")
                print()
        
        metadata = result.get('metadata', {})
        print(f"Processing Time: {metadata.get('processing_time_ms', 0):.2f}ms")
    
    def _print_batch_results(self, result):
        """Print formatted batch results"""
        print(f"\nBatch Analysis Results:")
        print(f"Batch ID: {result.get('batch_id')}")
        print(f"Total Documents: {result.get('total_documents', 0)}")
        print(f"Processed Documents: {result.get('processed_documents', 0)}")
        
        cross_pairs = result.get('cross_document_pairs', [])
        if cross_pairs:
            print(f"\nCross-Document Similarities ({len(cross_pairs)}):")
            for pair in cross_pairs:
                print(f"  {pair['doc1_filename']} <-> {pair['doc2_filename']}")
                print(f"  Similarity: {pair['cross_similarity']:.3f}")
                print()
    
    def _print_statistics(self, stats):
        """Print formatted system statistics"""
        print(f"Total Fingerprints: {stats.get('total_fingerprints', 0)}")
        print(f"Total Similarity Matches: {stats.get('total_similarity_matches', 0)}")
        print(f"Average Similarity Score: {stats.get('average_similarity_score', 0):.3f}")
        print(f"SimHash Bits: {stats.get('simhash_bits', 0)}")
        print(f"MinHash Permutations: {stats.get('minhash_permutations', 0)}")
        print(f"Similarity Threshold: {stats.get('similarity_threshold', 0):.3f}")
        
        method_dist = stats.get('method_distribution', {})
        if method_dist:
            print(f"\nMethod Distribution:")
            for method, count in method_dist.items():
                print(f"  {method}: {count}")
    
    def _print_search_results(self, result):
        """Print formatted search results"""
        print(f"Query File: {result.get('query_filename', 'Unknown')}")
        print(f"Total Matches: {result.get('total_matches', 0)}")
        
        similar_docs = result.get('similar_documents', [])
        if similar_docs:
            print(f"\nSimilar Documents:")
            for i, doc in enumerate(similar_docs):
                print(f"  {i+1}. {doc.get('filename', 'Unknown')}")
                print(f"     Similarity: {doc.get('similarity_score', 0):.3f}")
                print(f"     Method: {doc.get('match_method', 'unknown')}")


def run_comprehensive_test():
    """Run comprehensive test of Stage 3 clone detection"""
    print("🚀 Starting Enhanced Stage 3 Clone Detection Tests")
    print("=" * 60)
    
    tester = Stage3CloneDetectionTester()
    
    # Test 1: System Statistics (before any processing)
    print("\n📊 Getting initial system statistics...")
    initial_stats = tester.get_system_statistics()
    
    # Test 2: Single document analysis
    print("\n📄 Testing single document analysis...")
    test_files = [
        "backend/test_document.txt",
        "backend/test_document_similar.txt"
    ]
    
    file_ids = []
    for file_path in test_files:
        if os.path.exists(file_path):
            result = tester.test_single_document_analysis(file_path)
            if result:
                file_ids.append(result.get('file_id'))
        else:
            print(f"⚠️  Test file not found: {file_path}")
    
    # Test 3: Batch analysis
    print("\n📚 Testing batch analysis...")
    batch_documents = [
        {
            'file_id': 'test_doc_1',
            'filename': 'sample1.txt',
            'text': 'This is a test document for clone detection. It contains sample text for testing fingerprinting capabilities.',
            'document_type': 'test'
        },
        {
            'file_id': 'test_doc_2', 
            'filename': 'sample2.txt',
            'text': 'This is a test document for clone detection. It contains sample text for testing fingerprinting capabilities with slight modifications.',
            'document_type': 'test'
        },
        {
            'file_id': 'test_doc_3',
            'filename': 'different.txt',
            'text': 'Completely different content about machine learning and artificial intelligence applications in document processing.',
            'document_type': 'test'
        }
    ]
    
    batch_result = tester.test_batch_analysis(batch_documents)
    
    # Test 4: Threshold update
    print("\n⚙️  Testing threshold update...")
    tester.test_similarity_threshold_update(0.75)
    
    # Test 5: Search similar documents
    if file_ids:
        print("\n🔍 Testing similar document search...")
        tester.search_similar_documents(file_ids[0])
    
    # Test 6: Final statistics
    print("\n📊 Getting final system statistics...")
    final_stats = tester.get_system_statistics()
    
    print("\n✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_comprehensive_test()
