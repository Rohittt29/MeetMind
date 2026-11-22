from concurrent.futures import ThreadPoolExecutor

from meeting_analysis import Drafts, draft_emails, score_meeting


class Recovery:
    """One session's independent section jobs for a single extracted transcript."""

    def __init__(self, notes, transcript):
        self.notes = notes
        self.transcript = transcript
        self.drafts = Drafts(emails=[])
        self.quality = None
        self.jobs = {}
        self.failed = set()
        self.corrected_owners = set()

    def start(self, section, key, model):
        if section in self.jobs:
            return
        self.failed.discard(section)
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            if section == "emails":
                self.jobs[section] = executor.submit(draft_emails, self.notes.model_copy(deep=True), key, model)
            else:
                self.jobs[section] = executor.submit(score_meeting, self.transcript, key, model)
        finally:
            executor.shutdown(wait=False)

    def collect(self):
        changed = False
        for section, job in list(self.jobs.items()):
            if not job.done():
                continue
            del self.jobs[section]
            changed = True
            try:
                result = job.result()
            except Exception:
                self.failed.add(section)
                continue
            if section == "emails":
                # Corrections may have created or edited local drafts during generation.
                self.drafts.emails.extend(e for e in result.emails if e.owner not in self.corrected_owners)
            else:
                self.quality = result
        return changed

    @property
    def missing(self):
        return self.failed.union(self.jobs)
