from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

choices_yes_no = {
    True: (1, 'Yes'),
    False: (0, 'No')
}

class Page(FlaskForm):
    """Create a new page, with content and everything."""
    path = StringField(
        "Where should this article be located?",
        validators = [
            DataRequired(),
            Regexp(r"^[A-Za-z\d$-.+!*'(), \/]+$", message="Use only letters, numbers, spaces, and the following sympols: A-Za-z\d$-.+!*'(),/")
        ]
    )
    title = StringField(
        "What should the title of your article be?",
        validators = [
            DataRequired(),
            Length(min=3, max=255, message="The title must be between 3 and 255 characters"),
            Regexp(r"^[A-Za-z\d$-.+!*'(), ]+$", message="Use only letters, numbers, spaces, and the following sympols: A-Za-z\d$-.+!*'(),")
        ]
    )
    public = SelectField(
        "Should this article be accessible by people other than you?",
        choices = list(choices_yes_no.values()),
        coerce = lambda x: bool(int(x)),
    )
    text = TextAreaField(
        "Using markdown syntax, enter the page content below.",
        validators = [Optional()]
    )
    submit = SubmitField("Create Article")

    def from_obj(self, page):
        """ Takes vars(models.Page) and fills in the proper stuff. """
        self.title.data = page.title
        self.public.data = choices_yes_no.get(page.public)
        self.text.data = page.text

class Project(FlaskForm):
    """ Create a new project, in which to create pages. """
    title = StringField(
        "Choose a short and snappy title for your project!",
        validators = [
            DataRequired(),
            Length(min=3, max=255, message="The title must be between 3 and 255 characters"),
            Regexp(r"^[A-Za-z\d$-.+!*'(), ]+$", message="Use only letters, numbers, spaces, and the following sympols: A-Za-z\d$-.+!*'(),")
        ]
    )
    public = SelectField(
        "Should this project appear in searches and be accessible by people other than you?",
        choices = list(choices_yes_no.values()),
        coerce = lambda x: bool(int(x)),
    )
    text = TextAreaField(
        "Give a description of your project.",
        validators = [Optional()]
    )
    submit = SubmitField("Create Project")

    def from_obj(self, page):
        """ Takes vars(models.Page) and fills in the proper stuff. """
        self.title.data = page.title
        self.public.data = choices_yes_no.get(page.public)
        self.text.data = page.text

class SearchBar(FlaskForm):
    """Search box in navbar for pages."""
    input = StringField(
        'Search Box'
    )