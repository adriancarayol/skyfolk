from django import forms


class DashboardEntryMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop("user_id")
        super().__init__(*args, **kwargs)
