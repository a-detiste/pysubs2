import re

from .time import times_to_ms
from .formatbase import FormatBase
from .ssaevent import SSAEvent


# thanks to http://otsaloma.io/gaupol/doc/api/aeidon.files.mpl2_source.html
MPL2_FORMAT = re.compile(r"^\[(-?\d+)\]\[(-?\d+)\](.*)", re.MULTILINE)


class MPL2Format(FormatBase):
    """MPL2 subtitle format implementation"""
    @classmethod
    def guess_format(cls, text):
        """See :meth:`pysubs2.formats.FormatBase.guess_format()`"""
        if MPL2_FORMAT.search(text):
            return "mpl2"

    @classmethod
    def from_file(cls, subs, fp, format_, **kwargs):
        """See :meth:`pysubs2.formats.FormatBase.from_file()`"""
        def prepare_text(lines: str) -> str:
            out = []
            for s in lines.split("|"):
                s = s.strip()

                if s.startswith("/"):
                    # line beginning with '/' is in italics
                    s = r"{\i1}%s{\i0}" % s[1:].strip()

                out.append(s)
            return "\\N".join(out)

        text = fp.read()
        for start, end, text in MPL2_FORMAT.findall(text):
            e = SSAEvent(
                start=times_to_ms(s=float(start) / 10),
                end=times_to_ms(s=float(end) / 10),
                text=prepare_text(text)
            )
            subs.append(e)

    @classmethod
    def to_file(cls, subs, fp, format_, **kwargs):
        """
        See :meth:`pysubs2.formats.FormatBase.to_file()`

        No styling is supported at the moment.

        """
        # TODO handle italics
        for line in subs.get_text_events():
            start = int(line.start // 100)
            end = int(line.end // 100)
            text = line.plaintext.replace("\n", "|")
            print(f"[{start}][{end}] {text}", file=fp)
