import requests
from app.core.config import settings

class GrobidError(Exception):
    pass

def parse_pdf(file_path: str, timeout: int = 60) -> str:
    """
    Sends a PDF to the local GROBID container and returns raw TEI XML.
    Raises GrobidError if GROBID is unreachable or returns a non-200.
    """
    url = f"{settings.grobid_url}/api/processFulltextDocument"

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                url,
                files={"input": f},
                data={
                    "consolidateHeader": "1",
                    "consolidateCitations": "0",
                    "teiCoordinates": "p",  # ask for paragraph coordinates -> page numbers later
                },
                timeout=timeout,
            )
    except requests.exceptions.ConnectionError:
        raise GrobidError("GROBID is not reachable — is the Docker container running?")
    except requests.exceptions.Timeout:
        raise GrobidError(f"GROBID timed out after {timeout}s on {file_path}")

    if response.status_code != 200:
        raise GrobidError(f"GROBID returned {response.status_code}: {response.text[:300]}")

    return response.text  