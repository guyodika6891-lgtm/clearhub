import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    BooleanField, SubmitField, DateField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional, ValidationError
)


def strong_password(form, field):
    pw = field.data or ""
    errors = []
    if len(pw) < 8:
        errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", pw):
        errors.append("one uppercase letter")
    if not re.search(r"[a-z]", pw):
        errors.append("one lowercase letter")
    if not re.search(r"\d", pw):
        errors.append("one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", pw):
        errors.append("one special character")
    if errors:
        raise ValidationError("Password must contain: " + ", ".join(errors))


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 40)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(2, 120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(5, 120)])
    student_id = StringField("Student ID", validators=[Optional(), Length(0, 40)])
    phone = StringField("Phone", validators=[Optional(), Length(0, 30)])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 100), strong_password])
    confirm = PasswordField("Confirm", validators=[DataRequired(), EqualTo("password")])
    role = SelectField("I am a",
                       choices=[("student", "Student"), ("staff", "Staff")],
                       validators=[DataRequired()])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField("Login")


class ClearanceRequestForm(FlaskForm):
    semester_id = SelectField("Semester", coerce=int, validators=[DataRequired()])
    reason = TextAreaField("Reason for clearance",
                           validators=[Optional(), Length(0, 500)])
    submit = SubmitField("Submit Request")


class StepReviewForm(FlaskForm):
    status = SelectField("Decision",
                         choices=[("approved", "Approve"), ("rejected", "Reject")],
                         validators=[DataRequired()])
    comment = TextAreaField("Comment / reason",
                            validators=[Optional(), Length(0, 500)])
    submit = SubmitField("Submit Decision")


class DocumentForm(FlaskForm):
    file = FileField("Document",
                     validators=[FileAllowed(["pdf", "png", "jpg", "jpeg"],
                                             "PDF or image only")])
    submit = SubmitField("Upload")


class DepartmentForm(FlaskForm):
    name = StringField("Department Name", validators=[DataRequired(), Length(2, 120)])
    code = StringField("Code", validators=[DataRequired(), Length(2, 10)])
    description = TextAreaField("Description", validators=[Optional(), Length(0, 300)])
    contact_email = StringField("Contact Email", validators=[Optional(), Email()])
    order_index = SelectField("Order",
                              choices=[(str(i), f"#{i}") for i in range(1, 21)],
                              validators=[DataRequired()])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Department")


class SemesterForm(FlaskForm):
    name = StringField("Semester Name", validators=[DataRequired(), Length(2, 80)])
    start_date = DateField("Start Date", validators=[Optional()])
    end_date = DateField("End Date", validators=[Optional()])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Semester")


class ProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[Optional(), Length(0, 120)])
    phone = StringField("Phone", validators=[Optional(), Length(0, 30)])
    student_id = StringField("Student ID", validators=[Optional(), Length(0, 40)])
    submit = SubmitField("Update Profile")