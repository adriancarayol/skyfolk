from django.forms import BooleanField


class OppositeBooleanField(BooleanField):
    def prepare_value(self, value):
        return not value  # toggle the value when loaded from the model

    def to_python(self, value):
        value = super(OppositeBooleanField, self).to_python(value)
        return not value  # toggle the incoming value from form submission


def get_form_errors(form):
    list_errors = []
    for field, errors in form.errors.items():
        list_errors.append(", ".join(errors))
    return list_errors
