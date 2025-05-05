import sys
import os
import asyncio
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import json
from ydata_profiling import ProfileReport
# Configure environment first
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "false"
os.environ["GEMINI_USE_REST"] = "true"
os.environ["GRPC_POLL_STRATEGY"] = "poll"

# Add project directory to Python path
sys.path.append(str(Path(__file__).parent))
load_dotenv()


CSV_PATH = "/Users/noursameh/Downloads/eday_df/train.csv"
REPORTS_DIR = Path("reports")

async def main():
    """Run pipeline with your actual dataset"""
    try:
        # Validate environment
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY missing in .env file")

        # Load dataset
        if not Path(CSV_PATH).exists():
            raise FileNotFoundError(f"CSV not found at {CSV_PATH}")
            
        df = pd.read_csv(CSV_PATH)
        print(f"✅ Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

        # Initialize reporting
        REPORTS_DIR.mkdir(exist_ok=True)
        report_path = REPORTS_DIR / f"report_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.json"

        # Run pipeline
        print("\n🚀 Starting insight generation pipeline...")
        async for output in Start_Auto_InsightGen(project_id="real_data_run"):
            if isinstance(output, tuple):
                _, metadata = output
                if "report" in metadata:
                    with open(report_path, "w") as f:
                        json.dump(metadata["report"], f, indent=2)
                    print_report_summary(metadata["report"], report_path)

        print("\n🎉 Pipeline completed successfully!")

    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        raise

def print_report_summary(report: dict, path: Path):
    """Print human-readable report summary"""
    print(f"\n📄 Report saved to: {path}")
    print(f"📅 Generated at: {report.get('metadata', {}).get('generation_date', '')}")
    print("\n🔍 Key Findings:")
    for category, items in report.get('description_insights', {}).get('key_findings', {}).items():
        print(f"  {category.capitalize()}:")
        for item in items[:3]:  # Show top 3 items per category
            print(f"    - {item}")
    
    print("\n📊 Data Sample:")
    sample_df = pd.DataFrame(report.get('description_insights', {}).get('dataset_head', {}))
    print(sample_df.head(3).to_string(index=False))

if __name__ == "__main__":
    asyncio.run(main())