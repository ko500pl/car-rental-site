"""Run the complete local/CI quality gate and write a short artifact report."""
from __future__ import annotations
import argparse, datetime as dt, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def size_label(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB": return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default="dist"); p.add_argument("--report", default="artifacts/quality-gate-summary.md")
    p.add_argument("--node"); p.add_argument("--strict", action="store_true"); args = p.parse_args()
    output, report, python = (ROOT/args.output).resolve(), (ROOT/args.report).resolve(), sys.executable
    stages = [
        ("Environment check", [python,"scripts/check_environment.py"]),
        ("Project layout", [python,"scripts/check_project_layout.py"]),
        ("Content validation", [python,"build.py","--validate-only"]),
        ("Unit tests", [python,"-m","unittest","discover","-s","tests","-q"]),
        ("JavaScript syntax", [python,"scripts/check_javascript_syntax.py"]),
    ]
    if args.node: stages[-1][1].extend(["--node",args.node])
    build = [python,"build.py",args.output] + (["--strict"] if args.strict else [])
    stages += [("Site build",build),("HTML and internal links",[python,"scripts/check_internal_links.py",args.output])]
    started, completed = dt.datetime.now(dt.timezone.utc), []
    for index,(name,command) in enumerate(stages,1):
        print(f"\n==> [{index}/{len(stages)}] {name}",flush=True)
        result = subprocess.run(command,cwd=ROOT)
        if result.returncode:
            report.parent.mkdir(parents=True,exist_ok=True)
            report.write_text(f"# Quality gate — FAILED\n\n- ეტაპი: **{name}**\n- დასრულებული ეტაპები: {len(completed)}/{len(stages)}\n- დრო (UTC): {dt.datetime.now(dt.timezone.utc).isoformat()}\n\nკონსოლის ზემოთ მოცემული კონკრეტული შეცდომა გაასწორეთ და კარიბჭე თავიდან გაუშვით.\n",encoding="utf-8")
            print(f"\nQUALITY GATE FAILED: {name}\nReport: {report.relative_to(ROOT)}"); return result.returncode or 1
        completed.append(name)
    files=[x for x in output.rglob("*") if x.is_file()]; html=sum(x.suffix.lower()==".html" for x in files); size=sum(x.stat().st_size for x in files)
    elapsed=(dt.datetime.now(dt.timezone.utc)-started).total_seconds(); report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(f"# Quality gate — PASSED\n\n- ვერსია: `{os.environ.get('GITHUB_SHA','local')[:12]}`\n- დასრულებული ეტაპები: {len(completed)}/{len(stages)}\n- HTML გვერდები: {html:,}\n- არტეფაქტის ფაილები: {len(files):,}\n- არტეფაქტის ზომა: {size_label(size)}\n- ხანგრძლივობა: {elapsed:.1f} წამი\n- დრო (UTC): {dt.datetime.now(dt.timezone.utc).isoformat()}\n- strict რეჟიმი: {'კი' if args.strict else 'არა'}\n\nDeploy ამ ბრძანების ნაწილი არ არის და ცალკე დამტკიცებას საჭიროებს.\n",encoding="utf-8")
    print(f"\nQUALITY GATE PASSED\nArtifact: {output.relative_to(ROOT)} ({len(files):,} files, {size_label(size)})\nReport: {report.relative_to(ROOT)}"); return 0

if __name__ == "__main__": raise SystemExit(main())
