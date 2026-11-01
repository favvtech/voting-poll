from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PollForm
from .models import Choice, Poll

RECENT_POLL_LIMIT = 10


def _has_voted(request, poll_id):
    return poll_id in request.session.get('voted_polls', [])


def _mark_voted(request, poll_id):
    voted = request.session.get('voted_polls', [])
    voted.append(poll_id)
    request.session['voted_polls'] = voted


def _results_data(poll):
    choices = list(poll.choices.all())
    total = sum(choice.votes for choice in choices)
    top = max((choice.votes for choice in choices), default=0)
    return {
        'question': poll.question,
        'total': total,
        'last_vote_at': poll.last_vote_at.isoformat() if poll.last_vote_at else None,
        'choices': [
            {
                'id': choice.id,
                'text': choice.text,
                'votes': choice.votes,
                'percent': round(choice.votes * 100 / total, 1) if total else 0.0,
                'leading': top > 0 and choice.votes == top,
            }
            for choice in choices
        ],
    }


def home(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                poll = Poll.objects.create(question=form.cleaned_data['question'])
                Choice.objects.bulk_create(
                    Choice(poll=poll, text=text) for text in form.cleaned_data['options']
                )
            messages.success(request, 'Your poll is ready. Share the link below!')
            return redirect('polls:vote', poll_id=poll.id)
    else:
        form = PollForm()

    recent_polls = Poll.objects.annotate(total=Sum('choices__votes'))[:RECENT_POLL_LIMIT]
    return render(request, 'polls/home.html', {'form': form, 'recent_polls': recent_polls})


def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    already_voted = _has_voted(request, poll.id)

    if request.method == 'POST':
        if already_voted:
            messages.info(request, 'You have already voted in this poll.')
            return redirect('polls:results', poll_id=poll.id)

        choice_id = request.POST.get('choice')
        updated = 0
        if choice_id and choice_id.isdigit():
            with transaction.atomic():
                updated = Choice.objects.filter(pk=int(choice_id), poll=poll).update(
                    votes=F('votes') + 1
                )
                if updated:
                    Poll.objects.filter(pk=poll.pk).update(last_vote_at=timezone.now())

        if updated:
            _mark_voted(request, poll.id)
            messages.success(request, 'Thanks! Your vote was counted.')
            return redirect('polls:results', poll_id=poll.id)

        messages.error(request, 'Please pick one of the options before voting.')

    share_url = request.build_absolute_uri(poll.get_absolute_url())
    return render(
        request,
        'polls/vote.html',
        {'poll': poll, 'already_voted': already_voted, 'share_url': share_url},
    )


def results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    data = _results_data(poll)
    share_url = request.build_absolute_uri(poll.get_absolute_url())
    return render(
        request,
        'polls/results.html',
        {
            'poll': poll,
            'data': data,
            'already_voted': _has_voted(request, poll.id),
            'share_url': share_url,
        },
    )


def results_json(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return JsonResponse(_results_data(poll))
