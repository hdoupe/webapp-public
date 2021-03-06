from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import validate_comma_separated_integer_list
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import make_aware
from django.utils.functional import cached_property
from django.core.urlresolvers import reverse
import uuid
from dataclasses import dataclass, field
from typing import List, Union


class CoreInputs(models.Model):
    raw_gui_field_inputs = JSONField(default=None, blank=True, null=True)
    gui_field_inputs = JSONField(default=None, blank=True, null=True)

    # Validated GUI input that has been parsed to have the correct data types,
    # or JSON reform uploaded as file
    inputs_file = JSONField(default=dict, blank=True, null=True)

    errors_warnings_text = JSONField(default=None, blank=True, null=True)

    # The parameters that will be used to run the model
    upstream_parameters = JSONField(default=dict, blank=True, null=True)

    # Starting year of the reform calculation
    first_year = models.IntegerField(default=None, null=True)

    # List of years for which to calculate the reform, as offsets from the
    # first year
    years_n = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=300)

    @cached_property
    def years(self):
        return [self.first_year + int(i) for i in self.years_n.split(",")]

    class Meta:
        abstract = True


class CoreRun(models.Model):
    # Subclasses must implement:
    # inputs = models.OneToOneField(CoreInputs)
    outputs = JSONField(default=None, blank=True, null=True)
    aggr_outputs = JSONField(default=None, blank=True, null=True)
    uuid = models.UUIDField(
        default=uuid.uuid1,
        editable=False,
        max_length=32,
        unique=True,
        primary_key=True)
    error_text = models.CharField(
        null=True,
        blank=True,
        default=None,
        max_length=4000)
    user = models.ForeignKey(User, null=True, default=None)
    creation_date = models.DateTimeField(
        default=make_aware(datetime.datetime(2015, 1, 1)))
    exp_comp_datetime = models.DateTimeField(
        default=make_aware(datetime.datetime(2015, 1, 1)))
    job_id = models.UUIDField(blank=True, default=None, null=True)
    upstream_vers = models.CharField(blank=True, default=None, null=True,
                                     max_length=50)
    webapp_vers = models.CharField(blank=True, default=None, null=True,
                                   max_length=50)

    def get_absolute_url(self):
        raise NotImplementedError()

    def get_absolute_edit_url(self):
        raise NotImplementedError()

    def get_absolute_download_url(self):
        raise NotImplementedError()

    def zip_filename(self):
        return 'policybrain.zip'

    class Meta:
        abstract = True


@dataclass
class Tag:
    key: str
    values: List['TagOption']
    hidden: bool = False

    def __post_init__(self):
        for option in self.values[1:]:
            for child in option.children:
                child.hidden = True


@dataclass
class TagOption:
    value: str
    title: str
    tooltip: Union[str, None] = None
    children: List[Tag] = field(default_factory=list)
