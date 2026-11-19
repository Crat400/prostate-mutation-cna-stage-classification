"""Download cBioPortal MSK-IMPACT gene-panel definitions for reproducibility.

Run from the repository root: python scripts/download_gene_panels.py
No patient or research data are uploaded.
"""
from pathlib import Path
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "raw" / "panels"
PANEL_IDS = ("IMPACT341", "IMPACT410", "IMPACT468", "IMPACT505")


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for panel_id in PANEL_IDS:
        url = f"https://www.cbioportal.org/api/gene-panels/{panel_id}"
        try:
            request = Request(url, headers={"Accept": "application/json", "User-Agent": "EXSU500-educational-reproducibility"})
            with urlopen(request, timeout=45) as response:
                panel = json.load(response)
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise SystemExit(f"Could not retrieve {panel_id}: {exc}. Manually download {url} and save {DEST / (panel_id + '.json')}") from exc
        if not isinstance(panel, dict) or panel.get("genePanelId") != panel_id:
            raise SystemExit(f"Unexpected response for {panel_id}: incorrect genePanelId")
        genes = panel.get("genes")
        if not isinstance(genes, list) or not genes or not all(isinstance(g, dict) and g.get("hugoGeneSymbol") for g in genes):
            raise SystemExit(f"Unexpected gene list format for {panel_id}")
        destination = DEST / f"{panel_id}.json"
        destination.write_text(json.dumps(panel, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved {destination.relative_to(ROOT)} — {len(genes)} gene records")


if __name__ == "__main__":
    main()
