import json
from io import StringIO
from typing import NamedTuple
from zipfile import ZipFile

from rest_framework.exceptions import ValidationError

class HSAManifest(NamedTuple):
    hearthstone_version: str
    accessibility_version: str
    assembly_csharp_sha256: str

def parse_manifest(patch: ZipFile) -> HSAManifest:
    try:
        manifest = json.load(patch.open("patch/Accessibility/hsa_manifest.json", "r"))
        return HSAManifest(manifest["hearthstone_version"], manifest["accessibility_version"], manifest["assembly_csharp_sha256"])
    except Exception as e:
        raise ValidationError(f"Could not parse version from the patch file: {str(e)}")


def parse_changelog(patch: ZipFile) -> str:
    res = StringIO()
    headings_seen = 0
    try:
        for line in patch.open("changelog.md").readlines():
            line = line.decode("ascii")
            if line.startswith("###"):
                headings_seen += 1
                continue
            if headings_seen == 2:
                break
            res.write(line)
        return res.getvalue().strip()

    except Exception as e:
        raise ValidationError(f"Could not parse the changelog from the patch: {str(e)}")
