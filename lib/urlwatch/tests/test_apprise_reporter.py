import datetime
import time
import types

import pytest

from urlwatch.handler import Report, JobState
from urlwatch.reporters import AppriseReporter


class DummyConfigStorage:
    def __init__(self, config):
        self.config = config


class DummyUrlwatchConfig:
    def __init__(self, config):
        self.config_storage = DummyConfigStorage(config)


class DummyJob:
    diff_tool = None
    diff_filter = []

    def pretty_name(self):
        return 'JobName'

    def get_location(self):
        return 'http://example.com'


def make_default_config():
    # Minimal default config structure required by reporters
    return {
        'display': {
            'new': True,
            'error': True,
            'unchanged': False,
            'empty-diff': True,
        },
        'report': {
            'text': {
                'line_length': 75,
                'details': True,
                'footer': True,
                'minimal': False,
                'separate': False,
            },
            'markdown': {
                'details': True,
                'footer': True,
                'minimal': False,
                'separate': False,
            },
            'html': {
                'diff': 'unified',
                'separate': False,
            },
            'apprise': {
                'enabled': True,
                'urls': [],
                'config_urls': [],
                'format': 'text',
                'subject': '{count} changes: {jobs}',
            },
        },
        'job_defaults': {
            'all': {},
            'shell': {},
            'url': {},
            'browser': {},
        },
    }


def create_job_state(verb, old_data='old', new_data='new'):
    js = JobState(None, DummyJob())
    js.verb = verb
    js.old_data = old_data
    js.new_data = new_data
    js.timestamp = time.time()
    return js


def test_apprise_no_changes_does_not_notify(monkeypatch):
    # Prepare dummy apprise module capturing instances
    created = []

    class DummyApprise:
        def __init__(self):
            self.urls = []
            self.notified = []

        def add(self, url):
            self.urls.append(url)

        def notify(self, **kwargs):
            self.notified.append(kwargs)
            return True

    dummy_mod = types.SimpleNamespace(
        Apprise=lambda: (created.append(DummyApprise()) or created[-1]),
        NotifyFormat=types.SimpleNamespace(TEXT='TEXT', MARKDOWN='MARKDOWN', HTML='HTML'),
    )
    monkeypatch.setattr('urlwatch.reporters.apprise', dummy_mod, raising=False)

    config = make_default_config()
    # unchanged events are hidden by default in display config
    js = create_job_state('unchanged', old_data='same', new_data='same')
    report = Report(DummyUrlwatchConfig(config))
    report.job_states = [js]

    rep_cfg = config['report']['apprise']
    reporter = AppriseReporter(report, rep_cfg, [js], datetime.timedelta(seconds=1))
    # Should return early before constructing Apprise instance
    assert reporter.submit() is None
    assert created == []


def test_apprise_notify_with_text_format(monkeypatch):
    created = []

    class DummyApprise:
        def __init__(self):
            self.urls = []
            self.notified = []

        def add(self, url):
            self.urls.append(url)

        def notify(self, **kwargs):
            self.notified.append(kwargs)
            return True

    dummy_mod = types.SimpleNamespace(
        Apprise=lambda: (created.append(DummyApprise()) or created[-1]),
        NotifyFormat=types.SimpleNamespace(TEXT='TEXT', MARKDOWN='MARKDOWN', HTML='HTML'),
    )
    monkeypatch.setattr('urlwatch.reporters.apprise', dummy_mod, raising=False)

    config = make_default_config()
    config['report']['apprise']['urls'] = ['discord://token']
    js = create_job_state('changed', old_data='a', new_data='b')
    report = Report(DummyUrlwatchConfig(config))
    report.job_states = [js]

    rep_cfg = config['report']['apprise']
    reporter = AppriseReporter(report, rep_cfg, [js], datetime.timedelta(seconds=1))
    reporter.submit()

    assert len(created) == 1
    inst = created[0]
    assert inst.urls == ['discord://token']
    assert len(inst.notified) == 1
    n = inst.notified[0]
    assert n['title'] == '1 changes: JobName'
    assert n['body']
    assert n['body_format'] == dummy_mod.NotifyFormat.TEXT


def test_apprise_notify_markdown_format(monkeypatch):
    created = []

    class DummyApprise:
        def __init__(self):
            self.urls = []
            self.notified = []

        def add(self, url):
            self.urls.append(url)

        def notify(self, **kwargs):
            self.notified.append(kwargs)
            return True

    dummy_mod = types.SimpleNamespace(
        Apprise=lambda: (created.append(DummyApprise()) or created[-1]),
        NotifyFormat=types.SimpleNamespace(TEXT='TEXT', MARKDOWN='MARKDOWN', HTML='HTML'),
    )
    monkeypatch.setattr('urlwatch.reporters.apprise', dummy_mod, raising=False)

    # Work around MarkdownReporter.submit expecting a numeric max_length
    import urlwatch.reporters as reporters_mod
    _orig_md_submit = reporters_mod.MarkdownReporter.submit

    def _patched_md_submit(self, max_length=None):
        return _orig_md_submit(self, max_length=100000)

    monkeypatch.setattr(reporters_mod.MarkdownReporter, 'submit', _patched_md_submit, raising=True)

    config = make_default_config()
    config['report']['apprise']['format'] = 'markdown'
    js = create_job_state('changed', old_data='x', new_data='y')
    report = Report(DummyUrlwatchConfig(config))
    report.job_states = [js]

    rep_cfg = config['report']['apprise']
    reporter = AppriseReporter(report, rep_cfg, [js], datetime.timedelta(seconds=1))
    reporter.submit()

    inst = created[0]
    assert inst.notified[0]['body_format'] == dummy_mod.NotifyFormat.MARKDOWN


def test_apprise_missing_module_is_graceful(monkeypatch):
    # Simulate apprise not installed
    monkeypatch.setattr('urlwatch.reporters.apprise', None, raising=False)

    config = make_default_config()
    js = create_job_state('changed', old_data='1', new_data='2')
    report = Report(DummyUrlwatchConfig(config))
    report.job_states = [js]

    rep_cfg = config['report']['apprise']
    reporter = AppriseReporter(report, rep_cfg, [js], datetime.timedelta(seconds=1))
    # Should not raise
    reporter.submit()
