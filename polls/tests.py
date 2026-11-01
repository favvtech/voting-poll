from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Poll


def make_poll(question='Best fruit?', options=('Apple', 'Banana', 'Cherry')):
    poll = Poll.objects.create(question=question)
    for text in options:
        Choice.objects.create(poll=poll, text=text)
    return poll


class CreatePollTests(TestCase):
    def post(self, **data):
        return self.client.post(reverse('polls:home'), data)

    def test_home_page_lists_recent_polls(self):
        make_poll('Favorite color?')
        response = self.client.get(reverse('polls:home'))
        self.assertContains(response, 'Favorite color?')

    def test_valid_poll_is_created_and_redirects_to_vote_page(self):
        response = self.post(question='Lunch?', option_1='Pizza', option_2='Tacos', option_3='')
        poll = Poll.objects.get()
        self.assertRedirects(response, reverse('polls:vote', args=[poll.id]))
        self.assertEqual(poll.question, 'Lunch?')
        self.assertEqual([c.text for c in poll.choices.all()], ['Pizza', 'Tacos'])

    def test_empty_question_is_rejected(self):
        response = self.post(question='   ', option_1='A', option_2='B')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a question.')
        self.assertFalse(Poll.objects.exists())

    def test_fewer_than_two_options_is_rejected(self):
        response = self.post(question='Lunch?', option_1='Pizza', option_2='  ')
        self.assertContains(response, 'Please enter at least 2 options.')
        self.assertFalse(Poll.objects.exists())

    def test_duplicate_options_are_rejected(self):
        response = self.post(question='Lunch?', option_1='Pizza', option_2='pizza')
        self.assertContains(response, 'is listed more than once')
        self.assertFalse(Poll.objects.exists())


class VoteTests(TestCase):
    def setUp(self):
        self.poll = make_poll()
        self.apple, self.banana, _ = self.poll.choices.all()
        self.url = reverse('polls:vote', args=[self.poll.id])

    def test_vote_page_shows_question_and_options(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Best fruit?')
        self.assertContains(response, 'Banana')
        self.assertContains(response, 'Copy link')

    def test_vote_is_counted_and_redirects_to_results(self):
        response = self.client.post(self.url, {'choice': self.banana.id})
        self.assertRedirects(response, reverse('polls:results', args=[self.poll.id]))
        self.banana.refresh_from_db()
        self.assertEqual(self.banana.votes, 1)

    def test_vote_records_last_vote_time(self):
        self.assertIsNone(self.poll.last_vote_at)
        before = timezone.now()
        self.client.post(self.url, {'choice': self.banana.id})
        self.poll.refresh_from_db()
        self.assertIsNotNone(self.poll.last_vote_at)
        self.assertGreaterEqual(self.poll.last_vote_at, before)

    def test_rejected_votes_do_not_change_last_vote_time(self):
        self.client.post(self.url, {})
        self.poll.refresh_from_db()
        self.assertIsNone(self.poll.last_vote_at)

        self.client.post(self.url, {'choice': self.banana.id})
        self.poll.refresh_from_db()
        first_vote_at = self.poll.last_vote_at
        self.client.post(self.url, {'choice': self.apple.id})
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.last_vote_at, first_vote_at)

    def test_second_vote_from_same_browser_is_blocked(self):
        self.client.post(self.url, {'choice': self.banana.id})
        self.client.post(self.url, {'choice': self.apple.id})
        self.apple.refresh_from_db()
        self.banana.refresh_from_db()
        self.assertEqual((self.apple.votes, self.banana.votes), (0, 1))
        self.assertContains(self.client.get(self.url), 'already voted')

    def test_different_browsers_can_each_vote(self):
        self.client.post(self.url, {'choice': self.banana.id})
        self.client_class().post(self.url, {'choice': self.banana.id})
        self.banana.refresh_from_db()
        self.assertEqual(self.banana.votes, 2)

    def test_missing_choice_shows_error(self):
        response = self.client.post(self.url, {})
        self.assertContains(response, 'Please pick one of the options')

    def test_choice_from_another_poll_is_ignored(self):
        other = make_poll('Other?', ('X', 'Y'))
        other_choice = other.choices.first()
        self.client.post(self.url, {'choice': other_choice.id})
        other_choice.refresh_from_db()
        self.assertEqual(other_choice.votes, 0)


class ResultsTests(TestCase):
    def setUp(self):
        self.poll = make_poll(options=('Apple', 'Banana', 'Cherry', 'Date'))
        votes = [3, 1, 0, 0]
        for choice, count in zip(self.poll.choices.all(), votes):
            choice.votes = count
            choice.save()

    def test_results_page_shows_counts_and_percentages(self):
        response = self.client.get(reverse('polls:results', args=[self.poll.id]))
        self.assertContains(response, 'Apple')
        self.assertContains(response, '75.0')
        self.assertContains(response, 'results.js')

    def test_results_page_without_votes_says_so(self):
        poll = make_poll('Empty?', ('A', 'B'))
        response = self.client.get(reverse('polls:results', args=[poll.id]))
        self.assertContains(response, 'No votes yet')

    def test_results_json_includes_last_vote_time(self):
        voted_at = timezone.now()
        Poll.objects.filter(pk=self.poll.pk).update(last_vote_at=voted_at)
        data = self.client.get(reverse('polls:results_json', args=[self.poll.id])).json()
        self.assertEqual(data['last_vote_at'], voted_at.isoformat())

    def test_results_json(self):
        response = self.client.get(reverse('polls:results_json', args=[self.poll.id]))
        data = response.json()
        self.assertEqual(data['question'], 'Best fruit?')
        self.assertEqual(data['total'], 4)
        self.assertEqual(
            [(c['text'], c['votes'], c['percent']) for c in data['choices']],
            [('Apple', 3, 75.0), ('Banana', 1, 25.0), ('Cherry', 0, 0), ('Date', 0, 0)],
        )
        self.assertEqual([c['leading'] for c in data['choices']], [True, False, False, False])

    def test_results_json_with_no_votes(self):
        poll = make_poll('Empty?', ('A', 'B'))
        data = self.client.get(reverse('polls:results_json', args=[poll.id])).json()
        self.assertEqual(data['total'], 0)
        self.assertIsNone(data['last_vote_at'])
        self.assertEqual([c['percent'] for c in data['choices']], [0, 0])
        self.assertEqual([c['leading'] for c in data['choices']], [False, False])


class NotFoundTests(TestCase):
    def test_missing_poll_returns_404(self):
        for name in ('polls:vote', 'polls:results', 'polls:results_json'):
            response = self.client.get(reverse(name, args=[9999]))
            self.assertEqual(response.status_code, 404, name)
