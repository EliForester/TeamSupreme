from django.contrib.auth.forms import UserCreationForm
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import UploadedFile
from django.forms import (FileInput, Form, ImageField, ModelForm,
                          ModelMultipleChoiceField, Textarea, ValidationError,
                          inlineformset_factory)

from .models import Position, Project, Skill, User

VALID_IMG_FORMATS = ['image/jpeg', 'image/png', 'image/gif']
VALID_IMG_WIDTH = 200
VALID_IMG_HEIGHT = 300
MAX_IMG_SIZE = 100  # in kb


class UserCreateForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class UserProfileUpdateForm(ModelForm):
    avatar = ImageField(required=False, widget=FileInput)

    def clean_avatar(self):
        '''
        Make sure that avatar fits defined file format and size
        :return: avatar file
        '''
        avatar = self.cleaned_data.get('avatar', False)
        if avatar and isinstance(avatar, UploadedFile):
            if avatar.size > MAX_IMG_SIZE * 1024:
                raise ValidationError(
                    'Image files should be less than {} kB'.format(
                        str(MAX_IMG_SIZE)))
            w, h = get_image_dimensions(avatar)
            if avatar.content_type not in VALID_IMG_FORMATS:
                raise ValidationError(
                    'Avatar must be .png, .jpg or .gif format')
            if w >= VALID_IMG_WIDTH or h >= VALID_IMG_HEIGHT:
                raise ValidationError(
                    'Avatars should be within {} and {} pixels'.format(
                        str(VALID_IMG_WIDTH), str(VALID_IMG_HEIGHT)))
            return avatar

    class Meta:
        model = User
        fields = ['bio', 'avatar', 'profile', 'skills']
        widgets = {
            'bio': Textarea(attrs={'rows': 4, 'cols': 5}),
            'profile': Textarea(attrs={'rows': 5, 'cols': 20})
        }


class PositionForm(ModelForm):

    class Meta:
        model = Position
        exclude = ()


PositionFormSet = inlineformset_factory(Project,
                                        Position,
                                        form=PositionForm,
                                        extra=2)


class SkillCreateForm(ModelForm):
    class Meta:
        model = Skill
        exclude = ()


class SkillFilterForm(Form):
    skills = ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'))
