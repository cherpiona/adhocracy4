from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _

from . import forms, validators


class ConfiguredImageField(models.ImageField):

    def __init__(self, config_name, *args, **kwargs):
        defaults = {}
        self.config_name = config_name
        config = self.image_config

        if 'help_prefix' in kwargs:
            self.help_prefix = kwargs['help_prefix']
            del kwargs['help_prefix']
            defaults['help_text'] = self._help_text
        else:
            self.help_prefix = None

        defaults.update(kwargs)
        super().__init__(*args, **defaults)

    @property
    def validators(self):
        default_validators = super().validators
        image_validators = [
            lambda image: validators.validate_image(image, **self.image_config)
        ]
        image_validators.extend(default_validators)
        return image_validators

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        if self.help_prefix:
            del kwargs['help_text']
            kwargs['help_prefix'] = self.help_prefix

        return (name, path, [self.config_name], kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.ImageField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    @property
    def image_config(self):
        c = {}
        defaults = settings.IMAGE_ALIASES.get('*', {})
        c.update(defaults)
        c.update(settings.IMAGE_ALIASES[self.config_name])
        return c

    @property
    def _help_text(self):
        config = self.image_config

        help_text = _(
            '{help_prefix} It must be min. {min_resolution[0]} pixel wide and '
            '{min_resolution[1]} pixel tall. Allowed file formats are '
            '{fileformats_str}. The file size should be max. '
            '{max_size_mb} MB.'
        ).format(
            help_prefix=self.help_prefix,
            max_size_mb=int(self.image_config['max_size']/(10**6)),
            fileformats_str = ', '.join(
                f.split('/')[1] for f in config['fileformats']
            ),
            **config
        )
        return help_text