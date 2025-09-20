#!/usr/bin/env python3
"""
Scrypto Auto-Testing System
Completes the assignment requirements by adding:
1. Auto cargo scrypto test execution
2. Error retry logic
3. Results tracking in JSON
"""

import os
import json
import re
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class ScryptoAutoTester:
    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.results_file = Path("results.json")
        
        # Load existing results or create new
        self.results = self.load_results()
    
    def load_results(self) -> Dict[str, Any]:
        """Load existing results or create new structure."""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "total_attempts": 0,
                "successful_blueprints": 0,
                "failed_blueprints": 0,
                "retry_count": 0,
                "blueprints": []
            }
    
    def save_results(self):
        """Save results to JSON file."""
        self.results["last_updated"] = datetime.now().isoformat()
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def extract_rust_code(self, text: str) -> List[str]:
        """Extract Rust/Scrypto code blocks from AI response."""
        # Pattern for code blocks
        patterns = [
            r'```rust\n(.*?)\n```',
            r'```scrypto\n(.*?)\n```',
            r'```rs\n(.*?)\n```',
            r'```\n(.*?)\n```',  # Generic code blocks
        ]
        
        code_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            code_blocks.extend(matches)
        
        # Filter for likely Scrypto code
        scrypto_blocks = []
        for code in code_blocks:
            if any(keyword in code for keyword in ['blueprint', 'component', 'use scrypto', 'impl', 'pub fn']):
                scrypto_blocks.append(code.strip())
        
        return scrypto_blocks
    
    def create_scrypto_project(self, code: str, project_name: str) -> Path:
        """Create a temporary Scrypto project with the generated code."""
        project_dir = self.output_dir / project_name
        
        # Clean existing project
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
        
        # Create new Scrypto project
        try:
            subprocess.run(
                ["scrypto", "new-package", str(project_dir)],
                check=True,
                capture_output=True,
                cwd=self.output_dir
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Scrypto project: {e}")
            return None
        
        # Write the generated code to lib.rs
        lib_file = project_dir / "src" / "lib.rs"
        with open(lib_file, 'w') as f:
            f.write(code)
        
        return project_dir
    
    def run_scrypto_test(self, project_dir: Path) -> Tuple[bool, str, str]:
        """Run cargo scrypto test and return results."""
        try:
            result = subprocess.run(
                ["cargo", "test"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Test timed out after 60 seconds"
        except Exception as e:
            return False, "", str(e)
    
    def generate_code_with_retry(self, prompt: str, max_retries: int = 1) -> Dict[str, Any]:
        """Generate Scrypto code with automatic retry on compilation errors."""
        attempt = 0
        original_prompt = prompt
        
        while attempt <= max_retries:
            print(f"🤖 Attempt {attempt + 1}: Generating code...")
            
            # Get AI response
            try:
                response = self.rag_system.ask(prompt)
                answer = response['answer']
                sources = response['sources']
            except Exception as e:
                return {
                    "success": False,
                    "error": f"AI generation failed: {e}",
                    "attempts": attempt + 1
                }
            
            # Extract code blocks
            code_blocks = self.extract_rust_code(answer)
            
            if not code_blocks:
                if attempt < max_retries:
                    prompt = f"{original_prompt}\n\nPlease provide complete Rust/Scrypto code in a code block."
                    attempt += 1
                    continue
                else:
                    return {
                        "success": False,
                        "error": "No code blocks found in AI response",
                        "ai_response": answer,
                        "attempts": attempt + 1
                    }
            
            # Test each code block
            for i, code in enumerate(code_blocks):
                project_name = f"test_blueprint_{datetime.now().strftime('%H%M%S')}_{i}"
                
                print(f"📝 Testing code block {i + 1}...")
                
                # Create project
                project_dir = self.create_scrypto_project(code, project_name)
                if not project_dir:
                    continue
                
                # Run tests
                test_success, stdout, stderr = self.run_scrypto_test(project_dir)
                
                if test_success:
                    print(f"✅ Code block {i + 1} passed tests!")
                    return {
                        "success": True,
                        "code": code,
                        "project_dir": str(project_dir),
                        "test_output": stdout,
                        "ai_response": answer,
                        "sources": sources,
                        "attempts": attempt + 1
                    }
                else:
                    print(f"❌ Code block {i + 1} failed tests")
                    
                    # If this is not the last attempt, create retry prompt
                    if attempt < max_retries:
                        error_context = f"Compilation/test errors:\n{stderr}\n\nCode that failed:\n{code}"
                        prompt = f"{original_prompt}\n\nThe previous code had errors:\n{error_context}\n\nPlease fix the errors and provide corrected Scrypto code."
            
            attempt += 1
        
        # All attempts failed
        return {
            "success": False,
            "error": "All code generation attempts failed",
            "last_stderr": stderr if 'stderr' in locals() else "No test output available",
            "attempts": attempt
        }
    
    def test_blueprint_generation(self, prompt: str, test_name: str = None) -> Dict[str, Any]:
        """Main function to test blueprint generation with full pipeline."""
        if not test_name:
            test_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n🚀 Starting test: {test_name}")
        print(f"📝 Prompt: {prompt}")
        print("-" * 80)
        
        start_time = datetime.now()
        
        # Generate and test code
        result = self.generate_code_with_retry(prompt, max_retries=1)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Record results
        test_record = {
            "test_name": test_name,
            "prompt": prompt,
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "success": result["success"],
            "attempts": result["attempts"],
            "error": result.get("error"),
            "code": result.get("code"),
            "test_output": result.get("test_output"),
            "ai_sources_used": len(result.get("sources", []))
        }
        
        # Update global results
        self.results["total_attempts"] += result["attempts"]
        if result["success"]:
            self.results["successful_blueprints"] += 1
        else:
            self.results["failed_blueprints"] += 1
            
        if result["attempts"] > 1:
            self.results["retry_count"] += result["attempts"] - 1
        
        self.results["blueprints"].append(test_record)
        self.save_results()
        
        # Print summary
        if result["success"]:
            print(f"✅ SUCCESS: {test_name}")
            print(f"🕐 Time: {duration:.1f}s | Attempts: {result['attempts']}")
            print(f"📊 Test Output Preview:")
            print(result["test_output"][-200:])  # Last 200 chars
        else:
            print(f"❌ FAILED: {test_name}")
            print(f"🕐 Time: {duration:.1f}s | Attempts: {result['attempts']}")
            print(f"❌ Error: {result['error']}")
        
        print("-" * 80)
        return test_record
    
    def run_demo_tests(self) -> Dict[str, Any]:
        """Run the demo tests required by the assignment."""
        print("🎯 Running Demo Tests for Assignment Completion")
        print("=" * 80)
        
        # Test 1: Simple Blueprint (Assignment requirement)
        self.test_blueprint_generation(
            "Create a simple Scrypto blueprint that stores a greeting message and has a function to return it",
            "simple_greeting_blueprint"
        )
        
        # Test 2: Admin-controlled NFT (Assignment requirement)  
        self.test_blueprint_generation(
            "Create a Scrypto blueprint for an admin-controlled NFT with mint and burn functions",
            "admin_nft_blueprint"
        )
        
        # Test 3: Token Blueprint
        self.test_blueprint_generation(
            "Create a Scrypto blueprint that creates a simple token with fixed supply",
            "simple_token_blueprint"
        )
        
        # Print final summary
        self.print_final_summary()
        return self.results
    
    def print_final_summary(self):
        """Print final test summary."""
        print("\n" + "=" * 80)
        print("🏆 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Successful Blueprints: {self.results['successful_blueprints']}")
        print(f"❌ Failed Blueprints: {self.results['failed_blueprints']}")
        print(f"🔄 Total Retries: {self.results['retry_count']}")
        print(f"📊 Success Rate: {self.results['successful_blueprints']/(self.results['successful_blueprints'] + self.results['failed_blueprints']) * 100:.1f}%")
        print(f"📁 Results saved to: {self.results_file}")
        print(f"📂 Generated code in: {self.output_dir}/")
        
        # Assignment completion check
        if self.results['successful_blueprints'] >= 1:
            print("\n🎉 ASSIGNMENT REQUIREMENT MET!")
            print("✅ ≥ 1 blueprint passes tests")
        else:
            print("\n⚠️  Assignment requirement not yet met")
            print("❌ Need ≥ 1 blueprint that passes tests")


def main():
    """Main demo function."""
    print("Scrypto Auto-Testing System")
    print("Completing Assignment Requirements")
    print("=" * 50)
    
    try:
        # Load the RAG system
        from rag_system_openrouter import RadixRAGSystemOpenRouter
        
        print("🔄 Loading RAG system...")
        rag = RadixRAGSystemOpenRouter(model_name="meta-llama/llama-3.1-8b-instruct")
        
        # Create auto-tester
        auto_tester = ScryptoAutoTester(rag)
        
        # Run demo tests
        results = auto_tester.run_demo_tests()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())