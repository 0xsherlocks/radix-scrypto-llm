#!/usr/bin/env python3
"""
RadixDLT RAG System - OpenRouter Version
Uses OpenRouter API for access to multiple LLMs at competitive prices
"""
# Add at the very top:
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

try:
    from langchain.document_loaders import DirectoryLoader, TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import HuggingFaceEmbeddings  # Free local embeddings
    from langchain.vectorstores import Chroma
    from langchain.chains import RetrievalQA
    from langchain.llms import OpenAI  # We'll use this with OpenRouter endpoint
    from langchain.schema import Document
    from langchain.prompts import PromptTemplate
    from langchain.chat_models import ChatOpenAI
except ImportError:
    print("❌ Required packages not found. Please install:")
    print("pip install langchain openai chromadb sentence-transformers")
    sys.exit(1)

class RadixRAGSystemOpenRouter:
    def __init__(self, 
                 knowledge_base_path="kb/cleaned", 
                 persist_directory="./vectorstore_openrouter",
                 model_name="anthropic/claude-3.5-sonnet"):  # Default to Claude 3.5 Sonnet
        
        self.kb_path = Path(knowledge_base_path)
        self.persist_dir = persist_directory
        self.model_name = model_name
        self.vectorstore = None
        self.qa_chain = None
        
        # Model recommendations with costs (approximate per 1M tokens)
        self.available_models = {
            # Premium models (best quality)
            "anthropic/claude-3.5-sonnet": {"cost": "$3", "quality": "Excellent", "best_for": "Technical docs, coding"},
            "openai/gpt-4o": {"cost": "$5", "quality": "Excellent", "best_for": "General purpose"},
            
            # Good balance models
            "anthropic/claude-3-haiku": {"cost": "$0.25", "quality": "Good", "best_for": "Fast responses"},
            "meta-llama/llama-3.1-70b-instruct": {"cost": "$0.52", "quality": "Very Good", "best_for": "Technical content"},
            "mistralai/mistral-large": {"cost": "$3", "quality": "Very Good", "best_for": "Reasoning"},
            
            # Budget models
            "meta-llama/llama-3.1-8b-instruct": {"cost": "$0.055", "quality": "Good", "best_for": "Budget option"},
            "mistralai/mistral-7b-instruct": {"cost": "$0.06", "quality": "Good", "best_for": "Fast & cheap"},
            "qwen/qwen-2.5-72b-instruct": {"cost": "$0.56", "quality": "Good", "best_for": "Technical docs"},
        }
        
        # Check if knowledge base exists
        if not self.kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found at {knowledge_base_path}")
        
        # Check API key
        if not os.getenv("OPENROUTER_API_KEY"):
            print("❌ OPENROUTER_API_KEY not found!")
            print("Get your API key from: https://openrouter.ai/keys")
            print("Then set it: export OPENROUTER_API_KEY=your_key_here")
            sys.exit(1)
        
        # Initialize system
        print("🚀 Initializing RadixDLT RAG System (OpenRouter)...")
        print(f"🤖 Using model: {model_name}")
        if model_name in self.available_models:
            info = self.available_models[model_name]
            print(f"💰 Cost: ~{info['cost']}/1M tokens | Quality: {info['quality']}")
        self.setup_vectorstore()
        self.setup_qa_chain()
        print("✅ RAG System ready!")
    
    def show_available_models(self):
        """Show available models with pricing and recommendations."""
        print("\n🎯 Available OpenRouter Models:")
        print("=" * 80)
        
        categories = {
            "Premium (Best Quality)": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o"],
            "Balanced (Good Quality/Price)": [
                "anthropic/claude-3-haiku", 
                "meta-llama/llama-3.1-70b-instruct", 
                "mistralai/mistral-large",
                "qwen/qwen-2.5-72b-instruct"
            ],
            "Budget (Cheap & Fast)": [
                "meta-llama/llama-3.1-8b-instruct", 
                "mistralai/mistral-7b-instruct"
            ]
        }
        
        for category, models in categories.items():
            print(f"\n📊 {category}:")
            for model in models:
                if model in self.available_models:
                    info = self.available_models[model]
                    print(f"  • {model}")
                    print(f"    Cost: {info['cost']}/1M tokens | Best for: {info['best_for']}")
        
        print(f"\n🔥 RECOMMENDED: anthropic/claude-3.5-sonnet (Best for technical docs)")
        print(f"💰 BUDGET: meta-llama/llama-3.1-8b-instruct (20x cheaper)")
    
    def load_documents(self) -> List[Document]:
        """Load all markdown and rust files from knowledge base."""
        print("📚 Loading documents from knowledge base...")
        
        documents = []
        
        # Load markdown files
        try:
            md_loader = DirectoryLoader(
                str(self.kb_path), 
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            md_docs = md_loader.load()
        except Exception as e:
            print(f"⚠️  Error loading markdown files: {e}")
            md_docs = []
        
        # Load rust files
        try:
            rs_loader = DirectoryLoader(
                str(self.kb_path), 
                glob="**/*.rs",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            rs_docs = rs_loader.load()
        except Exception as e:
            print(f"⚠️  Error loading rust files: {e}")
            rs_docs = []
        
        # Combine and add metadata
        all_docs = md_docs + rs_docs
        
        for doc in all_docs:
            # Add file type metadata
            file_path = Path(doc.metadata['source'])
            doc.metadata['file_type'] = file_path.suffix
            doc.metadata['filename'] = file_path.name
            doc.metadata['directory'] = file_path.parent.name
            
            # Add content type metadata
            if 'example' in str(file_path).lower():
                doc.metadata['content_type'] = 'example'
            elif 'src' in str(file_path).lower():
                doc.metadata['content_type'] = 'source'
            elif file_path.suffix == '.md':
                doc.metadata['content_type'] = 'documentation'
            else:
                doc.metadata['content_type'] = 'code'
        
        documents.extend(all_docs)
        print(f"📄 Loaded {len(documents)} documents")
        return documents
    
    def setup_vectorstore(self):
        """Set up or load the vector store with local embeddings."""
        print("🔍 Setting up vector store with local embeddings...")
        
        # Use free local embeddings (no API key needed)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",  # Small but good
            model_kwargs={'device': 'cpu'},  # Use CPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Check if vector store already exists
        if os.path.exists(self.persist_dir):
            print("📁 Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=embeddings
            )
            try:
                count = self.vectorstore._collection.count()
                print(f"✅ Loaded vector store with {count} documents")
            except:
                print("✅ Loaded existing vector store")
        else:
            print("🔄 Creating new vector store...")
            
            # Load documents
            documents = self.load_documents()
            
            if not documents:
                raise RuntimeError("No documents found to process!")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,  # Good size for most models
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            splits = text_splitter.split_documents(documents)
            print(f"✂️  Split into {len(splits)} chunks")
            
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=self.persist_dir
            )
            
            # Persist the vector store
            self.vectorstore.persist()
            print(f"💾 Created and saved vector store with {len(splits)} chunks")
    
    def setup_qa_chain(self):
        """Set up the question-answering chain with OpenRouter."""
        print("🔗 Setting up QA chain with OpenRouter...")
        
        # Custom prompt optimized for technical documentation
        prompt_template = """You are an expert RadixDLT and Scrypto developer assistant. Use the provided context to answer questions about RadixDLT, Scrypto, blockchain development, and Rust programming.

Guidelines:
- Provide accurate, technical information based on the context
- Include relevant code examples when available
- Explain concepts clearly for developers
- If the context doesn't contain enough information, say so
- Focus on practical, actionable advice

Context:
{context}

Question: {question}

Answer: """

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Set up OpenRouter LLM
        llm = ChatOpenAI(
    model=self.model_name,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.1,
    max_tokens=1024,
)
        
        # Set up retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 6}  # Retrieve top 6 most relevant chunks
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        print("✅ QA chain ready")
    
    def ask(self, question: str) -> Dict[str, Any]:
        """Ask a question and get an answer with sources."""
        if not self.qa_chain:
            raise RuntimeError("QA chain not initialized")
        
        print(f"\n❓ Question: {question}")
        print("🔍 Searching knowledge base...")
        
        # Get answer
        result = self.qa_chain({"query": question})
        
        # Format response
        response = {
            "question": question,
            "answer": result["result"],
            "sources": []
        }
        
        # Add source information
        for doc in result["source_documents"]:
            source_info = {
                "filename": doc.metadata.get("filename", "Unknown"),
                "file_type": doc.metadata.get("file_type", "Unknown"),
                "content_type": doc.metadata.get("content_type", "Unknown"),
                "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            response["sources"].append(source_info)
        
        return response
    
    def print_answer(self, response: Dict[str, Any]):
        """Pretty print the answer with sources."""
        print("\n" + "="*80)
        print("📋 ANSWER")
        print("="*80)
        print(response["answer"])
        
        print(f"\n📚 SOURCES ({len(response['sources'])} files used):")
        print("-"*50)
        
        for i, source in enumerate(response["sources"], 1):
            print(f"{i}. {source['filename']} ({source['content_type']})")
            print(f"   Preview: {source['snippet']}")
            print()
        
        print("="*80)
    
    def interactive_mode(self):
        """Start interactive Q&A session."""
        print(f"\n🎯 RadixDLT Interactive Q&A (Using {self.model_name})")
        print("Type 'exit' to quit, 'help' for suggestions, 'models' to see available models")
        print("-" * 70)
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if question.lower() == 'help':
                    self.show_help()
                    continue
                
                if question.lower() == 'models':
                    self.show_available_models()
                    continue
                
                if not question:
                    continue
                
                response = self.ask(question)
                self.print_answer(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show example questions."""
        examples = [
            "How do I create a blueprint in Scrypto?",
            "What is a component in RadixDLT?",
            "Show me how to create a token in Scrypto",
            "How does the Radix Engine work?",
            "What are badges in RadixDLT?",
            "How do I implement access control in Scrypto?",
            "Show me examples of Rust code for RadixDLT",
            "What is a resource in RadixDLT?",
            "How do I deploy a blueprint to RadixDLT?",
            "What are the main Scrypto data types?",
        ]
        
        print("\n💡 Example questions you can ask:")
        print("-" * 40)
        for example in examples:
            print(f"• {example}")

def main():
    """Main function to run the RAG system."""
    print("RadixDLT RAG System (OpenRouter)")
    print("=" * 50)
    
    try:
        # Initialize RAG system with your preferred model
        # Recommendations:
        # - Best quality: "anthropic/claude-3.5-sonnet"
        # - Budget option: "meta-llama/llama-3.1-8b-instruct" 
        # - Balanced: "anthropic/claude-3-haiku"
        
        rag = RadixRAGSystemOpenRouter(model_name="anthropic/claude-3.5-sonnet")
        
        # Show model info
        print(f"\n💡 You can change the model by editing the model_name parameter")
        print(f"🔧 Type 'models' during chat to see all available options")
        
        # Start interactive mode
        rag.interactive_mode()
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure you've run clean_kb.py first to create the knowledge base")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())