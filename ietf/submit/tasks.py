# Copyright The IETF Trust 2022, All Rights Reserved
#
# Celery task definitions
#
from celery import shared_task

from django.db.models import Min
from django.conf import settings
from django.utils import timezone

from ietf.submit.models import Submission
from ietf.submit.utils import (cancel_submission, create_submission_event, process_uploaded_submission,
                               process_and_accept_uploaded_submission)
from ietf.utils import log


@shared_task
def process_uploaded_submission_task(submission_id):
    try:
        submission = Submission.objects.get(pk=submission_id)
    except Submission.DoesNotExist:
        log.log(f'process_uploaded_submission_task called for missing submission_id={submission_id}')
    else:
        process_uploaded_submission(submission)


@shared_task
def process_and_accept_uploaded_submission_task(submission_id):
    try:
        submission = Submission.objects.get(pk=submission_id)
    except Submission.DoesNotExist:
        log.log(f'process_uploaded_submission_task called for missing submission_id={submission_id}')
    else:
        process_and_accept_uploaded_submission(submission)


@shared_task
def cancel_stale_submissions():
    now = timezone.now()
    stale_submissions = Submission.objects.filter(
        state_id='validating',
    ).annotate(
        submitted_at=Min('submissionevent__time'),
    ).filter(
        submitted_at__lt=now - settings.IDSUBMIT_MAX_VALIDATION_TIME,
    )
    for subm in stale_submissions:
        age = now - subm.submitted_at
        log.log(f'Canceling stale submission (id={subm.id}, age={age})')
        cancel_submission(subm)
        create_submission_event(None, subm, 'Submission canceled: validation checks took too long')


@shared_task(bind=True)
def poke(self):
    log.log(f'Poked {self.name}, request id {self.request.id}')
