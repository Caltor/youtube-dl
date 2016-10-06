# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_urllib_parse_urlparse
from .generic import GenericIE

# IQM2 aka Accela is a municipal meeting management platform that
# (among other things) stores livestreamed video from municipal
# meetings.  After a hefty (several-hour) processing time, that video
# is avaialble in easily downloadable form from their web portal, but
# prior to that, the video can only be watched in realtime through
# JWPlayer. This extractor is designed to download the realtime video
# prior to download links being available. See:
#   http://www.iqm2.com/About/Accela.aspx
#   http://www.accela.com/

# This makes it challenging to produce a test case for, because the
# extractor will want to follow the processed and easily downloadble
# version. So there may be interesting bugs during the race condition
# time before the processed video is available (which is really the
# only time this extractor is especially important).

# This is also a relatively braindead extractor. It parses a given page like
#   http://cambridgema.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID=1679#
# to determine the location of an inner div defined by a URL of the form
#   http://cambridgema.iqm2.com/Citizens/VideoScreen.aspx?MediaID=1563&Frame=SplitView

# and then simply hands that URL to the generic extractor, which
# matches it under the "Broaden the findall a little bit: JWPlayer JS
# loader" (line 2372 as of 6 Oct 2016).

# It appears that the metadata associated with the video (like it's
# title) does not appear anywhere in the 2 HTML pages that get
# downloaded through this extractor. So it would need to download
# additional HTTP resources in order to get appropriate metadata.

# This also appears to be the only example to date of an extractor
# that calls-out to the GenericIE generic extractor, so it may be
# useful as an example. Or perhaps it means that there's a better way
# to do this and it should be rewritten differently, esp. to not
# leverage the generic.

# Contributed by John Hawkinson <jhawk@mit.edu>, 6 Oct 2016.

# Potential test URLs:
# http://cambridgema.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID=1679
# https://CambridgeMA.IQM2.com/Citizens/VideoMain.aspx?MeetingID=1679

class IQM2IE(InfoExtractor):

    # xxx is really right that InfoExtractor.suitable() calls re.compile()
    # on _VALID_URL in a case-sensitive fashion? It's obviously reasonable
    # for the path portion of a URL to be case-sensitive, but the hostname
    # ought not to be. And it seems like strict adherence might mess up a
    # bunch of extractors in funny-cased URLs? Redefine suitable() to search
    # case-insentitively. Note this also changes the re.match() call at the
    # start of _real_extract()
    #
    # In this case, we commonly see both iqm2.com and IQM2.com
    
    @classmethod
    def suitable(cls, url):
        """Receives a URL and returns True if suitable for this IE."""

        # This does not use has/getattr intentionally - we want to know whether
        # we have cached the regexp for *this* class, whereas getattr would also
        # match the superclass
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = re.compile(cls._VALID_URL, flags=re.IGNORECASE)
        return cls._VALID_URL_RE.match(url) is not None

    _VALID_URL = r'https?://(?:\w+\.)?iqm2\.com/Citizens/\w+.aspx\?.*MeetingID=(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://cambridgema.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID=1679#',
        'md5': '478ea30eee1966f7be0d8dd623122148',
        'info_dict': {
            'id': '1563_720',
            'ext': 'mp4',
            'title': 'Cambridge, MA (2)',
            'uploader': 'cambridgema.iqm2.com',
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url, flags=re.IGNORECASE)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)
        # title = self._html_search_regex(r'<h1>(.*?)</h1>', webpage, 'title')
        title = 'Video title goes here'

        purl = compat_urllib_parse_urlparse(url)
        hostname = purl.hostname
        print "URL is", url, "at", hostname
        nurl = self._html_search_regex(r'<div id="VideoPanelInner".*src="([^"]+)"',
                                      webpage, 'url');
        print "URL is", nurl
        nnurl = purl.scheme+'://'+purl.netloc+nurl
        print "URL is", nnurl

        return GenericIE(self._downloader)._real_extract(nnurl)
