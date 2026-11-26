"""Pure, narrow Video::setStatus patch for server-marked frontend imports.

Unmarked records keep native behavior. Retain the helper/model hook while marked
imports are queued or processing; disable new imports first during rollback.
"""
import re

def patch(source: str) -> str:
    if 'DM_IMPORT_DRAFT_HOLD' in source:
        return source
    signature = re.compile(r'(function\s+setStatus\s*\(\s*\$status\b[^)]*\)\s*(?::\s*[\w\\?]+)?\s*\{)')
    if len(signature.findall(source)) != 1:
        raise ValueError('Native Video status setter contract changed')
    hook = """
            // DM_IMPORT_DRAFT_HOLD: server-owned frontend import records only.
            $dmImportHelper = dirname(__DIR__) . '/divine-api/import-hold.php';
            if (is_file($dmImportHelper)) { require_once $dmImportHelper; }
            if (class_exists('DivineImportHold')) { $status = DivineImportHold::status($this, $status); }
"""
    return signature.sub(lambda match: match.group() + hook, source, count=1)
