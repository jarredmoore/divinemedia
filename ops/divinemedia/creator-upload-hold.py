"""Narrow native uploader patch: only the authenticated adapter can defer publishing."""
def patched(source: bytes) -> bytes:
    needle=b'$video->setAutoStatus(Video::STATUS_ACTIVE);'
    if source.count(needle)!=1:
        raise ValueError('Native uploader changed; inspect before applying')
    replacement=b'''if (defined('DM_FRONTEND_API') && !empty($GLOBALS['dm_frontend_upload_hold'])) {
                $video->setStatus(Video::STATUS_INACTIVE);
                $video->save();
            } else {
                $video->setAutoStatus(Video::STATUS_ACTIVE);
            }'''
    return source.replace(needle,replacement)
