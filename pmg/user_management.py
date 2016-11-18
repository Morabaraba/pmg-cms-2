import logging
from ga import ga_event
from collections import defaultdict

from flask import render_template, request, redirect, abort, flash, jsonify
from flask.ext.security import current_user, login_required

from pmg import app, db
from pmg.api.client import load_from_api
from pmg.models import Committee, CommitteeMeeting, SavedSearch
import pmg.models.serializers as serializers

logger = logging.getLogger(__name__)


@app.route('/email-alerts/', methods=['GET', 'POST'])
def email_alerts():
    """
    Allow a user to manage their notification alerts.
    """
    next_url = request.values.get('next', '')

    if current_user.is_authenticated() and request.method == 'POST':
        ids = request.form.getlist('committees')
        current_user.committee_alerts = Committee.query.filter(Committee.id.in_(ids)).all()
        current_user.subscribe_daily_schedule = bool(request.form.get('subscribe_daily_schedule'))

        db.session.commit()

        # register a google analytics event
        ga_event('user', 'change-alerts')

        if next_url:
            return redirect(next_url)

        return ''

    committees = load_from_api('v2/committees', return_everything=True)['results']
    if current_user.is_authenticated():
        subscriptions = set(c.id for c in current_user.committee_alerts)
    else:
        subscriptions = set()

    saved_searches = defaultdict(list)
    if current_user.is_authenticated():
        for ss in current_user.saved_searches:
            saved_searches[ss.search].append(ss)

    return render_template(
        'user_management/email_alerts.html',
        committees=committees,
        after_signup=bool(next_url),
        subscriptions=subscriptions,
        next_url=next_url,
        saved_searches=saved_searches)


@app.route('/user/committee/alerts/add/<int:committee_id>', methods=['POST'])
def user_add_committee_alert(committee_id):
    if current_user.is_authenticated() and request.method == 'POST':
        current_user.committee_alerts.append(Committee.query.get(committee_id))
        db.session.commit()
        ga_event('user', 'add-alert', 'cte-alert-box')
        flash("We'll send you email alerts for updates on this committee.", 'success')

    return redirect(request.headers.get('referer', '/'))

@app.route('/user/committee/alerts/remove/<int:committee_id>', methods=['POST'])
def user_remove_committee_alert(committee_id):
    if current_user.is_authenticated() and request.method == 'POST':
        current_user.committee_alerts.remove(Committee.query.get(committee_id))
        db.session.commit()
        ga_event('user', 'remove-alert', 'cte-alert-box')
        flash("We'll send you email alerts for updates on this committee.", 'success')

    return redirect(request.headers.get('referer', '/'))

@app.route('/user/follow/committee/<int:committee_id>', methods=['POST'])
def user_follow_committee(committee_id):
    if current_user.is_authenticated() and request.method == 'POST':
        committee = Committee.query.get(committee_id)
        current_user.follow_committee(committee)
        current_user.committee_alerts.append(committee)
        db.session.commit()
        ga_event('user', 'follow-committee', 'cte-follow-committee')

    return redirect(request.headers.get('referer', '/'))

@app.route('/user/unfollow/committee/<int:committee_id>', methods=['POST'])
def user_unfollow_committee(committee_id):
    if current_user.is_authenticated() and request.method == 'POST':
        committee = Committee.query.get(committee_id)
        current_user.unfollow_committee(committee)

        if committee in current_user.committee_alerts:
            current_user.committee_alerts.remove(committee)
        db.session.commit()
        ga_event('user', 'unfollow-committee', 'cte-follow-committee')

    return redirect(request.headers.get('referer', '/'))

@app.route('/user/followed/committee/meetings/')
def user_followed_committee_meetings():
    if current_user.is_authenticated():
        return jsonify(data=current_user.get_followed_committee_meetings().data)
    else:
        abort(404)

@app.route('/committee-subscriptions/', methods=['GET', 'POST'])
def committee_subscriptions():
    """
    Manage subscriptions to premium content.
    """

    premium_committees = load_from_api('committee/premium', return_everything=True)['results']
    return render_template('user_management/committee_subscriptions.html', premium_committees=premium_committees)


@app.route('/user/saved-search/', methods=['POST'])
@login_required
def create_search():
    saved_search = SavedSearch.find_or_create(
        current_user,
        request.form.get('q'),
        content_type=request.form.get('content_type') or None,
        committee_id=request.form.get('committee_id') or None)

    db.session.commit()

    return jsonify(id=saved_search.id)


@app.route('/user/saved-search/<int:id>/delete', methods=['POST'])
@login_required
def remove_search(id):
    saved_search = SavedSearch.query.get(id)
    if not saved_search or current_user != saved_search.user:
        abort(404)
    db.session.delete(saved_search)
    db.session.commit()

    return ''
