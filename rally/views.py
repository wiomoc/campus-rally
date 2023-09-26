from dataclasses import asdict

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.template import loader
from django.utils.safestring import SafeString
from django_htmx.middleware import HtmxDetails

from .models import Group
from .track_controller import track_controller, TrackElement


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def render_track_element(track_element: TrackElement):
    return loader.render_to_string("element.html", {"id": track_element.id,
                                                    "type": track_element.type.value,
                                                    "text": SafeString(track_element.text),
                                                    "hint": track_element.hint,
                                                    "location": track_element.location})


def index(request: HtmxHttpRequest) -> HttpResponse:
    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "_base.html"

    def render_login(error=None):
        return render(
            request,
            "login.html",
            {
                "base_template": base_template,
                "error": error,
            },
        )

    group_id = request.session.get("group_id")
    if group_id is None:
        entered_group_id = request.POST.get("group_id")
        if entered_group_id is None:
            return render_login()
        group = Group.objects.filter(public_id=entered_group_id).first()
        if group is None:
            return render_login("Gruppen-ID nicht valide.")
        request.session["group_id"] = group_id = entered_group_id
    else:
        group = Group.objects.get(public_id=group_id)

    current_element_index, current_element = track_controller.get_current_element(group)
    return render(
        request,
        "track_element_holder.html",
        {
            "base_template": base_template,
            "content": SafeString(render_track_element(current_element)),
            "group_id": group_id,
        },
    )
