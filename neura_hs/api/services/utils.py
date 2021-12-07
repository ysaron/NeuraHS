
def generate_choicefield_description(model, enum_choice: str) -> str:
    """
    Generates the description of the filtering fields for the API documentation generator
    :param model: Filtered model
    :param enum_choice: Enum with options defined in the model (subclass of django.db.models.TextChoices)
    """
    enum_choices = getattr(model, enum_choice, None)
    if not enum_choices:
        return 'Description is not provided'
    choices = enum_choices.choices
    choices = '\n'.join([f'value: {val}, description: {desc}' for val, desc in choices if val])
    return choices
