from django.contrib import admin
from django.db import models
from django.forms import ModelForm, ChoiceField, Media
from django.http import HttpResponse
from django.utils.safestring import SafeString

from .models import Group, TrackElementGroupAnswer
from .track_controller import track_controller


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["public_id", "current_element_id", "starting_element_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        element_ids = [(element.id, element.id) for element in track_controller.track_elements]

        self.fields['current_element_id'] = ChoiceField(
            choices=[(track_controller.start_track_element.id, track_controller.start_track_element.id),
                     (track_controller.end_track_element.id, track_controller.end_track_element.id)] + element_ids)
        self.fields['starting_element_id'] = ChoiceField(choices=element_ids)


class GroupAdmin(admin.ModelAdmin):
    fields = ["public_id", "current_element_id", "starting_element_id"]
    list_display = ["public_id", "current_element_id", "score", "progress"]
    form = GroupForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(score=models.Sum('trackelementgroupanswer__score'))
        return qs

    def score(self, obj):
        return obj.score

    score.admin_order_field = 'score'

    def progress(self, obj):
        from rally.track_controller import track_controller
        return f"{track_controller.get_progress(obj) * 100:0.1f} %"


admin.site.register(Group, GroupAdmin)


class TrackElementGroupAnswerAdmin(admin.ModelAdmin):
    list_display = ["element_id", "group", "date_finished", "answer", "score_selector", "hint_used"]

    def score_selector(self, obj):
        score = obj.score

        def score_radio(value):
            return f"""
         <label for="score-{obj.pk}-{value}">{value}</label>
         <input type="radio" id="score-{obj.pk}-{value}" name="score-{obj.pk}" value="{value}" {"checked" if score == value else ""} onchange="scoreChange({obj.pk}, {value})">
         """

        return SafeString(score_radio(0) + score_radio(1) + score_radio(2) + "<br>" + score_radio(3) + score_radio(4))

    score_selector.admin_order_field = 'score'

    def response_action(self, request, queryset):
        if request.POST["action"] == "set_score":
            score = int(request.POST["value"])
            queryset.filter(id=request.POST["_selected_action"]).update(score=score)
            return HttpResponse(status=204)
        return super().response_action(request, queryset)

    @property
    def media(self):
        base_media = super().media
        return base_media + Media(js=["score_updater.js"])


admin.site.register(TrackElementGroupAnswer, TrackElementGroupAnswerAdmin)
