from django import forms

MIN_OPTIONS = 2
MAX_OPTIONS = 6


class PollForm(forms.Form):
    question = forms.CharField(
        max_length=200,
        error_messages={'required': 'Please enter a question.'},
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Where should we eat on Friday?'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, MAX_OPTIONS + 1):
            self.fields[f'option_{i}'] = forms.CharField(
                max_length=100,
                required=False,
                label=f'Option {i}',
                widget=forms.TextInput(attrs={'aria-label': f'Option {i}'}),
            )

    def option_fields(self):
        return [self[f'option_{i}'] for i in range(1, MAX_OPTIONS + 1)]

    def clean_question(self):
        question = self.cleaned_data['question'].strip()
        if not question:
            raise forms.ValidationError('Please enter a question.')
        return question

    def clean(self):
        cleaned = super().clean()
        options = []
        seen = set()
        for i in range(1, MAX_OPTIONS + 1):
            text = (cleaned.get(f'option_{i}') or '').strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                raise forms.ValidationError(f'The option "{text}" is listed more than once.')
            seen.add(key)
            options.append(text)

        if len(options) < MIN_OPTIONS:
            raise forms.ValidationError(f'Please enter at least {MIN_OPTIONS} options.')

        cleaned['options'] = options
        return cleaned
