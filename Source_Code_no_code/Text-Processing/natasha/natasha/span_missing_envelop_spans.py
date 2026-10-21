
from .record import Record


class Span(Record):
    __attributes__ = ['start', 'stop', 'type']


def adapt_spans(spans):
    for span in spans:
        yield Span(span.start, span.stop, span.type)


def offset_spans(spans, offset):
    for span in spans:
        yield Span(
            offset + span.start,
            offset + span.stop,
            span.type
        )


def envelop_spans(spans, envelopes):
    """This function envelops the spans based on the given envelopes. It iterates through the spans and envelopes and yields the chunk of spans that are enveloped by each envelope.
    Input-Output Arguments
    :param spans: List of spans. The spans to be enveloped.
    :param envelopes: List of envelopes. The envelopes used to envelop the spans.
    :return: Yield the chunk of spans for each envelope.
    """