import json
import time
import sys
from flask import render_template
from rq import get_current_job
from application import create_app, db
from application.models import Post, Task, User
from application.email import send_email


app = create_app(ProductionConfig)  # separate app for separate processes
app.app_context().push()
'''pushing a context makes the app "current" app instance thus enabling
extensions (Flask-SQLAlchemy, etc) to use current_app.config to get their
configuration
'''


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()
        # need to be careful that the parent task does not change the database
        # b/c this commmit would write those as well as the notification and
        # task complete


def export_posts(user_id):
    # needs to capture unexpected errors b/c RQ does not catch exceptions the
    # way Flask does (in RQ, errors need to be logged to a file)
    try:
        #  read user posts from database
        user = User.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Post.timestamp.asc()):
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
                         #  Z indicates UTC timezone
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)
        # send email with data to user
        send_email('[Microblog] Your blog posts',
            sender=app.config['ADMINS'][0], recipients=[user.email],
            text_body=render_template('email/export_posts.txt', user=user),
            html_body=render_template('email/export_posts.html', user=user),
            attachments=[('posts.json', 'application/json',
                          json.dumps({'posts': data}, indent=4))],
            sync=True)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
